---
type: project
title: Repository layout
description: What sits where in this checkout — the marketplace root, the plugin payload and its asset families, the generated Codex mirror, and which command owns each surface
resource: plugins/**, scripts/**, docs/**
tags: [repository, layout, plugin, marketplace, codex]
timestamp: 2026-08-29
audience: both
authority: current
source: derived from the checkout itself on 2026-08-29 (`ls` over each directory named below); the ownership column restates each command's own declared write boundary
maintainer: quenching
---

# Repository layout

This repository is a **Claude Code plugin marketplace**, not an application. There is no build
step: command bodies and references are executable prose, and the local tools provide the local
checks. Knowing which directory owns what is therefore the difference between editing the source
of a behaviour and editing a generated copy of it.

## The root

| Path | What it is | Who writes it |
| --- | --- | --- |
| `docs/` | this OKF bundle — the knowledge tree **and** the source of this site | `/quenching:knowledge:*` |
| `plugins/quenching/` | the plugin payload that gets installed | the owning spec |
| `plugins/quenching-codex/` | **generated** mirror of the payload for Codex | `cq components translate` |
| `.claude/` | this repository's own local command surface | `/quenching:components:*` |
| `.agents/` | **generated** mirror of `.claude/` for Codex | `cq components translate` |
| `scripts/` | thin launchers CI calls | the owning spec |
| `zensical.toml` | the site layer — outside the bundle, on purpose | `/quenching:knowledge:documentation:build` |
| `CLAUDE.md`, `AGENTS.md` | harness pointers, kept thin over this bundle | `/quenching:components:harness:align` |

Two of those rows are the trap: `plugins/quenching-codex/` and `.agents/` are **regenerated
wholesale**. Editing them by hand produces a change that survives until the next translate and
then vanishes without a diff to explain it. Both carry a `.generated-from.json` naming their
source.

## Inside the plugin payload

```
plugins/quenching/
  VERSION               one of four artifacts kept in version lockstep
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
    translation/        the Codex translation rules
  tests/                the unittest suite the bundle gate runs
```

**`assets/knowledge/` is not this bundle.** It is the *skeleton* — the empty tree with its
listings — that `/quenching:knowledge:align` writes into someone else's repository. A link this
repository's own prose resolves may not exist there, which is exactly what
`citation-check.sh`'s third half measures.

## Where a change belongs

- Changing what a command *does* → its body under `commands/`, through
  `/quenching:components:command:new`.
- Changing the detail a body cites → the matching file under `assets/references/`.
- Changing a durable rule about how we build → a standard under
  [`standards/`](../standards/index.md), through `/quenching:knowledge:add`.
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
