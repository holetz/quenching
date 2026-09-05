---
type: how-to
title: Adopt quenching in a repository
description: Exercise the full convergence workflow on a disposable repository copy — probe, one plan, one OK per front — while preserving the target's existing files.
resource: plugins/quenching/README.md
tags:
  - how-to
  - align
timestamp: 2026-08-28
audience: human
authority: current
source: plugins/quenching/README.md §The seven fronts, the non-converging axes, and the one align per front; command bodies under plugins/quenching/commands/{knowledge,design,components,ops,proof,toolchain,delivery}/ and align.md
maintainer: Israel Holetz
---

# Exercise quenching in a repository

*Audience: implementer · One OK per front · Use a disposable copy while studying the workflow*

This page describes the adoption-shaped workflow as a study. It is not evidence that the plugin is
production-ready or that its declared read-only views provide process isolation. Copy the target
first if you are learning the method or testing a change.

## Install the plugin

For a bounded study target, install the published plugin from its marketplace inside Claude Code:

```text
/plugin marketplace add holetz/claude-quenching
/plugin install quenching@quenching
```

Run `/reload-plugins` if the session was already open. The direct checkout form is reserved for
plugin development and testing:

```bash
claude --plugin-dir ./plugins/quenching
```

Do not use `--plugin-dir` as the normal installation or upgrade path; the marketplace installation
lets Claude Code manage the published copy.

## Uninstall or reverse

To stop using the plugin but keep the marketplace configured, run:

```text
/plugin uninstall quenching@quenching
/reload-plugins
```

Uninstalling the plugin does not remove the target repository's `/docs/`, `.claude/` or
`.claude/quenching.json`; those files belong to the repository. If you need to undo an alignment,
review the target's commits and use its normal Git revert workflow. Removing the plugin is not a
rollback of data it already wrote. For an upgrade regression, disable or uninstall the plugin,
then reinstall the previously published version (or use a known checkout with `--plugin-dir` for
development-only recovery) and reload the session.

You have a real repository — a README that grew sideways, notes in three places, a `.claude/`
folder of one-off commands — and you want it on the canonical shape without losing anything it
already has. That is exactly what the aligns are for: **convergence over accommodation**, but
never convergence over your objection.

Every align runs the same loop:

```mermaid
flowchart LR
    A([probe]) -->|clean| Z([stop — a couple of tool calls])
    A -->|findings| B[read-only inventory]
    B --> C[ONE consolidated plan]
    C -->|your OK| D[apply]
    C -. declined .-> Z2([nothing written])
    D --> E[verify with the front's validator]
```

## Decide: one front, or the aligned set

| You want | Run | It converges |
| --- | --- | --- |
| Just the knowledge base | `/quenching:knowledge:align` | `/docs/` into the OKF bundle, pulling in out-of-band content |
| Just the automation surface | `/quenching:components:align` | `.claude/` onto one file per entry point, bodies audited |
| Just the design source | `/quenching:design:align` | `/.design/` source, projections, and genres |
| Just the operations surface | `/quenching:ops:align` | the declared root, router, registry and bounded structural drift |
| Just the verification surface | `/quenching:proof:align` | the declared test gate, fixtures, layers and bounded structural drift |
| Just the toolchain surface | `/quenching:toolchain:align` | manifests, locks, pins and tool configuration |
| Just the delivery surface | `/quenching:delivery:align` | workflows, reachability, provenance and release shape |
| The whole repository | `/quenching:align` | all seven local aligned fronts, dependency order, one nested OK |

!!! tip "Recommendation"
    Default to `/quenching:align` for the study target. The fronts feed each other — a spec's
    distillation is glossary work for the knowledge front; the design front's standards feed its
    projections; the automation front's registry is a listing the knowledge front indexes; the
    operations registry feeds the proof front's entry-point check; and proof resources can feed
    documentation listings. The conductor loops across these edges until nothing changes anywhere.
    Authorization nests one level: each front align inherits your OK and never re-asks, while a
    code-coupled rename and an irreversible close still gate on their own.

## Run it

1. Start from a **clean working tree** — the plan you are about to approve should be the only
   diff you end up reviewing.
2. Type `/quenching:align`. The probe runs each applicable front's own verifier first
   (`cq knowledge validate`, `cq design doctor`, `cq components doctor`/`lint`, `cq ops doctor`,
   `cq proof doctor`, `cq toolchain doctor`, `cq delivery doctor`); a clean front stops without ceremony. `ops` and `proof` are applicable
   when `.claude/quenching.json` declares `ops.opsRoot` or `proof.proofRoot`, or when their fixed conventional-root
   probes find an entry point or test module. Otherwise the report says *not applicable* and
   offers the declaration path without inventing a plan.
3. Read the ONE plan per drifted front. It names every move: which stray docs fold into which
   `/docs/` home, which `.claude/` files collapse onto one entry point, what
   `CLAUDE.md` keeps versus what moves into the bundle.
4. Give (or decline) the OK. Anything whose blast radius reaches **product code** confirms on
   its own even inside the conducted run — one blanket OK never covers a code-coupled rename.

## What the operations and proof fronts add

The operations front reads `ops.opsRoot` and `ops.router` from `.claude/quenching.json`, then probes before
it inventories. It may regenerate a stale registry and make bounded structural repairs; it never
arms a write-capable entry point, chooses an undeclared router, or drives judgement findings.
`/quenching:ops:status` is the read-only report, and `/quenching:ops:entrypoint:new` is the gated
minting path for one new Python entry point.

The proof front follows the same probe-first boundary over `proof.proofRoot`. It can make bounded gate
and fixture repairs, but it does not invent layers, choose the measured surface, install CI, run
the target suite, or raise a deferred floor. `/quenching:proof:status` reports those facts without
writing, while `/quenching:proof:layer:new` creates one named layer only after its own confirmation
and separately confirms any test migration.

When an applicable root exists without a declaration, treat that as adoption work: declare the
root and router in the target repository, then run the owning front align. A present but clean
front is **conformant**; a front excluded by scope or blocked by an earlier hard failure is
**skipped**; absence of both a declaration and a conventional signal is **not applicable**.

## What the knowledge front does beyond structure

The `docs` front is the one align with a real internal loop. After the structural pass it
offers, each on its own evidence: draining the project's Claude Code memory into the bundle,
thinning `CLAUDE.md` into a thin pointer over `/docs/`, and backfilling the glossary —
looping to a fixpoint until a pass changes nothing.

??? note "What 'converged' looks like on disk"
    The same tree in every adopted repository (a repo without data simply gets no `catalog/`):
    a root `/docs/index.md` with `okf_version: "0.1"`, a fixed `glossary.md`, and the
    homes `standards/`, `concepts/`, `external/`, `documentation/`, `vision/`, `catalog/`.
    The full anatomy is in [The OKF bundle](../explanation/okf-bundle.md).

## Verify

```bash
cq knowledge validate docs     # 0 error(s) is the gate
cq components doctor --json          # "ok": true
cq components lint --json            # zero error findings
cq --root . ops doctor --json        # exit 0 is a clean operations front
cq --root . proof doctor --json      # exit 0 is a clean proof front
```

Re-running an align after a green verify is cheap by design: the probe finds nothing and stops.

**Next:** with the shape in place, put real work through it —
[drive a spec from idea to merge](drive-a-spec.md).
