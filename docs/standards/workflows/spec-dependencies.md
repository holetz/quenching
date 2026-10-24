---
type: standard
title: Spec dependencies contract
description: A spec may declare the specs it depends on with a first-level `dependsOn` key written only by `cq specs depends`; `cq specs schedule` derives start, finish, slip and the critical path from that graph and the existing `start`/`target`, and validate raises four dependency findings
resource: plugins/quenching/assets/bin/quenching/specs/parse/deps.py, plugins/quenching/assets/bin/quenching/specs/commands/deps.py, plugins/quenching/assets/bin/quenching/specs/commands/validate.py, plugins/quenching/assets/specs/schema.json
tags: [workflows, specs, dependencies, schedule]
timestamp: 2026-10-24
audience: both
authority: current
source: spec 2039 (dependencies between any specs and a derived schedule)
maintainer: quenching
---

# Spec dependencies contract

Any spec may declare the specs it waits for. The edge lives in the spec's own document; the
schedule is derived on every read and never stored.

## The key

`dependsOn: [2036, 2037]` is a first-level frontmatter key beside `epic`, a flow list of ids of
this store. It is not one of the tracker-projected fields: no tracker has a native counterpart, so
it is carried in the document only. A scalar `dependsOn: 2036` reads as one id and a leading `#`
is tolerated. Cross-repository ids (`owner/repo#id`) are not read; the foreign-store read belongs to
epic members.

## The verbs

- `cq specs depends <id> [--add 12,34] [--remove 12] [--json]` is the only writer of the key. It is
  idempotent and prints the key when given no flag. It refuses, exit 2 and nothing written, an
  unknown id (`sp-dep-missing`), a self-reference (`sp-dep-self`) and an edge that would close a
  cycle (`sp-dep-cycle`).
- `cq specs schedule [--spec <id>] [--json]` prints the derived schedule: per spec the planned
  `start` and `target`, `earliestStart`, `earliestFinish`, `slipDays` (only when positive) and
  `critical`, plus `criticalPath` as an id list and `cycle` when one exists. Exit 1 on a cycle,
  0 otherwise. It writes nothing; the portal's Gantt view consumes the JSON.

## The derivation

Nodes are the open specs that declare an edge plus their transitive dependencies, archived ones
included as fixed inputs. In topological order, `earliestStart` is the latest `earliestFinish`
among the dependencies, never earlier than the spec's own `start`; `earliestFinish` is
`earliestStart` plus the days between `start` and `target`, or the spec's `target` when only that is
set. An unknown stays `null` and propagates as unknown, never as zero. A dependency archived `done`
finishes at its `target` when it has one, else it constrains nothing. `slipDays` is
`earliestFinish` minus `target` when positive. The critical path follows, from the latest known
`earliestFinish`, the dependency that fixed each `earliestStart`. Durations are calendar days.

## The findings

`cq specs validate` checks the whole graph:

| Code | Severity | Means |
| --- | --- | --- |
| `sp-dep-missing` | error | the id names no spec |
| `sp-dep-self` | error | a spec depends on itself |
| `sp-dep-cycle` | error | the graph closes a cycle; the message names the path |
| `sp-dep-dropped` | warn | depends on a spec archived with an outcome other than `done` |

## What it does not replace

`after:` between the items of one epic stays the epic-local edge ([epics.md](epics.md)), and
`dependsOn` never replaces it. `cq specs next --front` and `next --epic` keep their ordering:
folding `dependsOn` into the rank is a follow-up.
