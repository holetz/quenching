---
type: standard
title: Orchestration gears
description: The gears of the spec orchestrator — the three ways a lifecycle stage runs, the ONE gears plan derived from priority.complexity before any write, and the signals that re-evaluate a gear at the end of a stage and re-authorize the run when it moves up
resource: plugins/quenching/commands/specs/orchestrate.md, plugins/quenching/assets/specs/schema.json, specs/**
tags: [automation, specs, orchestration]
timestamp: 2026-08-10
audience: both
authority: current
source: fluxo-rapido-para-problemas-simplorios plan (task 2.3) — the gears contract the orchestrate body cites by section name; promoted to current by the phase-3 proof run (task 3.4, 2026-08-06) — a full minimal-gear cycle on the payload-quenching-orchestrate-entry spec ran capture → archive in one session and ended with pull request 886 open against develop, 19 tool calls against the ~50 the originating session spent without writing its change
maintainer: quenching
---

# Orchestration gears

`/quenching:specs:orchestrate` conducts ONE spec's whole lifecycle in one run. This standard is
the contract it derives that run from: what a gear is, how the `complexity` field on the
`priority` record becomes the ONE gears plan the run presents before any write, and how the
gear is re-evaluated at the end of every stage — with a fresh authorization when it moves up.

## What a gear is

A **gear** is the execution mode of ONE lifecycle stage. Each of the four stages — create,
develop, execute, conclude — runs in one of three gears:

- **in-session** — the stage runs here, in the conducting conversation;
- **sub-agent** — the stage runs isolated, and only its summary returns;
- **skipped** — the stage the derived stage has already passed never re-runs.

A gear changes **how** a stage runs, never **what** it writes. The per-task commit, the
`## Outcome` and the archiving are never skipped in any gear — the stages write them, and no
gear waives them.

The sub-agent gear's own test is [agents.md](agents.md) §When work is a subagent — and when it
is not: the returned summary must be **much smaller than the work** that produced it. A stage
whose summary would be as large as itself belongs in-session.

## Deriving the gears plan

ONE gears plan is presented before any write. The level on the `priority` record's
`complexity` field derives it; every stage appears in the plan — its gear, and what the gear
changes; the human adjusts it on the same screen, and the OK of the plan is the run's
authorization, per [convergence.md](/plugins/quenching/assets/references/align/convergence.md)
§The cycle-authorization contract: one confirmation at run start authorizes the run, narration
replaces each stage's plan gate, and code-coupled items and irreversible cycle actions still
gate individually.

The scale — four levels, each changing some gear, so no level is vocabulary without effect:

| Level | What it changes in the gears plan |
| --- | --- |
| `low` | the whole cycle runs in one session on a single authorization and ends opening a PR |
| `medium` | the larger stages run isolated in sub-agents |
| `high` | the stage-by-stage stops and confirmations are kept |
| `xhigh` | at least one judgment stage (adversarial review, premortem) joins the plan |

`complexity` is written by `triage`, `create` and `develop` — never silently: every write is
proposed with the scale in front of the human and lands on a confirmation, under a record
whose owner stays `triage` ([plan-lifecycle.md](../workflows/plan-lifecycle.md) §Frontmatter
records human judgments). The orchestrator derives its whole plan from this level before the
build, when the sections that would evidence the size do not exist yet — which is why the
field lives in frontmatter at all.

## Re-evaluating a gear

At the end of every stage, the state is read again (`cq specs status --spec <slug> --json`)
and the gear is re-evaluated against what the stage just revealed. Three signals move a gear
up:

- **tasks born** — the task count grew beyond what the plan assumed;
- **files beyond `## Impact`** — a stage wrote or revealed paths the spec never declared;
- **a `- [!]` task** — work that started and stopped, which a plan made from the input could
  not have predicted.

A gear that moved up returns to the plan: a new gears plan and a fresh authorization — the
run's OK covers the gear the plan presented, never the one above it. A stage that changed no
size keeps its gear; the level on disk remains the latest word on it.

The re-evaluation is what keeps the gear honest. Derived from `complexity` at the start, the
gear is a bet placed with the input's information; the stages that ran are newer information,
and a run that never re-checked would execute the whole cycle under a bet it already outgrew.
