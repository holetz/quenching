---
type: decision
title: The Omnigent operator agent, the source plugin manifest, the source launcher and cq components translate are retired
description: Why the plugin-model remnants left after ADR 0017 were removed — the generated Omnigent bundle, the source plugin.json, the duplicate bin/cq of the source and the cq components translate verb — and what identifies the source instead
resource: quenching/assets/bin/cq, quenching/assets/bin/quenching/components/surface.py, quenching/assets/bin/quenching/deploy/tree.py, quenching/assets/bin/quenching/common/modules.py, quenching/assets/bin/quenching/components/commands/migrate.py
tags: [decision, architecture, plugin, deploy, cleanup]
timestamp: 2026-11-03
audience: both
authority: current
source: spec 2168 (epic 2167)
maintainer: quenching
---

# 0018 — The plugin-model remnants are retired

[ADR 0017](0017-install-only-by-deploy.md) made `cq deploy` the only way the product reaches a
repository, but kept four things that belonged to the plugin model. This records why they went. It
supersedes the part of 0017 that kept the Omnigent operator agent as a plugin that stays.

## Context

- `plugins/omnigent/quenching/` was a generated bundle (one operator agent, no payload) with its own
  generator, a `--check` in the gate, an eval profile, a model-compatibility table and a release
  regeneration step. It installed into no repository and pinned its MCP server to a published tag.
- The source's `.claude-plugin/plugin.json` was the manifest of a plugin that is no longer
  published. Code still used it as the identity of the source (`package_root`, `plugin_prefix`) and
  as a lockstep artifact.
- The source's `bin/cq` and `bin/cq.cmd` existed only for the `PATH` entry Claude Code builds
  for an enabled plugin. The real entry point is `assets/bin/cq`, which the wheel, the release tool,
  the evals and the vitrine already call.
- `cq components translate` packaged the Codex plugin; ADR 0017 removed its purpose but kept it so
  `cq components migrate` could recognise the copies it had written.

## Decision

- The Omnigent bundle, its generator, its eval profile, its model table and its release step are
  removed. Nothing in the product runs on Omnigent.
- **No code identifies the source by a harness manifest.** A root is the source of quenching when it
  carries `VERSION` and `assets/modules.json`. The source `plugin.json` is deleted and leaves the
  version lockstep, which is now `VERSION`, `common/version.py`, the HUD `plugin.json` and the
  marketplace catalog.
- The source ships one launcher, `assets/bin/cq`. `cq deploy` **generates** the target's
  `.agents/quenching/bin/cq` and `bin/cq.cmd` in the vendor runtime, as it already does for `uvx`;
  the target path does not change.
- `cq components translate` and its adaptation map are removed. `cq components migrate` no longer
  recognises what the old verb generated: such a copy is a second editable copy, reported as a
  conflict for the human, never overwritten. Rewriting `migrate` for skills is a separate spec.
- `quenching@claude-quenching` leaves `enabledPlugins` in this repository's `.claude/settings.json`.

## Consequences

- A release no longer regenerates anything but the repository's own deployed surface.
- The source keeps its path, `quenching/`; the published-tag subdirectory pin that justified
  it in 0017 no longer applies.
- The wheel and `uvx` keep working: they enter through `quenching_launch.py` and `assets/bin/cq`.
