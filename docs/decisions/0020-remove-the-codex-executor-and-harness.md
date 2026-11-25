---
type: decision
title: The Codex executor and the codex harness are removed
description: Why the Codex executor, its quota probe and git guard, the shared.codex configuration and the codex deploy harness were removed, what a target that still carries them sees for one version, and the part of ADR 0014 this supersedes
resource: quenching/assets/bin/quenching/deploy/cli.py, quenching/assets/bin/quenching/deploy/mcpfiles.py, quenching/assets/bin/quenching/config/effective.py, quenching/skills/quenching-specs/references/execute.md, docs/standards/architecture/deploy-mode.md
tags: [decision, architecture, codex, deploy, cleanup]
timestamp: 2026-11-23
audience: both
authority: current
source: spec 287 (epic 288)
maintainer: quenching
---

# 0020 - The Codex executor and the codex harness are removed

[ADR 0014](0014-tier-pequeno-em-tarefa-testavel.md) admitted `gpt-6-luna` as a small-tier executor
beside `haiku`, and the Codex pillar (`cq codex probe | eligible | implement`) let Codex write one
eligible task per `execute` step. This records why both left. It supersedes the part of 0014 that
admits `gpt-6-luna`; the `haiku` rung stands.

## Context

- The project no longer runs Codex. The executor had been off by default since the change that made
  `shared.codex.executor.enabled` an opt-in, and it lost its cross review before this decision.
- The pillar was the code with the most defects in the history: more than thirty archived specs
  about its git guard, probe, eligibility and the retire of its `.quenching/codex/` state. Every one
  of them was cost for a path nobody took.
- About 150 files cited it: a package of five modules, its tests and fixture, configuration keys, the
  worktree and slot handling of `.quenching/codex/`, a delegation section in `execute`, the
  `CODEX:` line of the runner and its check in the verifier, and the `codex` deploy harness that
  wrote `.codex/config.toml`.

## Decision

- The `codex` package, its tests and fixtures, its router entry and MCP catalog rows are deleted.
- `cq deploy` takes `claude` and `opencode` as harnesses; an explicit `--harness codex` is refused
  (`ct-deploy-harness`). A manifest an earlier version wrote that still lists `codex` is read
  without the harness, and the `quenching` entry an earlier deploy wrote into `.codex/config.toml`
  is taken out on the next write, leaving every other entry of the user's file.
- The generic surface (`.agents/` and `AGENTS.md`) stays: OpenCode reads it.
- A `shared.codex` block in a target's configuration is accepted and named in the warnings as
  obsolete for one version; it is never seeded and nothing reads it. A later release removes the
  tolerance.
- `execute` has no consultation step and no `Codex:` line; the runner returns no `CODEX:` line and
  the verifier has no check 11.
- `codex-pillar.md` is deleted; the history keeps it.
- Worktree and slot handling of `.quenching/codex/` is removed. A slot that still holds that
  directory now counts it as ignored content: `retire` asks for `--discard-ignored`, and `release`
  keeps the slot held until the directory is cleared.

## Consequences

- A script or CI job that passes `--harness codex` fails and must drop it; the release notes say so.
- `.codex-plugin/` patterns in the git audit stay: they cover manifests a target may still carry.
- Cost provenance still names native Codex usage as not measured: that is a reading of a transcript,
  not the executor.
