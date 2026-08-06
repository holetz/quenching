---
type: standard
title: Spec backend interface
description: Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation with the whole document (not just the parts it models) as its reassembly obligation, and the in-memory fake that turns "identical" into a checked property
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/references/specs-develop/spec-driven.md
tags: [architecture, specs, backend, interface, serialization]
timestamp: 2026-08-06
audience: both
authority: current
source: configurable-spec-backend plan (task 2.5); §What "the canonical document" covers added by fix-github-backend-tasks-fidelity (task 3.2), after the `github` backend was measured dropping every `### N.` group heading it stored; the `## Tasks`→sub-issue mapping retired by migrate-this-repo-to-github-backend, after 689 task sub-issues against 68 spec issues were measured serving a projection nothing ever read back; the issue title turned from a projection into storage, and the criterion refusing the capture date's, by evaluate-spec-creation-flow (tasks 2.2-2.3, 5.4) — 68 of 70 dates would have been rewritten to the migration's own day; §Placement is declared, and reaffirmed on every write added by provar-e-posicionar-o-backend-azure-boards (task 2.7), measured against the `azure-boards` backend's own `azurePlacement`; §Armazenado não é projetado added by the same plan (task 3.6), after `not found` was measured on this repository's own tracker for a label GitHub does not already have; §What this standard does not yet cover updated by the same plan (task 7.3), after task 6.3 ran `azure-boards` end to end against a real Azure DevOps project
maintainer: quenching
---

# Spec backend interface

Where a repository's specs live is a choice it declares — markdown files on a dedicated branch,
GitHub issues, Azure Boards work items. This standard is the interface that lets that choice change
nothing else: the conceptual model, the fourteen sections, the frontmatter records and the derived
stages are the same on every backend, and only the serialisation moves.

## The interface is the document, not the verbs

The CLI exposes eight verbs — `list`, `status`, `show`, `section`, `task`, `discover`, `promote`,
`validate`. **A backend implements none of them.** It implements five primitives over the canonical
markdown document:

| Primitive | Answers |
| --- | --- |
| `list_specs(phase=None)` | which specs exist, as descriptors |
| `read_spec(slug)` | the document for one spec, plus everything derived from it |
| `write_spec(info, text)` | replace one spec's whole document |
| `create_spec(phase, filename, text)` | store a new spec |
| `move_spec(info, dest_phase)` | the one lifecycle hop, `plans/` → `archive/` |

The eight verbs are shared code layered on those five.

**This is what makes "every backend behaves identically" a property of the code rather than a
promise.** One method per verb reads like the obvious design, and it is the wrong one: each backend
would re-derive stages, gates, records and task state from its own storage, three parsers would be
free to disagree, and the only thing standing between them would be a test suite exercising every
combination. With the document as the contract there is nothing to disagree about — `resolve_one`
picks the spec, `derive_info` derives everything, and both are pure and shared.

A corollary worth stating: **a backend that starts deriving anything is broken**, even if its answer
happens to be right today.

## The selected backend is the source of truth

There is no canonical local store shadowing an external one. When a repository declares `github`,
its specs live in GitHub, with no authoritative local copy — losing access to the tool is losing the
specs, which is the accepted cost of choosing it. `specs.py export` dumps the canonical markdown on
demand; nothing reads it back and nothing keeps it in sync, which is exactly what keeps it from
being a second store.

A backend named in the configuration but not implemented by the running copy of `specs.py`
**refuses with exit 2** and neither reads nor writes. It never falls back to `files`: silently
writing to the local filesystem for a repository that asked for GitHub loses work instead of
reporting it.

**No backend lets a spec share a branch with the code.** That is the property the whole design
exists for — the `files` backend puts its documents on a dedicated branch, an external backend puts
them outside git entirely — and it is why the task→commit anchor could move from the commit subject
to the sha.

## Hybrid serialisation lives inside each external implementation

An external backend is free to use its host's native constructs where a mapping exists, and to fall
back to serialised markdown where none does. The one obligation is that it **reassembles the
canonical document on read**.

That obligation is not a restriction on native storage; it is what makes native storage safe. The
mapping is confined to the one implementation that owns it, and it can never leak into the JSON the
CLI prints, because the CLI never sees the storage.

### A native mapping earns its cost only if something reads it back

The permission above is not an invitation. Both external backends took it up for `## Tasks` — one
sub-issue per task on `github`, one child work item on `azure-boards` — because `## Tasks` is the
one section with a native counterpart carrying its own state and identity. That is true, and it was
not the question. The question is whether anything ever **read** the native state, and nothing did:
`parse_tasks` takes a task's checked/blocked from its raw block text on both ends, never from the
issue. A construct written on every save and never consulted is a **projection**, and a projection
belongs wherever it is free — never wherever it costs a call per item per write.

**The issue title was the other one, and it was fixed rather than retired.** It too was rewritten
from the frontmatter on every write and never read, which made it duplicated truth that merely
happened to be cheap. The test above admits exactly one remedy for that: make something read it
back. So the canonical document is now stored **without** its `title:` key and without the
`# <TITLE>` heading, both reassembled on read from the native title — one native mapping that
earns its cost, at no extra call, because the write was already being made.

The price of putting it where it was not free, measured on this repository on 2026-08-03,
mid-migration:

- **68 spec issues against 689 task sub-issues.** 91% of the tracker's volume was the projection;
  43 specs were open, and 332 sub-issues with them.
- **The full listing every specs command pays was 8 pages, 4.4 MB and 8.4 seconds.** Collapsed, it
  is one page.
- **`write_spec` on a ten-task spec spent twelve round trips where one now does** — one PATCH on
  the parent, one GET of the sub-issues, one PATCH per task. A newly created task cost three of its
  own (POST, POST to link it as a child, PATCH to close it when the box was already ticked).
- **`read_spec` paid one GET of sub-issues per spec read.** A one-part spec now costs nothing
  beyond the listing, which already carries every body.

So the mapping is retired. On both external backends the **whole canonical document is the issue
body / the work item description**, and there are no sub-issues and no child work items.

What is given up, stated plainly, is **per-task addressability** — an assignee, labels, a comment
thread of its own, a PR that closes a task issue. Nothing in quenching used any of it;
`/specs:execute` anchors a task to its commit by the sha recorded in the document. What is kept is
the part that renders: `- [ ]` in an issue body is a native GitHub task list, with a checkbox and a
progress count, and ticking it in the web UI **edits the document** — which closing a sub-issue
never did.

**The same now holds for the title, and it is a deliberate reversal.** Editing an issue's title in the web UI renames the spec instead of being undone by the next write. That is what storage
means: the value is read back, so a human's edit to it is an edit to the document. The reversal is
bounded by the refusal above — a title the tracker would cut is never projected — so the one case
where a web edit could silently truncate a spec's name is the one case that is not stored there.

### A native value is the same fact, or it is not a mapping at all

The test above asks whether anything reads the native value back. It has a twin, and the twin is
what decides *which* fields may be mapped in the first place:

> A native mapping is valid only when the native value is **the same fact** as the canonical one.

The two spec fields that look mappable answer it differently, and both were measured rather than
argued:

- **The title passes.** An issue's title and a spec's `title:` are the same fact — one line naming
  the spec — so storing it once, natively, removes a duplicate.
- **The capture date fails.** An issue's `created_at` is when the ISSUE was created, not when the
  spec was captured. On this repository, on 2026-08-03, issue #776 carried `created_at
  2026-08-03T03:32:51Z` for a spec captured on **2026-07-25**: the numbers jump from 7 to 776
  because a migration created ~769 issues in one afternoon. Deriving the date natively would have
  rewritten **68 of 70** capture dates to the migration's own day, destroying the one thing the
  field records.

So the date is **not** projected. It is `date:` in the canonical frontmatter, in every backend, and
that is not duplicated truth precisely because no store holds an honest copy of it to duplicate.
The rule generalises: a field with no faithful native counterpart stays in the document, and a
backend that invents one — a synthetic filename minted only to carry a date — has moved the
duplication rather than removed it.

### What "the canonical document" covers, and how the obligation is checked

**The whole document, byte for byte** — not the fields a backend happens to model. The obligation
reads as obvious and was not: the `github` backend shipped mapping `## Tasks` to sub-issues by
emptying that section and concatenating the blocks back, which loses every `### N. <Section>` group
heading and every line of prose the section carried. Nothing failed. The write succeeded, the read
returned a well-formed document, and the loss was visible only by comparing it to what went in.
Measured across this repository's own specs, 49 of 68 carry groups.

That loss was the sub-issue mapping's, and the mapping is retired (above) along with the per-task
keys, indices and anchors its reassembly ran on. **The obligation did not go with it.** It is now
close to free on both external backends — the document is what is *stored*, not what is rebuilt —
and it is checked exactly as before, because these three rules hold for any backend, including the
next one to take the native-construct permission up:

- **Structure a backend does not model is structure it must carry, not structure it may drop.** A
  section's grouping, its prose and the blank lines between its items are content. A mapping that
  keeps only the parts with a native counterpart is a lossy projection wearing a serialisation's
  name.
- **The check is equality on the document, never an assertion about the pieces.** "The headings are
  still there" passes with them reordered and the prose gone. `specs.py selftest` runs a grouped
  fixture through store-and-reload — including the CRLF round trip a tracker really performs — and
  compares the result to the original with `==`.
- **A store's own ceilings are the backend's problem, not the caller's.** A title over the
  tracker's limit used to be cut, because a title was a projection and cutting one lost nothing.
  **That stopped being true the moment the title became storage**: a cut title read back is a
  renamed spec. So the projection is now *refused* for a title that would not survive — the
  document keeps its own `title:` and the tracker gets the cut copy it can hold — and the general
  rule is that **a native mapping is taken only where it round-trips**, checked rather than
  assumed. A **document** over the ceiling is not cut and is no longer refused: a GitHub
  issue body holds 65,536 characters, and of this repository's 69 specs **two exceed that as whole
  documents — 69,498 and 74,180 — one of them an active plan**. Refusing would mean refusing to
  store a spec somebody is building, so an over-size document spills into **continuation comments on
  its own issue**, cut on line boundaries and joined back on read. The refusal survives as a
  backstop at the one point every write passes through, so no later caller can hand the tracker a
  body it will answer 422 to; and a declared part the comments no longer hold is its own **refusal
  (`sp-gh-parts-missing`, exit 2)** — returning the shorter document would let the next write
  persist that truncation as the new truth.

## Placement is declared, and reaffirmed on every write

A work item's position in an external tracker — its area, its type, its parent, its iteration,
its board column — is not one of the fourteen sections, and it is not derived from anything the
canonical document carries. **It is declared**, in `.claude/quenching.json`'s `azurePlacement`
([plugin-configuration.md](../workflows/plugin-configuration.md)), for the same reason
`azureStates` already is: the document is identical on every backend, and an external tracker's
own organisational scheme belongs to the project the backend writes into, never to the spec.

A backend free to GUESS placement would not fail loudly. Measured on `azure-boards`'s own
target project: the declared area covers **one** sub-area of 761 unrelated work items, and a
guessed default would write into the wrong part of somebody else's board — silently
indistinguishable from a right write until a human goes looking. Declaring it, with no default for
the one field with no honest guess (`areaPath`), is what turns that failure loud — the same
argument `azureStates` already carries, applied to WHERE a spec is born rather than WHAT state it
reads as.

**Declared placement is reaffirmed on every write, not only at creation.** A human who moves the
work item's area or its board column between two writes sees the next one bring it back — the
tracker is the projection, `.claude/quenching.json` is the authority, and that is the same
one-way relationship `state` already has with `move_spec`. This costs nothing extra: the fields
travel on the SAME create/update call the write was already making, never a round trip of their
own.

## Armazenado não é projetado

`tags`, `assignee`, `start` and `target` are the frontmatter's four STATE keys — first-level,
never a record — and each passes the same test §A native value is the same fact already applies
to `title:`: a native mapping is valid only when the native value is the SAME FACT as the
canonical one, and it earns its keep only once something reads it back.

| Field | `files` | `azure-boards` | `github` |
| --- | --- | --- | --- |
| `tags` | frontmatter | `System.Tags` | issue labels |
| `assignee` | frontmatter | `System.AssignedTo` | issue assignees (first only) |
| `start` | frontmatter | `Microsoft.VSTS.Scheduling.StartDate` | frontmatter |
| `target` | frontmatter | `Microsoft.VSTS.Scheduling.TargetDate` | frontmatter |

**`tags` and `assignee` pass on both external backends.** A label and a spec's tag are the same
fact — a name attached to the item — and so is an assignee: a login, an identity, one name a
human reads as "who owns this". Both are reassembled on read and reaffirmed on every write, at no
extra call: they ride the SAME create/update request the write was already making, exactly as
placement does.

**`start`/`target` pass ONLY on `azure-boards`.** `Microsoft.VSTS.Scheduling.StartDate`/
`TargetDate` are the same fact a spec's own `start`/`target` name — a planned date, not a
projection of something else. `github` has no equivalent: an issue carries no scheduling field,
so `start`/`target` stay in the frontmatter there, unmapped, for the same reason `date:` stayed in
the document when no backend had an honest native counterpart for IT either.

**The discovery tag is the one exception `tags` carries, and it is a floor, not a ceiling.**
`azure-boards`'s `System.Tags` also carries the discovery tag (`azurePlacement.discoveryTag`) —
this backend's own index, never a spec's declared content. Reassembly on read EXCLUDES it, so
`tags` reflects only what the spec itself declared; the write that reaffirms `tags` always
re-adds it regardless, because a write that forgot it would make the spec invisible to its own
listing on the very next read. `github` has no equivalent constant: discovery there is the body
marker alone, never a label.

**A backend with no faithful counterpart stores the document ONLY.** `write_spec` strips
`tags`/`assignee` (and, on `azure-boards`, `start`/`target` too) from the text it stores — the
native field is the storage, and a document that ALSO carried the value would be the same
duplicated-truth failure `title:` was fixed for, at a smaller scale. An ORDINARY write — a
section edit, a ticked task — never mentions these keys at all, because they are not in the
document to begin with; reading that silence as "clear them" would wipe every stored field on
the next unrelated save, so each backend carries forward the prior read's value for a key its
own write's text does not explicitly declare.

## Granular reading is about context, not I/O

`show` returns an **index** by default — the fourteen headings with their state, and the task ids.
One task comes back on request; the whole document only under `--full`, which refuses to combine
with a selector. Section **bodies** are `section`'s, which already reads N headings in one call and
resolves a `--moment` to its declared set: two ways to ask for a heading would be two spellings of
the same measured answer, and they would drift.

The cost this addresses is the **agent's context**, not disk or network. An agent handed all fourteen
sections in order to edit one pays for the other thirteen on every call. Whether the backend had to
fetch the whole document to answer is an implementation detail — a local cache inside `specs.py` is
free to exist and is **not** a store: it is not authoritative, nothing outside the CLI reads it, and
the backend remains the source of truth.

## The fake is how "identical" stays true

A second backend holding specs in a dict — no disk, no network, no fixture — is not a convenience.
It is the other side of an equality the selftest asserts: a canonical case list runs against `files`
and against `memory`, and every field must match except the locator (`path`) and the document text
echoed back.

Two backends sharing nothing but the interface is the only arrangement in which a command that
reaches around the interface to a filesystem path shows up immediately, with no repository to stage.

The check earns its place on history rather than on argument: the first time it ran it caught the
fake deriving a spec's date from frontmatter while `files` reads it from the filename, where `new`
stamps it once and never again. The same document, two dates. Left alone, an external backend would
have inherited the asymmetry.

The fake is deliberately **not selectable from configuration**. A store that forgets on exit must
never be somewhere real work can land.

## What this standard does not yet cover

The interface and the equality are proved for `files` and `memory`, and the reassembly obligation is
proved offline for the hybrid serialisation both external backends share.

`azure-boards` has been exercised end to end once (`provar-e-posicionar-o-backend-azure-boards`,
task 6.3), against a real Azure DevOps project (org `unicredbr`, team "Diretoria Risco") and a
throwaway test spec: `new --subject`, every `section --write`, `record`, `task --check`, `status`,
`show` and `promote --outcome done`, each matching `files` for the same state, the board's own
column tracked against the declared de-para through every transition — `captured` → `Backlog`/
`New` through `archived` → `Concluído`/`Closed`. The test spec, like `github`'s own first run, had
no `### N.` groups — but `azure-boards` never splits a document into continuation parts at all
(`hybrid_split` is handed no limit; the field's own measured ceiling is 1,048,576 characters, and
this repository's largest real spec is 74,180), so the loss `github`'s split-and-join mapping once
took does not apply the same way here. What the run did surface, live, three times: a WIQL clause
comparing a GUID where only a name resolves, a CLI flag that does not exist on `create`, and — the
one that changed the interface's own assumption — `System.State` and the board's `Kanban.Column`
are not two independent fields on this process; the column is what a write actually controls, and
the state is a resolved consequence of it.

`github` has been exercised end to end once, against a throwaway test spec. That is worth less than
it sounds, and the gap is the reason this section stays: the test spec had no `### N.` groups and no
over-long task line, so the run proved the transport and not the shape of real documents — which is
exactly where the loss described above was hiding. **A backend is proved by the documents it will
actually be given, not by the ones written to exercise it.**

That sentence has since been earned a second time by the same test spec: it was also nowhere near
the 65,536-character body ceiling, and two of this repository's 69 real specs are over it. So the
retirement was paid for the way the sentence asks — **all 69 real documents were run through the new
serialisation offline**, split, wrapped, put through the CRLF round trip a tracker performs,
unwrapped and joined, and every one came back byte for byte, the two that spill included.

A finding that an external implementation cannot satisfy some rule above is a reason to revisit this
document, not to work around it quietly.
