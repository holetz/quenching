---
type: standard
title: Align surface — one align per front, probe first
description: The 1×4 align column that replaced the 2×4 matrix — one align per front carrying its content stages, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, the rule that no sweep records itself: an align's account of its own run goes in the report, never into the bundle, and the two conductor categories sharing the cycle-authorization contract — `/align` conducts the three fronts, `/quenching:specs:orchestrate` conducts the four stages of one spec, and neither reimplements what it conducts
resource: plugins/quenching/commands/align.md, plugins/quenching/commands/knowledge/align.md, plugins/quenching/commands/specs/align.md, plugins/quenching/commands/specs/orchestrate.md, plugins/quenching/commands/components/align.md, plugins/quenching/assets/references/align/**
tags: [architecture, aligns, commands, probe, convergence]
timestamp: 2026-08-11
audience: both
authority: current
source: specs-flow-consolidation plan (section 4); the cross-front drift probe added by the notice-installed-tool-version-drift spec, 2026-07-28, and retired by modularizar-specs-knowledge-components task 10.3 once the four scripts it compared a legacy copy against stopped existing; the no-sweep-records-itself rule from the retire-docs-log spec's branch review, 2026-07-29; the probe's subject rewritten from stale-copy to legacy-copy (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec) once no align installed a tool any more; the two conductor categories and the drop of "cited by `/align` alone" by the fluxo-rapido-para-problemas-simplorios plan (task 2.4)
maintainer: quenching
---

# Align surface — one align per front, probe first

The shape of the plugin's alignment surface after the fold: **one align per front**, each
carrying its front's content stages, opened by a probe that makes the no-op case free. The full
behavioral contract every align shares lives in
`plugins/quenching/assets/references/align/sweep-doctrine.md`; this standard records the
architectural rule — why the surface has this shape and not the previous one.

## The 1×4 column

| Front | Command |
| --- | --- |
| `/.knowledge/` | `/quenching:knowledge:align` |
| `/.specs/` | `/quenching:specs:align` |
| `.claude/` | `/quenching:components:align` |
| all three | `/align` — conducts the three, in dependency order, on one nested OK |

There is no `align-and-update` anywhere. The previous surface was a 2×4 matrix — a structural
align plus a looping content conductor per front — which gave equal billing to conductors that
conducted almost nothing: the specs-front loop reduced to a structural align plus a sweep (its
other stages need fresh human intent per plan), and the skill-front loop converged in one pass by
construction. Each front's align now runs the content stages its front actually has, conditional
on the probe finding work; per-item stages that need fresh human intent are **reported with the
command that closes them, never driven**.

The two real loops survive where the looping is real: `/quenching:knowledge:align` keeps its
internal fixpoint (memory → harness → glossary feed each other), and `/align` keeps the
cross-front pass, because the fronts feed each other (a spec's distillation is glossary work; the
components front's registry is a `/.knowledge/` listing). The conductor contract — one human OK
authorizing the whole run, nesting one
level, with code-coupled confirmations still surfacing individually — lives in
`align/convergence.md`, shared by both conductors and never restated by either (§Two conductor
categories).

## Two conductor categories

The conductor contract is shared, never owned by a single command. Two conductors exist, told
apart by what they conduct:

| The conductor | What it conducts | The contract |
| --- | --- | --- |
| `/align` | the three fronts, in dependency order, on one nested OK | `align/convergence.md` — cited, never restated |
| `/quenching:specs:orchestrate` | the four stages of ONE spec — create, develop, execute, conclude — in one run, entering at the derived stage | `align/convergence.md`, plus its own gears plan ([orchestration-gears.md](../automation/orchestration-gears.md)) |

The spec orchestrator is a conductor, not an align: it conducts no front, so it earns no row in
the 1×4 column. It conducts the lifecycle of one spec, invoking each stage as the command that
owns it — the same conduct-never-reimplement rule that binds `/align` — and derives its run from
the `complexity` the spec's `priority` record carries, per the gears contract. Both open on one
human OK that authorizes the whole run, nest one level, and surface code-coupled confirmations
individually; the clause that once limited the contract to `/align` is gone.

## Probe before the inventory

**Nothing is inventoried until the front's own verifier has said there is work.** Each front
already ships a program that answers "is there work?" with an exit code — `cq knowledge validate`
(`/.knowledge/`), `cq specs doctor`/`validate` (`/.specs/`), `cq components doctor`/`lint` (`.claude/`) —
and the align opens by running it, branching on the code:

- **exit 0, nothing found** → report "conformant, nothing to align" and stop. No inventory, no
  plan, no confirmation.
- **exit 0, only report-don't-drive findings** → stop the same way and list each with the command
  that closes it.
- **exit 1 or 2** → run the full inventory and continue: one plan, one OK, apply, re-verify.

The probe and the closing verification are the **same programs run twice**, which is why the rule
costs a couple of tool calls rather than a second contract to maintain — and why it inverted the
old order, where a full read-only inventory was paid before anything knew whether there was work.

**The rule is load-bearing, not an optimization.** An align that is expensive on a clean repo is
an align nobody runs as the repo grows — which is exactly when drift accumulates. A free no-op
case is what permits an align to carry its front's content stages at all, instead of those stages
living in a separate command nobody invokes.

**A stage the probe cannot price is offered, never run to find out.** The standing example is the
whole-bundle glossary sweep in `/quenching:knowledge:align`: no cheap signal exists, so it is gated on a free
proxy (doc count against glossary size) and offered with its cost stated, never entered
automatically.

## No sweep records itself

**Every write a sweep makes belongs to the front it is aligning. The report is the only account
of the run itself.** Each align used to close by appending one consolidated line to `/.knowledge/log.md`
— `converged in N passes`, `aligned workspace (N migrated, M renamed)`, `ranked N specs` — and
`/align` added a fifth for the cross-front run. All five are gone, and the rule that replaced
them holds for any sweep added later.

The entry was self-describing, and that is what made it worthless. What a pass did to `/.knowledge/` is
legible **from `/.knowledge/`** and from the repo's own history; a line saying a sweep ran told a reader
nothing the tree and the git log did not already say, and cost a write on every invocation —
including the no-op runs the probe rule exists to make free. A sweep whose clean case costs three
tool calls should not spend a fourth narrating that it found nothing.

It also removed the one thing every align wrote **outside its own front**. `/quenching:specs:align` and
`/quenching:specs:triage` reached into the `/.knowledge/` bundle for a log line and nothing else; with that gone,
the `specs` front writes into `/.knowledge/` at exactly one point — a concluded spec's distillation,
which mints real knowledge rather than a record of activity. The cross-front dependency in
[§The 1×4 column](#the-14-column) is unchanged: `/.knowledge/` still goes first, because that
distillation and the components front's rule + registry still need the tree to exist.

The general form: **a command's own account of itself goes in its report, never into the artifact
it maintains.** A store that accumulates entries about the tools that touched it is a second
history competing with git, and the reader who needs it can read git.
