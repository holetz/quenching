---
type: standard
title: The fan-out criterion and the measurement that decided it
description: The criterion that separates the two regimes for conducting N specs — whatever writes to the working tree serializes, whatever does not, does not — the collision measurement over this front's 20 buildable specs that ruled out parallelism in the building regime, and the four shapes considered and rejected; the procedure both entries read at runtime lives in specs-fanout/fanout.md and is cited, never restated
resource: plugins/quenching/commands/specs/execute-queue.md, plugins/quenching/commands/specs/develop-batch.md, plugins/quenching/assets/references/specs-fanout/**
tags: [workflows, specs, queue, orchestration, isolation, parallelism]
timestamp: 2026-08-16
audience: both
authority: current
source: orquestrar-specs-em-paralelo plan (task 1.1) — the collision measurement over this front's 20 buildable specs, and session d45c0252-9c39-42c4-956a-6badb9fb58ee, which assembled the queue by hand for ~1.2M tokens and ~2.1h of serial wall clock and ended in five PRs that collided with each other; tightened to what only the bundle can carry by the same spec's branch review, which measured six of the eight sections restating specs-fanout/fanout.md — the second copy plugin-layout.md §A contract a command reads at runtime is a reference, not a standard exists to prevent
maintainer: quenching
---

# The fan-out criterion and the measurement that decided it

Conducting N specs in one authorization has only two regimes, and this standard owns **why** they
are what they are: the criterion that separates them, the measurement that ruled out parallelism in
the building regime, and the shapes that were considered and rejected.

**The procedure both entries read at runtime is not here.** The queue's shape, the branch mark, the
entry contract, the block classification and the recursive return are
`plugins/quenching/assets/references/specs-fanout/fanout.md` §The two regimes
§The queue's shape §The branch carries the slugs §The entry contract §Classifying a block
§The recursive return — cited, never restated. A procedure a command reads while running inside a
target is payload, not a fact about the target
([../architecture/plugin-layout.md](../architecture/plugin-layout.md) §A contract a command reads at
runtime is a reference, not a standard). What is left here is what that reference cannot carry: a
decision measured against **this** front.

A spec's lifecycle is [plan-lifecycle.md](plan-lifecycle.md) and a task's execution is
[task-execution.md](task-execution.md). Nothing here replaces either.

## The criterion that separates the two regimes

| Regime | Shape | Entry |
| --- | --- | --- |
| **building** | a **serial** queue over a single isolation | `/quenching:specs:execute-queue` |
| **defining** | a genuinely **parallel** batch | `/quenching:specs:develop-batch` |

**Whatever writes to the working tree serializes; whatever does not, does not.** That is the entire
criterion, and it is what a third fan-out entry will be measured against: `create` and `develop`
take no branch at all and, under the `github` and `azure-boards` backends, touch no file at all;
`execute` writes code, and code collides.

The criterion decides the name along with the shape. The defining entry **is not called a queue**
because serialization is a declared feature of the other one alone, and a name whose apparent object
differs from what it operates is prohibited by
[../naming/command-surface.md](../naming/command-surface.md) §Verb-first names that reveal the
action.

## The measurement that ruled out parallelism in the building regime

Over this front's 20 buildable specs, with 143 files declared under `## Impact` and 190 possible
pairs:

| Measure | Value |
| --- | --- |
| pairs that collide, path as declared | **107 of 190 (56%)** |
| pairs that collide, path normalized by basename | **150 of 190 (79%)** |
| largest provably disjoint batch | **4 of 20** |
| the worst single spec — `upgrade-okf-to-v0-2` | collides with **19 of 19** |

The disjunction parallelism would require does not exist at that density, and the two collision rows
diverge because `## Impact` declares paths in inconsistent notation — which makes any mechanical
disjunction proof **between** specs unreliable, unlike the `[P]` check **within** one spec, whose
paths one author wrote only once.

The serial form fixes a second defect for free, and this is the argument that would survive even if
collision were zero: **spec N's gate runs over the result of 1..N−1**. Parallel runs each measure
their gates in isolation against the same base, and the combination is only verified after the
merges — which is exactly when nobody is looking.

**The token saving does not come from parallelism, which is why serializing does not cost it.** It
comes from each spec running in a sub-agent of its own context — an in-session queue would make spec
N re-send the previous N−1 specs' context every turn — and from **one** `conclude` instead of N,
with the branch review, the release and the archive paid once.

## What this shape deliberately is not

Four alternatives were considered and rejected. Each of them looks obvious again to anyone who only
sees the finished queue, and that is why the rejection is written down with its reason:

- **Provably disjoint batches** — the `[P]` check raised one level. Measured ceiling of 4 in 20, and
  the inconsistent path notation makes the proof unreliable without prior normalization.
- **An integration train** — N branches merged in order into a `train/<data>`, each rebasing onto
  the result of the previous one. It is the only one that would scale to 50, and it is the one that
  lets spec 3 have its ground moved by spec 2.
- **A merge queue with rebase-on-green** — it would preserve per-spec review, at the cost of
  re-running the gates N times and of keeping the parallelism whose ceiling the measurement already
  showed to be 4.
- **A menu of run modes** — invocation flags for question volume, isolation shape or effort level.
  They were removed once already, with the reason written into a standard of its own; the queue does
  not reintroduce them through a side door.
