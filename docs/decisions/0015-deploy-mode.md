---
type: decision
title: Deploy mode — a vendored surface in the target generic layer
description: "Why quenching gained a deterministic deploy command instead of a second harness plugin: the target keeps AGENTS.md and .agents as its editable source, the payload is vendored or pinned by uvx, and Claude receives only a generated bridge because it does not discover .agents/skills."
resource: plugins/quenching/assets/bin/quenching/deploy/**, docs/standards/architecture/deploy-mode.md
tags: [decision, deploy, agents, skills, installation]
timestamp: 2026-10-28
audience: both
authority: current
source: deploy-mode implementation (2026-10-28)
maintainer: quenching
---

# 0015 — Deploy mode: a vendored surface in the target generic layer

<!-- rules -->

## Context

quenching was usable only as a harness plugin. A target that wanted the method had to install the
marketplace modules, and a target whose harness did not load them had no surface at all. The
target layer already standardized on `.agents/` and `AGENTS.md`, and Claude Code 2.1.277+ reads
`AGENTS.md` directly when no `CLAUDE.md` exists. Claude Code still does not discover
`.agents/skills/`, so a Claude bridge remains necessary.

The options considered were:

1. **npx wrapper** — a Node package that downloads and runs the Python tool. It adds a second
   ecosystem, a second release surface and a Node prerequisite for a Python, stdlib-only tool.
2. **uvx-only, no vendoring** — small target payload, but every target command needs network and
   `uvx`, and the target is not operable offline.
3. **Full vendoring in `.agents/quenching/`** — larger target payload, but deterministic, offline
   and independent of the harness; the manifest makes upgrades and conflicts explicit.
4. **One router skill** — lower context cost, but it loses per-command routing and the existing
   deterministic command bodies.

## Decision

`cq deploy` is a top-level command, not a front. It materializes selected modules in
`.agents/`, vendors the payload by default (`--runtime vendor`), and offers `--runtime uvx` for a
pinned shim. It generates one skill per selected command, the Claude bridge, Claude agent
definitions and OpenCode subagents when their harness is selected. It never invokes a model and
never aligns content.

`uvx` is the official distribution channel: the plugin already publishes a wheel with the `cq`
entry point, and the package is stdlib-only. `npx` remains a possible thin wrapper, never a second
source.

`AGENTS.md` is seeded, not managed; `CLAUDE.md` is never created and a pointer-only file is
removed only on request. `.claude/skills/` and `.claude/agents/` are generated and versioned, so a
clone works without a per-user setup step.

## Consequences

- A target gains a generated, read-only `.agents/quenching/` that must be upgraded with
  `cq deploy --write` from a new release; editing it is drift.
- The manifest is the only ownership proof; an unowned file at a generated path refuses the write
  rather than being overwritten.
- The target's own `.agents/skills/` remain editable and are bridged alongside the generated ones;
  `components` audits only those, reporting generated skills separately.
- The target's `.claude/` is generated surface, not an authoring layer. A host before Claude Code
  2.1.277 can still be served by the legacy `CLAUDE.md` pointer, but that is not the conformant
  layout.
- The vendored payload adds roughly 3–4 MB to a target; `--runtime uvx` trades that size for a
  network/uvx dependency.

## Alternatives rejected

A single router skill was rejected for the first release because it loses the existing
per-command descriptions and the deterministic body translation. The npx-first channel was
rejected because it duplicates the release surface and adds an unnecessary runtime. A uvx-only
default was rejected because the target should remain operable after the initial install; it is
kept as an explicit option.
