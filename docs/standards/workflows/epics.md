---
type: standard
title: Epics contract
description: An epic is a spec whose `## Tasks` items reference member specs — item state derived from the member and never ticked, the `epic:` key read from both ends, `epic add`, `status --epic`, `next --epic` and the findings validate raises
resource: plugins/quenching/assets/bin/quenching/specs/parse/epics.py, plugins/quenching/assets/bin/quenching/specs/commands/epic.py, plugins/quenching/assets/bin/quenching/specs/commands/validate.py, plugins/quenching/assets/specs/schema.json
tags: [workflows, specs, epics, orchestration]
timestamp: 2026-10-07
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
- `### N.` headings are groups (waves); an item without one is ungrouped.
- Every other section keeps its meaning: `## Problem` is the program's goal, `## Design` the shared
  decisions, `## Validation` the done criteria, `## Handoff` the operating rules and state.

## State is derived, never ticked

An item's state is computed from the member document on every read and written nowhere:

| Member | Item |
| --- | --- |
| archived with `outcome: done` | `done` |
| archived with any other outcome | `dropped` — never satisfies a dependency |
| open, a task is `[!]` | `blocked` |
| open, an `after` item is not `done` | `waiting` |
| open, approved or ready gate met | `ready` (`in-progress` when executing) |
| absent | `missing` |

`cq specs task` refuses every action on an epic (`sp-epic-derived-task`): a box written in the
epic would be a second, stale copy of a fact the member already holds. An epic archives as `done`
only when every item is `done`.

## Both ends of the link

A member carries a first-level `epic: <id>` key. `cq specs epic add <epic> <spec> [--after S1,S2]
[--group "Wave 1"] [--label S9]` writes the item and the key together — one commit on the git store —
and is idempotent, so it is also the repair for a half-written link. One level only: an epic cannot
be a member, and a spec belongs to one epic.

## Reading an epic

- `cq specs status --epic <id>` — progress per group, blocked items with their reasons, the critical
  path (the longest chain of items not yet `done`).
- `cq specs next --epic <id> [--limit N]` — the ready set an orchestrator runs: in-flight members
  first, then the `priority` record, then wave order. It is the only entry an orchestrator needs.

Members are read in one `read_specs` call, a single snapshot on the git store.

## What `validate` raises

Errors: `sp-epic-missing-member`, `sp-epic-divergent` (the item and the member's `epic:` disagree),
`sp-epic-orphan` and `sp-epic-not-an-epic` (the member names an absent or non-epic spec),
`sp-epic-cycle`, `sp-epic-unknown-dependency`, `sp-epic-duplicate-label`,
`sp-epic-duplicate-member`, `sp-epic-item-unlinked` and `sp-epic-nested`. Warnings:
`sp-epic-manual-tick`, `sp-epic-empty` and `sp-epic-too-large` (over 100 items, a GitHub
parent-card ceiling).

Epics are not a card concern: the native parent link on a tracker card is a rendering of this
document, written once and never read back.
