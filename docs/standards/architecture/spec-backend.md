---
type: standard
title: Spec backend interface
description: The spec store is a git branch holding the canonical documents, with thin tracker cards as a projection written at lifecycle transitions; five document primitives, one ID identity and one refusal boundary keep every backend identical, and the deprecated tracker backends keep their serialisation rules
resource: plugins/quenching/assets/bin/quenching/specs/backends/**, plugins/quenching/assets/bin/quenching/specs/commands/**, plugins/quenching/assets/references/specs-develop/spec-driven.md
tags: [architecture, specs, backend, interface, serialization]
timestamp: 2026-10-07
audience: both
authority: current
source: history in ADR 0001 and ADR 0006
maintainer: quenching
---


# Spec backend interface

<!-- rules -->

Specs live in a **git store**: the canonical documents on the `quenching` branch of the code
repository's remote, with a thin tracker **card** beside each as a human-facing projection. This
standard is the interface that keeps the conceptual model, the thirteen sections, the frontmatter
records and the derived stages identical across the git store, the deprecated tracker backends
(`github`, `azure-boards`) and the test fake.

## The interface is the document, not the verbs

The CLI exposes eight verbs — `list`, `status`, `show`, `section`, `task`, `discover`, `promote`,
`validate`. **A backend implements none of them.** It implements five primitives over the canonical
markdown document:

| Primitive | Answers |
| --- | --- |
| `list_specs(phase=None)` | which specs exist, as descriptors |
| `read_spec(spec_id)` | the document for one spec, plus everything derived from it |
| `write_spec(info, text)` | replace one spec's whole document |
| `create_spec(phase, text)` | store a new document and return its locator |
| `move_spec(info, dest_phase)` | archive the spec and return its new locator |

The eight verbs are shared code layered on those five.

**This is what makes "every backend behaves identically" a property of the code rather than a
promise.** One method per verb reads like the obvious design, and it is the wrong one: each backend
would re-derive stages, gates, records and task state from its own storage, three parsers would be
free to disagree, and the only thing standing between them would be a test suite exercising every
combination. With the document as the contract there is nothing to disagree about — `resolve_one`
picks the spec, `derive_info` derives everything, and both are pure and shared.

A corollary worth stating: **a backend that starts deriving anything is broken**, even if its answer
happens to be right today.

## The shared layer never derives a repository path from provider configuration

The corollary above has an inverse, and it is the one that was missing: **the shared layer never
derives a path from provider configuration.** The configured provider and placement are connection
parameters, not repository addresses. The component that knows where a document is, is the
backend that stored it.

Three defects had that single cause, and each looked like its own bug until they were put side by
side:

| The shared code asked | It answered | Because |
| --- | --- | --- |
| is the provider placement valid? (`promote`) | a tracker-side refusal or a provider locator | shared code tried to answer a provider question with a repository path |
| is the provider configured? (`doctor`) | a provider health finding | shared code inspected a store it does not own |
| where do the specs live? (`--json` payloads) | a provider locator or `null` | shared code emitted a repository path that may not exist |

The three fixes are the same fix, applied where each answer belongs:

- **Provider questions stay inside the provider.** Placement, existence, and lifecycle transitions
  are answered by the selected implementation and become `BackendRefusal` values at the CLI edge.
- **A diagnostic stays read-only.** `doctor` checks provider configuration and transport health;
  it never creates a provider object or invents a repository store to make the check pass.
- **A payload states which world it is in.** One helper emits the provider name and a locator when
  one exists, otherwise `null`; consumers display it and never compose a repository path from it.

**One helper and not ten corrections**, for the same reason the interface is five primitives and not
eight verbs: a rule enforced at each site is a rule the next site is added without. Ten emit sites
carried the same wrong answer because each wrote its own copy of it.

## The spec ID is the spec identity

**The ID is the same fact as the spec's identity, and the store owns it.** With a card it is the
tracker's native number (GitHub issue number, Azure work-item ID); without one it is the counter on
the branch. `cq specs` accepts that exact ID and resolves it directly. The document does not mirror
the ID, invent a filename for it or resolve a title or fuzzy alias. A missing ID is `sp-unknown-id`,
never a guess.

The locator is a different fact: it says where the document lives, the ID says which document it
is. A transition may change the locator (archiving moves the file) and must not change the identity.
The shared layer derives stages and state from the canonical text; it never manufactures another key
or lists the front to find a document whose ID it was given.

## The git store is the source of truth

The canonical document on the branch is the only authoritative copy of a spec. A card, a `spec:*`
label, a board column and a cached listing are projections that can be discarded and rebuilt from
the document. A repository selects the store with `"backend": "git"`; without it, the remote URL
selects a deprecated tracker backend.

`cq specs export` dumps the canonical markdown on demand; nothing reads it back.

A backend named in the configuration but not implemented by the running copy of `cq specs`
**refuses with exit 2** and neither reads nor writes. An unknown or removed backend value never
falls back to another transport: silently writing elsewhere loses work instead of reporting it.

**Specs do not share a code branch.** The `quenching` branch carries documents only, and CI
ignores it. The task-to-commit anchor remains the sha recorded in the document.

## The git store

`"backend": "git"` in `.claude/quenching.json` selects the `git` store whatever provider the
remote URL implies. It keeps the canonical documents on a branch of the code repository's remote,
and the GitHub and Azure Boards backends keep working unchanged beside it.

- **Layout.** The branch is `quenching`, on remote `origin`. `specs/<id>.md` holds an open spec and
  `specs/archive/<id>.md` an archived one. Each file is the canonical document, byte for byte, so
  `derive_info` reads it unchanged. The phase is the directory and never a frontmatter fact, so
  archiving moves the file without editing its text. `specs/.next-id` is the ID counter and
  `quenching.json` at the branch root holds the specs-axis configuration under its `specs`
  namespace. The locator is `quenching:<path>`.
- **Configuration.** With the git store selected, each specs-axis key the branch declares
  (`subjects`, `tagCatalog`, `workItemTypes`, `azurePlacement`, `azureColumns`, `azureStates`,
  `artifactLanguage`, `card`, `cardAt`) replaces the same key from `.claude/quenching.json`.
  Everything that describes the code tree stays in `.claude/quenching.json`.
- **Reads never check out.** A process fetches the branch into its remote-tracking ref at most
  once, and not at all while the per-repository fetch stamp under
  `${XDG_CACHE_HOME:-~/.cache}/quenching/git/` is fresh. It then reads with `git ls-tree` and one
  `git cat-file --batch`. A read is therefore as fresh as the last fetch. A reader that must not
  touch the target's `.git` fetches into a bare mirror of its own and cannot write.
- **Writes never check out.** A write builds one commit on the tip with a throwaway
  `GIT_INDEX_FILE` and pushes it without force, so the push is the compare-and-swap. Commit
  subjects are `[skip ci] specs: <verb> <id>`. The first write to a remote without the branch
  creates it as an orphan commit.
- **A rejected push re-applies the same operation, never a merge.** The writer fetches and runs
  the same operation again on the new tip, for five attempts at most. A document whose blob on the
  new tip differs from the blob it was read at refuses with `sp-git-stale-write`, and nothing is
  written. Writes to different specs therefore both land, while two writes to the same spec land
  once and refuse once. A creation allocates its ID again on each attempt, so concurrent creations
  never share an ID. When the attempts run out, the writer refuses with `sp-git-cas-exhausted`,
  never with a silent loss.
- **Identity.** Without a tracker, the store owns identity: the counter is read and incremented
  inside the same compare-and-swap as the document. `create_spec(phase, text, spec_id=...)`
  accepts an ID that a tracker card already allocated, and refuses one the branch already holds.
- **A batch is one commit.** `write_specs` replaces N documents in a single commit, checking every
  blob before writing. A triage writes its priorities this way.

### Cards

The card is the thin tracker item beside a git-store spec: a projection a human can read, label
and discuss under. The spec on the branch stays the source of truth.

- **Configuration.** `card: {"provider": "github" | "azure-boards" | "none", "at": "capture"}`
  on the branch or in `.claude/quenching.json`. An absent provider is `github` when the remote is
  GitHub and `none` otherwise.
- **Identity.** With a provider, the card is created first, in one request, and its native number
  is the spec ID. `cq specs new --card <n>` adopts an existing issue or work item instead: its
  text becomes `## Problem` when the spec has none, `<n>` is the ID, and the item is rewritten to
  the thin card after the spec is written. A tracker backend refuses `--card`.
- **Body.** A `<!-- quenching-card -->` marker (never the tracker backends' spec marker), the
  title, the summary or the first paragraph of `## Problem`, `Tasks n/N`, phase and stage, and the
  location of the spec file on the branch. The `spec:*` labels come from `derive_labels` and
  `reconcile_label_set`, and the item closes and reopens with the phase.
- **Written only on lifecycle transitions.** The facts that justify a write are the title, the
  tags, the derived `spec:*` labels, the board state and the phase. The card layer compares them
  before and after the spec write, and a plain section edit or a task tick that changes none of
  them makes no card request. The first tick is a transition, because it moves the stage to
  `executing`. One transition is one request, and progress and summary ride along without
  causing a write.
- **Azure Boards.** Writes use `az boards work-item create|update`, which accept a PAT, and never
  `az rest`. `azurePlacement` (area, iteration, board column, declared state) is applied at
  create and at transitions only, so a tick never undoes a move on the board.
- **A card failure never rolls back the spec.** The spec is written first (the card first only
  at creation, where there is no spec yet). A failed card write after it raises `sp-card-failed`
  naming the spec, and the next transition refreshes the card.
- **Migration.** `cq specs migrate --to git` is a dry run unless `--write`. It writes every spec
  under its own ID in one commit (open in `specs/`, closed in `specs/archive/`), copies the
  specs-axis keys into the branch `quenching.json`, and prints the `.claude/quenching.json`
  change. It then proves that the `git` listing equals the source modulo locator and reports
  every difference. `--thin-open-cards` rewrites only open items to the thin card; closed ones
  are never touched. The tracker backends stay supported, and `cq specs doctor` flags them as
  deprecated.

## Legacy tracker backends (deprecated)

`github` and `azure-boards` still read and write specs through the five primitives and
`cq specs doctor` flags them with `sp-backend-deprecated`. `cq specs migrate --to git` moves a
repository off them. The rules below hold for any backend that keeps a spec in a tracker item.

- **The whole canonical document is the issue body or work-item description**, and the item has no
  sub-issues and no child work items. A discovery marker in the body (GitHub) or a discovery tag
  (`azurePlacement.discoveryTag`, Azure Boards) makes a spec listable.
- **Reassembly is byte for byte.** A backend reassembles the whole canonical document on read:
  structure it does not model (group headings, prose, blank lines) is structure it carries. The
  check is `==` on the document after store-and-reload, including the CRLF round trip a tracker
  performs, never an assertion about pieces (`tests/test_specs_backends.py`, `HybridSerialization`).
- **A native mapping is valid only when the native value is the same fact as the canonical one, and
  only when something reads it back.** The title passes: it is stored natively, so the document
  carries no `title:` key and no `# <TITLE>` heading, both reassembled on read, and a title the
  tracker would cut is never projected. The capture date fails (`created_at` is when the item was
  made), so `date:` stays in the document on every backend.
- **Ceilings are the backend's problem.** A GitHub body over 65,536 characters spills into
  continuation comments on its own issue, cut on line boundaries and joined on read; a declared part
  the comments no longer hold refuses with `sp-gh-parts-missing` (exit 2). Azure descriptions are
  never split.
- **Rendering derived state is admitted only under four conditions:** it duplicates no canonical
  field, it is recalculated from the document on every write, it costs no request beyond the write
  already made, and deleting it loses nothing. The `spec:*` labels (`derive_labels`,
  `reconcile_label_set`) qualify; label sets are compared as sets, and the `spec:` prefix is
  reserved, so reads exclude it from `tags`.
- **Stored state keys.** `tags` and `assignee` map to labels and assignees on both trackers;
  `start`/`target` map only on Azure Boards; `workItemType` stays in the document on every backend
  and its concrete name is projected once, at creation. Each backend carries forward the prior
  value of a key an ordinary write does not declare, and `System.Tags` also carries the discovery
  tag, which reads exclude and every write re-adds.
- **Azure placement is declared, never guessed, and reaffirmed on every write** in the same request
  the write already makes (`azurePlacement`: area, iteration, board column, state; `areaPath` has no
  default). Ops are diffed against the item as read, and a field whose read shape differs from its
  write shape (identity, datetime) is normalised first. A rejected op refuses naming the op. The
  organisation and project come from the CLI's own defaults, never from configuration.
- **Branch, PR and commit links.** `github` has no mapping for `branch.work`; a PR body ending in
  `Refs #<issue>` populates the issue's Development panel. `azure-boards` links a branch and a task
  commit as `ArtifactLink` relations (with `attributes.name`) only when
  `azurePlacement.repository` is declared, in a separate request that never rolls the document
  back, and never links a `github` PR.
- **A direct read by ID reuses the listing the process already holds.** A cold read fetches one
  item; a read after a listing in the same process takes the row from that listing, never a request
  per spec. Both paths hand the same document to the one shared derivation.
- **`list --lean` is an index, not the front.** It returns the verified set without bodies and is
  eventually consistent; the full listing is authoritative.

## Granular reading is about context, not I/O

`show` returns an **index** by default — the thirteen headings with their state, and the task ids.
One task comes back on request; the whole document only under `--full`, which refuses to combine
with a selector. Section **bodies** are `section`'s, which already reads N headings in one call and
resolves a `--moment` to its declared set: two ways to ask for a heading would be two spellings of
the same measured answer, and they would drift.

The cost this addresses is the **agent's context**, not disk or network. An agent handed all thirteen
sections in order to edit one pays for the other twelve on every call. Whether the backend had to
fetch the whole document to answer is an implementation detail — a local cache inside `cq specs` is
free to exist and is **not** a store: it is not authoritative, nothing outside the CLI reads it, and
the backend remains the source of truth.

**A cache may cross processes, under one added condition: it may only ever narrow a read, never
authorise a write.** Every CLI invocation is a new process, so a cache that lives only in memory is
paid for again on every command — measured on `azure-boards`, resolving the organisation, the
project name and the team's board column field cost 3,8s of an 8,5s write, all of it re-derivation
of answers the previous process already had. The three conditions above still hold when the answer
outlives the process; what changes is that a wrong entry now survives the process that wrote it.

So the reader re-validates rather than trusting the hit: a remembered provider ID is used to fetch
**one** item instead of the whole front, and the identity that comes back is
compared against what was asked for. A mismatch falls through to the full listing. Nothing is ever
written on the strength of a cached answer alone, which is what keeps the store the source of
truth rather than the cache.

Two placement rules follow. The cache lives **outside the repository**, because one in the tree is
committed, travels to another machine and to another checkout, and a stale entry there points at a
recreated work item while looking exactly like a hit. And it is **keyed by the identity it answers
for** — organisation, project, and whatever else scopes the answer — so two projects never read
each other's.

## The fake is how "identical" stays true

A memory-backed fake used only by tests — no disk, no network, no fixture — is not a convenience.
It is the other side of an equality the test suite asserts: a canonical case list runs against the
GitHub and Azure transports' strict offline fixtures and the fake, and every field must match
except the provider locator and the document text echoed back.

Two backends sharing nothing but the interface is the only arrangement in which a command that
reaches around the interface to a repository path shows up immediately, with no provider fixture to stage.

The check earns its place on history rather than on argument: it catches the fake or a provider
fixture deriving a spec's date differently from the canonical document. The same document must
have the same date and stage everywhere.

The fake is deliberately **not selectable from configuration**. A store that forgets on exit must
never be somewhere real work can land.

## What this standard does not yet cover

The interface and the equality are proved for the git store, the two tracker backends and the memory
fake. A backend is proved by the documents it will actually be given, not by the ones written to
exercise it: run real specs through store-and-reload, including those over any ceiling. A write is
idempotent only if the value the tool produces is byte-identical to the value the store keeps;
that cannot be established offline and needs an end-to-end run. `azure-boards` `create_spec` is not
atomic between creating the work item and patching its board column.

A finding that an implementation cannot satisfy some rule above is a reason to revisit this
document, not to work around it quietly. Evidence and measurements: [ADR 0001](../decisions/0001-spec-backend-measurements.md),
[ADR 0006](../decisions/0006-specs-move-to-a-git-store-with-thin-cards.md).
