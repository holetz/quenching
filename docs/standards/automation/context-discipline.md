---
type: standard
title: Context discipline — open less, and run for less time
description: The two halves of a run's integral `tokens × turns remaining` and the only two ways to cut it — open less (the declared files rather than the folder, the cited sections rather than the file, N sections in ONE call, and the rules/rationale marker convention) and run for less time (the section boundary as a legitimate stopping point, triggered by an event and never by a threshold); plus the two things measured and refused, segmenting the bundle into more files and deleting rationale to compact it
resource: plugins/quenching/commands/**, plugins/quenching/assets/references/**, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/bin/specs.py
tags: [automation, context, reading, cost, commands, references]
timestamp: 2026-08-01
audience: both
authority: background
source: read-by-section-not-by-file spec — every figure below is a static count of files on disk plus arithmetic over the integral, measured while building the spec that wrote this file; the integral itself and the 344-turn run behind it come from context-budget.md §The other half, which carries the same grading for the same reason
maintainer: quenching
---

# Context discipline — open less, and run for less time

Every turn re-sends the whole conversation. A block of context loaded once is therefore paid once
for **each turn that follows it**, and a run's true cost is `tokens × turns remaining`, not
`tokens`. [context-budget.md](context-budget.md) §The other half owns that integral and the run it
was measured on; this file owns what to *do* about it.

There are exactly two factors, so there are exactly two ways to cut it: **open less** and **run for
less time**. Nothing else is available, and a proposal that does neither is not an optimisation.

Born `authority: background`: the counts below are this repository's own, taken once. They graduate
when a second adopting repo reproduces the shape.

## Open less: read the narrowest thing that answers the question

<!-- rules -->

Three rules, in descending order of what they were measured to be worth:

1. **Read the files a spec *declares*, never the folder they sit in.** `## Impact` names the
   `docs/standards/` paths a spec expects to touch; those, plus whatever the current task's own text
   names, are the binding contracts. A `docs/standards/<subject>/` folder is a location, not a
   claim about relevance.
2. **Read the *sections* a body cites, never the file that holds them.** Every citation in this
   repository is already written `§Section name` — the address exists; what was missing was the
   resolver. `skills.py read <path> --sections "§A" --sections "§B"` answers it for any markdown,
   and `specs.py section <slug> "A,B"` for a spec's fourteen canonical headings.
3. **N sections in ONE call.** Turns are the *other* factor. Five sections fetched over five turns
   trades tokens for turns and can lose to reading the whole file, because a turn spent early is
   repaid by every turn after it. Both readers take a list for this reason; it is half the result,
   not a convenience.

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

<!-- rationale -->

Seven runs of ~45 turns cost roughly **a seventh** of one run of 300 for the same work. That is
declared arithmetic over the integral, not a measured run, and it assumes resumption costs about
nothing. Measured against the workspace that would use it: 34 specs in `plans/`, a median of 4
sections each (0:4, 2:1, 3:6, 4:11, 5:5, 6:4, 7:3) — so the event fires a median of three times per
spec, and the smallest threshold that would change anything (≥2 sections remaining) would remove
the offer entirely from the 2- and 3-section specs, which are the runs most able to end cleanly
early.

## Two things measured and refused

<!-- rules -->

Neither of these is an available move here, and both come back looking obvious:

- **Do not segment the bundle into more files.** Taking the 50 files of `docs/standards/**` and
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
