---
type: decision
title: Task execution contract history
description: Why the blocked marker replaced the attempt counter, the Handoff cadence measurement and an unresolvable archived subject
resource: plugins/quenching/commands/specs/execute.md, plugins/quenching/assets/references/specs-execute/execution.md
tags: [decision, history, workflows]
timestamp: 2026-10-07
audience: both
authority: current
source: cut-specs-execute-turns; task-execution standard (history moved 2026-10-07)
maintainer: quenching
---

# Task execution contract history

History moved out of [task-execution](../standards/workflows/task-execution.md) so the standard keeps the rule. Sections are the original text.

## Why the marker replaced the counter

The earlier contract kept an attempt count in a `.specs.json` sidecar and hard-stopped at five. The
count was machine state a human never saw: a task went quiet after five failures with **no trace of
why**, and the only way to resume was a `--reset-attempts` incantation that bought five more
attempts at the same wrong approach.

The objection to a third glyph was that `- [!]` would break consumers of `CHECKBOX_RE` and would not
survive hand-editing. Both were answered rather than argued away: the regex admits the glyph
explicitly, and a marker a human can read is *more* likely to survive hand-editing than a sidecar
they never open — because the reason is right there in the line they are already looking at.

## Unresolvable subject on an archived spec, measured 2026-08-17

Measured on this repository's `github` backend (2026-08-17): the archived spec
`revisar-politica-de-assets-checks` (issue #902) carries a `subject:` on task 5.1 that
`git log --grep` cannot resolve, because the tick was API-only and the commit it names was never
made. It is **not** backfilled — an archived spec is never rewritten
([plan-git-record.md](../standards/workflows/plan-git-record.md) §The subject is the anchor) — and a task-level checker
symmetric to `sp-bad-merge` remains a separate surface, deliberately not built here.

## Why the Handoff cadence is four events

The cadence it replaced was *after each committed task*. Measured on a 13-task run, four rewrites of
~400 words each were **~90% identical** to one another: the section is sent with every task, so the
cost is paid on both sides, and near-identical rewrites buy nothing on either.

