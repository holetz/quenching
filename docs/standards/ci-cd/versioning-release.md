---
type: standard
title: Versioning and release — the version lockstep
description: The version surfaces cq specs release bumps together — the source VERSION, the HUD plugin manifest, every Claude marketplace entry and the bundled cq identity — and the copies it regenerates before the release commit
resource: plugins/quenching/assets/modules.json, plugins/quenching/VERSION, plugins/claude/quenching-hud/**, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/quenching/common/version.py, plugins/quenching/assets/bin/quenching/common/modules.py, plugins/quenching/assets/bin/quenching/specs/release.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-11-03
audience: both
authority: current
source: modularizar-specs-knowledge-components, one-entry-point, notice-installed-tool-version-drift, 2026-08-03, enxugar-create-e-eliminar-o-rung-hooks, configurable-branch-strategy, spec 1634, spec 1635 (module extraction); Codex marketplace upgrade regression, 2026-10-22; spec 2125 (release redeploys the surface); spec 2160 (install only by deploy); spec 2168; lineage in ADR 0004, 0013, 0017
maintainer: quenching
---

# Versioning and release — the version lockstep

<!-- rules -->

A release bumps the version surfaces in lockstep. The rule is not bookkeeping tidiness:
Claude Code, the marketplace, `cq deploy` and the bundled `cq` identity read different halves of
the set, and a partial bump makes one of them wrong.

`cq specs release <version>` — the tool this section's *Verifying* block names — requires a matching
`## <version>` entry in `CHANGELOG.md`, then moves every surface in one release operation.

The release commit is self-contained: the verb refuses (exit 2, nothing written) when the tree
has changes beyond `CHANGELOG.md`, bumps, **regenerates the copy** — only
where `.agents/.quenching-deploy.json` exists, the bundled
`plugins/quenching/assets/bin/cq deploy --target . --write`, so the gate's deployed surface lockstep
holds at the new version — and commits everything with the `CHANGELOG.md` entry, so
`verify_repo.sh` is already green on the tag. A failed regeneration leaves the bump uncommitted and
makes no commit or tag. The `/release` command runs `QUENCHING_FUNCTIONAL=1 bash scripts/verify_repo.sh`
before the bump, so the surface-load checks are measured, not skipped.

## The version set

`plugins/quenching/assets/modules.json` is the declarative source, and `release_artifacts` in
`common/modules.py` derives the set from it:

| # | Artifact | Read by |
| --- | --- | --- |
| 1 | `plugins/quenching/VERSION` (the unpublished source; it carries no `plugin.json`) | `cq deploy`, which records the version in a target's `.agents/.quenching-deploy.json` |
| 2 | `.claude-plugin/plugin.json` of every entry of `plugins` with `marketplace: true` — today only `plugins/claude/quenching-hud` | Claude Code, to detect and apply the HUD upgrade |
| 3 | `.claude-plugin/marketplace.json` → **every** entry's `version` | the marketplace listing |
| 4 | `plugins/quenching/assets/bin/quenching/common/version.py` → `VERSION` | every pillar's own `--version` (`cq specs`, `cq knowledge`, `cq components`) |

Adding a marketplace plugin to `plugins` changes the derived set without editing the release code.
`cq specs release` loads the **target repository's** manifest; `RELEASE_ARTIFACTS` in `release.py`
is a derived export of the bundled manifest for existing callers, not a separately maintained list.
Artifact presence, the changelog entry, marketplace membership and existing version agreement must
all pass before any version moves.

## Why each half matters

<!-- rationale -->

**Artifact 1 is what a deploy installs.** A target receives the source's version with its payload
and moves only when `cq deploy --write` runs from the new release; a release that skipped the
source would redeploy the old number.

**Artifacts 2–3 are the HUD's upgrade route.** The HUD is the one plugin Claude Code still
installs from the marketplace, so its `plugin.json` and the listing must agree with each other and
with the release, or the upgrade either never fires or fires against a plugin that reports a
version it does not have.

**Artifact 4 is the *tool identity*, held once.** Every command invokes the deployed `cq` at
`.agents/quenching/bin/cq` ([deploy-mode.md](../architecture/deploy-mode.md);
`plugins/quenching/assets/references/align/tool-resolution.md` §Resolving the tool), so a bump
*delivers* nothing by itself. What the one constant still does is answer `--version` for every
pillar alike. Four scripts each carrying their own copy of this constant was never a design
choice — it was the shape a self-contained, no-import single file forced, back when each pillar
shipped as its own script ([frontmatter-parser.md](../code/frontmatter-parser.md), which owns that
history). One package with internal imports has no such constraint: `common/version.py` is read by
every pillar's `--version`, not duplicated by it.

`cq specs release` rewrites the `version` of **every** plugin entry in
`.claude-plugin/marketplace.json`, never only the first. A marketplace entry with no `version`, or
a catalog that disagrees with the declared marketplace plugins, is refused.
`test_specs_release.py` asserts that every one of these versions is equal. The manifests carry no
hard-coded command counts, since they drift on the next command change.

## Publication is checked before and after regeneration

`distribution_findings` in `common/modules.py` proves that `.claude-plugin/marketplace.json` lists
exactly the `plugins` entries with `marketplace: true`, each at its declared source path, with a
`plugin.json` bearing the declared name. `cq specs release` runs it before writing any version and
again after regeneration, so a generator cannot remove a delivery route between the preflight and
the tag. A missing catalog, a missing entry, a wrong source or a wrong identity is a failure even
when version equality passes.

Spec 2160 retired the module plugins, the specs reader, the Codex plugin and its 6.4.0 upgrade
baseline, and the OpenCode distribution
([ADR 0017](../../decisions/0017-install-only-by-deploy.md)). A target that installed them keeps a
frozen version until it runs `cq deploy`; the release that ships this is a major one and its
changelog entry says so.

## When the bump happens — once, at the release, on the primary branch

The surfaces move **once per release, on the primary branch, as the deliberate act that publishes
it** — see [branching.md](../git/branching.md). A version bump is never a task in a
spec's `## Tasks`, `/quenching-specs:specs:execute` never makes one, and `/quenching-specs:specs:conclude` no longer makes one
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

A deployed target carries the version in `.agents/.quenching-deploy.json` and moves only when
`cq deploy --write` runs from the new release, which is an explicit target action rather than an
upgrade a marketplace can miss. Earlier plugin generations shipped separate scripts an align could
copy into a target's `.claude/hooks/`, which meant a bump could leave a stale, still-executing copy
behind; a dedicated detector (`cq components drift`) existed for exactly that gap. That copying is
gone, so the detector was retired with the four scripts it used to compare an installed copy
against (`modularizar-specs-knowledge-components` spec, task 10.3); `cq deploy --check` is the
drift check for what a deploy owns.

## Verifying

The deterministic repository gate checks this checkout's own deployed
surface against the source. Direct read-only checks are:

```bash
python3 plugins/quenching/assets/bin/cq deploy --target . --check --json
```

Drift exits 1. Neither `--write` bumps an authored version surface or repairs a marketplace
version disagreement. Release regression fixtures prove a new consumer's surfaces move
with the set and preexisting disagreement changes no artifact.

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
