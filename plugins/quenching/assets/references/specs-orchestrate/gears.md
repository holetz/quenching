# The gears contract — how `/quenching:specs:orchestrate` derives its run

[orchestrate.md](${CLAUDE_PLUGIN_ROOT}/commands/specs/orchestrate.md) conducts ONE spec's whole
lifecycle in one run. This file is the contract it derives that run from: what a gear is, how the
`complexity` field on the `priority` record becomes the ONE gears plan the run presents before any
write, and how the gear is re-evaluated at the end of every stage — with a fresh authorization when
it moves up.

This contract lives in the plugin, never in a target's bundle: it is procedure a command needs
while running inside a target, not a fact about that target, so it is cited by
`${CLAUDE_PLUGIN_ROOT}` from every repo the same way — never installed, and never resolved from a
target's own `/.docs/`.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

## What a gear is

<!-- rules -->

A **gear** is the execution mode of ONE lifecycle stage. Each of the four stages — create,
develop, execute, conclude — runs in one of three gears:

- **in-session** — the stage runs here, in the conducting conversation;
- **sub-agent** — the stage runs isolated, and only its summary returns;
- **skipped** — the stage the derived stage has already passed never re-runs.

A gear changes **how** a stage runs, never **what** it writes. The per-task commit, the
`## Outcome` and the archiving are never skipped in any gear — the stages write them, and no gear
waives them.

**The sub-agent gear's own test:** delegate when the returned summary is **much smaller than the
work** that produced it (a repo-wide sweep, a many-file audit, a read that ends in one table), when
slices run in parallel, or when the tool set must be narrower than the conversation's. Keep work
inline when its output is as large as itself (a rewrite lands in context anyway), when it is one
quick lookup, or when the handoff context would cost what the isolation saves. A recurring
*workflow* is a command; a delegated *unit of work* is an agent — the two are not rivals, and a
command may invoke an agent as one step. A stage whose summary would be as large as itself belongs
in-session.

## Deriving the gears plan

<!-- rules -->

ONE gears plan is presented before any write. The level on the `priority` record's `complexity`
field derives it; every stage appears in the plan — its gear, and what the gear changes; the human
adjusts it on the same screen, and the OK of the plan is the run's authorization, per
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) §The
cycle-authorization contract: one confirmation at run start authorizes the run, narration replaces
each stage's plan gate, and code-coupled items and irreversible cycle actions still gate
individually.

The scale — four levels, each changing some gear, so no level is vocabulary without effect:

| Level | What it changes in the gears plan |
| --- | --- |
| `low` | the whole cycle runs in one session on a single authorization and ends opening a PR |
| `medium` | the larger stages run isolated in sub-agents |
| `high` | the stage-by-stage stops and confirmations are kept |
| `xhigh` | at least one judgment stage (adversarial review, premortem) joins the plan |

`complexity` is written by `triage`, `create` and `develop` — never silently: every write is
proposed with the scale in front of the human and lands on a confirmation, under a record whose
owner stays `triage`. The orchestrator derives its whole plan from this level before the build,
when the sections that would evidence the size do not exist yet — which is why the field lives in
frontmatter at all.

## Re-evaluating a gear

<!-- rules -->

At the end of every stage, the state is read again (`specs.py status --spec <slug> --json`) and the
gear is re-evaluated against what the stage just revealed. Three signals move a gear up:

- **tasks born** — the task count grew beyond what the plan assumed;
- **files beyond `## Impact`** — a stage wrote or revealed paths the spec never declared;
- **a `- [!]` task** — work that started and stopped, which a plan made from the input could not
  have predicted.

A gear that moved up returns to the plan: a new gears plan and a fresh authorization — the run's OK
covers the gear the plan presented, never the one above it. A stage that changed no size keeps its
gear; the level on disk remains the latest word on it.

The re-evaluation is what keeps the gear honest. Derived from `complexity` at the start, the gear
is a bet placed with the input's information; the stages that ran are newer information, and a run
that never re-checked would execute the whole cycle under a bet it already outgrew.
