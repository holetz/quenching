---
type: decision
title: quenching reaches a repository only through cq deploy; the plugin distributions are retired
description: Why the eight Claude module plugins, the read-only specs reader, the Codex plugin and the OpenCode user-level distribution were removed, and which plugins stay because they install into no repository
resource: quenching/assets/modules.json, quenching/assets/bin/quenching/common/modules.py, quenching/assets/bin/quenching/specs/release.py, quenching/assets/checks/functional-checks.sh, .claude-plugin/marketplace.json
tags: [decision, architecture, plugin, deploy, distribution]
timestamp: 2026-11-03
audience: both
authority: current
source: spec 2160
maintainer: quenching
---

# 0017 — quenching reaches a repository only through `cq deploy`

> Superseded in part by [ADR 0018](0018-retire-omnigent-and-source-manifest.md): the Omnigent operator
> agent, the source `plugin.json`, the source `bin/cq` and `cq components translate` were later removed.

The rules live in [source-layout](../standards/architecture/source-layout.md),
[deploy-mode](../standards/architecture/deploy-mode.md) and
[versioning-release](../standards/ci-cd/versioning-release.md); this records why they changed. It
supersedes [ADR 0013](0013-plugin-module-split.md), which split the published plugin into eight
generated modules.

## Context

Two delivery models ran side by side. [ADR 0015](0015-deploy-mode.md) made `cq deploy` install the
surface into a target repository's generic layer (`.agents/`, `AGENTS.md`, a generated Claude
bridge, OpenCode agents). Beside it the repository still generated and published:

- eight Claude module plugins plus `quenching-specs-reader`, listed in `.claude-plugin/marketplace.json`;
- the Codex plugin `quenching-codex`, listed in `.agents/plugins/marketplace.json`;
- the OpenCode distribution copied by hand into `~/.opencode/`.

Each had a generator, a `--check` in the gate, version artifacts in the release lockstep, a Codex
upgrade check against the 6.4.0 baseline, and an install section in the manual. None of them
delivered anything a deployed target did not already receive, and a stale plugin install competes
with the deployed copy for the same command names.

## Decision

The product is served only by installation into the target repository. The human owner decided it
on 2026-11-03; the specs reader goes with it because a deployed target already carries the read
verbs.

- Removed: the module plugin trees under `plugins/claude/` (except the HUD), `plugins/codex/`,
  `plugins/opencode/quenching-opencode/`, `.agents/plugins/marketplace.json`, and the scripts
  `generate_plugin_modules.py`, `sync_codex_plugin.py`, `sync_opencode_plugin.py`,
  `sync_specs_reader_plugin.py`, `validate_codex_plugin.py` and `check_codex_upgrade.py`.
- `assets/modules.json` (schema 2) is the deploy manifest: the modules `cq deploy --modules`
  selects, plus a `plugins` list of what is not installed into a repository.
- Stay as plugins, because they install into no repository: `plugins/claude/quenching-hud` (the only
  entry of the Claude marketplace and the only plugin in the version lockstep),
  `plugins/opencode/quenching-vitrine` (hand-written, installed by OpenCode configuration) and
  `plugins/omnigent/quenching` (the hosted operator agent, still generated).
- The surface-load checks deploy this checkout into throwaway targets instead of loading
  `--plugin-dir` trees, so they measure exactly what a deploy installs.
- `cq components translate`, which packaged the Codex plugin, is removed; the per-file translation
  `cq components migrate` uses to recognise legacy copies stays.

## Consequences

- A target that installed the plugins keeps a frozen version until it runs `cq deploy`. The release
  that ships this is a major one and its changelog entry says so.
- The source keeps its path, `quenching/`: the Omnigent bundle pins its MCP server with
  `#subdirectory=plugins/quenching` on published tags, and the command ids keep their
  `/quenching-<module>:<front>:<verb>` spelling in the source, which `cq deploy` translates to
  `quenching-<front>-<verb>`.
- The release lockstep moves `quenching/VERSION`, the source `plugin.json`, the HUD
  `plugin.json`, the Claude marketplace and `common/version.py`; regeneration runs only the Omnigent
  generator and the repository's own deploy.
