---
type: standard
title: Skill evaluation
description: What it takes to claim a skill works — with/without runs in isolated processes, assertions graded on quoted evidence, a rate reported with its fixture, and a delta reported even when it is zero
resource: plugins/quenching/assets/evals/**, plugins/quenching/commands/skill/eval.md
tags: [automation, skills, evaluation, testing, benchmark]
timestamp: 2026-07-29
audience: both
authority: current
source: instrument-and-extend-skill-front plan — formats adopted from Anthropic's skill-creator. Graduated to current on its own stated gate: /skill:agent:new and /skill:hook:new each carry a committed evals.json + grading.json + benchmark.json with a non-zero stated delta (2026-07-27)
maintainer: quenching
---

# Skill evaluation

Every rule in [skills.md](skills.md) and [context-budget.md](context-budget.md) is a claim about
how an agent behaves — that triggers in the second sentence get found, that a step with a
criterion does not end early, that a body under the cap still teaches. `skills.py lint` checks
that a skill is *shaped* correctly. Nothing checks that the shape *works*. This standard is what
"works" has to mean before anyone says it.

Born `authority: background` and **graduated to `current` on 2026-07-27**, on its own stated gate:
`/skill:eval` implements the contract, and two commands have now been measured against it with the
artifacts committed — `/skill:agent:new` and `/skill:hook:new`, each with a non-zero stated delta.
The gate was *at least one committed benchmark*, and every rule below was either exercised by those
two runs or written from what they measured.

## The claim a run is allowed to make

> On **this case set**, the skill moved the pass rate by **X** and cost **Y** extra tokens.

Bounded by the case set, stated with both numbers. Anything broader — "the skill works", "the
doctrine is validated" — is not something a run supports.

## Two arms or no claim

A case runs **twice**: once with the skill available, once without it.

A with-only run measures the model, not the skill. Most cases a skill is written for are cases a
capable model can already half-do, so a with-only run reports a high pass rate whether or not the
skill contributed anything. The comparison *is* the measurement.

Both arms run in **isolation**, and neither is the conversation that authored the cases: that
context has already read the skill, so any arm it runs is contaminated by exactly the text the
without-arm is defined by lacking.

**Isolation is a property of the process, not of the agent.** A sub-agent gets a fresh context but
**inherits the session's plugin registry**, so a without-arm dispatched that way is still listed
the command it is defined by lacking — it merely has not read the body. That is a weaker claim than
"no path to it", and the delta it produces understates the skill by whatever the description alone
taught. The honest without-arm is a **separate process** the skill cannot reach: a fresh `claude -p`
whose settings carry `enabledPlugins` for the with-arm and omit it for the without-arm, the pattern
`functional-checks.sh` already uses. When a run cannot achieve that, it says so and downgrades its
claim; it does not report the number as if it had.

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

## A measured rate is conditional on its fixture

A routing rate is not a property of the description alone — it is a property of the description
**in the repo the probe ran in**, because an intent-shaped phrase names a subject the session looks
for before it routes.

Measured while building these two evals: `/skill:agent:new`'s phrase *"set up something that audits
our migrations and reports back"* routed 5/5 in a fixture that shipped
`/.docs/standards/automation/agents.md` — and the identical phrase in a bare repo routed to
`/skill:new` instead. Single variable, both runs healthy. The 5/5 was **fixture-assisted**: the
description was borrowing routing the target repo supplied.

Two rules follow:

- **Report the fixture with the rate.** A number cited without what the repo contained is not
  reproducible, and a later run in a different fixture will read as a regression that never
  happened.
- **A probe grades the fixture unless the fixture contains the subject the phrase names.** A phrase
  about migrations needs a migration; a phrase whose command wants an OKF bundle needs one, or the
  probe spends its budget discovering the subject is missing. Seed the smallest repo in which every
  phrase can be answered without exploring.

## Description tuning is the one edit measurement authorizes

Routing is the single skill property a run can count directly, so it is the only one this front
edits on measured evidence: run the `shouldTrigger` and `shouldNotTrigger` prompts and count what
routes where.

- A trigger is **removed only on a measured miss** — never to shorten a description. Cutting a
  trigger for length is how a skill quietly stops firing for the user who worded it differently.
- **A truncated run is not a miss.** A probe that hits its turn cap while still orienting reports a
  FALSE miss, and a false miss argues for deleting a trigger that works. Measured here: at
  `--max-turns 3` two working triggers reported as misses (`error_max_turns`), and at 8 both routed
  correctly. A run that ends on the cap is recorded **inconclusive** and graded as nothing — never
  as evidence in either direction.
- A `shouldNotTrigger` prompt that fires sharpens the `Not for:` boundary, not the triggers.
- After any edit, `skills.py lint` runs again: the caps and the trigger position still hold, and
  tuning must not trade one finding for another.

Everything else a run finds is **reported with the `/skill:new` invocation that fixes it**.
Rewriting a body is authoring, and authoring needs the human whose intent the skill encodes.

## Artifacts

`evals/evals.json` beside the skill, and a timestamped run directory holding `grading.json` and
`benchmark.json`. The shapes are adopted verbatim from Anthropic's `skill-creator` and owned by
[`skill-eval/evaluation.md`](/plugins/quenching/assets/references/skill-eval/evaluation.md); this
standard states what they must contain, not how they are keyed.

The case set is **committed and reviewed in the same diff as the body it tests** — a case set that
lives elsewhere stops matching the skill within two edits.

**A rename carries its eval tree.** The artifacts mirror the command's path, so renaming the
command orphans them silently — nothing errors, and the stale tree keeps answering to a name that
no longer routes. Move the tree in the same commit as the rename, or the mirroring the design
depends on is the one property it does not have.

**And an orphan is deleted, not re-pointed.** `assets/evals/specs/capture/` was the standing
example of the failure above, and how it was settled (2026-07-29) is the rule for the next one.
Renaming the folder to the successor command was the obvious move and the wrong one: the case set
did not merely carry a stale *name*, it asserted a retired *model* — a task file under
`/.specs/backlog/` with `type: task`, reindexed by a `specs.py` subcommand that no longer exists —
and its only run had already recorded itself `citable: false` over a case set it called defective.
Re-pointing it would have made measurements of a dead command read as evidence for the live one.
So the tree was removed. **A run measures the command it was written against; when that command
is gone, the run is history with nothing to attach to, and history that cannot be attached is
deleted rather than re-labelled.** A rename moves an eval tree only while the case set still
asserts what the command still does.
