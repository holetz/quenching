---
type: standard
title: Versioning and release — the four-artifact lockstep
description: The four source version surfaces that cq specs release bumps together, with the generated Codex sibling refreshed from the same source version
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/quenching/common/version.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-08-15
audience: both
authority: current
source: modularizar-specs-knowledge-components, one-entry-point, notice-installed-tool-version-drift, 2026-08-03, enxugar-create-e-eliminar-o-rung-hooks, configurable-branch-strategy; lineage in ADR 0004
maintainer: quenching
---

# Versioning and release — the four-artifact lockstep

<!-- rules -->

A release bumps four source version surfaces in lockstep. The rule is not bookkeeping tidiness:
Claude, the marketplace and the bundled `cq` identity read different halves of the set, and a
partial bump makes one of them wrong.

`cq specs release <version>` — the tool this section's *Verifying* block names — requires a matching
`## <version>` entry in `CHANGELOG.md`, then moves the four surfaces in one release operation.

## The published set

| # | Artifact | Read by |
| --- | --- | --- |
| 1 | `plugins/quenching/.claude-plugin/plugin.json` → `version` | Claude Code, to detect and apply an upgrade |
| 2 | `plugins/quenching/VERSION` | the same detection, as the pair's other half |
| 3 | `.claude-plugin/marketplace.json` → the plugin entry's `version` | the marketplace listing |
| 4 | `plugins/quenching/assets/bin/quenching/common/version.py` → `VERSION` | every pillar's own `--version` (`cq specs`, `cq knowledge`, `cq components`) |

## Why each half matters

<!-- rationale -->

**Artifacts 1–2 are the Claude upgrade trigger.** The `plugin.json` `version` and the `VERSION` file are
the pair Claude Code uses to decide that an installed plugin is stale and should be replaced. Bump
one without the other and the upgrade either never fires or fires against a plugin that reports a
version it does not have.

**Artifact 3 is the marketplace listing.** It must agree with the two Claude upgrade surfaces so the
published plugin advertises the version it actually contains.

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

The two generated siblings are bumped in the same operation. `cq specs release` also moves
`plugins/quenching-codex/VERSION`, `plugins/quenching-codex/.codex-plugin/plugin.json`,
`plugins/quenching-specs-reader/VERSION` and its `.claude-plugin/plugin.json`, and it rewrites the
`version` of **every** plugin entry in `.claude-plugin/marketplace.json`, never only the first. A
marketplace entry with no `version` is refused. Afterwards `cq components translate --write` and
`sync_specs_reader_plugin.py --write` regenerate the copied assets, and the translation and Codex
artifact gates prove them. `test_specs_release.py` asserts that every one of these versions is
equal. The manifests carry no hard-coded command counts, since they drift on the next command change.

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
