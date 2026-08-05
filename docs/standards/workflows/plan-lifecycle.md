---
type: standard
title: Plan lifecycle contract
description: The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, the append-only archive rule for facts that did not exist at the move, and the moment a follow-up becomes a spec — definition parks it as a Discoveries line, close-out mints it
resource: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/**, plugins/quenching/assets/references/specs-develop/questions.md, specs/**
tags: [workflows, specs, lifecycle, stages, frontmatter, records, discoveries]
timestamp: 2026-08-05
audience: both
authority: current
source: specs-flow-consolidation plan (sections 1-2); the merge record's form and branch's owner amended by the move-conclude-merge-last plan (task 5.2); the append-only archive rule from the retire-docs-log plan's branch review; `date` moved from derived-from-the-basename to declared by evaluate-spec-creation-flow (task 5.6), after an external backend left the derivation with nothing to derive from; `branch`'s owner moved from the retired isolation command to `execute`, and `merge` gained `pr`, by the rework-specs-isolate-flow plan (task 3.4); the follow-up parking rule from the stop-develop-offering-follow-up-specs plan (task 2.1); the records-narration line corrected from "built" to "isolated" by labels-historico-spec-issue (task 7.1), which had read `branch` as narrating the derived `executing` stage it does not write
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
| `merge: {strategy, subject, pr}` | the subject names a merge commit that does not exist yet, and — on the PR route — `pr` names a pull request that does not exist until it is opened; stamping any of it *after* the merge would mean a write on the base branch, the exact thing the merge-last ordering exists to prevent |
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
| `branch: {base, work}` | `execute` | yes | after a merge, git cannot say what the base was |
| `reviewed: {date}` | `conclude` | no | that a human read the whole branch diff |
| `merge: {strategy, subject, pr}` | `conclude` | yes | the strategy was a choice; the subject names the merge it produced; `pr` names the pull request on the PR route, unwritable before it exists |
| `outcome: done \| abandoned` | `conclude` | yes | the verdict on whether the work completed |

Read top to bottom, the records narrate the spec's history in order: ranked, interrogated,
approved, isolated, reviewed, merged, closed. **Not** "built" — `branch` narrates that isolation
was taken (a worktree or a branch cut, `base` and `work` recorded), never that the work
finished; "built" is the derived stage `executing` (`stages.derived`, keyed off task state or a
filled `## Handoff`), which a spec built in place, with no `branch` record at all, still reaches.
`writeOnce: true` marks an irreversible transition —
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

## When a follow-up becomes a spec

A pass that **defines** parks; only the pass that **closes out** mints. The rule is about the
moment in the lifecycle, not about which command happens to be running:

| Moment | What happens to an out-of-scope finding |
| --- | --- |
| definition — `/specs:develop`, any bank | one line of `## Discoveries` on the spec being developed, written with `specs.py discover` inside the pass's one confirmed edit |
| close-out — `/specs:conclude` on a `done` outcome | the harvest turns it into a fresh spec, if it still deserves one |

The asymmetry is the whole rule. At definition time nobody knows whether the parent will ship, so
a spec minted then is a bet placed before the information arrives; at close-out that fact is in
hand, which is why the harvest table in `specs-conclude/distill.md` is the only place a follow-up
becomes a file.

**The measurement.** One autonomous `/specs:develop` pass over 32 open specs, one agent per spec,
raised 4–6 follow-up candidates each — well over a hundred — and the same `specs.py` defects
surfaced independently in three or four agents that could not see one another. A definition-time
offer scales with what the pass *imagines*, and the queue it fills is charged again to every
`specs.py next --front` ranking, `/specs:continue` table and `/specs:triage` read that has to walk
past it. Duplicates arriving through that door are turned away at it: the discoveries bank's
`promoted:` resolution reads the front first and resolves a line an open spec already covers as
`dismissed: already covered by {slug}` — still three resolutions, never a fourth token.

Where the rule is written: `commands/specs/develop.md` carries it as an `## Invariants` entry, with
the guard that `specs.py new` runs inside a develop pass **only** as that `promoted:` resolution;
its step 5 shows the parked line in the consolidated plan and its step 6 makes the `specs.py
discover` call part of that same edit, because nothing may be written mid-bank.
`assets/references/specs-develop/questions.md` carries the dedup step on the bank's resolution
table.

**The dependency that makes parking free.** `assets/specs/schema.json` derives the stage ladder
from `## Problem` through `## Risks` plus `## Tasks`; `## Discoveries` appears in no stage rule, so
filling it moves nothing. Parking therefore costs one line and no derived state. A future change
that made `## Discoveries` a stage trigger would silently turn every parked finding into a stage
regression — which is why the independence is recorded here rather than left to be rediscovered.

**One route this does not touch.** A human who asks mid-pass for something that would rewrite an
already-agreed spec is not filing a follow-up: the alternative there is damaging the spec that
exists, so `/specs:develop`'s intent-change route still names `/specs:create`. Parking is for what
the pass surfaced on its own.

## The v2→v3 migration

`specs.py migrate` performs the fold exactly once per workspace: every file in `backlog/` and
`ready/` moves to `plans/` with its basename unchanged, `archive/**` is never touched, and an
already-v3 workspace exits 2. Nothing is renamed, so every recorded slug, date and cross-reference
survives; the completeness `ready/` used to imply is recomputed on the next read, and the human OK
it used to carry is whatever `approved` records say.
