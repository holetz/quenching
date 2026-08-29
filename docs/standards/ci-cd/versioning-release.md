---
type: standard
title: Versioning and release — the Claude/Codex lockstep
description: Every published Claude and Codex version surface must agree at release time, including both marketplace entries and the generated Codex manifest
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, plugins/quenching-codex/.codex-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/quenching/common/version.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-08-15
audience: both
authority: current
source: modularizar-specs-knowledge-components spec, tasks 9.2 and 10.2 — rewritten for the one-package, one-entry-point (`cq`) architecture; the lockstep target dropped from seven artifacts to four once a single `common/version.py` constant answered for every pillar and `cq specs release` (task 10.2) was narrowed to match; the legacy-copy detector this standard used to document (`notice-installed-tool-version-drift` task 4.1) was retired the same spec, task 10.3, once the four scripts it compared against stopped existing to be compared against (moved from CLAUDE.md; plugin-first rewrite 2026-08-03, enxugar-create-e-eliminar-o-rung-hooks; bump moved to release by configurable-branch-strategy task 1.2, 2026-08-04); artifact 4's resolution sentence corrected by the cq-nao-resolve-como-comando-nu spec's branch review (2026-08-15), which found it still asserting "no fallback and no manual rung" after that branch replaced the rule with two doors onto one file and a prohibition on any third
maintainer: quenching
---

# Versioning and release — the Claude/Codex lockstep

A release bumps the Claude source and its published Codex sibling in lockstep. The rule is not bookkeeping
tidiness: two independent consumers read two different halves of the set, and a partial bump
makes each one wrong in its own way.

`cq specs release <version>` — the tool this section's *Verifying* block names — moves the source
version and regenerates the Codex manifest from it in one release operation.

## The published set

| # | Artifact | Read by |
| --- | --- | --- |
| 1 | `plugins/quenching/.claude-plugin/plugin.json` → `version` | Claude Code, to detect and apply an upgrade |
| 2 | `plugins/quenching/VERSION` | the same detection, as the pair's other half |
| 3 | `.claude-plugin/marketplace.json` → the plugin entry's `version` | the marketplace listing |
| 4 | `plugins/quenching/assets/bin/quenching/common/version.py` → `VERSION` | every pillar's own `--version` (`cq specs`, `cq knowledge`, `cq components`) |
| 5 | `plugins/quenching-codex/.codex-plugin/plugin.json` → `version` | Codex marketplace installation and upgrade detection |
| 6 | `.claude-plugin/marketplace.json` → `plugins[].version` for both `quenching` and `quenching-codex` | the marketplace entries that publish the two installable surfaces |

## Why each half matters

**Artifacts 1–2 are the Claude upgrade trigger.** The `plugin.json` `version` and the `VERSION` file are
the pair Claude Code uses to decide that an installed plugin is stale and should be replaced. Bump
one without the other and the upgrade either never fires or fires against a plugin that reports a
version it does not have.

**Artifact 4 is the *tool identity*, now held once.** Nothing installs a tool standalone any more —
every command invokes the plugin's own `cq`, bare through the `bin/` shim on `PATH` or at
`${CLAUDE_PLUGIN_ROOT}/assets/bin/cq`, with no third rung
(`plugins/quenching/assets/references/align/tool-resolution.md`
§Resolving the tool) — so a bump no longer *delivers* anything. What the one constant still does is
answer `--version` for every pillar alike. Four scripts each carrying their own copy of this
constant was never a design choice — it was the shape a self-contained, no-import single file
forced, back when each pillar shipped as its own script
([frontmatter-parser.md](../code/frontmatter-parser.md), which owns that history). One package with
internal imports has no such constraint: `common/version.py` is read by every pillar's `--version`,
not duplicated by it.

**Artifacts 5–6 publish the generated sibling.** The Codex manifest is generated from the same
source version and marketplace exposes it as a separate installable plugin. A release that bumps
only Claude leaves Codex pinned to an older generated tree; a release that edits Codex's version
independently breaks the deterministic generation contract. Regenerate first, then publish both
marketplace entries at the identical version.

## When the bump happens — once, at the release, on the primary branch

The four move **once per release, on the primary branch, as the deliberate act that publishes
it** — see [branching.md](../git/branching.md). A version bump is never a task in a
spec's `## Tasks`, `/quenching:specs:execute` never makes one, and `/quenching:specs:conclude` no longer makes one
either: a spec's own conclude merges into the primary branch with the lockstep untouched, and the
artifacts move only when the release command runs `cq specs release`.

**Why not a task, and why not conclude either.** Three things break when the bump is scheduled as
anything other than the release's own act:

- **What the release *is* is not knowable at task 1, or even at one spec's conclude.** Whether the
  change is patch, minor or major depends on everything the primary branch has accumulated since
  the last tag — which may be several specs, not just the one concluding — and the task list inside
  any one of them is routinely revised mid-build. A number chosen at the top of a branch, or at that
  branch's own conclude, is a guess nothing downstream re-checks.
- **Two specs concluding into the primary branch no longer collide.** Under the old rule both
  bumped from the same base to the same number, and the second to merge resolved a conflict in
  `plugin.json`, `marketplace.json` and the version module by hand. With the bump moved to the
  release, no conclude touches the lockstep at all — the primary branch accumulates any number of
  specs with nothing to conflict on, and the collision this section used to warn about does not
  arise.
- **A spec that is abandoned or descoped carries no version claim to unwind.** Nothing in its own
  conclude touched the lockstep, so there is nothing to revert beyond the merge itself.

**Why the release, specifically.** That is the one moment everything accumulated on the primary
branch is about to be tagged and published: the bump commit IS the published state, and the tag
points at it, contained in the primary branch. A bump committed after the tag would be the one
thing the release forbids outright, the same way a post-merge commit to the base is forbidden
everywhere else in this front.

## What a bump does not need to do any more

Resolution is **plugin-first with no third rung**, so a bump reaches every repo the moment the
plugin upgrades — nothing installs a tool standalone, and the two doors that do exist (`bin/cq` on
`PATH`, the plugin path) are the same file inside the plugin, so there is no installed copy left
running an old version for a bump to miss. Earlier plugin generations shipped as separate
scripts an align could copy into a target's `.claude/hooks/`, which meant a bump could leave a
stale, still-executing copy behind; a dedicated detector (`cq components drift`) existed for
exactly that gap. Neither the copying nor the gap exists any more — a target repository holds
nothing this plugin ships beyond the command bodies Claude Code itself loads — so the detector was
retired with the four scripts it used to compare an installed copy against
(`modularizar-specs-knowledge-components` spec, task 10.3).

## Verifying

The lockstep is checked by reading every version surface back and confirming one value.
**No checker catches any of them**, so this block is the whole enforcement:

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/cq --version
```

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
