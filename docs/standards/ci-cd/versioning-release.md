---
type: standard
title: Versioning and release — the six-artifact lockstep
description: Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and each installing align compares its own tool's --version against the copy already installed in a target repo — plus the half a bump cannot do, which is noticing that a target's copy has fallen behind, run ahead, or sits on disk with nothing invoking it
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-07-28
audience: both
authority: current
source: moved from CLAUDE.md; the drift half added by the notice-installed-tool-version-drift spec (task 4.1), proved by `skills.py drift` and its selftest fixture
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
| 4 | `plugins/quenching/assets/hooks/okf-validate.py` → `VERSION` | `/docs:align`, comparing against an installed copy |
| 5 | `plugins/quenching/assets/bin/specs.py` → `VERSION` | `/specs:align`, likewise |
| 6 | `plugins/quenching/assets/bin/skills.py` → `VERSION` | `/skill:align`, likewise |

## Why each half matters

**Artifacts 1–2 are the upgrade trigger.** The `plugin.json` `version` and the `VERSION` file are
the pair Claude Code uses to decide that an installed plugin is stale and should be replaced. Bump
one without the other and the upgrade either never fires or fires against a plugin that reports a
version it does not have.

**Artifacts 4–6 are the *installed-copy* trigger.** Each of the three stdlib tools is **installed
into a target repository** by its own align, and each align decides whether to overwrite the copy
already there by comparing `python3 <tool> --version` against the plugin's own `VERSION`. A tool
whose constant was not bumped is therefore never upgraded in any target repo that already has it —
the plugin ships a fix that silently never reaches the repos it was written for.

That asymmetry is the whole reason the constant is duplicated in three places rather than imported
from one: the tools **may not import each other**, because each installs standalone into a target's
`.claude/hooks/` (see [frontmatter-parsing.md](../code/frontmatter-parsing.md) for the same
constraint applied to the shared parser rule).

## Noticing drift — the half a bump cannot do

Bumping the six is what makes an upgrade *possible*. It does nothing about a target that already
holds a copy and never runs an align again: the offer is the only moment a version is compared, so
that repo keeps whatever it got, indefinitely, and nothing says so. This repository ran
`.claude/hooks/specs.py` at **1.0.0** against a plugin at **4.2.0** for months — long enough that
the stale copy's `status` still took `--plan` where the current one takes `--spec`.

`python3 assets/bin/skills.py drift --json` is what notices. Three rules make its answer worth
trusting:

**1. It runs from the plugin's copy, and refuses otherwise.** An installed copy would answer from
the same stale `VERSION` it is being asked about, so `drift` derives the plugin root from its own
location (or takes `--plugin-root`) and **exits 2** when neither resolves. A checker that cannot
tell "no drift" from "could not look" reports the silence it exists to break.

**1b. It reads; it never runs the copy.** The version comes from each tool's `VERSION = "…"`
constant, parsed. Shelling out for `--version` would mean a probe **executing** whatever script a
target happens to have under `.claude/hooks/` — a far larger claim than reading three lines, and
one that also needs `python3` on `PATH`. A copy too old to declare a constant reads `unreadable`,
which carries the same call to action as `behind`, so nothing is lost by not running it.

**2. Both directions are findings.** `behind` is the obvious one. `ahead` matters because
resolution is **plugin-first** and every align deliberately leaves a newer installed copy alone —
so an ahead copy is code that is never executed and never repaired, with both halves of that
behaving correctly and saying nothing.

**3. Installed is not wired.** `okf-validate.py` does nothing unless a `hooks` block invokes it.
This repo held it on disk with **no `hooks` block at all**: deleting it would have changed no
behaviour, which is exactly why nobody noticed. A drift check comparing only versions would have
caught 1.0.0-vs-4.2.0 and still missed the silence, so the wiring question is asked for the one
tool that is a hook — and never for `specs.py` or `skills.py`, which are CLIs whose absence from
`settings.json` is normal.

The same asymmetry decides severity. `behind` and `unwired` are **errors** (a different CLI
contract; an inert script). `ahead`, `unreadable` and a missing **hook** are **warnings**. A
missing CLI is not a finding at all: the plugin copy is what resolution runs, so warning about it
would fire on every plugin-only repo — including this one — and a probe whose output is routine
noise gets skipped.

## The operator-manual rider

A release on its own adds no manual work: each `QUENCHING.md` banner carries a `<VERSION>`
placeholder filled at copy time, so the manuals re-stamp themselves.

But a **command rename or a new command** is a different change, and it *does* mean editing the
`QUENCHING.md` of **that command's own front** — each manual enumerates only its own front's
surface. Adding `/specs:isolate` needed `assets/specs/QUENCHING.md` alone; touching the other two
would have been churn.

## Verifying

The lockstep is checked by reading all four version surfaces back and confirming one value:

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
```

And the other end of the same rule — what a target actually holds, in both directions, with the
wiring question answered:

```bash
python3 assets/bin/skills.py drift --json      # 0 ok · 1 findings · 2 refused to guess
```

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
