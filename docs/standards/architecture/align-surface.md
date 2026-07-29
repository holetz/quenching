---
type: standard
title: Align surface — one align per front, probe first
description: The 1×4 align column that replaced the 2×4 matrix — one align per front carrying its content stages, and the probe-before-inventory rule that makes a no-op align cost a couple of tool calls
resource: plugins/quenching/commands/align.md, plugins/quenching/commands/docs/align.md, plugins/quenching/commands/specs/align.md, plugins/quenching/commands/skill/align.md, plugins/quenching/assets/references/align-all/**
tags: [architecture, aligns, commands, probe, convergence]
timestamp: 2026-07-28
audience: both
authority: current
source: specs-flow-consolidation plan (section 4); the cross-front drift probe added by the notice-installed-tool-version-drift spec, 2026-07-28
maintainer: quenching
---

# Align surface — one align per front, probe first

The shape of the plugin's alignment surface after the fold: **one align per front**, each
carrying its front's content stages, opened by a probe that makes the no-op case free. The full
behavioral contract every align shares lives in
`plugins/quenching/assets/references/align-all/sweep-doctrine.md`; this standard records the
architectural rule — why the surface has this shape and not the previous one.

## The 1×4 column

| Front | Command |
| --- | --- |
| `docs/` | `/docs:align` |
| `specs/` | `/specs:align` |
| `.claude/` | `/skill:align` |
| all three | `/align` — conducts the three, in dependency order, on one nested OK |

There is no `align-and-update` anywhere. The previous surface was a 2×4 matrix — a structural
align plus a looping content conductor per front — which gave equal billing to conductors that
conducted almost nothing: the specs-front loop reduced to a structural align plus a sweep (its
other stages need fresh human intent per plan), and the skill-front loop converged in one pass by
construction. Each front's align now runs the content stages its front actually has, conditional
on the probe finding work; per-item stages that need fresh human intent are **reported with the
command that closes them, never driven**.

The two real loops survive where the looping is real: `/docs:align` keeps its internal fixpoint
(memory → harness → glossary feed each other), and `/align` keeps the cross-front pass, because
the fronts feed each other (a spec's distillation is glossary work; the skill front's registry is
a `docs/` listing). The conductor contract — one human OK authorizing the whole run, nesting one
level, with code-coupled confirmations still surfacing individually — lives in
`align-all/convergence.md`, cited by `/align` alone.

## Probe before the inventory

**Nothing is inventoried until the front's own verifier has said there is work.** Each front
already ships a program that answers "is there work?" with an exit code — `okf-validate.py`
(`docs/`), `specs.py doctor`/`validate` (`specs/`), `skills.py doctor`/`lint` (`.claude/`) — and
the align opens by running it, branching on the code:

- **exit 0, nothing found** → report "conformant, nothing to align" and stop. No inventory, no
  plan, no confirmation.
- **exit 0, only report-don't-drive findings** → stop the same way and list each with the command
  that closes it.
- **exit 1 or 2** → run the full inventory and continue: one plan, one OK, apply, re-verify.

The probe and the closing verification are the **same programs run twice**, which is why the rule
costs a couple of tool calls rather than a second contract to maintain — and why it inverted the
old order, where a full read-only inventory was paid before anything knew whether there was work.

**One probe call is deliberately cross-front.** `skills.py drift` reports all three installed tool
copies and the hook's wiring at once, so each align reads its own row from the same payload rather
than hand-comparing a `--version` in prose — and a run of any one align can report the other two
fronts' drift without a second probe. It is a **read**: it parses each tool's `VERSION` constant
and never executes a script sitting in the target's `.claude/hooks/`, because a probe that runs
whatever a repo has on disk is a much larger claim than one that reads three lines. The rule it
implements is [../ci-cd/versioning-release.md](../ci-cd/versioning-release.md) §Noticing drift.

**The rule is load-bearing, not an optimization.** An align that is expensive on a clean repo is
an align nobody runs as the repo grows — which is exactly when drift accumulates. A free no-op
case is what permits an align to carry its front's content stages at all, instead of those stages
living in a separate command nobody invokes.

**A stage the probe cannot price is offered, never run to find out.** The standing example is the
whole-bundle glossary sweep in `/docs:align`: no cheap signal exists, so it is gated on a free
proxy (doc count against glossary size) and offered with its cost stated, never entered
automatically.
