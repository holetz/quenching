# The gears contract — how `/quenching:specs:cycle` derives its run

[cycle.md](${CLAUDE_PLUGIN_ROOT}/commands/specs/cycle.md) conducts ONE spec's lifecycle, in two
halves authorized separately. This file is the contract it derives each half from: what a gear is,
how the `complexity` field on the `priority` record becomes the ONE gears plan a half presents
before any write, and how the gear is re-evaluated at the end of every stage — with a fresh
authorization when it moves up.

**A gear governs the stages of ONE spec, and nothing about N.** Conducting N specs, the form a
run's recursive return takes, how a block in one spec is classified against the ones after it, and
the deliberate absence of a cap on N all belong to
[fanout.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-fanout/fanout.md) §The two regimes
§The queue's shape §The entry contract §Classifying a block §The recursive return, which
`/quenching:specs:execute-queue` and `/quenching:specs:develop-batch` derive their runs from.
Neither of them has a gear, and nothing here is theirs to read.

This contract lives in the plugin, never in a target's bundle: it is procedure a command needs
while running inside a target, not a fact about that target, so it is cited by
`${CLAUDE_PLUGIN_ROOT}` from every repo the same way — never installed, and never resolved from a
target's own `/.knowledge/`.

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

**Capture is the one stage whose gear is not derived.** A spec that does not exist yet carries no
`priority` record, so there is nothing to derive a plan from; `create` runs in-session on its own
gate, and the `complexity` it proposes is what the first gears plan is then derived from.

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

**Two halves, two plans, two authorizations.** Defining (`develop`) and building (`execute` →
`conclude`) are authorized separately, and no level of the scale below collapses the seam — the
building half is authorized after the spec is `ready`, on a plan derived from the `complexity` then
on disk.

ONE gears plan is presented before a half's first write. The level on the `priority` record's
`complexity` field derives it; every stage of that half — and no other — appears in the plan, with
its gear and what the gear changes; the human adjusts it on the same screen, and the OK of the plan
is that half's authorization and no more, per
[convergence.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/convergence.md) §The
cycle-authorization contract: one confirmation authorizes the run it opens, narration replaces
each stage's plan gate, and code-coupled items and irreversible cycle actions still gate
individually.

The scale — four levels, each changing some gear, so no level is vocabulary without effect:

| Level | What it changes in the gears plan |
| --- | --- |
| `low` | each half runs in one session on its own authorization, and building ends opening a PR |
| `medium` | the larger stages run isolated in sub-agents |
| `high` | the stage-by-stage stops and confirmations are kept |
| `xhigh` | at least one judgment stage (adversarial review, premortem) joins the plan |

**What the scale actually measures.** `complexity` is not the size of the change, its scope or its
difficulty — a small change can still need a human at every step, and a large mechanical one can
need almost none. It measures how much a human needs to be part of the process: `low` says the LLM
can be trusted to carry the whole half with close to no supervision; `medium` accepts some real
risk in leaving stage-by-stage judgment to the LLM alone; `high` and `xhigh` escalate the need for
a human's presence, which the table above already encodes as stops, isolation and judgment stages.
`triage`, `create` and `develop` propose a level against this criterion, never against the word's
plain reading.

`complexity` is written by `triage`, `create` and `develop` — never silently: every write is
proposed with the scale in front of the human and lands on a confirmation, under a record whose
owner stays `triage`. **`create` is the one exception to the ordering, never to the rule.** It
writes the level it computed from the input BEFORE anyone sees it, because the spec does not exist
yet for a confirmation to gate on — but the scale still reaches the human, on the capture's own
closing screen, or on `/quenching:specs:develop`'s first pass over a spec nobody looked at. The
proposal survives; only its position relative to the write moves. The defining half derives its
plan from this level before the build, when the sections that would evidence the size do not exist
yet — which is why the field lives in frontmatter at all.

## Re-evaluating a gear

<!-- rules -->

At the end of every stage, the state is read again (`cq specs status --spec <id> --json`) and the
gear is re-evaluated against what the stage just revealed. Three signals move a gear up:

- **tasks born** — the task count grew beyond what the plan assumed;
- **files beyond `## Impact`** — a stage wrote or revealed paths the spec never declared;
- **a `- [!]` task** — work that started and stopped, which a plan made from the input could not
  have predicted.

A gear that moved up returns to the plan of the half the run is in: a new gears plan and a fresh
authorization — that half's OK covers the gear its plan presented, never the one above it. A stage
that changed no size keeps its gear; the level on disk remains the latest word on it.

The re-evaluation is what keeps the gear honest. Derived from `complexity` at the start of a half,
the gear is a bet placed with the information that half opened on; the stages that ran are newer
information, and a run that never re-checked would execute the rest of the half under a bet it
already outgrew.
