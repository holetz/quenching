---
type: decision
title: The small tier executes a testable task below the context cut
description: Why haiku and gpt-6-luna are admitted as per-task executors when the task carries a protected verify oracle and its projected context stays at or under 80k, the price evidence with its date, the short escalation ladder, and why the rule stays provisional until a pilot
resource: plugins/quenching/assets/references/specs-execute/execution-delegation.md
tags: [decision, models, execution, codex, cost]
timestamp: 2026-10-17
audience: both
authority: current
source: spec 1661
maintainer: quenching
---

# The small tier executes a testable task below the context cut

This decision revises the model policy that kept every production-code writer on the session
model and named `haiku` (and, on the Codex side, `gpt-6-luna`) as never admitted. It is
**provisional**: a pilot of about ten eligible tasks decides whether it stands (see §Pilot).

## Finding

The prohibition was written when the small tier was Haiku 4, which could not be trusted with code.
Two things changed:

- **The model.** Haiku 5.5 performs well on bounded, testable work, provided its prompt stays under
  100k tokens.
- **The defense.** Many execute tasks already carry a deterministic oracle (`verify:`) and run in a
  disposable worktree. Under those two conditions a cheaper executor's mistake is caught by the
  oracle and cost only a retry, not a shipped defect.

Pricing, checked on **2026-10-14** (Claude API reference, cached 2026-10-06):

| Model | Input / output per MTok |
| --- | --- |
| Haiku 5.5, prompt ≤ 100K tokens | $0.10 / $0.50 |
| Haiku 5.5, prompt > 100K tokens | $0.50 / $2.50 (5×, applied to the whole prompt) |
| Sonnet 5.5 (flat to 1M) | $2 / $10 |
| Opus 5.5 | $4 / $20 |

Cache reads cost 0.1× the input rate in force; cache writes 1.25× (5 min) or 2× (1 h). Haiku 5.5's
tokenizer counts about 30% more tokens than Haiku 4.5's. Below the cut, haiku is **20× cheaper per
token than sonnet**; above it only 4×, and a small model also degrades in long context. An agentic
executor's prompt grows every turn, so a task that crosses 100K loses most of the advantage at the
moment it is most likely to fail. The cut therefore shapes the rule, not just the price.

## Decision

Decided by the human on 2026-10-17 (spec 1879's decision sheet, D2 A). The small tier — `haiku` in
Claude, `gpt-6-luna` in Codex — may execute ONE task when **all** of these hold:

1. **Protected oracle.** The task has an executable `verify:`, and the oracle's files (the tests the
   command runs) sit **outside** its `files:`: the executor never edits the test it is judged by.
2. **Reversible.** A disposable worktree, no destructive git, nothing under `/docs/` or
   `knowledge/`.
3. **Projected context ≤ 80,000 tokens.** Computed by `cq specs estimate --task` as
   `ceil(bytes / 4) × 1.3` over the task's `files:` and `pattern:` plus `EXECUTOR_FIXED_TOKENS`.
   The 1.3 factor is Haiku 5.5's tokenizer; 80k is a **margin under** the 100k cut, which is the
   measured worker budget (`BUDGETS worker: 100000`) reused, not a new number.
4. **A short ladder.** One attempt on the small tier. A failed `verify:` → the session model
   **corrects on the diff** (the same rule as spec 1879's Codex executor); a second failure → the
   human.
5. **Review by reading.** Execute's own self-review, on the session model, reads the diff before
   the tick. No extra sub-agent, no new budget.

`EXECUTOR_FIXED_TOKENS = 33000`, measured on 2026-10-17: the first-turn context of `general-purpose`
`Task` sub-agents launched in this repository (system prompt, tools and project instructions,
minus the launch prompt) sat between 32,065 and 33,329 tokens across the sessions of 2026-10-15 to
2026-10-17. No per-task executor transcript existed yet, so the constant comes from the nearest
launch with the same harness; the pilot re-measures it.

Effort: `haiku` at `medium` (the 5.5 default); `gpt-6-luna` at `medium`, like the 1879 executor.

**Judgment never moves down.** develop, triage, conclude, the orchestrator, the verifier, the
reviewer, the spec-architect and every write to `/docs/standards/` keep their current pins; the
whole-spec routing (spec-runner sonnet/opus) does not change. The new rung lives **per task, inside
execute**. `/quenching-align:knowledge:import-memory` stays never-haiku: its executors authorize an
irreversible deletion and have no oracle.

## Alternatives rejected

- **Keep the prohibition** — its premise (a weak Haiku 4) lapsed.
- **Admit the small tier by spec `complexity: low`** — complexity measures how much the human is
  present, not testability; a `low` spec without `verify:` would reach haiku.
- **Admit luna only inside spec 1879** — the Claude and Codex policies would diverge, with no record.
- **Haiku for a whole spec-runner** — it would put develop's and conclude's judgment on a small model.

## Pilot

About ten eligible tasks against a sonnet/sol baseline, measuring cost per **finished** task
(retries and corrections included) through `cq components session cost` by model (`byModel`, never
summing tiers), the first-try `verify:` pass rate, the self-review rejection rate and the context
peak. The pilot also answers whether the subscription weighs models by API price, which this
decision could not establish. Until it reports, this decision stays provisional.

## Consequence

- `capabilities.md` conditions the parent rule: never on a step whose output authorizes a deletion,
  or that lands in production code **without a protected oracle**.
- `execution-delegation.md`, `execute.md` step 5b, `docs/standards/automation/agents.md` and
  `docs/standards/workflows/task-execution.md` declare the rung; `orchestrator.md` says the rung is
  execute's, not its own.
- `surface-translation.md` and the generated Codex skills admit `gpt-6-luna` under the same
  conditions; the Codex executor's `verified` class picks luna when the oracle is protected and the
  projection fits, and `gpt-6.1-sol` otherwise.
