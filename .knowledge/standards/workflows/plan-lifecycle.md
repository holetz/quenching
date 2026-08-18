---
type: standard
title: Plan lifecycle contract
description: The single-folder lifecycle — plans/ plus archive/ — the derived ready stage and the approved record, `conclude` archiving before the merge and what `## Outcome` asserts because of it, the rule that frontmatter records human judgments while the filesystem, git and section presence record everything else, `branch`/`pr`/`merge` split across `execute`-or-`git:branch`, `git:pr:create` and `git:merge` now that `conclude` writes neither of the last two, the append-only archive rule for facts that did not exist at the move — no longer all landing in the same run — and the moment a follow-up becomes a spec — definition parks it as a Discoveries line, close-out mints it
resource: plugins/quenching/assets/specs/schema.json, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/commands/specs/**, plugins/quenching/commands/git/branch.md, plugins/quenching/commands/git/merge.md, plugins/quenching/commands/git/pr/create.md, plugins/quenching/assets/references/specs-develop/questions.md, /.specs/**
tags: [workflows, specs, lifecycle, stages, frontmatter, records, discoveries]
timestamp: 2026-08-18
audience: both
authority: current
source: specs-flow-consolidation plan (sections 1-2); the merge record's form and branch's owner amended by the move-conclude-merge-last plan (task 5.2); the append-only archive rule from the retire-docs-log plan's branch review; `date` moved from derived-from-the-basename to declared by evaluate-spec-creation-flow (task 5.6), after an external backend left the derivation with nothing to derive from; `branch`'s owner moved from the retired isolation command to `execute`, and `merge` gained `pr`, by the rework-specs-isolate-flow plan (task 3.4); the follow-up parking rule from the stop-develop-offering-follow-up-specs plan (task 2.1); the records-narration line corrected from "built" to "isolated" by labels-historico-spec-issue (task 7.1), which had read `branch` as narrating the derived `executing` stage it does not write; `complexity`'s own writers (`[triage, create, develop]`) and its exit from the frontmatter admission test by the fluxo-rapido-para-problemas-simplorios plan (task 1.5); the `pr` record, the third append and the isolation narration corrected for the in-place `work == base` pair by vincular-spec-a-branch-commits-e-pr at its conclude — the third append argued against both clauses of the test above, as this section demands, rather than assumed from the two that preceded it; the parking row's edit de-qualified from "confirmed" to "consolidated" by revisar-fluxo-do-develop-custo-e-gates at its branch review (2026-08-16), which removed `/quenching:specs:develop`'s plan gate while leaving the one-edit-per-bank mechanic the row actually depends on; the criterion `complexity` measures — how much a human needs to be part of the process, never size or scope — and the `fanoutMinComplexity` consumer that reads it as a configurable floor, by redefinir-o-que-complexity-mede-e-configurar-o-limiar-do-fan-out (2026-08-16); `pr:`/`merge:` ownership moved off `conclude` onto `git:pr:create`/`git:merge`, the append-only table split by writer and run, the records-narration reordered, and `## Outcome`'s narrowed assertion documented, by pilar-git-e-specs-agnosticas-ao-git (task 6.5); `outcome`'s `done` half moved from asked-every-time to derived-from-the-boxes (2026-08-18), the third field to be argued against the admission test rather than assumed past it, on session `c5ffb0aa`'s measurement that the question was ratifying what the payload already carried
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

A spec spends its whole pre-archive life in `/.specs/plans/` and moves exactly once, to
`/.specs/archive/` when it closes. The basename — `<slug>.md`, with the capture date declared as
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

### `conclude` archives before the merge, and `## Outcome` asserts only what it delivered

`/quenching:specs:conclude` promotes to `archive/` — the one hop above — **before** any merge
happens, not after. `## Outcome` is drafted and written at that same gate, so what it can honestly
assert is bounded by what is true at that moment: for `done`, that the branch was **reviewed**,
the emergent `/.knowledge/` was **written**, the spec was **distilled**, and the pre-merge gate ran
**green** — never that the work is merged, live on the base, or that a PR exists, because none of
those are decided yet. The merge itself, and any PR, are facts of the git host from here on:
`git log` on the base once it lands, `gh pr view` while it is open. A reader who needs to know
whether an archived `done` spec actually reached the base reads git, the same way `cq specs next
--front` already reads git rather than a record to answer "is this spec in flight" — `## Outcome`
was never the place that question was answered from.

This is a deliberate narrowing from what `## Outcome` used to assert, and the trade it makes is
named in [plan-git-record.md](plan-git-record.md) §What `conclude` hands off: nothing is lost,
because the merge strategy and the PR — when a run for either happens — still land in `merge:`
and `pr:`, readable off the very same archived spec once those records exist. `## Outcome` narrates
the run that closed the spec; the two records narrate whatever ran after it.

### The archive is append-only, for facts that did not exist at the move

`archive/` is history, and nothing revises it. The one thing that may be added is a fact that
**came into being after the move** — which is not a revision of what the spec claimed, but a
record of what happened to it. There are exactly three, and — unlike before `conclude` stopped
short of the merge — they no longer share one writer or one run: the distillation line is
`/quenching:specs:conclude`'s own, made in the same run as the archive move; `merge:` and `pr:` are
made later, by whichever of `/quenching:git:merge` / `/quenching:git:pr:create` the human runs next,
onto the spec that command's own invocation names. All three still land only onto the spec being
touched, and none of them after the merge:

| Append | Written by | Why it cannot be written earlier |
| --- | --- | --- |
| the distillation's one line per minted doc, appended to `## Outcome` | `conclude`, same run as the archive move | `## Outcome` is drafted at the archive gate, before the distillation pass knows what it minted; the paths do not exist until the harvest runs |
| `pr: {number, url, date}`, when a PR was opened | `git:pr:create`, a later, separate run | the number does not exist until `gh pr create` returns, which is after the archive move by construction. It is not `merge.pr` restated: under `specs:cycle`'s minimal gear the run **stops** at the open PR, so `merge` is never stamped at all and this is the spec's only record of the PR — the fact would otherwise have no home anywhere |
| `merge: {strategy, subject, pr}` | `git:merge`, a later, separate run | the subject names a merge commit that does not exist yet, and — when a PR came first — `pr` names a pull request that does not exist until it is opened; stamping any of it *after* the merge would mean a write on the base branch, the exact thing the merge-last ordering exists to prevent |

The shape of the test is what generalizes, not the count: an append is permitted only when the
fact is **unavailable at promote time and unwritable anywhere else** — not that it lands in the
same run as the promote. The distillation line qualifies on the second clause too — `/.knowledge/log.md`
used to carry that provenance, and with the log retired the archived spec is the only honest home
left for "this doc came from this spec".

**A further exception is argued for, never assumed from the ones already here.** Precedents are how
a bounded rule becomes an unbounded one; if a future run wants to write into `archive/`, the case is
that the fact meets both clauses, not that the archive was already written to before. The `pr:`
row is what that demand looks like when it is met: it was added by a spec that had to show the
number is unavailable at promote time *and* that no other record could hold it, rather than
pointing at the row above it. A spec other
than the one being closed is never touched, and a spec archived by an earlier run is never
revisited.

## Frontmatter records human judgments; everything else is derived

The organizing principle, and the admission test for every frontmatter key:

> A field earns its place only when it records a **human judgment no derivation can reproduce**.
> The filesystem, git, and section presence record everything else.

That is why there is no `phase` (the folder), no `ready` flag (the ten gate sections), and no
attempt counter (the visible `- [!]` marker).

**`date` was the first field to move the other way, and the test is what moved it.** It used to be
excluded on exactly these grounds — the filename's `YYYY-MM-DD-` prefix recorded it, so a field
would have been a second copy. The test says a field earns its place when no derivation reproduces
it, and the derivation that supported the exclusion was *the basename*. A store with no filenames
has none, and the native value that looks like a substitute is a different fact: an issue's
`created_at` is when the issue was made, and a migration stamps them all on one day — measured
here, 68 of 70 capture dates would have been rewritten to the migration's own afternoon. So `date`
is **declared, not derived**, and the basename went back to being the slug alone. The rule did not
bend; the derivation it relied on stopped existing.

**`outcome` is the third, and it did not move — half of it stopped having to be asked.** The field
still earns its place under the test: nothing derives `abandoned`, and no count of ticked boxes
separates "shipped" from "dropped after the work was already done", so the value stays a claim only
a human makes. What changed is who states the easy half. `/quenching:specs:conclude` derives `done`
when every box is ticked and none is blocked, announces it rather than asking, and writes it — and
that derivation is safe not because it is clever but because `cq specs promote` refuses `done` over
an open box on its own, so a wrong derivation has no way to land. Anything short of that is still
asked, and that question is where abandonment lives. The record itself is unchanged and stays
`writeOnce: true`; what left is a question that used to be paid every single time to hear the answer
the boxes already gave.

**`complexity` is the second — and it moved against the test rather than by it.** It used to earn
its place as a human's guess, the triage sweep's rough size in hours, a judgment like any other.
Then part of it became computed: `/quenching:specs:create` derives a level from its own classification of
the input (a sentence is `low`, a plan file is `medium`), `/quenching:specs:develop` re-evaluates the level
when a pass closes, and both write through `cq specs record` on a human's confirmation, never a
silent restamp — the judgment left in the field is the word on the proposal, not the value itself.
What keeps it in frontmatter is the consumer: the orchestrator derives its whole gears plan from
this level before the build, when the sections that would evidence it do not exist yet, and no
file, filesystem or git state carries the level in the discrete scale the gears plan needs. So the
field declares its own writers — `[triage, create, develop]` — under a record whose owner stays
`triage`, and the admission test keeps its shape for every other key.

**What the level measures is not the size of the change.** `complexity` answers how much a human
needs to be part of the process — `low` says the LLM can carry it with close to no supervision,
`medium` accepts some real risk in leaving stage-by-stage judgment to it alone, `high` and `xhigh`
escalate the need for a human's presence — never the size, scope or difficulty of the input, which
`triage`'s `level`/`criticality` pair already answers on its own axis. `/quenching:specs:execute-queue` and
`/quenching:specs:develop-batch` read the level against a configurable floor, `fanoutMinComplexity`
(`.claude/quenching.json`, via `cq specs config --json`, default `medium`): a spec below the floor
joins the defining regime and runs through to the end; at or above it, the spec must already be
`ready`/`approved` to join the building regime.

Beyond the declared identity (`slug`, `title`, `date`) and the optional `verification` — absent
means the default, applied on read, never stamped to make it explicit — every optional key is one
record:

| Record | Written by | Write-once | What only a human can answer |
| --- | --- | --- | --- |
| `priority: {level, criticality, complexity, date}` | `triage` — `complexity` its own `[triage, create, develop]` | no | this spec's rank against every other one — `complexity` is the exception below |
| `refined: {mode, date}` | `develop` | no | that a real interrogation happened, and in which mode |
| `approved: {date}` | `develop`, or `execute` inline | yes | that a human said go |
| `branch: {base, work}` | `execute`, or `git:branch` when it hands off there | yes | after a merge, git cannot say what the base was |
| `pr: {number, url, date}` | `git:pr:create` | no | which pull request carries this spec, before any merge decides its fate — restampable because a PR may be reopened or recreated |
| `reviewed: {date}` | `conclude` | no | that a human read the whole branch diff |
| `merge: {strategy, subject, pr}` | `git:merge` | yes | the strategy was a choice; the subject names the merge it produced; `pr` names the pull request when one came first, unwritable before it exists |
| `outcome: done \| abandoned` | `conclude` | yes | that the work will **not** be built — `abandoned` is derived from nothing, ever. `done` is derived from every box ticked and none blocked, and an `--outcome` in the input outranks the derivation either way |

Read top to bottom, the table order is the order the table's own writers touch a spec still open —
ranked, interrogated, approved, isolated (or explicitly not), reviewed, closed — but `pr:` and
`merge:` no longer narrate a step *inside* that sequence. Both land later, in a separate run of
`git:pr:create`/`git:merge` the human chooses on their own word, onto a spec `conclude` already
archived; "PR opened" and "merged" are true facts about the spec's life, just no longer facts this
table's own row order places before "closed". **Not** "built" —
`branch` narrates which work ref was resolved, taken (a worktree or a branch cut) or declined
(`work` equal to `base`), never that the work finished; "built" is the derived stage `executing`
(`stages.derived`, keyed off task state or a filled `## Handoff`), which a spec built in place
reaches exactly the same way an isolated one does. **`work == base` is a record about isolation,
not a live work ref** — the base branch never dies, so anything asking git whether that ref is
alive gets *yes* forever ([plan-git-record.md](plan-git-record.md) §Three frontmatter records).
`writeOnce: true` marks an irreversible transition —
rewriting the value would falsify a fact that already happened; the restampable three each carry
their own `date` because their owning command may legitimately re-judge. In neither case may a
command other than the one named in `writtenBy` touch the record — `complexity` excepted, which
names its own list because part of it is computed (§ above), under a record whose owner stays
`triage`. The vocabulary lives in
`assets/specs/schema.json` (`frontmatter.records`), which `cq specs` embeds as its fallback.

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
| definition — `/quenching:specs:develop`, any bank | one line of `## Discoveries` on the spec being developed, written with `cq specs discover` inside the pass's one consolidated edit |
| close-out — `/quenching:specs:conclude` on a `done` outcome | the harvest turns it into a fresh spec, if it still deserves one |

The asymmetry is the whole rule. At definition time nobody knows whether the parent will ship, so
a spec minted then is a bet placed before the information arrives; at close-out that fact is in
hand, which is why the harvest table in `specs-conclude/distill.md` is the only place a follow-up
becomes a file.

**The measurement.** One autonomous `/quenching:specs:develop` pass over 32 open specs, one agent per spec,
raised 4–6 follow-up candidates each — well over a hundred — and the same `cq specs` defects
surfaced independently in three or four agents that could not see one another. A definition-time
offer scales with what the pass *imagines*, and the queue it fills is charged again to every
`cq specs next --front` ranking, `/quenching:specs:status` view and `/quenching:specs:triage` read that has to walk
past it. Duplicates arriving through that door are turned away at it: the discoveries bank's
`promoted:` resolution reads the front first and resolves a line an open spec already covers as
`dismissed: already covered by {slug}` — still three resolutions, never a fourth token.

Where the rule is written: `commands/specs/develop.md` carries it as an `## Invariants` entry, with
the guard that `cq specs new` runs inside a develop pass **only** as that `promoted:` resolution;
its step 5 shows the parked line in the consolidated plan and its step 6 makes the `cq specs
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
exists, so `/quenching:specs:develop`'s intent-change route still names `/quenching:specs:create`. Parking is for what
the pass surfaced on its own.

## The v2→v3 migration

`cq specs migrate` performs the fold exactly once per workspace: every file in `backlog/` and
`ready/` moves to `plans/` with its basename unchanged, `archive/**` is never touched, and an
already-v3 workspace exits 2. Nothing is renamed, so every recorded slug, date and cross-reference
survives; the completeness `ready/` used to imply is recomputed on the next read, and the human OK
it used to carry is whatever `approved` records say.
