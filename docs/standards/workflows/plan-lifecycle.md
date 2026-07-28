---
type: standard
title: Plan lifecycle contract
description: The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, and the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else
resource: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/**, specs/**
tags: [workflows, specs, lifecycle, stages, frontmatter, records]
timestamp: 2026-07-28
audience: both
authority: current
source: specs-flow-consolidation plan (sections 1-2); the merge record's form and branch's owner amended by the move-conclude-merge-last plan (task 5.2)
maintainer: quenching
---

# Plan lifecycle contract

Where a spec lives over its life, which of its states are computed, and which facts are recorded
because nothing can compute them. This is the v3 lifecycle — one active folder, stages derived,
human judgments in frontmatter. The spec-*file* contract (the thirteen canonical sections, the
phase-scoped explicit-none rule, the duplicated template) is
[plan-artifacts.md](plan-artifacts.md) and is untouched by v3; that file's v2 *lifecycle* claims —
the three-folder phase model, promote-as-the-human-OK, and the minimal frontmatter list — are
superseded by this one.

## One active folder

A spec spends its whole pre-archive life in `specs/plans/` and moves exactly once, to
`specs/archive/` when it closes. The filename — `YYYY-MM-DD-<slug>.md`, date stamped at capture
and never rewritten — and the bare-slug identity rule are unchanged from
[plan-artifacts.md](plan-artifacts.md) §One spec is one file.

v3 folded `backlog/` and `ready/` into `plans/` because the split lied twice: `backlog/` held both
one-line captures and fully designed specs (it was never an inbox, only "not building yet"), and
`ready/` restated a fact the sections already carry — completeness — which is now derived. The one
fact the `backlog/ → ready/` `git mv` recorded that no derivation reproduces is *a human said go*,
and that fact moved into frontmatter as `approved: {date}`.

`promote` therefore has one hop, `plans/ → archive/`, and it is the only move a spec ever makes.
Archiving as `done` refuses while `- [ ]` boxes remain (`--force` overrides); `abandoned` is
always allowed, because open tasks are what closing out unbuilt work looks like.

## Frontmatter records human judgments; everything else is derived

The organizing principle, and the admission test for every frontmatter key:

> A field earns its place only when it records a **human judgment no derivation can reproduce**.
> The filesystem, git, and section presence record everything else.

That is why there is no `created` (the filename's date prefix), no `phase` (the folder), no
`ready` flag (the ten gate sections), and no attempt counter (the visible `- [!]` marker). Beyond
the declared identity (`slug`, `title`, `verification`), every optional key is one record:

| Record | Written by | Write-once | What only a human can answer |
| --- | --- | --- | --- |
| `priority: {level, criticality, complexity, date}` | `triage` | no | this spec's rank against every other one |
| `refined: {mode, date}` | `develop` | no | that a real interrogation happened, and in which mode |
| `approved: {date}` | `develop`, or `execute` inline | yes | that a human said go |
| `branch: {base, work}` | `isolate` | yes | after a merge, git cannot say what the base was |
| `reviewed: {date}` | `conclude` | no | that a human read the whole branch diff |
| `merge: {strategy, subject}` | `conclude` | yes | the strategy was a choice; the subject names the merge it produced |
| `outcome: done \| abandoned` | `conclude` | yes | the verdict on whether the work completed |

Read top to bottom, the records narrate the spec's history in order: ranked, interrogated,
approved, built, reviewed, merged, closed. `writeOnce: true` marks an irreversible transition —
rewriting the value would falsify a fact that already happened; the restampable three each carry
their own `date` because their owning command may legitimately re-judge. In neither case may a
command other than the one named in `writtenBy` touch the record. The vocabulary lives in
`assets/specs/schema.json` (`frontmatter.records`), which `specs.py` embeds as its fallback.

## `ready` is derived, and `approved` is a human's word

Every stage is computed from heading presence and frontmatter — last match wins, and derived state
regresses automatically when a section empties, which declared state never does:

`captured` → `proposed` → `designed` → `refined` → `ready` → `approved` → `executing`

`ready` is the v3 replacement for the `ready/` folder: the **same ten sections** that were its
entry gate (`## Problem` through `## Risks`, plus `## Tasks`), resolved by computation instead of
a `git mv`. Its rule in `schema.json` carries `gate: true` and is the single source of the ready
set — nothing may restate those ten sections elsewhere. It refuses nothing: a gate that moves no
file is a **floor** that `execute` reports against, not a verdict.

`approved` sorts after `ready` but does not require it — a human may say go before every section
is filled. `execute` on an unapproved spec **never refuses**: it asks inline, stamps
`approved: {date}` on a yes, and proceeds — refusing would rebuild the folder hop v3 removed. The
distinction matters because an agent can satisfy every section itself (`- none — <reason>` counts
as filled), so section completeness can never stand in for the human OK.

## The v2→v3 migration

`specs.py migrate` performs the fold exactly once per workspace: every file in `backlog/` and
`ready/` moves to `plans/` with its basename unchanged, `archive/**` is never touched, and an
already-v3 workspace exits 2. Nothing is renamed, so every recorded slug, date and cross-reference
survives; the completeness `ready/` used to imply is recomputed on the next read, and the human OK
it used to carry is whatever `approved` records say.
