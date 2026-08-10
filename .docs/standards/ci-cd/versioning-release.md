---
type: standard
title: Versioning and release — the four-artifact lockstep
description: Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and the one shared version module is what every pillar's --version and cq components drift read — bumped once per release, at the develop → main merge, never at conclude and never as a task; `cq specs release` still moves the four pre-refactor scripts' own constants as well, pending their retirement
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/quenching/common/version.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-08-10
audience: both
authority: background
source: modularizar-specs-knowledge-components spec, task 9.2 — rewritten for the one-package, one-entry-point (`cq`) architecture; the lockstep target drops from seven artifacts to four now that a single `common/version.py` constant answers for every pillar, but `cq specs release` (task 10.2 of the same spec) has not yet been narrowed to match, so this file states the target the mechanical half has not caught up to — background until 10.2 lands and the release tool itself proves it; inherits the drift/legacy-copy reasoning from the six-artifact doc it replaces (moved from CLAUDE.md; drift half added by notice-installed-tool-version-drift task 4.1; plugin-first rewrite 2026-08-03, enxugar-create-e-eliminar-o-rung-hooks; bump moved to release by configurable-branch-strategy task 1.2, 2026-08-04)
maintainer: quenching
---

# Versioning and release — the four-artifact lockstep

A release bumps **four** version strings, and they must agree. The rule is not bookkeeping
tidiness: two independent consumers read two different halves of the set, and a partial bump
makes each one wrong in its own way.

**This is the target, not yet the mechanism.** `cq specs release <version>` — the tool this
section's *Verifying* block names — still moves the **seven** artifacts the one-package
refactor inherited: the four below, plus the three pre-refactor scripts' own `VERSION`
constants that this repository has not yet retired (`modularizar-specs-knowledge-components`
task 10.1) and narrowed the release tool to match (task 10.2). Until then, bumping still touches
seven files and this standard's own `authority: background` says so honestly.

## The four

| # | Artifact | Read by |
| --- | --- | --- |
| 1 | `plugins/quenching/.claude-plugin/plugin.json` → `version` | Claude Code, to detect and apply an upgrade |
| 2 | `plugins/quenching/VERSION` | the same detection, as the pair's other half |
| 3 | `.claude-plugin/marketplace.json` → the plugin entry's `version` | the marketplace listing |
| 4 | `plugins/quenching/assets/bin/quenching/common/version.py` → `VERSION` | every pillar's own `--version` (`cq specs`, `cq knowledge`, `cq components`); `cq components drift`, identifying a legacy copy under a target's `.claude/hooks/` |

## Why each half matters

**Artifacts 1–2 are the upgrade trigger.** The `plugin.json` `version` and the `VERSION` file are
the pair Claude Code uses to decide that an installed plugin is stale and should be replaced. Bump
one without the other and the upgrade either never fires or fires against a plugin that reports a
version it does not have.

**Artifact 4 is the *tool identity*, now held once.** Nothing installs a tool standalone any more —
every command invokes `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq` with no fallback and no manual rung
([align/tool-resolution.md](/plugins/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool) — so a bump no longer *delivers* anything. What the one constant still does is
answer `--version` for every pillar alike, and give `cq components drift` the number a **legacy
copy** left under a target's `.claude/hooks/` is identified against. Three scripts each carrying
their own copy of this constant was never a design choice — it was the shape a self-contained,
no-import single file forced, back when each pillar shipped as its own script
([frontmatter-parser.md](../code/frontmatter-parser.md), which owns that history). One package with
internal imports has no such constraint: `common/version.py` is read by every pillar's `--version`,
not duplicated by it.

## When the bump happens — once, at the release, before the develop → main merge

The four move **once per release, on `develop`, immediately before the `develop → main` merge that
publishes it** — see [branching.md](../git/branching.md). A version bump is never a task in a
spec's `## Tasks`, `/specs:execute` never makes one, and `/specs:conclude` no longer makes one
either: a spec's own conclude merges into `develop` with the lockstep untouched, and the artifacts
move only when the release command runs `cq specs release`.

**Why not a task, and why not conclude either.** Three things break when the bump is scheduled as
anything other than the release's own act:

- **What the release *is* is not knowable at task 1, or even at one spec's conclude.** Whether the
  change is patch, minor or major depends on everything `develop` has accumulated since the last
  tag — which may be several specs, not just the one concluding — and the task list inside any one
  of them is routinely revised mid-build. A number chosen at the top of a branch, or at that
  branch's own conclude, is a guess nothing downstream re-checks.
- **Two specs concluding into `develop` no longer collide.** Under the old rule both bumped from the
  same base to the same number, and the second to merge resolved a conflict in `plugin.json`,
  `marketplace.json` and the version module by hand. With the bump moved to the release, no
  conclude touches the lockstep at all — `develop` accumulates any number of specs with nothing to
  conflict on, and the collision this section used to warn about does not arise.
- **A spec that is abandoned or descoped carries no version claim to unwind.** Nothing in its own
  conclude touched the lockstep, so there is nothing to revert beyond the merge itself.

**Why the release, specifically.** That is the one moment everything accumulated on `develop` is
about to become the published state of `main`, so the single `develop → main` merge carries the
version together with whatever the release actually ships — and reverting that merge reverts the
version claim with it. A bump committed to `main` after that merge would be the one thing the
release forbids outright, the same way a post-merge commit to the base is forbidden everywhere else
in this front.

## Noticing drift — the half a bump cannot do

Resolution is **plugin-first with no fallback and no manual rung**, so a bump reaches every repo
the moment the plugin upgrades. What a bump cannot do is clear out what earlier versions left
behind: a repo that once accepted an align's install offer still has a pre-refactor script sitting
under `.claude/hooks/`, and **nothing executes any of it**. This repository ran an installed copy
at an old version against a much newer plugin for months, back when the manual rung could still
resolve ahead of the plugin — long enough that the stale copy's own CLI shape had already drifted
from the current one's. That failure is now impossible; what survives it is the copy, still on
disk, read by nothing.

`python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" components drift --json` is what notices. Three
rules make its answer worth trusting:

**1. It runs from the plugin's copy, and refuses otherwise.** `drift` derives the plugin root from
its own location (or takes `--root`) and **exits 2** when neither resolves. A checker that cannot
tell "nothing left over" from "could not look" reports the silence it exists to break.

**1b. It reads; it never runs the copy.** The version comes from each legacy script's own
`VERSION = "…"` constant, parsed. Shelling out for `--version` would mean a probe **executing**
whatever script a target happens to have under `.claude/hooks/` — a far larger claim than reading
one line, and one that also needs `python3` on `PATH`. A copy too old to declare a constant reads
`unreadable`, which carries the same call to action as the rest: remove it.

**2. Every copy is a finding, and its version only says what kind of debris it is.** `behind`,
`ahead` and `unreadable` are the three shapes a leftover takes, and none of them changes the
remedy — the align for that front offers to **remove** it, never to overwrite it. There is no
stale-dependency case left to distinguish, because there is no dependency.

**3. `absent` is the expected state, and is not reported.** Every legacy script is `absent` in any
repo that never took the old offer, and in every repo an align has since cleaned. A probe that
announced the normal case on every run would be noise, and a probe whose output is routine noise
gets skipped.

Severity follows from there: every finding is a **warning**. A leftover copy breaks nothing — it
is unread weight, and the repo is already running the current tool — so none of them is an error.

## Verifying

The lockstep is checked by reading every version surface back and confirming one value.
**No checker catches any of them**, so this block is the whole enforcement:

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/cq --version
```

And the other end of the same rule — which legacy copies a target still carries:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/bin/cq" components drift --json      # 0 ok · 1 findings · 2 refused to guess
```

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
