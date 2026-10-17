---
type: standard
title: Context discipline — open less, run for less time, and emit fewer turns
description: The two halves of a run's integral `tokens × turns remaining` and the three ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, the block rather than the section where a section has blocks, and the rules/rationale marker convention), run for less time (the section boundary as a legitimate stopping point, with measured role budgets checked only at existing boundaries), and emit fewer turns per unit of work (the batching contract, and the ban on a turn that exists only to announce the next tool call); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**, plugins/quenching/assets/bin/quenching/components/**, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/agents/**, scripts/measure_context_distribution.py
tags: [automation, context, reading, cost, commands, references]
timestamp: 2026-10-16
audience: both
authority: background
source: read-by-section-not-by-file, narrow-the-execute-preamble, extensible-surface-and-budget-retirement, 2026-08-06, 2026-08-04, scope-the-handoff-rewrite; spec 1629 measured context budgets (2026-10-13); spec 1631 measured stage-boundary tone (2026-10-14); spec 1633 declared-reading estimation and build-cost provenance (2026-10-14); lineage in ADR 0004; spec 1754 decision sheet as the default question form (2026-10-16)
maintainer: quenching
---

# Context discipline — open less, run for less time, and emit fewer turns

Every turn re-sends the whole conversation. A block of context loaded once is therefore paid once
for **each turn that follows it**, and a run's true cost is `tokens × turns remaining`, not
`tokens`. The measurement history behind the integral, 344-turn run included, retired with
context-budget.md; this file owns what to *do* about it.

There are exactly two factors, and three ways to reach them: **open less**, **run for less time**,
and **emit fewer turns per unit of work**. The first attacks the tokens; the other two attack the
count from opposite ends — one ends the run sooner, the other buys the same work with fewer turns
inside it. Nothing else is available, and a proposal that does none of the three is not an
optimisation.

Born `authority: background`, and still there. The counts below are this repository's own, and the
declared graduation condition is a **second adopting repo** reproducing the shape.

**Re-evaluated 2026-08-16** against session `c56cff41-e5b1-43f0-85dc-eca1b17e03d0` (§Emit fewer
turns per unit of work), the first measurement here taken from a *live run* rather than from a
static count of files on disk. It confirms the central claim numerically — the integral really is
dominated by the turn count — and the grade stays `background` anyway, because the grade was never
about whether the mechanism is real. It is about whether **these numbers** hold outside this
repository, and a second measurement in the same repository is not a second repository.

## Open less: read the narrowest thing that answers the question

<!-- rules -->

Four rules. The first three are in descending order of what they were measured to be worth; the
fourth extends the same philosophy one level deeper and is a **qualitative estimate** until a real
run measures its cut.

1. **Read the files a spec *declares*, never the folder they sit in.** `## Impact` names the
   `/docs/standards/` paths a spec expects to touch; those, plus whatever the current task's own text
   names, are the binding contracts. A `/docs/standards/<subject>/` folder is a location, not a
   claim about relevance.
2. **A reference citation in a command body IS a `§`-address — never a bare path.** Surface-wide
   rule, proved on one command: measured on `/quenching-specs:specs:execute`, six of its top-preamble
   citations named only a file, and five of its `§`-addresses named a section with no file to
   resolve it in. A citation is resolvable, by a reader and by `cq components` alike, only when four
   halves hold together — the first three about how the address is written, the fourth about how
   the reader takes it:
   1. every `§`-address carries the file it belongs to, in the same link or glued to it;
   2. an address is never split across a line break;
   3. a step of the body's own workflow is `step 5g`, never `§5g` — `§` keeps one meaning, a file's
      section, never a step number.
   4. **a value handed to the reader is first an ADDRESS, and only then a list.** A heading may
      carry a comma of its own — `## What crosses, what stays` — so a reader that splits every
      value unconditionally leaves those headings unciteable by the very title the prose writes.
      Each value resolves whole first, by the same ladder a single name uses (exact, then unique
      prefix); only one that resolves to nothing **and** carries a comma is read as a list.
      Whole-first is what makes the reading deterministic, and starting the ladder at *prefix*
      rather than at exact-match alone is what preserves every prefix citation already written.

   A reference used only inside one conditional branch is read in that branch, never hoisted into
   the preamble every turn pays for regardless of which branch runs.

   A citation with **no consumer** — no step of the body needs the rule, because the body already
   states it or already executes it through an explicit tool call — **leaves**. The section stays on
   disk, whole: what leaves is the pointer, never the knowledge. The condition that makes the
   removal safe: the rule the citation carries is already written in the body, or executed by an
   invocation the body writes literally — where that does not hold, the section descends, never
   leaves. The rule itself is `authority: background`, the same grade as this file: a triage this
   repository ran once, agreed but unproven elsewhere, that graduates when a second adopting repo
   reproduces the shape.

   `cq components read <path> --sections "§A" --sections "§B"` answers it for any markdown, and
   `cq specs section <slug> "A,B"` for a spec's fourteen canonical headings. **Only the first
   implements the ladder** — the fourteen canonical headings carry no comma and `cq specs` refuses
   any name outside them, so the defect is unreachable there and the asymmetry is deliberate.
   Seven command bodies are converted to this shape today — `/quenching-specs:specs:execute`,
   `/quenching-specs:specs:develop`, and the five `specs/*` commands (`align`, `conclude`,
   `create`, `status`, `triage`). Seventeen remain: `docs/` (ten bodies), `skill/` (six bodies),
   and the root `align` command (one body).
3. **N sections in ONE call.** Turns are the *other* factor. Five sections fetched over five turns
   trades tokens for turns and can lose to reading the whole file, because a turn spent early is
   repaid by every turn after it. Both readers take a list for this reason; it is half the result,
   not a convenience.
4. **Where a section is built out of blocks, the block is the unit — and the cut is opt-in.**
   `## Handoff` is the one canonical section with internal blocks, one per `### N.` of `## Tasks`,
   so a reader taking it whole loads the record of every section already closed. `cq specs section
   <slug> --moment build --scope current` asks for the evergreen global block plus the block of the
   section the next actionable task sits in, and returns the other `build` sections whole — which
   is what keeps rule 3 intact: the narrower read costs no extra turn. Two halves make it safe to
   generalize:
   1. **The cut is asked for, never applied silently.** Without `--scope`, the raw body comes back
      whole, exactly as before — the same opt-in precedent `--rules-only` set. A read that got
      quieter by itself would be indistinguishable from a section that had emptied.
   2. **The payload says it was cut** (`"scope": "current"`), so a caller never infers it by
      comparing sizes.

   The floor is the block, not the byte: a section with no blocks is already its own narrowest
   unit, and inventing sub-block addressing for it would buy nothing — see §Two things measured and
   refused, which is the same refusal at file granularity.

A section is the right unit because the files are already the right size. Counted on this bundle:
**315 `##` sections across 488,149 chars, averaging 1,549 chars (~387 tokens)**. Reading
`execution.md` §The verification policy costs ~400 tokens; reading `execution.md` costs 4,600. The
factor of eleven is not the file being large — it is asking for a file when you wanted a section.

<!-- rationale -->

Measured on `/quenching-specs:specs:execute` while narrowing it: the preamble it loads before the first
task writes a line fell from **263,839 to 174,051 chars (~66.0k → ~43.5k tokens, −35%)**, split as
the spec read by section rather than whole (35,099 → 18,994, −46%) and the standards read as the
five declared rather than the four subject folders (126,720 → 53,037, 19 files → 5, −59%). The
folder rule is the larger of the two and was the one nothing had attacked.

**The fourth half of rule 2 came from a defect, not from a design.** `cq components read --sections`
split every value on the comma before resolving anything, and its own `--help` documented an escape
by repeating the flag that the code did not implement — so a body citing `§What crosses, what
stays` got `sk-read-no-section`, which reads to an agent as *the section does not exist*, whose
fallback is opening the file whole. Measured across `assets/references/`, `/docs/` and
`assets/docs/`: **146 headings carry a comma**. 145 resolved only by the accident that the fragment
before the comma happened to be unique, and one — `/docs/standards/git/branching.md`
"Publication, in two halves" (measured while that heading still read "A publicação, em duas
metades"; translating it changed the words, not the comma or the finding) — resolved by no form at
all.

Whole-first was chosen over three alternatives, and the deciding evidence was a simulation rather
than an argument: every ordered pair of headings in every file, joined by `,` and by `, ` —
**14,944 values, of which zero resolve whole**. So the precedence cannot shadow a legitimate list on
this corpus, and the short form loses nothing. A new `--section` flag was rejected as permanent CLI
surface for a case precedence already settles, and dropping the comma split outright as a break of
a documented form whose `--help` promises it — though the same sweep found **zero** callers passing
a comma to the short form today, which is what makes that form a retirement candidate rather than a
constraint.

**Rule 4 is declared, not measured — and says so.** The nearest figure this file owns is §Run for
less time's: on a real 29-task, 7-section run the flat `## Handoff` resent **~79,556 chars
(~19,900 tokens)**, peaking at ~5,680 per task, almost all of it sections that had already closed.
`scope-the-handoff-rewrite` closed that leak on what a *rewrite sends*; this rule closes the same
leak on what a *reader takes* — the two halves of one section, and the read half had been left to
agent discipline (`spec-driven.md` §The executor contract sliced it by hand for a delegated
sub-agent, and not at all for the orchestrator that read it first). What the read side saves
depends on how deep into a plan a run starts and how large the closed blocks are by then, so no
number is claimed until a run measures one. The graduation condition is the file's own: a second
adopting repo, plus one measured run.

The alternative of a dedicated `cq specs handoff` verb was rejected for the reason rule 3 exists —
it returns step 4 to two calls, trading tokens for a turn, which is the trade this whole section is
about.

## The rules/rationale marker convention

<!-- rules -->

A normative section may separate its binding half from its story with two markers:

```markdown
<!-- rules -->
The rule, imperative.
<!-- rationale -->
The measurement, what was reverted, the v1 that failed.
```

- **A marker, never a heuristic.** A model deciding per read which sentences bind is
  non-deterministic and its failure is *silent* — a dropped binding sentence appears nowhere. The
  marker is written once, by whoever wrote the rule.
- **Compaction is relocation, never deletion.** The rationale stays on disk, in full, and stays
  contract. Only its position moves.
- **No marker → the whole section, and the caller is told.** `--rules-only` degrades to today's
  behaviour, never to emptiness, and reports the absence. A convention applied in five files must
  not turn the others into silence.
- **A marker's reach ends at the next heading.** Asked for a section, a caller receives its
  sub-sections too, so one `<!-- rationale -->` inside a `###` would otherwise truncate every rule
  after it. Mark **per sub-section**, not once per block.
- **Relocation only pays when the destination is not already loaded.** Rationale moved into a
  section the citing body *already addresses* has changed position without changing cost — the
  chars are still paid every turn. Read the body's citation set first, and relocate into a section
  outside it. The failure is **silent**: both the body and the destination file read as correct
  afterwards, and only a whole-branch review recomputes the number.
- **A section's cost is the section plus its `###` children.** The same reach that governs the
  marker governs the count: a caller asking for `§X` receives everything under it, so a budget
  computed from the level-2 prose alone under-reads by whatever the sub-sections hold.

<!-- rationale -->

Measured after applying it to the five references `/quenching-specs:specs:execute` loads: of 76,376 chars
across their level-2 sections, 65,564 are rule and **5,306 are rationale — 7%**, against the
25–35% the spec had declared as a guess. Reading those five `--rules-only` instead of whole saves
15%. That is why the convention was **not** extended to the other eighteen references: reading by
section had already taken the order of magnitude, and this is the residue. The 7% is honestly the
fraction of the markup as applied — conservative, only clearly narrative prose was relocated — not
of an exhaustive classification.

The last rule was not foreseen. Applied to `execution.md` §Delegating an executor, a single
`<!-- rationale -->` inside one `###` swallowed three entirely normative `###` blocks, silently.

**The two rules above it were not foreseen either, and both were caught by a branch review rather
than by the task that introduced them.** Measured 2026-08-02 while relocating rationale out of
`/quenching-specs:specs:execute`: the destination chosen was `execution.md` §Declared versus emergent
`docs/` — one of the *seven* sections that command's preamble cites on every run. The section went
1,547 → 2,366 chars, so **819 chars per turn were relocated into the bill they were being moved
off**. Nothing detected it: the body was correct, the destination file was correct, and the task's
own diff self-review saw one file's change with no view of the citation set. Moving the same two
blocks to §Tooling asides, relocated — cited by nothing — returned the section to 1,547 exactly.

The sub-section rule has the same provenance and the same shape of cost. That relocation's spec
budgeted `execution.md`'s seven cited sections at 11,610 chars and `git.md`'s five at 4,233; they
actually cost 16,212 and 8,491, because the estimate counted level-2 prose and the reader returns
the `###` children too. The gap turned a cut declared at −36% into a measured −30.1% — not a
regression, an under-read baseline, and the correction is to count what the reader returns.

## Run for less time: the section boundary

<!-- rules -->

The integral is quadratic in the turn count, so **shortening the window beats shortening the
reads**. A `## N.` section's last task committing, with another section still ahead, is a clean
boundary, and a build offers to stop there.

- **The boundary triggers the check; the measured budget informs the action.** Check the
  applicable role budget from §Measured context budgets at an existing stage end, task-section
  end or worker return. Never stop in the middle of a task because a count crossed a threshold.
- **The event triggers; the measured threshold decides only the tone — offer or recommendation.**
  A human-led `/quenching-specs:specs:develop`, `/quenching-specs:specs:execute` or `/quenching-specs:specs:conclude`
  reads `cq components session context --json` once at its stage end, and `execute` once more at
  each section boundary. Within the main-session budget, or unmeasured, the next stage stays an
  offer; over it, the command recommends the next stage in a new session, with the exact command,
  inside the payload of a question it already asks or in the `→` line. Nothing is stopped and
  nothing is recorded. An autonomous conductor already authorized to enforce its budget returns
  `STATE: continue` with the handoff at that boundary; enforcing worker and conductor budgets by
  code is S5 of epic 1627.
- **It writes no new state.** The resumption trail — `## Handoff`, `git log`, and the recorded
  commit subjects — is already maintained for other reasons. Preparation in the new context still
  has a measured cost; §Measured context budgets records that cost separately. An offer needing a record of its own would be moving cost, not cutting it.
- **The same event also bounds what a rewrite touches, not only whether a run stops.**
  `## Handoff`'s per-section blocks close on it: a `### N.` block is never targeted again once its
  section's last task commits, so a task built later is never resent the record of a section
  already done.

<!-- rationale -->

Seven runs of ~45 turns cost roughly **a seventh** of one run of 300 for the same work. That is
declared arithmetic over the integral, not a measured run, and it assumes negligible resumption
cost. That assumption is not evidence: the measured worker preparation below is non-zero. Measured against the workspace that would use it: 34 specs in `plans/`, a median of 4
sections each (0:4, 2:1, 3:6, 4:11, 5:5, 6:4, 7:3) — so the event fires a median of three times per
spec, and the smallest threshold that would change anything (≥2 sections remaining) would remove
the offer entirely from the 2- and 3-section specs, which are the runs most able to end cleanly
early.

Measured on a real 29-task, 7-section run predating the per-section `## Handoff` redesign
(`configurable-spec-backend`): the flat `## Handoff` resent **~79,556 characters (~19,900 tokens)**
across the run, averaging ~2,743 chars per task and peaking at **~5,680 chars per task** in the
closing sections — almost entirely the record of sections that had already closed. The section
boundary was already the point where a run may stop; `scope-the-handoff-rewrite` is the same
boundary applied to what a rewrite sends, closing a section's block the moment that boundary is
crossed rather than resending it to every task built after.

## Declared reading is a warning, not measured build usage

<!-- rules -->

`cq specs estimate <id> --json` derives section-level declared reading from UTF-8 file sizes,
rounded upward at four bytes per token. Each section counts its unique declared task files and
Impact standards once, plus the shipped execute body and spec build sections; another section
counts the shared files again. Missing/new files and undeclared task inputs remain unresolved.
The largest section is compared with the worker policy budget above. Total reading volume is
not a context peak, and even complete declared-input coverage never proves the build fits:
host/harness overhead, conditional references, outputs, generated code and iterations are excluded.

Develop checks this signal before every approval path. Known reading above the budget proposes
independently verifiable slices through `spec-architect` in proposal-only mode. Capturing/linking
children needs explicit authorization; the source problem and approval/task history survive.
Low/forced-low autonomous runs return the oversized-plan decision to their conductor, without
approving it automatically. A human may explicitly accept the unsplit estimate risk.

Conclude preserves observed usage separately in `buildCost`, before archive. A measured record
requires exact build-only transcript/agent attribution and known models, with request counts,
input/cache/output totals and maximum reported request exposure per model. That exposure is not
silently a context peak. Native Codex usage that was not measured, ambiguous scope and partial or
refused metering are unavailable with source and reason, never estimated numbers or zero fillers.
Valid measured evidence survives resume; replacing unavailable evidence writes all fields together.

<!-- rationale -->

Spec 1633 adopted two evidence classes because a static reading heuristic is reproducible from
files while observed usage disappears with its scoped transcript. Keeping them distinct prevents
an inexpensive estimate from becoming a false build-fit or calibration claim. Regression coverage
proves the declaration and workflow contract; calibration across actual builds remains future
measurement, so this standard retains its existing background authority.

## Measured context budgets

<!-- rules -->

Use these selected policy budgets in input-context tokens, measured by code from the transcript:

| Role | Budget | Applies to |
| --- | --- | --- |
| Main session | 200000 | Human-led spec stages and the top-level conversation |
| Worker | 100000 | The spec-runner building one spec in its isolated context |
| Conductor | 150000 | Orchestrator and autopilot coordination contexts |

Role comes from topology/agent metadata, independently of command attribution. A conductor
uses its conductor budget even when its transcript is a subagent. A new role or missing
metadata is reported as unknown, never classified from prompt prose. The main-session budget
also covers a top-level autopilot conversation; its separately spawned conductor uses the
conductor budget. These numbers are engineering policy chosen from the distributions below,
not limits automatically inferred by the host or a model remembering its own usage.

A request's reported input is `input_tokens + cache_read_input_tokens +
cache_creation_input_tokens`, deduplicated by `message.id` with final usage. For context peak,
use the maximum executor `type: message` iteration when `usage.iterations` is available:
top-level input fields can sum multiple executor iterations. Declare missing iteration coverage;
do not silently call aggregated request exposure a single context window. Keep model tiers
separate for cost claims. Unknown command attribution stays unknown; an unclosed conducted
stage remains an upper bound under [session-evidence.md](session-evidence.md).

The rollout target is **at most 4.33%** of main-session token exposure coming from sessions
whose input-context peak exceeds 200000 (fraction `0.0433`). This is a **project hypothesis**,
using the observed worker distribution as a reference, not a causal savings prediction or an
already measured enforcement result. Validate after S3–S6 of epic 1627, using the same role/model
accounting and reporting boundary stops, overshoot, parse coverage and workload differences.
Do not count a changed sample or model mix as demonstrated causal savings.

Keep context changes at the existing boundaries described in §Run for less time. Preserve
`## Handoff` and task commits. Do not treat fresh-context preparation as free, split one task
because of its window, or extrapolate the worker restart sample to a measured main/conductor
restart cost. Budget enforcement is not implemented by publishing this standard.

<!-- rationale -->

**Measured 2026-10-13**, JSONL arm, by
[`scripts/measure_context_distribution.py`](../../../scripts/measure_context_distribution.py),
with sanitized evidence in
[`scripts/evidence/context-budget-1629.json`](../../../scripts/evidence/context-budget-1629.json).
The private inventory checksum in that artifact fixes the sample without publishing prompts
or tool payloads. The scan found 1387 files, 1385 with usable requests: 58 main sessions and
1327 subagents. Two files had no requests; 88 records were invalid JSON and 11 conducted-stage
attributions were unclosed. Measurement exit 1 means evidence with findings, not a clean read.

The captured 1383-usable-transcript baseline (57 main, 1326 subagents) had no inventory hash;
the new usable sample is larger by two, and those additions cannot be identified exactly from
the captured totals. Preserve the captured evidence; do not relabel it as the new sample.

| Role | Sessions | Median peak | p90 peak | Maximum peak | Sessions above selected budget |
| --- | --- | --- | --- | --- | --- |
| Main | 58 | 106752.5 | 292503 | 510539 | 14 |
| Worker | 364 | 63721.5 | 97126 | 244482 | 32 |
| Conductor | 49 | 46959 | 127383 | 180379 | 3 |
| All subagents | 1327 | 20081 | 84976 | 244482 | Not one shared budget |

Median is the statistical median; p90 is nearest rank. All 3209 main requests have exactly
one executor iteration, so the main peak is a single observed prompt: `2 + 233 + 510304 =
510539`, on Claude Code 2.1.292, `claude-opus-5-5`. The artifact quotes the three usage fields,
message id, source hash and line. No maximum host capacity is inferred from that observation.
The [prompt-caching contract](https://platform.claude.com/docs/en/build-with-claude/prompt-caching)
defines total input; the
[advisor usage contract](https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool)
explains aggregation across executor iterations.

Main exposure is 602003067 tokens; the 14 sessions above 200000 account for 517451010
(85.954879%). A 150000 cut would affect 23/58 sessions. Choose 200000 to address the
concentrated long tail with less fragmentation. Worker 100000 rounds above p90 97126;
conductor 150000 rounds above p90 127383. These choices price different role distributions
rather than copying the old unmeasured 150k/200k prose.

Four identified opus-only worker resumes (specs 1368, 1419, 1386 and 1457), paired with an
earlier task-check invocation for the same spec, each took three requests through the first
`cq specs next`. Preparation context peaked at median 32429, maximum 33159; fresh input was
median 27499, maximum 28229; preparation exposure was median 74169, maximum 75984. Worker
100000 is more than three times that observed preparation peak. A task-check invocation is
not inferred to have succeeded merely because its text exists; these are bounded preparation
observations, not warm-versus-cold treatment comparisons. No clean main/conductor restart pair
was identified. The two main `configurable-spec-backend` executions are contaminated by dirty
mid-task work, scope changes and a model change.

Worker exposure from its one session above 200000 is 18019295/416636200 = 4.324947%; rounding
up yields the 4.33% reference target. Main and worker scopes, model mixes and attribution
coverage differ. The target asks whether explicit context boundaries can move the main long
tail toward the observed worker profile; this spike does not prove that outcome. Command
attribution is absent for 1842/3209 main requests, 7015/7182 worker requests and 2316/2336
conductor requests, so pointer-labeled stage distributions are partial evidence only.

## Emit fewer turns per unit of work

<!-- rules -->

The axis above shortens the run; this one makes the same work cost fewer turns inside it. Two
rules, both about turns rather than tokens:

- **Batch by dependency, never for tidiness.** Consecutive tool calls go in ONE call unless the
  next command's *input* depends on the previous one's output. A body with several such points
  states them as a **batching contract** — a named block naming which calls are one call — so the
  rule is checkable against the body instead of re-judged every run.
- **No turn exists only to announce what the next tool call will do.** "Now I'll load X", "next
  I'll write Y": a turn whose entire content is the call that follows it says nothing that call's
  own output will not say, and costs a re-send of the whole conversation to say it. Narration that
  carries content — a plan, a report, a stop condition — is not this.

Where a turn must carry a recommendation, the recommendation lives **inside the question itself**
— option A of each `D<n>` on the decision sheet, its reasoning in A's own text, or the option
marked "(Recommended)" on a menu the human asked for — never in a turn of prose set in front of the
question. The decision sheet, which ends the turn, is that question; its shape is owned by
`specs-develop/questions.md` §The four shared mechanics.

**Neither rule reaches how questions are grouped.** Two questions whose answers can change each
other are asked separately whatever this axis costs. That limit is owned by the command surface's
own contract and is not negotiable against a turn count.

**The third rule is the same one applied to a workflow's own crossings.** Where a body traverses
several stages over one artifact, and no stage's *input* depends on the previous stage's write, the
stages are one pass and one edit — the same dependency test, raised from the tool call to the
traversal. `/quenching-specs:specs:develop` is where this was first applied: it crossed three stages with
an edit, a `validate` and a re-derivation between each, for a spec nobody had finished, and the
re-derivations answered a question the pass already held. **It changes when a question is asked,
never whether it is** — which is what keeps it on this side of the limit above, and what its report
proves by carrying the question count.

<!-- rationale -->

Measured on session `c56cff41-e5b1-43f0-85dc-eca1b17e03d0` — two `/quenching-specs:specs:develop` passes
over one spec — by summing `cache_read_input_tokens + cache_creation_input_tokens + input_tokens`
over the assistant turns of the session's `.jsonl`: **9.73M tokens of context read across 100
turns**. Of that, **4.44M is a single 44.4k base re-read 100 times** — ~46% of the session spent
re-sending what was already known. The command body is ~7k of that base, so **shrinking the body
buys ~7% of the session**, while halving the turn count halves the base term and cuts the
accumulated growth by ~4×.

That arithmetic is what ranks the three axes against each other, and it is why this one is separate
rather than a footnote to "open less": that command had *already* been converted to read by section,
and the session still spent nearly half its budget on re-reads — because the turn count had never
been the thing under attack.

## Two things measured and refused

<!-- rules -->

Neither of these is an available move here, and both come back looking obvious:

- **Do not segment the bundle into more files.** Taking the 50 files of `/docs/standards/**` and
  `assets/references/**` to their 315 sections would cost **265 new frontmatters × 1,424 chars ≈
  371k chars (~93k tokens)**, ~76% growth over the current 488k, in pure header — and it does not
  address the cause, since N sections remain N reads, which is N turns.
- **Do not delete rationale to compact a document.** It is the one asset a model cannot
  reconstruct: the *why* of a rule is what stops the next session from "fixing" a deliberate
  decision. Relocate it under a marker instead.

<!-- rationale -->

Both were priced while writing the spec that produced this file, not argued about. The refusal to
segment also explains why the reader exists at all: given files of the right size, the missing
piece was never a smaller file — it was the tool that resolves an address the prose was already
writing.

## What a delegated executor costs

<!-- rules -->

A sub-agent runs on a cold context and does **not** share the session's prompt cache, so it pays
the full first read of every file it touches. Where N tasks declare the same large file, that is N
cold reads against one warm one. Delegate **by file or by section of tasks, never task by task**,
run the diff self-review *inside* the sub-agent so the diff never re-enters the long context, and
where the tasks are small and the shared file is large, keep the work.

<!-- rationale -->

Declared arithmetic, per
[session-evidence.md](session-evidence.md) §The rule a counted claim must obey: on this repo's
`configurable-spec-backend`, 18 of 29 tasks are delegation-eligible and 13 declare the same ~37k
token file, so task-by-task is ~13 × 37k ≈ 480k against roughly 150k for one warm reader. Nothing
about the permission changed; what was missing was the account that says when it pays.
