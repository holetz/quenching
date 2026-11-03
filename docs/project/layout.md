---
type: project
title: Repository layout
description: What sits where in this checkout — the editable source cq deploy installs, its asset families, the plugins that install into no repository, and which command owns each surface
resource: plugins/**, scripts/**, docs/**
tags: [repository, layout, plugin, deploy]
timestamp: 2026-11-03
audience: both
authority: current
source: derived from the checkout itself on 2026-08-29 (`ls` over each directory named below); the ownership column restates each command's own declared write boundary; spec 2160
maintainer: quenching
---

# Repository layout

This repository is the **source of quenching**, which `cq deploy` installs into target
repositories ([ADR 0017](../decisions/0017-install-only-by-deploy.md)); it is not an application.
There is no build step: command bodies and references are executable prose, and the local tools provide the local
checks. Knowing which directory owns what is therefore the difference between editing the source
of a behaviour and editing a generated copy of it.

## The root

| Path | What it is | Who writes it |
| --- | --- | --- |
| `docs/` | this OKF bundle — the knowledge tree **and** the source of this site | `/quenching-align:knowledge:*` |
| `plugins/quenching/` | the single editable source `cq deploy` installs | the owning spec |
| `plugins/omnigent/quenching/` | **generated** Omnigent operator agent, no payload | `scripts/sync_omnigent_plugin.py` |
| `plugins/opencode/quenching-vitrine/` | **hand-written** OpenCode Desktop GUI plugin (Specs panel); built with npm, `dist/` committed | the owning spec |
| `plugins/claude/quenching-hud/` | band above the prompt (active spec, stage, task progress; read with `cq specs status --no-fetch`: local ref only, no fetch, no network); **hand-written**, validated by the gate with `claude plugin validate` | the owning spec |
| `.agents/skills/`, `.agents/quenching/`, `.claude/skills/` | this repository's own deployed surface, generated from `plugins/quenching/` | `cq deploy --target . --write` |
| `.claude/` | this repository's own local command surface | `/quenching-align:components:*` |
| `scripts/` | thin launchers CI calls | the owning spec |
| `zensical.toml` | the site layer — outside the bundle, on purpose | `/quenching-align:knowledge:documentation:build` |
| `AGENTS.md` (legacy `CLAUDE.md`) | the harness pointer, kept thin over this bundle | `/quenching-align:components:harness:align` |

Every generated tree is the trap: it is **regenerated wholesale**, so editing it by hand produces a
change that survives until the next sync and then vanishes without a diff to explain it. That holds
for `plugins/omnigent/quenching/` and for this repository's own deployed surface. The first level
under `plugins/` is the source or a harness, the second the name that harness registers
([plugin-layout.md](../standards/architecture/plugin-layout.md) §One tree per harness).
`plugins/claude/quenching-hud/` and `plugins/opencode/quenching-vitrine/` are the hand-written trees
under a harness: edit the vitrine's `src/` and rebuild `dist/`, never a generated copy. The Claude
module plugins, the specs reader, the Codex plugin and the OpenCode user-level distribution were
retired on 2026-11-03 with their generators.

## Inside the plugin payload

```
plugins/quenching/
  VERSION               one of the artifacts kept in version lockstep
  commands/             one file per entry point — the executable prose
  assets/
    bin/                the `cq` CLI (`quenching.knowledge`, `.specs`, `.components`, `.ops`, `.proof`, `.git`)
    references/         the detail a command body cites instead of restating
    knowledge/          the OKF skeleton `knowledge:align` installs into a target repo
    checks/             the shipped verifiers, plus their fixtures
    zensical/           the site-layer payload: config template, CSS, CI workflows
    templates/          moulds a command fills in
    specs/              spec-backend payloads
    evals/              command evaluation suites
    translation/        per-file translation rules `cq components migrate` uses
  tests/                the unittest suite the bundle gate runs
```

**`assets/knowledge/` is not this bundle.** It is the *skeleton* — the empty tree with its
listings — that `/quenching-align:knowledge:align` writes into someone else's repository. A link this
repository's own prose resolves may not exist there, which is exactly what
`citation-check.sh`'s third half measures.

## Where a change belongs

- Changing what a command *does* → its body under `commands/`, through
  `/quenching-align:components:command:new`.
- Changing the detail a body cites → the matching file under `assets/references/`.
- Changing a durable rule about how we build → a standard under
  [`standards/`](../standards/index.md), through `/quenching-align:knowledge:add`.
- Changing what a new target repo receives → `assets/knowledge/`, and never only there: the
  bundle in `docs/` and the skeleton must describe the same shape.

## The gate

From `plugins/quenching/`, zero errors is the bundle gate; `stale-doc` is advisory.

```bash
cat VERSION
python3 assets/bin/cq --version
python3 assets/bin/cq knowledge validate ../../docs
python3 assets/bin/cq --root . components doctor --json
python3 assets/bin/cq --root . components lint --json
python3 -m unittest discover -s tests
```

Surface-load checks live in `assets/checks/functional-checks.sh`; **exit 2 is inconclusive, not
green**.
