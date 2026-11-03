---
type: standard
title: Spec composition contract
description: Any spec may list other specs as members of its `## Tasks` — one item grammar for a task and a member, composition derived from the document and never declared, the three levels derived from the waves (story, feature, epic), the member's state read from its own document and never ticked, the `link add` and `link remove` verbs with their `epic add` alias, cross-repository members read-only, the tracker card that keeps one work-item type and links members as predecessors, and the `sp-link-*` findings validate raises
resource: quenching/assets/bin/quenching/specs/parse/epics.py, quenching/assets/bin/quenching/specs/parse/tasks.py, quenching/assets/bin/quenching/specs/parse/derive.py, quenching/assets/bin/quenching/specs/members.py, quenching/assets/bin/quenching/specs/commands/epic.py, quenching/assets/bin/quenching/specs/cards.py, quenching/assets/bin/quenching/specs/backends/azure.py, quenching/assets/bin/quenching/specs/portal.py, quenching/assets/bin/quenching/specs/commands/validate.py, quenching/assets/specs/schema.json
tags: [workflows, specs, composition, orchestration]
timestamp: 2026-11-01
audience: both
authority: current
source: spec 2137 (spec composition); retired with epics.md (spec 2137, 2026-11-01)
maintainer: quenching
---

# Spec composition contract

Any spec may contain other specs. There is no second document type, no declared parent and no
`epic:` flag to keep in sync: an item under `## Tasks` is a task or a member spec, and the
composition of the store is whatever those items say.

This file replaces `epics.md`. The old contract — an epic as a `workItemType: epic` spec, a
member's `epic:` back-reference, one parent per spec — is retired; what survives is the derived
model and the compatibility spellings named below.

## One grammar, two readings

```markdown
## Tasks

### 1. Foundations

- [ ] 1.1 Write the parser — files: parse/refs.py
- [ ] S1 Honest local gate — spec: #2138

### 2. Rollout

- [ ] S2 Migration — spec: #2139 — after: S1
- [ ] 2.1 Wire the job — after: S2
```

- A checkbox whose text carries `— spec: #<id>` (or `— spec: <owner>/<repo>#<id>`) is a **spec
  item**: the first token is its **label** (`S1`), the rest its title, the reference its **member**.
- Every other checkbox is a **task item**, unchanged since v1 — `- [ ] <id>. <text>` plus its
  indented metadata (`files:`, `pattern:`, `verify:`, `subject:`, `commit:`).
- `after: S1,S2` is read on both kinds: on a task it orders work inside this document, on a spec
  item it orders the member.
- `### N.` headings are **waves** — the groups the document already had. The first heading is
  wave 1; items before any heading are ungrouped.

`info["tasks"]` holds the task items and `info["links"]` the spec items, split once at parse time
(`parse/derive.py`); every caller reads the split instead of re-parsing the line.

**Composition is a property, not a type.** A spec with at least one spec item is a composite. It
may be a member of another composite, and one spec may belong to several composites — the same
member listed by two different programs is not an error, it is two edges. `workItemType: epic` is
still a legal declared type, but nothing derives composition from it.

## The levels are derived, never declared

```text
Story    — no spec item.
Feature  — spec items in one wave (or in no `###` heading at all).
Epic     — spec items in two or more waves; each wave is a feature.
```

| Document | Level |
| --- | --- |
| only task items | `story` |
| task items + one wave of members | `feature` |
| one wave of members, no `###` at all | `feature` |
| members in two waves, even if one wave is task-only | `epic` |

The level is a projection of the document (`presentation_level`), recomputed on every read, stored
nowhere, and never a work-item type. It reaches the outside world twice, both derived: the label
`spec:feature` / `spec:epic` on the card (`spec:story` writes nothing, so a leaf spec carries no
extra label), and a `Level: Feature` line in the card body. A board filter reads the label; a
human reads the body.

`workItemTypes` in `plugin-configuration.md` gains no `level` key: the three levels are structural,
so there is nothing to configure.

## State is derived, never ticked

An item's state is computed from the member document on every read and written nowhere:

| Member | Item |
| --- | --- |
| archived with `outcome: done`, no `pr:` record or its PR `MERGED` (or the PR state unreadable) | `done` |
| archived with `outcome: done`, a `pr:` record and its PR explicitly not `MERGED` | `unmerged` — never satisfies a dependency, stays on the critical path and in `blocked` |
| archived with `outcome: done` and a `pr:` record whose state the lookup could not read | `unverified` — never claims a delivery |
| archived with any other outcome | `dropped` — never satisfies a dependency |
| open, one of its own tasks is `[!]` | `blocked` |
| open, an `after` item is not `done` | `waiting` |
| open, approved or the ready gate met | `ready` (`in-progress` when it is already executing) |
| absent from a store that was read | `missing` |
| in a store that could not be read | `unreadable` — never satisfies a dependency, keeps the composite from archiving as `done` |

The box written in the composite is never read as state, which is why `cq specs task` refuses every
action on a spec item (`sp-link-derived-task`, exit 2): a tick there would be a second, stale copy
of a fact the member owns. A composite archives as `done` only when its own tasks are done and every
member is `done`; `promote` counts both (`sp-open-tasks` names the open count and the total).

## The item is the only link

The composite's `## Tasks` is the single place an edge lives. The member writes nothing.

- `cq specs link add <composite> <spec> [--after S1,S2] [--group "Wave 1"] [--label S9]` lists the
  item with the title read from the member, in one write, and is idempotent — the repair for a
  half-written link. An unknown member is `sp-unknown-id`; a label that is taken or not a plain
  token is `sp-link-bad-label`; an `after:` naming no item is `sp-link-unknown-dependency`; a spec
  linking itself is `sp-link-self`.
- `cq specs link remove <composite> <spec>` drops the item, and reports `changed: false` when it was
  not listed. It refuses (`sp-epic-move-dependents`, nothing written) while another item of the
  composite waits `after` the one being removed.
- `cq specs epic add` is the historical spelling of `link add` and stays accepted. `--move` is
  accepted as a no-op: with no single parent there is nothing to move out of, and a spec may belong
  to several composites at once.
- A member's `epic: <id>` key is **deprecated and ignored**. Derivation never reads it; `validate`
  reports it once per document as `sp-epic-key-deprecated` (warn) with the remedy "remove the key".
  The composite is found from its own items, never from the member.

## Members in another repository

`spec: holetz/quenching#2036` names spec 2036 of the `holetz/quenching` store. The item key is
`owner/repo#id`, owner and repo lower-cased; `#<id>` keeps meaning this store. A reference naming
this repository's own `<owner>/<repo>` reads the local store, and `link add` writes it as the bare
id, so a member is never listed under two spellings.

- **Resolution is derived from `origin`, never configured.** The foreign store's URL is this
  repository's `origin` URL with its trailing `<owner>/<repo>[.git]` swapped: `https://`, scp-like
  `git@host:` and local paths alike. A URL without that path shape (Azure DevOps `/_git/`) and a
  tracker backend resolve nothing: their foreign members are `unreadable`.
- **Read-only by construction.** The store is read through the git backend's read-only mirror under
  `$XDG_CACHE_HOME/quenching/mirrors/`, one `read_specs` per foreign repository; nothing is written
  into either repository's `.git` or store. The fetch TTL and `QUENCHING_SPECS_NO_FETCH` apply as on
  the local store; with fetching off and no mirror yet, the member is `unreadable`. The mirror reads
  only the remote branch: a member's writes still pending in its own clone are invisible here until
  that clone syncs.
- **Unreadable is a state, not an absence.** A store that cannot be fetched makes its items
  `unreadable`; a store that was read and lacks the id makes the item `missing`.
- **PR state** of a foreign member is read with `gh pr view <n> --repo <owner>/<repo>`, never
  against this repository.
- `cq specs link add <composite> <owner>/<repo>#<id>` lists the item with the title read from the
  foreign store and writes nothing there; an unreadable store refuses it
  (`sp-link-member-unreadable`).

`status --epic`, `next --epic`, `validate`, the archive gate and the portal's composition views all
resolve foreign members the same way.

## Reading a composite

- `cq specs status --spec <id>` — on a composite the ordinary status payload carries `level` and
  a `composition` block (`progress`, `groups`, `items`, `blocked`, `criticalPath`, `cycle`); the
  task, records and gates half is untouched, because a composite is also a spec that is developed,
  approved and executed. `cq specs status --epic <id>` returns that same block as the whole payload,
  for a caller that only wants the composition. Any spec id is accepted: a spec with no member
  derives an empty composition, never an error (`sp-unknown-id` is the only refusal).
- `cq specs next --epic <id> [--limit N]` — the ready set an orchestrator runs: in-flight members
  first, then the `priority` record, then wave order. It is the only entry an orchestrator needs.

Members are read in one `read_specs` call per store, a single snapshot on each git store.

## The card: one work-item type, members as predecessors

A composite is a card like any other. The tracker keeps the project's default work-item type — the
`workItemTypes` catalogue entry the spec was born under (`User Story`, `Technical Story`, whatever
the project calls it) — and **never** a type invented for the level: composition is a property of
the document, so the card must not encode a hierarchy the model does not have.

- **Level** rides in the body (`Level: Feature`) and in the label (`spec:feature`, `spec:epic`).
- **Members** ride as lines in the body (`S1 spec 2138 — ready: Foundations`), and as **predecessor
  links** from the composite to each all-digit member id
  (`System.LinkTypes.Dependency-Reverse`). Never a parent-child link: a member may belong to several
  composites, and a hierarchy cannot say that.
- **The lane follows the members.** `board_state_of` returns `executing` when any member is
  `in-progress`, `ready` or `unmerged`, so the composite's card moves when its work starts without
  anyone touching the document. `lifecycle_key` includes the member states, so a member transition
  is a real card write; nothing else about the members is written back.
- The decomposition reads the document: `derive_labels`, `card_state` and `render_card_body` all
  compute level and members on read, so the tracker is a projection, never a second source.

## What `validate` raises

Errors: `sp-link-missing-member` (the id names no spec in a store that was read),
`sp-link-item-unlinked` (an item that looks like a spec item and names nothing),
`sp-link-duplicate-label`, `sp-link-duplicate-member`, `sp-link-unknown-dependency`,
`sp-link-cycle` (an `after:` cycle inside one document) and `sp-link-member-cycle` (a document-level
loop across composites, reported once). Warnings: `sp-link-member-unreadable` (a cross-repository
member's store could not be read — a network failure is not a defect of the composition),
`sp-link-manual-tick` and `sp-link-too-large` (over 100 items, a GitHub parent-card
ceiling), plus `sp-epic-key-deprecated` for the retired back-reference.

The `sp-epic-*` codes were renamed to `sp-link-*`; `sp-epic-key-deprecated` keeps its name because
it names the retired key, not the composition.

## What composition is not

- **It is not `dependsOn`.** `dependsOn` is a frontmatter edge between whole specs, written by
  `cq specs depends` and fed to `cq specs schedule`
  ([spec-dependencies.md](spec-dependencies.md)); composition is membership, written in the
  composite's body. A member may also be a dependency of something else; the two graphs never merge.
- **It is not a work-item hierarchy.** No parent-child link is written, no type changes, and the
  level never reaches the tracker as anything but a label and a body line.
- **It is not a license to tick.** A spec item's box stays open; the state lives in the member.
