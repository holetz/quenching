---
type: standard
title: Skill evaluation
description: What it takes to claim a skill works — with/without runs in isolated agents, assertions graded on quoted evidence, and a reported delta
resource: plugins/quenching/assets/evals/**, plugins/quenching/commands/skill/eval.md
tags: [automation, skills, evaluation, testing, benchmark]
timestamp: 2026-07-27
audience: both
authority: background
source: instrument-and-extend-skill-front plan — formats adopted from Anthropic's skill-creator
maintainer: quenching
---

# Skill evaluation

Every rule in [skills.md](skills.md) and [context-budget.md](context-budget.md) is a claim about
how an agent behaves — that triggers in the second sentence get found, that a step with a
criterion does not end early, that a body under the cap still teaches. `skills.py lint` checks
that a skill is *shaped* correctly. Nothing checks that the shape *works*. This standard is what
"works" has to mean before anyone says it.

Born `authority: background`: the contract is written, and `quenching-skill-eval` implements it,
but no skill in this repo has yet been measured against it. It graduates to `current` when at
least one committed benchmark exists.

## The claim a run is allowed to make

> On **this case set**, the skill moved the pass rate by **X** and cost **Y** extra tokens.

Bounded by the case set, stated with both numbers. Anything broader — "the skill works", "the
doctrine is validated" — is not something a run supports.

## Two arms or no claim

A case runs **twice**: once with the skill available, once without it.

A with-only run measures the model, not the skill. Most cases a skill is written for are cases a
capable model can already half-do, so a with-only run reports a high pass rate whether or not the
skill contributed anything. The comparison *is* the measurement.

Both arms run in **isolated agents**, and neither is the conversation that authored the cases:
that context has already read the skill, so any arm it runs is contaminated by exactly the text
the without-arm is defined by lacking.

Both arms run on the **same model**. A delta between arms on different models measures the models.
Never a cheaper model for one arm, and never for the grader.

## Assertions are observable, and grades carry evidence

An assertion names something a reader can check in the arm's output or on disk: a file that
exists, a zone regenerated, a path *not* written, a command reported as run. An assertion about
the wording of a reply grades prose style and flaps between runs on a skill that never changed.

Every grade is `pass`, `fail`, or `unknown`, and carries a **quoted excerpt** from that arm's own
output — not a summary of it. A grader that cannot find the excerpt records `unknown` and says
why. **An unquoted pass is indistinguishable from a guess**, and one of those in a benchmark makes
the whole number unciteable.

A run with a high `unknown` count is a finding about the case set, not evidence about the skill.

## Every branch, and the boundary

One case per branch the workflow can take — the happy path, each conditional, each documented
special case. A branch with no case is untested surface and the report names it as such rather
than implying coverage.

At least one case must exercise the `Not for:` boundary, asserting on the **absence** of work
outside the skill's scope. A skill that fires on its neighbours' jobs is worse than one that never
fires, and only a declining case can catch it.

## Report the delta, including when it is zero or negative

| Result | What it means | What the report must do |
| --- | --- | --- |
| Positive | the skill changed what the agent did, on these cases | state the token cost beside the gain |
| **Zero** | the skill taught nothing here — either it is redundant, or the cases were too easy | report **both** readings; the numbers cannot separate them |
| **Negative** | the skill made the agent worse | report it first |

A zero or negative delta is the outcome this whole contract exists to surface. Burying it makes
the evaluation decorative, and a decorative evaluation is worse than none — it converts "nobody
checked" into "somebody checked and it passed".

A benchmark measures one skill against **its own case set**. Two skills' numbers are not
comparable and are never tabled side by side.

## Description tuning is the one edit measurement authorizes

Routing is the single skill property a run can count directly, so it is the only one this front
edits on measured evidence: run the `shouldTrigger` and `shouldNotTrigger` prompts and count what
routes where.

- A trigger is **removed only on a measured miss** — never to shorten a description. Cutting a
  trigger for length is how a skill quietly stops firing for the user who worded it differently.
- A `shouldNotTrigger` prompt that fires sharpens the `Not for:` boundary, not the triggers.
- After any edit, `skills.py lint` runs again: the caps and the trigger position still hold, and
  tuning must not trade one finding for another.

Everything else a run finds is **reported with the `/skill:new` invocation that fixes it**.
Rewriting a body is authoring, and authoring needs the human whose intent the skill encodes.

## Artifacts

`evals/evals.json` beside the skill, and a timestamped run directory holding `grading.json` and
`benchmark.json`. The shapes are adopted verbatim from Anthropic's `skill-creator` and owned by
`quenching-skill-eval/references/evaluation.md`; this standard states what they must contain, not
how they are keyed.

The case set is **committed and reviewed in the same diff as the body it tests** — a case set that
lives elsewhere stops matching the skill within two edits.
