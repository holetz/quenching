---
type: standard
title: Plan lifecycle contract
description: The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, and the append-only archive rule for facts that did not exist at the move
resource: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/**, specs/**
tags: [workflows, specs, lifecycle, stages, frontmatter, records]
timestamp: 2026-08-03
audience: both
authority: current
source: specs-flow-consolidation plan (sections 1-2); the merge record's form and branch's owner amended by the move-conclude-merge-last plan (task 5.2); the append-only archive rule from the retire-docs-log plan's branch review; `date` moved from derived-from-the-basename to declared by evaluate-spec-creation-flow (task 5.6), after an external backend left the derivation with nothing to derive from
maintainer: quenching
---

# Plan lifecycle contract

Where a spec lives over its life, which of its states are computed, and which facts are recorded
because nothing can compute them. This is the v3 lifecycle — one active folder, stages derived,
human judgments in frontmatter. The spec-*file* contract (the fourteen canonical sections, the
phase-scoped explicit-none rule, the duplicated template) is
[plan-artifacts.md](plan-artifacts.md) and is untouched by v3; that file's v2 *lifecycle* claims —
the three-folder phase model, promote-as-the-human-OK, and the minimal frontmatter list — are
superseded by this one.

## One active folder

A spec spends its whole pre-archive life in `specs/plans/` and moves exactly once, to
`specs/archive/` when it closes. The basename — `<slug>.md`, with the capture date declared as
`date:` in the frontmatter and never rewritten — and the bare-slug identity rule are unchanged from
[plan-artifacts.md](plan-artifacts.md) §One spec is one file.

v3 folded `backlog/` and `ready/` into `plans/` because the split lied twice: `backlog/` held both
one-line captures and fully designed specs (it was never an inbox, only "not building yet"), and
`ready/` restated a fact the sections already carry — completeness — which is now derived. The one
fact the `backlog/ → ready/` `git mv` recorded that no derivation reproduces is *a human said go*,
and that fact moved into frontmatter as `approved: {date}`.

`promote` therefore has one hop, `plans/ → archive/`, and it is the only move a spec ever makes.
Archiving as `done` refuses while `- [ ]` boxes remain (`--force` overrides); `abandoned` is
always allowed, because open tasks are what closing out unbuilt work looks like.

### The archive is append-only, for facts that did not exist at the move

`archive/` is history, and nothing revises it. The one thing that may be added is a fact that
**came into being after the move** — which is not a revision of what the spec claimed, but a
record of what happened to it. There are exactly two, both written by `/specs:conclude` onto the
spec that run is closing, and both before the merge:

| Append | Why it cannot be written earlier |
| --- | --- |
| `merge: {strategy, subject}` | the subject names a merge commit that does not exist yet — and stamping it *after* the merge would mean a write on the base branch, the exact thing the merge-last ordering exists to prevent |
| the distillation's one line per minted doc, appended to `## Outcome` | `## Outcome` is drafted at the archive gate, before the distillation pass knows what it minted; the paths do not exist until the harvest runs |

The shape of the test is what generalizes, not the count: an append is permitted only when the
fact is **unavailable at promote time and unwritable anywhere else**. The distillation line
qualifies on the second clause too — `docs/log.md` used to carry that provenance, and with the
log retired the archived spec is the only honest home left for "this doc came from this spec".

**A third exception is argued for, never assumed from these two.** Two precedents are how a
bounded rule becomes an unbounded one; if a future run wants to write into `archive/`, the case is
that the fact meets both clauses, not that the archive was already written to twice. A spec other
than the one being closed is never touched, and a spec archived by an earlier run is never
revisited.

## Frontmatter records human judgments; everything else is derived

The organizing principle, and the admission test for every frontmatter key:

> A field earns its place only when it records a **human judgment no derivation can reproduce**.
> The filesystem, git, and section presence record everything else.

That is why there is no `phase` (the folder), no `ready` flag (the ten gate sections), and no
attempt counter (the visible `- [!]` marker).

**`date` is the one fact that moved the other way, and the test is what moved it.** It used to be
excluded on exactly these grounds — the filename's `YYYY-MM-DD-` prefix recorded it, so a field
would have been a second copy. The test says a field earns its place when no derivation reproduces
it, and the derivation that supported the exclusion was *the basename*. A store with no filenames
has none, and the native value that looks like a substitute is a different fact: an issue's
`created_at` is when the issue was made, and a migration stamps them all on one day — measured
here, 68 of 70 capture dates would have been rewritten to the migration's own afternoon. So `date`
is **declared, not derived**, and the basename went back to being the slug alone. The rule did not
bend; the derivation it relied on stopped existing.

Beyond the declared identity (`slug`, `title`, `date`) and the optional `verification` — absent
means the default, applied on read, never stamped to make it explicit — every optional key is one
record:

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
