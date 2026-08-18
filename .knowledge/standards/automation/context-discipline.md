---
type: standard
title: Context discipline — open less, run for less time, and emit fewer turns
description: The two halves of a run's integral `tokens × turns remaining` and the three ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, the block rather than the section where a section has blocks, and the rules/rationale marker convention), run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold), and emit fewer turns per unit of work (the batching contract, and the ban on a turn that exists only to announce the next tool call); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**, plugins/quenching/assets/bin/quenching/components/**, plugins/quenching/assets/bin/quenching/specs/**
tags: [automation, context, reading, cost, commands, references]
timestamp: 2026-08-18
audience: both
authority: background
source: read-by-section-not-by-file spec, then narrow-the-execute-preamble — every figure below is a static count of files on disk plus arithmetic over the integral, measured while building the spec that wrote it; the integral's measurement history, 344-turn run included, retired with context-budget.md (extensible-surface-and-budget-retirement, 2026-08-06); the second converted body (`/quenching:specs:develop`, 2026-08-04) came with a corpus measurement of the cost the rule addresses — 107 whole-file reference reads against 13 sectioned ones across 159 transcripts, 34.6M token-turns, half of it in the three references that one command cited by bare path; scope-the-handoff-rewrite adds the `## Handoff` section-block measurement below, taken on a real 29-task, 7-section run predating that redesign; the fourth half of rule 2 (the address-then-list ladder) comes from the skills-py-sections-comma-split-bug spec, measured on 146 comma-carrying headings and a 14,944-value simulation over this repo's own markdown; the third triage result — the consumerless citation that leaves, with its rule at the file's own grade — added by alinhar-citacoes-de-preambulo-do-execute (task 2.2, 2026-08-06), which triaged the eighteen preamble citations of /quenching:specs:execute; the third axis — emit fewer turns per unit of work — added by revisar-fluxo-do-develop-custo-e-gates (2026-08-16), measured on session c56cff41-e5b1-43f0-85dc-eca1b17e03d0 by summing cache_read_input_tokens + cache_creation_input_tokens + input_tokens over the assistant turns of its .jsonl: 9.73M tokens of context read across 100 turns, 4.44M of it 100 re-reads of a 44.4k base; the question-grouping paragraph de-escalated from a restatement to a citation of `questions.md` §1 (2026-08-18), after it had been carrying a stronger rule than its own declared owner; rule 4 of §Open less — the block rather than the section — added by escopar-a-leitura-por-task (2026-08-17), which put the cut in `cq specs section --scope` on the READ path and is declared rather than measured, leaning on the ~79,556-char figure §Run for less time already owns
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
   `/.knowledge/standards/` paths a spec expects to touch; those, plus whatever the current task's own text
   names, are the binding contracts. A `/.knowledge/standards/<subject>/` folder is a location, not a
   claim about relevance.
2. **A reference citation in a command body IS a `§`-address — never a bare path.** Surface-wide
   rule, proved on one command: measured on `/quenching:specs:execute`, six of its top-preamble
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
   Seven command bodies are converted to this shape today — `/quenching:specs:execute`,
   `/quenching:specs:develop`, and the five `specs/*` commands (`align`, `conclude`,
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

Measured on `/quenching:specs:execute` while narrowing it: the preamble it loads before the first
task writes a line fell from **263,839 to 174,051 chars (~66.0k → ~43.5k tokens, −35%)**, split as
the spec read by section rather than whole (35,099 → 18,994, −46%) and the standards read as the
five declared rather than the four subject folders (126,720 → 53,037, 19 files → 5, −59%). The
folder rule is the larger of the two and was the one nothing had attacked.

**The fourth half of rule 2 came from a defect, not from a design.** `cq components read --sections`
split every value on the comma before resolving anything, and its own `--help` documented an escape
by repeating the flag that the code did not implement — so a body citing `§What crosses, what
stays` got `sk-read-no-section`, which reads to an agent as *the section does not exist*, whose
fallback is opening the file whole. Measured across `assets/references/`, `/.knowledge/` and
`assets/docs/`: **146 headings carry a comma**. 145 resolved only by the accident that the fragment
before the comma happened to be unique, and one — `/.knowledge/standards/git/branching.md`
"A publicação, em duas metades" — resolved by no form at all.

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

Measured after applying it to the five references `/quenching:specs:execute` loads: of 76,376 chars
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
`/quenching:specs:execute`: the destination chosen was `execution.md` §Declared versus emergent
`docs/` — one of the *seven* sections that command's preamble cites on every run. The section went
1,547 → 2,366 chars, so **819 chars per turn were relocated into the bill they were being moved
off**. Nothing detected it: the body was correct, the destination file was correct, and the task's
own diff self-review saw one file's change with no view of the citation set. Moving the same two
blocks to §Tooling asides, relocated — cited by nothing — returned the section to 1,547 exactly.

The sub-section rule has the same provenance and the same shape of cost. That relocation's spec
budgeted `execution.md`'s seven cited sections at 11,610 chars and `git.md`'s five at 4,233; they
actually cost 16,212 and 8,491, because the estimate counted level-2 prose and the reader returns
the `###` children too. The gap turned a cut declared at −36% into a measured −30,1% — not a
regression, an under-read baseline, and the correction is to count what the reader returns.

## Run for less time: the section boundary

<!-- rules -->

The integral is quadratic in the turn count, so **shortening the window beats shortening the
reads**. A `## N.` section's last task committing, with another section still ahead, is a clean
boundary, and a build offers to stop there.

- **The trigger is that event, never a window size.** No threshold, no token count, no "this is
  getting long". A number invented before it is measured fixes the answer.
- **It offers; it never imposes and never ends a run itself.** An unattended run that decides to
  stop trades a cost for a surprise.
- **It writes no new state.** The resumption trail — `## Handoff`, `git log`, and the recorded
  commit subjects — is already maintained for other reasons, and that is precisely what makes the
  cut nearly free. An offer needing a record of its own would be moving cost, not cutting it.
- **The same event also bounds what a rewrite touches, not only whether a run stops.**
  `## Handoff`'s per-section blocks close on it: a `### N.` block is never targeted again once its
  section's last task commits, so a task built later is never resent the record of a section
  already done.

<!-- rationale -->

Seven runs of ~45 turns cost roughly **a seventh** of one run of 300 for the same work. That is
declared arithmetic over the integral, not a measured run, and it assumes resumption costs about
nothing. Measured against the workspace that would use it: 34 specs in `plans/`, a median of 4
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

Where a turn must carry a recommendation, the recommendation lives **inside the question's own
payload** — an option marked "(Recommended)", the reasoning in its description — never in a turn of
prose set in front of the question.

**How questions are grouped is not this axis's to settle, and not this file's to state.** The rule
is owned by
[`specs-develop/questions.md`](/plugins/quenching/assets/references/specs-develop/questions.md)
§1: a question travels with the ones whose answers cannot change it, alone otherwise, up to the
harness cap of four per call. It is a rule about **dependence**, and it cuts both ways — it neither
licenses grouping to save a turn where an answer would move the next question, nor forbids it where
two questions cannot reach each other. Read it there; restating it here only produced a harder rule
than its owner's. Whether a command owes a stop at all, and whether it owes one per stage or one per
pass, is [plan-gates.md](plan-gates.md)'s.

<!-- rationale -->

Measured on session `c56cff41-e5b1-43f0-85dc-eca1b17e03d0` — two `/quenching:specs:develop` passes
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

- **Do not segment the bundle into more files.** Taking the 50 files of `/.knowledge/standards/**` and
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
