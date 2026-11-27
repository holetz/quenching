---
type: decision
title: The codex harness returns, and .agents/skills is always the source
description: Why cq deploy declares every harness by default with codex among them, writes each generated skill in .agents/skills whatever the harnesses and projects it into .claude/skills for claude, and the parts of ADR 0020 and of the 7.18.0 publication rule this supersedes
resource: quenching/assets/bin/quenching/deploy/tree.py, quenching/assets/bin/quenching/deploy/cli.py, quenching/assets/bin/quenching/deploy/mcpfiles.py, quenching/assets/bin/quenching/components/commands/bridge.py, docs/standards/architecture/deploy-mode.md
tags: [decision, architecture, deploy, codex, skills, bridge]
timestamp: 2026-11-27
audience: both
authority: current
source: spec 656
maintainer: quenching
---

# 0022 — The codex harness returns, and `.agents/skills` is always the source

## Context

- Since 7.18.0 `cq deploy` published each generated skill into one directory, the minimal cover of
  the declared harnesses: `.claude/skills` alone for a target with `claude`, `.agents/skills`
  otherwise. In a `claude` target the generated skills existed only in the Claude projection, while
  the target's own skills were authored in `.agents/skills` and reached `.claude/skills` through the
  bridge. Two rules governed the same thing.
- [ADR 0020](0020-remove-the-codex-executor-and-harness.md) removed the `codex` harness with the
  Codex executor. Codex 0.165.0 reads only `.agents/skills` (probe of 2026-11-25 in
  [deploy-mode.md](../standards/architecture/deploy-mode.md) §Verified facts), so a `claude` target
  served it nothing.
- The human request of 2026-11-27 fixed the direction: every harness by default, `codex` among
  them, and `.agents/` as the source whatever the harness.

## Decision

- `--harness` takes `claude`, `codex` and `opencode`; omitted, with no manifest to reuse, it
  declares all three. A manifest's recorded harnesses still win over the default, and a recorded
  `codex` is kept rather than dropped.
- The `codex` harness is the skills in `.agents/skills` and the `[mcp_servers.quenching]` table in
  `.codex/config.toml`, merged into the user's file. It gets no subagent file and no hooks.
- Every generated skill is written in `.agents/skills`. With `claude` declared, the deploy projects
  it into `.claude/skills` by the bridge's rule: the same bytes plus the marker line. Both copies
  cite the skill's files at `.agents/skills/<name>/`.
- The deploy owns both copies, mirrored skills of a module outside the selection included; the
  bridge keeps owning only the target's own skills.

## Consequences

- A 7.18.x `claude` target gains the `.agents/skills` source of its generated skills on the next
  `cq deploy --write`, reported as `create` by `--check` first.
- OpenCode reads both copies and keeps the `.agents` one; VS Code + Copilot Chat deduplicates by
  name. No client lists a generated skill twice.
- The Codex executor stays removed: this decision restores only the harness.
- A script that relied on `--harness codex` being refused now deploys the Codex registration.
