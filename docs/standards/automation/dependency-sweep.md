---
type: standard
title: Dependency sweep
description: The contract of the sub-agent dependency sweep that runs at the open of a /quenching:specs:develop pass, before it asks anything — trigger, tool profile, deliverable, and the persistence of the map with the date it carries
resource: plugins/quenching/commands/specs/develop.md, plugins/quenching/assets/references/specs-develop/questions.md
tags: [automation, dependency-sweep, subagent, specs-develop]
timestamp: 2026-08-25
audience: both
authority: background
source: spec varredura-de-dependencias-antes-do-banco-shape — the comparison between /plan (2.99M tokens over 27 Explore calls, six findings) and /quenching:specs:develop (20 files touched) that motivated inserting the sweep before the pass asks; re-anchored at the pass's open when compose and refine replaced the ladder of banks (compor-e-refinar, 2026-08-25)
maintainer: quenching
---

# Dependency sweep

With no cross-file dependency data on the table, `/quenching:specs:develop`'s refine asks the right
question and has nothing to answer it with — that was the signal that motivated this contract. The
sweep exists to put that data on the table **before** the pass asks anything, instead of merely
confirming decisions already taken.

## Position in the flow

At the pass's open, before compose asks. It is the only position where the data arrives in time to
change the questions — and, with compose and refine in a single pass, it is literal for the first
time: one sweep, before everything.

## The trigger

The sweep fires once per pass, when `### Mapa de dependências` is not yet under `## Design` — which
covers in one stroke the captured spec compose is about to shape and the spec born with
`## Proposal` filled that arrives straight at refine. Before, these were two triggers declared
separately because each bank entered by a path of its own.

**A spec is swept at most once**, and never for having crossed a `complexity` level — a spec looks
small exactly while nobody has read its dependencies yet.

## The sub-agent's profile

A **new** profile, distinct from the `Read, Grep, Glob` of the adversarial and gate banks'
sub-agents. It follows the `Explore` of Claude Code's native planning mode:

- the full read-only set — everything but `Edit`, `Write`, `NotebookEdit` and `Agent`, with `Bash`
  included;
- the model inherited from the session, with no override and no pinned effort;
- search breadth declared per invocation.

`Bash` is what allows returning the aggregate a `grep`/`gh`/`cq` produces instead of the raw dump —
the same demand the evidence doctrine and [agents.md](agents.md) §The verifier shape already make
of an inspecting sub-agent.

## The deliverable

A cross-file dependency map, not a reading trail: the sub-agent returns a table and touches nothing.

## Persistence of the map

The map goes into the spec itself, in `### Mapa de dependências` under `## Design`, inside the
consolidated write of the bank that asked for it — written by the **orchestrator**, never by the
sub-agent. Written there it persists on the board, is read for free by the following banks instead
of being re-swept, and stays visible to the human on the issue.

The map carries the **sweep's date**, because a spec whose scope changed afterwards is never
re-swept and the map would go stale in silence without that date to expose the lag.

## The graduation gate

Born `authority: background`: the rule above is a contract this repository declared, not yet proven
by repeated and independent use. It would graduate to `current` once the sweep's result — compared
against `/plan`'s reference pass (findings on the table before the adversarial bank, the session's
summed cost) — is measured in a real run of `/quenching:specs:develop` against the `res4966_v02`
task, per the `## Handoff` of the spec that originated it.
