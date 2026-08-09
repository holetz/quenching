---
type: standard
title: Versioning and release — the six-artifact lockstep
description: Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and the three tool constants are the lockstep unit each tool's own selftest holds to — bumped once per release, at the develop → main merge, never at conclude and never as a task, plus the half a bump cannot do, which is noticing the legacy copies a target still carries under .claude/hooks/ from before resolution went plugin-first, and the seventh version-carrying file that stays outside the six because no consumer reads it
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py, plugins/quenching/assets/bin/session.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-08-04
audience: both
authority: current
source: moved from CLAUDE.md; the drift half added by the notice-installed-tool-version-drift spec (task 4.1), proved by `skills.py drift` and its selftest fixture; the plugin-side-only rider revealed by the improve-command-from-session branch review, which caught session.py shipping 4.2.0 against a 4.3.0 plugin; rewritten for plugin-first resolution with no install (2026-08-03, enxugar-create-e-eliminar-o-rung-hooks spec) — drift's subject became the legacy copy, not the stale dependency; the bump moved from conclude to the develop → main release by the configurable-branch-strategy spec (task 1.2, 2026-08-04) once [branching.md](../git/branching.md) gave the publication a moment of its own to move on
maintainer: quenching
---

# Versioning and release — the six-artifact lockstep

A release bumps **six** version strings, and they must agree. The rule is not bookkeeping
tidiness: two independent consumers read two different halves of the set, and a partial bump
makes each one wrong in its own way.

## The six

| # | Artifact | Read by |
| --- | --- | --- |
| 1 | `plugins/quenching/.claude-plugin/plugin.json` → `version` | Claude Code, to detect and apply an upgrade |
| 2 | `plugins/quenching/VERSION` | the same detection, as the pair's other half |
| 3 | `.claude-plugin/marketplace.json` → the plugin entry's `version` | the marketplace listing |
| 4 | `plugins/quenching/assets/hooks/okf-validate.py` → `VERSION` | the tool's own `--version`; `skills.py drift`, identifying a legacy copy |
| 5 | `plugins/quenching/assets/bin/specs.py` → `VERSION` | likewise |
| 6 | `plugins/quenching/assets/bin/skills.py` → `VERSION` | likewise |

## Why each half matters

**Artifacts 1–2 are the upgrade trigger.** The `plugin.json` `version` and the `VERSION` file are
the pair Claude Code uses to decide that an installed plugin is stale and should be replaced. Bump
one without the other and the upgrade either never fires or fires against a plugin that reports a
version it does not have.

**Artifacts 4–6 are the *tool identity*.** Nothing installs them any more — every command invokes
`${CLAUDE_PLUGIN_ROOT}/assets/{bin,hooks}/<tool>` with no fallback and no manual rung
([align/tool-resolution.md](/plugins/quenching/assets/references/align/tool-resolution.md)
§Resolving the tool) — so a bump no longer *delivers* anything. What the three constants still do
is answer `--version`, which is half the uniform tool contract every tool here obeys, and give
`skills.py drift` the number a **legacy copy** left under a target's `.claude/hooks/` is identified
against. A tool whose constant was not bumped reports a version the plugin does not ship, and the
one probe that reads it says nothing is wrong.

The constant is duplicated in three places rather than imported from one because the tools **may
not import each other** — see [frontmatter-parsing.md](../code/frontmatter-parsing.md), which owns
that rule and the reason it survived the removal of install.

## When the bump happens — once, at the release, before the develop → main merge

The six move **once per release, on `develop`, immediately before the `develop → main` merge that
publishes it** — see [branching.md](../git/branching.md). A version bump is never a task in a
spec's `## Tasks`, `/specs:execute` never makes one, and `/specs:conclude` no longer makes one
either: a spec's own conclude merges into `develop` with the lockstep untouched, and the six move
only when the release command runs `specs.py release`.

**Why not a task, and why not conclude either.** Three things break when the bump is scheduled as
anything other than the release's own act:

- **What the release *is* is not knowable at task 1, or even at one spec's conclude.** Whether the
  change is patch, minor or major depends on everything `develop` has accumulated since the last
  tag — which may be several specs, not just the one concluding — and the task list inside any one
  of them is routinely revised mid-build. A number chosen at the top of a branch, or at that
  branch's own conclude, is a guess nothing downstream re-checks.
- **Two specs concluding into `develop` no longer collide.** Under the old rule both bumped from the
  same base to the same number, and the second to merge resolved a conflict in `plugin.json`,
  `marketplace.json` and three Python constants by hand. With the bump moved to the release, no
  conclude touches the six at all — `develop` accumulates any number of specs with nothing to
  conflict on, and the collision this section used to warn about does not arise.
- **A spec that is abandoned or descoped carries no version claim to unwind.** Nothing in its own
  conclude touched the lockstep, so there is nothing to revert beyond the merge itself.

**Why the release, specifically.** That is the one moment everything accumulated on `develop` is
about to become the published state of `main`, so the single `develop → main` merge carries the
version together with whatever the release actually ships — and reverting that merge reverts the
version claim with it. A bump committed to `main` after that merge would be the one thing the
release forbids outright, the same way a post-merge commit to the base is forbidden everywhere else
in this front.

## The seventh file — a version nothing reads

`plugins/quenching/assets/bin/session.py` also carries a `VERSION` constant
(`session.py:109`), and it is **not** a seventh member of the lockstep. It fits neither half above:
Claude Code never reads it, and `drift` never compares it, because **no target repo can be holding
a copy of it**. Every tool now runs from `${CLAUDE_PLUGIN_ROOT}`, so that is no longer what sets
`session.py` apart — what does is that no align ever offered to install it, so it left no legacy
copy under anyone's `.claude/hooks/` for a probe to find.

**It must still be bumped with the rest**, and since install went away it is no longer the only one
in that position. Artifacts 4–6 used to be enforced by a consumer — miss one and an align silently
stopped upgrading a target. With nothing installing them, **no automated check asserts any of the
six agree**: `drift` deliberately compares a legacy copy against the *shipped tool's own* constant
rather than the plugin's `VERSION`, no selftest reads the pair, and `--version` still answers, just
with the wrong number. The whole lockstep is now the discipline this one file always was.

That is not theoretical. `session.py` was authored at `4.2.0` on a branch that stayed open while
main released `4.3.0`, back when the bump still happened at that branch's own conclude; it reached
the branch review still reporting `4.2.0`, under a comment that read *"tracks the plugin"*. The
only thing that caught it was a human reading the whole branch diff at
[`/specs:conclude`](../workflows/plan-lifecycle.md) — which is exactly the class of miss a
long-lived branch produces and no checker covers, and which the bump moving to the release does not
retire: a stale constant on `develop` is still only caught by a human reading the diff, now at the
release rather than at any one spec's conclude.

The rule, stated so a future plugin-side-only tool inherits it:

- A tool no target repo could be carrying a legacy copy of **stays out of the six**. Adding it
  would give `drift` a row that is `absent` in every repo, forever.
- It **carries a `VERSION` anyway**, because `--version` is part of the uniform tool contract
  (`0` ok · `1` findings · `2` refusal, `--json` everywhere) that every tool here answers to.
- It is bumped **with the six, at the same moment** — the `develop → main` release, per §*When the
  bump happens* above — and §*Verifying* reads it back like the others. Since nothing enforces it,
  the bump is a discipline, and a stale value survives until somebody reads the file at the release.

## Noticing drift — the half a bump cannot do

Resolution is **plugin-first with no fallback and no manual rung**, so a bump reaches every repo
the moment the plugin upgrades. What a bump cannot do is clear out what earlier versions left
behind: a repo that once accepted an align's install offer still has `specs.py`, `skills.py` or
`okf-validate.py` sitting under `.claude/hooks/`, and **nothing executes any of it**. This
repository ran `.claude/hooks/specs.py` at **1.0.0** against a plugin at **4.2.0** for months, back
when the manual rung could still resolve ahead of the plugin — long enough that the stale copy's
`status` really did take `--plan` where the current one takes `--spec`. That failure is now
impossible; what survives it is the copy, still on disk, read by nothing.

`python3 assets/bin/skills.py drift --json` is what notices. Three rules make its answer worth
trusting:

**1. It runs from the plugin's copy, and refuses otherwise.** `drift` derives the plugin root from
its own location (or takes `--plugin-root`) and **exits 2** when neither resolves. A checker that
cannot tell "nothing left over" from "could not look" reports the silence it exists to break.

**1b. It reads; it never runs the copy.** The version comes from each tool's `VERSION = "…"`
constant, parsed. Shelling out for `--version` would mean a probe **executing** whatever script a
target happens to have under `.claude/hooks/` — a far larger claim than reading three lines, and
one that also needs `python3` on `PATH`. A copy too old to declare a constant reads `unreadable`,
which carries the same call to action as the rest: remove it.

**2. Every copy is a finding, and its version only says what kind of debris it is.** `behind`,
`ahead` and `unreadable` are the three shapes a leftover takes, and none of them changes the
remedy — the align for that front offers to **remove** it, never to overwrite it. There is no
stale-dependency case left to distinguish, because there is no dependency.

**3. `absent` is the expected state, and is not reported.** All three tools are `absent` in any
repo that never took the old offer, and in every repo an align has since cleaned. A probe that
announced the normal case on every run would be noise, and a probe whose output is routine noise
gets skipped.

Severity follows from there: all three findings are **warnings**. A leftover copy breaks nothing —
it is unread weight, and the repo is already running the current tool — so none of them is an
error. What was once `sk-tool-unwired` is gone entirely: the plugin's own `hooks/hooks.json` wires
`okf-validate.py`, so an installed copy's wiring is no longer a question anyone can be wrong about.

## Verifying

The lockstep is checked by reading every version surface back and confirming one value — the four
the six resolve to, plus the plugin-side-only tool above. **No checker catches any of them**, so
this block is the whole enforcement:

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
python3 assets/bin/session.py --version        # outside the six; nothing else reads it
```

And the other end of the same rule — which legacy copies a target still carries:

```bash
python3 assets/bin/skills.py drift --json      # 0 ok · 1 findings · 2 refused to guess
```

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
