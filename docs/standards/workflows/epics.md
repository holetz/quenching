---
type: standard
title: Epics contract
description: An epic is a spec whose `## Tasks` items reference member specs — item state derived from the member and never ticked, the `epic:` key read from both ends, members in another repository's store read-only, `epic add`, `status --epic`, `next --epic` and the findings validate raises
resource: plugins/quenching/assets/bin/quenching/specs/parse/epics.py, plugins/quenching/assets/bin/quenching/specs/members.py, plugins/quenching/assets/bin/quenching/specs/commands/epic.py, plugins/quenching/assets/bin/quenching/specs/portal.py, plugins/quenching/assets/bin/quenching/specs/commands/validate.py, plugins/quenching/assets/specs/schema.json
tags: [workflows, specs, epics, orchestration]
timestamp: 2026-10-24
audience: both
authority: current
source: S28 of the specs-store program (epics and programs of specs)
maintainer: quenching
---

# Epics contract

Work that spans several specs has a representation: an **epic** is an ordinary spec carrying
`workItemType: epic` whose `## Tasks` items are member specs instead of checkboxes to build. One
document format, one parser, one derivation — the same canonical document every backend stores.

## The grammar

```markdown
### 1. Wave 1 — foundations
- [ ] S1 Honest local gate — spec: #1201
### 2. Wave 2
- [ ] S2 One English AGENTS.md — spec: #1202 — after: S1
```

- `S1` is the item's **label**, `spec: #<id>` its member, `after: S1,S2` the labels it waits for.
- `spec: <owner>/<repo>#<id>` names a member in another repository's store (§Members in another
  repository); `after:` edges cross between local and foreign items unchanged.
- `### N.` headings are groups (waves); an item without one is ungrouped.
- Every other section keeps its meaning: `## Problem` is the program's goal, `## Design` the shared
  decisions, `## Validation` the done criteria, `## Handoff` the operating rules and state.

## State is derived, never ticked

An item's state is computed from the member document on every read and written nowhere:

| Member | Item |
| --- | --- |
| archived with `outcome: done`, no `pr:` record or its PR `MERGED` (or the PR state unreadable) | `done` |
| archived with `outcome: done`, a `pr:` record and its PR explicitly not `MERGED` | `unmerged` — never satisfies a dependency, stays on the critical path and in `blocked` |
| archived with any other outcome | `dropped` — never satisfies a dependency |
| open, a task is `[!]` | `blocked` |
| open, an `after` item is not `done` | `waiting` |
| open, approved or ready gate met | `ready` (`in-progress` when executing) |
| absent from a store that was read | `missing` |
| in a store that could not be read | `unreadable` — never satisfies a dependency, keeps the epic from archiving as `done` |

`cq specs task` refuses every action on an epic (`sp-epic-derived-task`): a box written in the
epic would be a second, stale copy of a fact the member already holds. An epic archives as `done`
only when every item is `done`.

## Both ends of the link

A member carries a first-level `epic: <id>` key. `cq specs epic add <epic> <spec> [--after S1,S2]
[--group "Wave 1"] [--label S9]` writes the item and the key together — one commit on the git store —
and is idempotent, so it is also the repair for a half-written link. One level only: an epic cannot
be a member, and a spec belongs to one epic.

A spec that already belongs to another epic is refused (`sp-epic-member-taken`). `--move` takes it
out of that epic and into this one in the same write: the old item leaves the old epic's `## Tasks`,
the new item is listed, and `epic:` is restamped. A move is refused (`sp-epic-move-dependents`, nothing
written) while another item of the old epic waits `after` the moved one.

## Members in another repository

`spec: holetz/quenching#2036` names spec 2036 of the `holetz/quenching` store. The item's key is
`owner/repo#id`, owner and repo lower-cased; `#<id>` keeps meaning this store. A reference naming
this repository's own `<owner>/<repo>` reads the local store, and `epic add` writes it as the bare
id, so a member is never listed under two spellings.

- **Resolution is derived from `origin`, never configured.** The foreign store's URL is this
  repository's `origin` URL with its trailing `<owner>/<repo>[.git]` swapped: `https://`, scp-like
  `git@host:` and local paths alike. A URL without that path shape (Azure DevOps `/_git/`) and a
  tracker backend resolve nothing: their foreign members are `unreadable`.
- **Read-only by construction.** The store is read through the git backend's read-only mirror under
  `$XDG_CACHE_HOME/quenching/mirrors/`, one `read_specs` per foreign repository; nothing is written
  into either repository's `.git` or store. The fetch TTL and `QUENCHING_SPECS_NO_FETCH` apply as on
  the local store; with fetching off and no mirror yet, the member is `unreadable`.
- **Unreadable is a state, not an absence.** A store that cannot be fetched makes its items
  `unreadable`; a store that was read and lacks the id makes the item `missing`.
- **No back-reference across repositories.** A foreign member's `epic:` names an epic in its own
  store, so the same spec may also belong to a local epic there. `sp-epic-divergent` is checked only
  for same-store members, `sp-epic-nested` still applies, and a member whose own `epic:` uses the
  reference form is accepted unverified.
- **PR state** of a foreign member is read with `gh pr view <n> --repo <owner>/<repo>`, never
  against this repository.
- `cq specs epic add <epic> <owner>/<repo>#<id>` lists the item with the title read from the foreign
  store and writes nothing there; an unreadable store refuses it (`sp-epic-member-unreadable`).

`status --epic`, `next --epic`, `validate`, the archive gate and the portal's epic views all
resolve foreign members the same way.

## Reading an epic

- `cq specs status --epic <id>` — progress per group, blocked items with their reasons, the critical
  path (the longest chain of items not yet `done`).
- `cq specs next --epic <id> [--limit N]` — the ready set an orchestrator runs: in-flight members
  first, then the `priority` record, then wave order. It is the only entry an orchestrator needs.

Members are read in one `read_specs` call per store, a single snapshot on each git store.

## What `validate` raises

Errors: `sp-epic-missing-member`, `sp-epic-divergent` (the item and the member's `epic:` disagree),
`sp-epic-orphan` and `sp-epic-not-an-epic` (the member names an absent or non-epic spec),
`sp-epic-cycle`, `sp-epic-unknown-dependency`, `sp-epic-duplicate-label`,
`sp-epic-duplicate-member`, `sp-epic-item-unlinked` and `sp-epic-nested`. Warnings:
`sp-epic-member-unreadable` (a cross-repository member's store could not be read — a network
failure is not a defect of the epic), `sp-epic-manual-tick`, `sp-epic-empty` and `sp-epic-too-large` (over 100 items, a GitHub
parent-card ceiling).

Epics are not a card concern: the native parent link on a tracker card is a rendering of this
document, written once and never read back.
