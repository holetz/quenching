---
type: standard
title: Align surface — one align per front, probe first
description: The aligned-front column — one align per local front carrying its content stages, the fifth pillar (`git`) declared with no align because it ships no verifier a probe could run, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, the rule that no sweep records itself, and conductor categories sharing the cycle-authorization contract — `/align` conducts the three local fronts (`knowledge`, `design`, `components`), `/quenching:specs:cycle` the four stages of one spec, and the two fan-out entries N specs each; none reimplements what it conducts
resource: plugins/quenching/commands/align.md, plugins/quenching/commands/knowledge/align.md, plugins/quenching/commands/design/align.md, plugins/quenching/commands/specs/cycle.md, plugins/quenching/commands/specs/execute-queue.md, plugins/quenching/commands/specs/develop-batch.md, plugins/quenching/commands/components/align.md, plugins/quenching/assets/bin/quenching/design/**, plugins/quenching/assets/bin/quenching/git/**, plugins/quenching/assets/references/align/**, plugins/quenching/assets/references/specs-fanout/**
tags: [architecture, aligns, commands, probe, convergence]
timestamp: 2026-08-27
audience: both
authority: current
source: specs-flow-consolidation plan (section 4); the cross-front drift probe added by the notice-installed-tool-version-drift spec, 2026-07-28, and retired by modularizar-specs-knowledge-components task 10.3 once the four scripts it compared a legacy copy against stopped existing; the no-sweep-records-itself rule from the retire-docs-log spec's branch review, 2026-07-29; the probe's subject rewritten from stale-copy to legacy-copy (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec) once no align installed a tool any more; the two conductor categories and the drop of "cited by `/align` alone" by the fluxo-rapido-para-problemas-simplorios plan (task 2.4); retired with orchestration-gears.md (marchas-do-orquestrador-vivem-no-plugin, 2026-08-11); the third and fourth conductor rows, and the N-is-the-only-difference rule, by orquestrar-specs-em-paralelo (task 4.3), which also carried the orchestrate → cycle rename through; the column widened to 1×5 by pilar-git-e-specs-agnosticas-ao-git (task 6.1), which minted the fourth pillar (`git`) and declared it alignless; varrer-nomes-de-comando-legados (2026-08-27) — the specs front's align was retired with its local backend, so the column reads none for two rows and each carries its own reason
maintainer: quenching
---

# Align surface — one align per local front, probe first

The shape of the plugin's alignment surface after the fold: **one align per local front**, each
carrying its front's content stages, opened by a probe that makes the no-op case free. The full
behavioral contract every align shares lives in
`plugins/quenching/assets/references/align/sweep-doctrine.md`; this standard records the
architectural rule — why the surface has this shape and not the previous one.

## The aligned-front column

| Front | Command |
| --- | --- |
| `/docs/` | `/quenching:knowledge:align` |
| `/.specs/` | **none** — see §The specs front lost its align with its backend, below |
| `/.design/` | `/quenching:design:align` |
| `.claude/` | `/quenching:components:align` |
| `git` | **none** — see §The fifth pillar has no align, below |
| all three aligned fronts | `/align` — conducts them in dependency order, on one nested OK |

There is no `align-and-update` anywhere. The previous surface was a 2×4 matrix — a structural
align plus a looping content conductor per front — which gave equal billing to conductors that
conducted almost nothing: the specs-front loop reduced to a structural align plus a sweep (its
other stages need fresh human intent per plan), and the skill-front loop converged in one pass by
construction. Each front's align now runs the content stages its front actually has, conditional
on the probe finding work; per-item stages that need fresh human intent are **reported with the
command that closes them, never driven**.

### The specs front lost its align with its backend, and the reason is structural too

The specs front's align existed while the front had a **local** tree to converge: `/.specs/` with
its phased folders, its scaffold and its stray-file sweep. `remover-backend-local-do-plugin`
retired that backend — the canonical documents live in the repository provider, GitHub Issues or
Azure Boards — and the align went with it, because there is no longer a tree of this repo's own for
a probe to find drifted. What survives is read (`/quenching:specs:status`, `cq specs doctor`) and
ranking (`/quenching:specs:triage`, on the human's own confirmation), neither of which is a
convergence sweep.

The name is deliberately not spelled out anywhere on this page. A three-segment command name is a
citation, and `citation-check.sh --half 2` reads a standard like any other file: writing the
retired name to explain that it is retired would report this page as promising a body that does not
exist. The check's own header carries the same restraint for the same reason.

**This is a different reason from the `git` pillar's, and the difference matters.** `git` never had
a tree; the specs front had one and lost it. So the column below reads **none** for both, and the
two paragraphs are not interchangeable: were a local backend to come back, so would its align.

### The fifth pillar has no align, and the reason is structural

`git` — the `cq git` axis and its seven `commands/git/**` bodies — is a **pillar**, in the sense
[glossary.md](../../glossary.md) already gives the term: an axis `cq` routes. It is not a
**front**: a front is a tree this plugin converges toward a canonical shape (`/docs/` toward
the OKF bundle, `.claude/` toward one file per entry point), and convergence is exactly what
§Probe before the inventory needs a verifier for. `git`
has no tree of its own to converge — `cq git base`, `slugs`, `stale` and `conventions` each answer
a question about the *target* repository's live state (which branch, which marking, which
branches are stale, which conventions apply), and a live answer is not a drifted artifact a probe
could find wrong. This is also why `cq git` ships no `doctor` and no `validate`: inventing one
would be filling a table for a front that does not exist, the same reasoning
[naming/command-surface.md](../naming/command-surface.md) applies to the pillar's
own place in the command taxonomy.

**A repo whose git hygiene has drifted is not this column's problem.** A stale `plan/*` branch or
an orphaned worktree is what `cq git stale` reports and `/quenching:git:cleanup` prunes — on the
human's own word, per that command's own doctrine — never something an align sweeps unattended,
because deleting a branch is exactly the kind of irreversible action the align surface otherwise
conducts only through a stage's own gate.

The two real loops survive where the looping is real: `/quenching:knowledge:align` keeps its
internal fixpoint (memory → harness → glossary feed each other), and `/align` keeps the
cross-front pass, because the three aligned fronts feed each other (the design front's standards
and the components front's registry
is a `/docs/` listing). The conductor contract — one human OK
authorizing the whole run, nesting one
level, with code-coupled confirmations still surfacing individually — lives in
`align/convergence.md`, shared by every conductor and restated by none (§The conductor
categories).

## The conductor categories

The conductor contract is shared, never owned by a single command. Conductors are told apart by
**what** they conduct, and the axis is one: fronts, stages, or specs.

| The conductor | What it conducts | The contract |
| --- | --- | --- |
| `/align` | the three local fronts (`knowledge`, `design`, `components`), in dependency order, on one nested OK | `align/convergence.md` — cited, never restated |
| `/quenching:specs:cycle` | the four stages of ONE spec — create, develop, execute, conclude — in one run, entering at the derived stage | `align/convergence.md`, plus its own gears plan (`specs-cycle/gears.md`, retired with `orchestration-gears.md` — see below) |
| `/quenching:specs:execute-queue` | N specs, serially, over one isolation — one branch, one pull request | `align/convergence.md`, plus `specs-fanout/fanout.md` |
| `/quenching:specs:develop-batch` | N specs to the `ready` gate, in real parallel | `align/convergence.md`, plus `specs-fanout/fanout.md` |

**None of the three spec conductors is an align**: they conduct no front, so none earns a row in
the aligned-front column. They conduct a lifecycle — one spec's four stages, or N specs through one of them —
invoking each stage as the command that owns it, the same conduct-never-reimplement rule that binds
`/align`. All four open on one human OK that authorizes the whole run, nest one level, and surface
code-coupled confirmations individually; the clause that once limited the contract to `/align` is
gone.

**What separates the cycle from the two fan-out entries is N, and nothing else.** The cycle derives
its run from the `complexity` on the spec's `priority` record, per the gears contract; the fan-out
entries derive **where each spec enters** from that same field, and everything about conducting more
than one — the serial-versus-parallel split, the recursion form, cross-spec block classification —
is `specs-fanout/fanout.md`'s and never a gear's.

Both contracts live in the plugin's own `assets/references/`, never in this bundle — procedure a
command needs while running inside a target is payload, not a fact about the target, so it is cited
by `${CLAUDE_PLUGIN_ROOT}` the same way from every repo. `specs-cycle/gears.md` is retired with
`orchestration-gears.md` (marchas-do-orquestrador-vivem-no-plugin, 2026-08-11).

## Probe before the inventory

**Nothing is inventoried until the front's own verifier has said there is work.** Each front
already ships a program that answers "is there work?" with an exit code — `cq knowledge validate`
(`/docs/`), `cq design doctor` (`/.design/`), `cq components doctor`/`lint` (`.claude/`) —
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
of the run itself.** Each align used to close by appending one consolidated line to `/docs/log.md`
— `converged in N passes`, `aligned workspace (N migrated, M renamed)`, `ranked N specs` — and
`/align` added a fifth for the cross-front run. All five are gone, and the rule that replaced
them holds for any sweep added later.

The entry was self-describing, and that is what made it worthless. What a pass did to `/docs/` is
legible **from `/docs/`** and from the repo's own history; a line saying a sweep ran told a reader
nothing the tree and the git log did not already say, and cost a write on every invocation —
including the no-op runs the probe rule exists to make free. A sweep whose clean case costs three
tool calls should not spend a fourth narrating that it found nothing.

It also removed the one thing every align wrote **outside its own front**. The specs front's align
and `/quenching:specs:triage` reached into the `/docs/` bundle for a log line and nothing else; with that gone,
the `specs` front writes into `/docs/` at exactly one point — a concluded spec's distillation,
which mints real knowledge rather than a record of activity. The cross-front dependency in
[§The aligned-front column](#the-aligned-front-column) records the dependency: `/docs/` still
goes first, `/.design/` consumes and adds knowledge, and the components front follows both.

The general form: **a command's own account of itself goes in its report, never into the artifact
it maintains.** A store that accumulates entries about the tools that touched it is a second
history competing with git, and the reader who needs it can read git.
