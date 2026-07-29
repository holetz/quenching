---
type: standard
title: Versioning and release — the six-artifact lockstep
description: Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and each installing align compares its own tool's --version against the copy already installed in a target repo
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-07-28
audience: both
authority: current
source: moved from CLAUDE.md
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

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
