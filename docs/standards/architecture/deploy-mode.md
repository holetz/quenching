---
type: standard
title: Deploy mode — install the surface in a target repository
description: "`cq deploy` materializes the selected quenching modules in a target's generic layer — AGENTS.md, .agents/skills and a vendored runtime — while Claude Code receives only a generated bridge under .claude; install is not alignment and never calls a model."
resource: plugins/quenching/assets/bin/quenching/deploy/**, plugins/quenching/assets/bin/cq, plugins/quenching/assets/modules.json, plugins/quenching/pyproject.toml
tags: [architecture, deploy, installation, agents, skills, bridge]
timestamp: 2026-10-30
audience: both
authority: current
source: deploy-mode implementation (2026-10-28); surface facts re-measured on Claude Code 2.1.312; drift redefined as content plus the executable bit (spec 2126, 2026-10-30)
maintainer: quenching
---

# Deploy mode — install the surface in a target repository

<!-- rules -->

## Two modes, one source

The plugin remains the first-class mode: a harness loads the published modules and every command
resolves `cq` through the host. **Deploy mode** materializes the selected surface in a target
repository so it can operate without a marketplace install. Both modes are generated from
`plugins/quenching`; neither edits a target's knowledge or code by itself.

`cq deploy` is a **top-level command**, not a front. `delivery` and `ops` keep their own meaning
for deployment; this verb installs the tool surface. It never invokes a model, never aligns
`/docs/`, never chooses a provider and never runs a target pipeline.

## The target layout

| Path | Kind | Owner |
| --- | --- | --- |
| `AGENTS.md` | instructions | target; seeded only when absent |
| `.agents/quenching.json` | configuration | target; seeded only when absent |
| `.agents/skills/quenching-<command>/SKILL.md` | one-segment skills | generated |
| `.agents/quenching/` | vendored payload: runtime, references, templates, commands, agent protocols | generated, read-only |
| `.agents/.quenching-deploy.json` | manifest: version, modules, profiles, hashes, skills | generated |
| `.claude/skills/<name>/` | Claude bridge, byte copy of every skill | generated |
| `.claude/agents/quenching-<name>.md` | Claude subagents | generated when the `claude` harness is selected |
| `.opencode/agents/quenching-<name>.md` | OpenCode subagents, `mode: subagent` | generated when the `opencode` harness is selected |
| `CLAUDE.md` | legacy pointer to `AGENTS.md` | never created; removed only by `--prune-legacy` |
| `.claude/commands/`, `.claude/references/` | legacy layout | refused; run `cq components migrate` first |

`AGENTS.md` is read natively by Claude Code 2.1.277+ when no `CLAUDE.md`/`CLAUDE.local.md` exists
in the working directory or above it ([surface-translation.md](surface-translation.md)). Claude
does **not** read `.agents/skills/`; the generated `.claude/skills/` bridge is the only reason it
is present. A repository therefore never authors `.claude` for quenching.

## Selection and the manifest

`--modules` selects principal modules, not fronts. `core` means `quenching-specs` plus
`quenching-align` (specs, git, knowledge and components); `specs` is always included because it
owns the one `cq`. `--profiles` overrides the `shared.profiles.installed` seed; otherwise the
fronts of the selected modules are derived. `specs` is kept in that list as the provider axis.

A target that already carries a manifest reuses its recorded `modules`, `harnesses`, `runtime` and
`profiles` for every flag the caller omits, so `cq deploy --write` upgrades what is installed
instead of reinstall `core`. An explicit flag always wins; the manifest is a default, not an
authority over the plan.

The manifest is the authority for what deploy owns. A generated file must be listed before it may
be overwritten; a file at a generated path that the manifest does not own is a conflict
(`ct-deploy-unowned`, exit 2) and nothing is written. Generated files may be edited by hand only
as drift: `--check` reports it and `--write` regenerates them. Drift is content and the executable
bit — the only part of the mode git carries — so a checkout that creates files group-writable
(`umask 0002`) is clean. A target's own skills, references, `AGENTS.md` and configuration are never
in the manifest's write set.

## Runtime

`--runtime vendor` copies the selected Python packages and the launcher into
`.agents/quenching/assets/bin/`; it is offline and self-contained. `--runtime uvx` omits the
packages and writes `.agents/quenching/bin/cq` as a shim pinned to the release tag, so the target
needs network and `uvx` at call time.

Every deployed command body uses the target-local path `.agents/quenching/bin/cq`; the generated
grant is `Bash(.agents/quenching/bin/cq:*)`. The plugin's bare-`cq` rule remains the rule for a
plugin installation, not for a deployed target.

## What deploy does not do

- It does not install `/docs/` or call an align; the target runs its own
  `quenching-knowledge-align` skill after the surface exists. `AGENTS.md` names that next step when the bundle is absent.
- It does not install hooks or rewrite `.claude/settings*.json`.
- It does not choose the specs backend, license, release provider or any product policy.
- It does not merge a content-bearing `CLAUDE.md`; the target's
  `quenching-components-harness-align` skill owns that, and a pointer-only file is removed only on
  `--prune-legacy`.

## Verify

```bash
cq deploy --target . --modules core --check --json   # 0 clean, 1 drift, 2 refusal
python3 .agents/quenching/bin/cq --version
python3 .agents/quenching/bin/cq components status --json
python3 .agents/quenching/bin/cq components bridge --target . --check --json
```

The target's `components` surface excludes the skills listed in the deploy manifest and reports
them as `generated`; only the target's own skills are audited.
