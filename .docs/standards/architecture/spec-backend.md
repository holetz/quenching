---
type: standard
title: Spec backend interface
description: Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation with the whole document (not just the parts it models) as its reassembly obligation, rendering derived state onto a native surface as a third category beside projection and storage, the receipt a tolerant slug resolution owes every payload and why it is folded in at a choke point rather than written verb by verb, and the in-memory fake that turns "identical" into a checked property
resource: plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/references/specs-develop/spec-driven.md
tags: [architecture, specs, backend, interface, serialization]
timestamp: 2026-08-06
audience: both
authority: current
source: configurable-spec-backend plan (task 2.5); §What "the canonical document" covers added by fix-github-backend-tasks-fidelity (task 3.2), after the `github` backend was measured dropping every `### N.` group heading it stored; the `## Tasks`→sub-issue mapping retired by migrate-this-repo-to-github-backend, after 689 task sub-issues against 68 spec issues were measured serving a projection nothing ever read back; the issue title turned from a projection into storage, and the criterion refusing the capture date's, by evaluate-spec-creation-flow (tasks 2.2-2.3, 5.4) — 68 of 70 dates would have been rewritten to the migration's own day; §Rendering derived state is a third category added by labels-historico-spec-issue (task 6.1), after the `spec:` label/tag reconciliation it documents was measured live against a throwaway issue, catching an order-sensitive comparison that cost an extra round trip on every write; §Placement is declared, and reaffirmed on every write added by provar-e-posicionar-o-backend-azure-boards (task 2.7), measured against the `azure-boards` backend's own `azurePlacement`; §Armazenado não é projetado added by the same plan (task 3.6), after `not found` was measured on this repository's own tracker for a label GitHub does not already have, and reconciled with the third category above at that plan's conclude, when the two mechanisms met on the same field; §What this standard does not yet cover updated by the same plan (task 7.3), after task 6.3 ran `azure-boards` end to end against a real Azure DevOps project; §A tolerant resolution announces itself added by anunciar-resolucao-aproximada-em-todos-os-verbos (task 2.1), after the count of verbs owing the receipt was measured moving three times — six at capture, ten at design, eleven at build — and the structural guard it describes was proved firing on a reintroduced bypass; §Placement is declared, and reaffirmed on every write and §Granular reading is about context, not I/O both rewritten by reduzir-as-chamadas-az-por-escrita-no-azure-boards (task 5.1), after one `azure-boards` section edit was measured spending nine `az` calls and 8,5s — four of them writes to the same work item — and the sentence claiming those fields cost 'never a round trip of their own' turned out to be a description that had been false for a year; §What this standard does not yet cover updated by the same plan (task 6.1), whose live run found four ways a write was not idempotent that no offline check could have seen
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

## A tolerant resolution announces itself, at a choke point rather than verb by verb

`resolve_one` is tolerant in four rungs: the exact slug, the exact title, one close match above the
threshold, then nothing. The last two answer a slug the human did not type, so the descriptor comes
back carrying **`resolvedBy`** — `"title"` or `"approximate"` — and **`resolvedFrom`**, what it
matched. Acting on a spec the human did not name is worse than refusing; the receipt is what makes
the tolerance honest rather than a wrong answer delivered confidently.

**A receipt only one verb carries is not a receipt.** For a while `status` was the only payload that
propagated the two keys, while `section`, `task`, `record`, `promote` and the rest resolved through
the same tolerance and announced nothing — `promote` among them, which archives. Every one of those
verbs could write to a spec nobody named, and nothing in the JSON a caller branched on said so.

The fix is not to write the two keys into each verb's payload. **The receipt is recorded where the
human's slug is resolved and folded in where the payload is emitted** — one entry point
(`read_one`) and one exit (`emit`), with the verb in between never mentioning it. A verb added
tomorrow announces without its author knowing the rule exists.

Three properties this shape has and the enumerated one does not:

- **The count cannot go stale.** It was six verbs when the problem was written down, ten when it
  was designed and eleven when it was built — and each number was produced by somebody reading the
  file carefully. This is the failure mode
  [shared-mold-keys.md](shared-mold-keys.md) measured on `resource:`: a rule that depends on the
  author remembering is a rule the next author forgets.
- **`resolve_one` stays pure.** The receipt is recorded one layer above it, in the command layer,
  never inside the resolution — the purity over the listing is what makes "every backend resolves
  the same way and gets the same refusals" a property instead of a claim, and a side effect there
  would spend it to buy what the layer above already gives.
- **The guard is structural.** `specs.py selftest` walks `DISPATCH` — the registry a verb must join
  to exist — and refuses any verb whose own source resolves `args.spec` directly. It parses rather
  than matches text, because the finding it emits names the very call it forbids.

Both keys ride on every payload from a verb that resolved a spec at all, `null` on the exact path,
so a caller reads `payload["resolvedBy"]` without testing for presence. A verb that resolves no spec
carries neither: a null answer to a question nobody asked is noise. The receipt goes to the human
reader too — the person running the verb by hand is exactly the one who mistyped the slug.

**Only the human's own argument is announced.** Code already walking a listing resolves slugs it
just read itself, and a receipt for those would be a receipt for nothing.

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

### Rendering derived state is a third category, admitted under cumulative conditions

Projection and storage, above, are not the only way a native construct earns its place.
A native surface may also carry a RENDERING of state this document already derives —
never a duplicate of a canonical field, never read back, and free. This is the third
category, and admission is cumulative: all four conditions below, none optional.

The `spec:` labels `github` reconciles onto its own issue's `labels` (`azure-boards`:
`System.Tags`, on the work item) are exactly this — one per frontmatter record present,
plus `spec:built` for the derived `executing` stage. `derive_labels` computes the desired
set from `info` alone, wholly independent of whatever the issue already carries, and
`reconcile_label_set` folds that set into the native surface without touching anything
outside the `spec:` prefix. Nothing in `list_specs`, `read_spec` or `validate` ever reads
a label back — the reassembly obligation above is untouched, because nothing here is part
of what gets reassembled.

- **It does not duplicate a canonical field.** A label names a MILESTONE — that a record
  exists — never the record's own fields. `priority: {level, criticality, complexity,
  date}` has no label form for the same reason it was refused a label-only encoding above:
  a label can hold a name, not a struct.
- **It is recalculated from the source on every write**, never edited in place and never
  trusted to still be correct from an earlier one. `derive_labels` takes `info` and
  nothing cached, and runs again on every `write_spec`.
- **It costs zero calls beyond the write already being made.** GitHub's label set rides
  inside the SAME `PATCH` `_store` already sends; Azure's `System.Tags` rides inside the
  SAME `--fields` update `_update` already sends. MEASURED live, 2026-08-05, against this
  repository's own issue #877: a write that changes no record and no stage costs exactly
  the one `PATCH` it always did. The first cut did not — it compared the desired label set
  against the issue's current one as ORDERED lists, and GitHub returns a listing's labels
  alphabetically, never in the schema's own order, so a same-set reorder read as a change
  on every write and cost an extra `GET` fixing colors that were already right. Comparing
  the two as sets was the fix.
- **It is discardable without loss.** Deleting a `spec:` label deletes nothing the document
  does not already say; the next write recreates it. Deleting every `spec:` label in the
  repository loses zero information — the claim `labels-historico-spec-issue`'s own
  `## Proposal` made before this rule existed to check it against.

The twin test above — whether a native value is the same fact as the canonical one —
does not apply here: a rendering is not a claim that the label IS the record, only that
the record's presence is visible without opening the issue.

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
one-way relationship `state` already has with `move_spec`.

**And it must cost nothing extra: every reaffirmed field travels in the SAME request the write
was already making, never a round trip of its own.** That sentence was written as a description
and was false for a year — measured on `azure-boards`, one section edit spent nine `az` calls and
8,5s, of which four writes went to the same work item: the document, then the parent, then the
board column, then the tags. The cost was never the reaffirmation. It was spending one process per
field, on a CLI whose startup is the floor (0,45s for `az rest` against 0,9s for `az boards
work-item update`, measured on the same org).

An external tracker pays **per request, not per byte**, so the rule is: assemble one body, send it
once. Two consequences follow, and both are load-bearing rather than incidental:

- **Ops are diffed against the item as it was read, and an unchanged field emits none.** This does
  not weaken the reaffirmation — a card a human moved has a column that disagrees with the derived
  one, so the op is emitted and the card comes back. What it removes is the tracker revision an
  unchanged field used to bump on every write.
- **A field whose read shape is not its write shape must be normalised before it is diffed**, or
  it is "changed" on every write forever. Two are known on `azure-boards`: an identity field comes
  back as an object and goes out as a UPN, and a scheduling field comes back as a datetime and
  goes out as a date.

One request is **all-or-nothing**, which is the trade this rule accepts: a rejected op takes the
document edit down with it, where four separate writes would have left the document saved and the
column stale. That is the better failure — but only on one condition, which is part of the rule:
**the refusal must name the op the tracker rejected.** A body of eight ops that fails without
saying which is worse to diagnose than the four writes it replaced.

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

**The `spec:` prefix is reserved, and that is what lets storage and rendering share one field.**
`tags` is stored in the very surface §Rendering derived state renders onto — issue `labels`, and
`System.Tags` on the work item — so the two mechanisms would fight over it if neither yielded.
Neither has to: **reassembly on read excludes every `spec:`-prefixed name**, exactly as it excludes
the discovery tag, so a rendered label never becomes a tag the document claims to declare; and the
write hands the native surface the union of both — the carried-forward `tags` plus the freshly
derived `spec:` set — in the one call it was already making. A tag a human declares may not start
with `spec:`, for the same reason it may not be the discovery tag: the prefix belongs to the
rendering, and a spec claiming one would be claiming a fact the next write recomputes anyway.
Neither the catalogue check (`tagCatalog`) nor `doctor`'s uncatalogued-tag finding sees the
reserved names at all — they are not the spec's tags, so a catalogue that never lists them is
complete, not lacking.

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

**A cache may cross processes, under one added condition: it may only ever narrow a read, never
authorise a write.** Every CLI invocation is a new process, so a cache that lives only in memory is
paid for again on every command — measured on `azure-boards`, resolving the organisation, the
project name and the team's board column field cost 3,8s of an 8,5s write, all of it re-derivation
of answers the previous process already had. The three conditions above still hold when the answer
outlives the process; what changes is that a wrong entry now survives the process that wrote it.

So the reader re-validates rather than trusting the hit: a remembered id is used to fetch **one**
item instead of the whole front, and the identity that comes back — the marker, the slug — is
compared against what was asked for. A mismatch falls through to the full listing. Nothing is ever
written on the strength of a cached answer alone, which is what keeps the backend the source of
truth rather than the cache.

Two placement rules follow. The cache lives **outside the repository**, because one in the tree is
committed, travels to another machine and to another checkout, and a stale entry there points at a
recreated work item while looking exactly like a hit. And it is **keyed by the identity it answers
for** — organisation, project, and whatever else scopes the answer — so two projects never read
each other's.

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

`azure-boards` has now been exercised a **second** time end to end, by
reduzir-as-chamadas-az-por-escrita-no-azure-boards (task 6.1), against the same real project — and
that run is the reason §Placement and §Granular reading above changed. What it surfaced, live, was
not the transport but the **idempotence** of a write, and every one of the four was invisible to an
offline check that asserted the request body against a fixture:

- a field that is reaffirmed but not read back can never be diffed, so it is written on every
  request forever — `System.AreaPath`, `System.IterationPath` and the board's own column field were
  all in that state;
- a set-valued field returned in the tracker's order and written in the tool's differs by
  permutation alone, which a string comparison reads as a change;
- a tracker that **normalises** what it stores — an HTML attribute given its semicolon, a tag given
  a space before its closing angle — hands back something other than what went out, so the one
  field every write carries could never be elided until the writer produced that exact form;
- and `az devops invoke` cannot address a single work item at all: it routes by resource name, and
  `workitems` resolves to the create route, so a PATCH by id dies inside the SDK with
  `KeyError: 'type'` — a traceback rather than a refusal, and the one failure mode the interface
  promises never to have.

The rule that generalises them: **a write is idempotent only if the value the tool produces is
byte-identical to the value the tracker stores.** Anything less is not a cosmetic difference; it is
a diff that never converges, and it silently defeats every optimisation built on comparing the two.
That property cannot be established offline. It is what an end-to-end run is for.

A finding that an external implementation cannot satisfy some rule above is a reason to revisit this
document, not to work around it quietly.
