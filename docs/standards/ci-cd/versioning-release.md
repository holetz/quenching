---
type: standard
title: Versioning and release — the version lockstep
description: The version surfaces cq specs release bumps together — the unpublished source, every published module manifest (the eight principal modules, the specs reader and the HUD) and every marketplace entry
resource: plugins/quenching/assets/modules.json, plugins/quenching-*/VERSION, plugins/quenching-*/.claude-plugin/plugin.json, plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, .agents/plugins/marketplace.json, plugins/quenching/assets/bin/quenching/common/version.py, scripts/generate_plugin_modules.py, scripts/check_codex_upgrade.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-10-22
audience: both
authority: current
source: modularizar-specs-knowledge-components, one-entry-point, notice-installed-tool-version-drift, 2026-08-03, enxugar-create-e-eliminar-o-rung-hooks, configurable-branch-strategy, spec 1634, spec 1635 (module extraction); Codex marketplace upgrade regression, 2026-10-22; lineage in ADR 0004 and ADR 0013
maintainer: quenching
---

# Versioning and release — the version lockstep

<!-- rules -->

A release bumps the version surfaces in lockstep. The rule is not bookkeeping tidiness:
Claude, the marketplace and the bundled `cq` identity read different halves of the set, and a
partial bump makes one of them wrong.

`cq specs release <version>` — the tool this section's *Verifying* block names — requires a matching
`## <version>` entry in `CHANGELOG.md`, then moves every surface in one release operation.

The release commit is self-contained: the verb refuses (exit 2, nothing written) when the tree
has changes beyond `CHANGELOG.md`, bumps, **regenerates the copies**
(`scripts/generate_plugin_modules.py --write` and `scripts/sync_codex_plugin.py --write`, each when
present) and commits everything with the `CHANGELOG.md` entry, so `verify_repo.sh` is already green
on the tag. A failed regeneration leaves the bump uncommitted and makes no commit or tag.

## The published set

`plugins/quenching/assets/modules.json` is the declarative source. Each published module
contributes its `.claude-plugin/plugin.json` and, when declared, its `VERSION` file. The editable
source `plugins/quenching` contributes its pair **although it is not published**: it is the
version every generated module copies, so a release that skipped it would regenerate every module
back to the old number. The marketplace and source `common/version.py` complete the set. A module
record that is not published (and is not the source) contributes no release surface. `cq specs release` loads the **target repository's**
manifest; `RELEASE_ARTIFACTS` in `release.py` is a derived export of the bundled manifest for
existing callers, not a separately maintained list.

| # | Artifact | Read by |
| --- | --- | --- |
| 1 | `plugins/quenching-<module>/.claude-plugin/plugin.json` → `version`, for every published module | Claude Code, to detect and apply an upgrade |
| 2 | `plugins/quenching-<module>/VERSION`, for every published module that declares one | the same detection, as the pair's other half |
| 3 | `.claude-plugin/marketplace.json` → **every** entry's `version` | the marketplace listing |
| 4 | `plugins/quenching/assets/bin/quenching/common/version.py` → `VERSION` | every pillar's own `--version` (`cq specs`, `cq knowledge`, `cq components`) |
| 5 | `plugins/quenching/VERSION` and `plugins/quenching/.claude-plugin/plugin.json` (the unpublished source) | `scripts/generate_plugin_modules.py`, which writes it into every generated module |

The published modules are the eight principal modules (`quenching-specs`, `quenching-align`,
`quenching-design`, `quenching-ops`, `quenching-proof`, `quenching-toolchain`,
`quenching-delivery`, `quenching-security`), the generated `quenching-specs-reader` and the
authored `quenching-hud`, whose manifest carries no `VERSION` file.
Adding a published module changes the derived release set without editing the release code.
Manifest paths and ownership are validated before writes; artifact presence, changelog entry,
marketplace membership and existing version agreement must all pass before any version moves.

## Why each half matters

<!-- rationale -->

**Artifacts 1–2 are the Claude upgrade trigger, once per module.** Each enabled module is its own
installed plugin, so a module left at the old number is a module the host never upgrades while its
siblings move: the one `cq` in `quenching-specs` refuses to load a module package whose version
differs from its own, so a split version silently removes that module's fronts. The `plugin.json` `version` and the `VERSION` file are
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

Every module is bumped in the same operation. `cq specs release` moves each published module's
`VERSION` and `.claude-plugin/plugin.json` — the eight principal modules, the specs reader and the
HUD's manifest — together with the source pair, and it rewrites the `version` of **every** plugin
entry in `.claude-plugin/marketplace.json`, never only the first. A
marketplace entry with no `version`, or entries that disagree with published module membership,
are refused. Afterwards `python3 scripts/generate_plugin_modules.py --write` regenerates the
copied assets; `--check` proves generated consumers, published versions and the single active
PATH `cq` owner together. The old `sync_specs_reader_plugin.py` invocation remains a compatibility
wrapper over that same generator. The generated Codex package
(`plugins/quenching-codex/VERSION` and `.codex-plugin/plugin.json`), declared under
`distributions` in `assets/modules.json` with its platform, identity, package path, plugin manifest
and marketplace path, moves in the same lockstep. Afterwards
`sync_codex_plugin.py --write` regenerates its payload and translation manifest; the repository
gate checks both translation drift and package validity.
`test_specs_release.py` asserts that every one of these versions is equal. The manifests carry no hard-coded command counts, since they drift on the next command change.

## Publication is checked per platform

The principal `modules` declare the Claude distribution and its `.claude-plugin/marketplace.json`.
Additional `distributions` declare the Codex package and `.agents/plugins/marketplace.json`.
The latter catalog keeps the existing `quenching` marketplace and `quenching-codex` plugin identity
so installations from 6.4.0 retain their update route. Its entries are versionless: Codex reads the
version from the package manifest, which moves with `VERSION` in the release lockstep.

`distribution_findings` in `common/modules.py` checks both catalogs before a release writes any
version. Every declared package must be listed exactly once, at its declared source path, with an
existing manifest bearing the declared identity; the Codex entry must be installable. The
repository gate uses the same check. A missing catalog, missing entry, wrong source or wrong
identity is a failure even when generation and version equality pass.

Removing or renaming a published package also requires an explicit migration path for existing
installations. Keep the old catalog identity until the host upgrade test proves the replacement;
changing the declared set and the catalog together is not evidence of a successful migration.

## Upgrade acceptance

`python3 scripts/check_codex_upgrade.py` measures the actual Codex CLI installation route without
calling a model. It installs the published `6.4.0` Codex package in an isolated home, advances a
disposable Git marketplace to the candidate package, runs `plugin marketplace upgrade` and
`plugin add`, then checks the installed cleanup skill against the candidate bytes, executes that
skill's own tool resolver and runs the installed `scripts/cq --version`. It also checks that the
installed plugin is enabled. Git rewrites
a reserved test URL to the disposable local repository; no user installation or cache is edited.

CI runs this check with Codex CLI 0.163.0. The ordinary repository gate reports it skipped unless
`QUENCHING_DISTRIBUTION=1`; `/release` requires that flag alongside `QUENCHING_FUNCTIONAL=1`
before the bump. Missing Codex or the baseline tag exits 2 (inconclusive), which blocks a release.
The baseline is kept until an explicit migration changes the acceptance contract.

This proves package delivery, not the skills loaded in an existing model session. Start a new
session after updating; the generated Codex README includes installation, upgrade, version/path
inspection and migration guidance for mixed installations.

Generated shell blocks resolve the host-provided plugin root or the single enabled installation
from `codex plugin list --json`, including its exact cache version. They never choose the first
or newest cached directory. Regression tests retain multiple cache versions and require the
selected host version; missing or ambiguous selections refuse instead of falling back to a stale
copy. This check is separate from session loading.

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

The deterministic repository gate checks the manifest-derived published surfaces and copied
consumer payloads. A direct read-only check is:

```bash
python3 scripts/generate_plugin_modules.py --check
```

Exit 0 reports generated modules in lockstep, published versions in agreement and one PATH
`cq` owner. Drift exits 1; an unsafe or malformed distribution contract refuses with exit 2.
`--write` refreshes generated payloads only: it does not bump authored version surfaces or
silently repair a marketplace version disagreement. Release regression fixtures prove a new
consumer's surfaces move with the set and preexisting disagreement changes no artifact.

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
