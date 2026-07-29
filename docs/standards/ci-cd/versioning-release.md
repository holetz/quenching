---
type: standard
title: Versioning and release — the six-artifact lockstep
description: Every version string the plugin ships must be bumped together, because two different consumers read two different halves — Claude Code decides an upgrade from the manifest pair, and each installing align compares its own tool's --version against the copy already installed in a target repo — bumped once per spec at conclude, immediately before the merge, never as a task, plus the half a bump cannot do, which is noticing that a target's copy has fallen behind, run ahead, or sits on disk with nothing invoking it, and the seventh version-carrying file that stays outside the six because no consumer reads it
resource: plugins/quenching/VERSION, plugins/quenching/.claude-plugin/plugin.json, .claude-plugin/marketplace.json, plugins/quenching/assets/bin/specs.py, plugins/quenching/assets/bin/skills.py, plugins/quenching/assets/hooks/okf-validate.py, plugins/quenching/assets/bin/session.py
tags: [release, versioning, lockstep, plugin, distribution]
timestamp: 2026-07-29
audience: both
authority: current
source: moved from CLAUDE.md; the drift half added by the notice-installed-tool-version-drift spec (task 4.1), proved by `skills.py drift` and its selftest fixture; the conclude-time rule added after `/specs:develop` inferred a bump task from this doc's `resource:` alone; the plugin-side-only rider revealed by the improve-command-from-session branch review, which caught session.py shipping 4.2.0 against a 4.3.0 plugin
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

## When the bump happens — once, at conclude, before the merge

The six move **once per spec, on the work branch, in `/specs:conclude` step 5 — the last writing
stage before the merge**. A version bump is never a task in a spec's `## Tasks`, and
`/specs:execute` never makes one.

**Why not a task.** Three things break when the bump is scheduled as work rather than as the merge's
own act:

- **What the release *is* is not knowable at task 1.** Whether the change is patch, minor or major
  depends on what task 7 turned out to be — a new command makes it minor, and the task list is
  routinely revised mid-build. A number chosen at the top of the branch is a guess that nobody
  re-checks at the bottom.
- **Two specs in flight collide on all six files.** Both bump from the same base to the same number,
  and the second to merge resolves a conflict in `plugin.json`, `marketplace.json` and three Python
  constants by hand. Deferring to just-before-merge means the second spec bumps from the base it is
  actually merging into.
- **A branch that is abandoned or descoped carries a version claim it never earned.** Nothing shipped
  it, but the branch's history says a release happened.

**Why conclude step 5 specifically.** That stage is where everything still lands on the work branch,
so the single merge carries the code, the emergent docs, the archived spec and the version together
— and reverting that merge reverts the version claim with them. A bump committed to the base after
the merge would be the one thing this command forbids outright.

The [operator-manual rider](#the-operator-manual-rider) below is settled at the same moment and for
the same reason: a command rename or a new command is only fully known once the branch is written.

## The seventh file — a version nothing reads

`plugins/quenching/assets/bin/session.py` also carries a `VERSION` constant
(`session.py:109`), and it is **not** a seventh member of the lockstep. It fits neither half above:
Claude Code never reads it, and no align ever compares it, because `session.py` is a plugin-side
tool that is **never installed into a target repo** — `/skill:retro` invokes it at
`${CLAUDE_PLUGIN_ROOT}`, where the copy that executes is always the one that shipped with the
plugin. The three-copy duplication the six exist to manage does not arise.

**It must still be bumped with the rest**, and the reason is the opposite of the one that governs
artifacts 4–6. Those are enforced by a consumer: miss one and an align silently stops upgrading a
target. This one is enforced by **nothing at all** — `skills.py drift` does not know about it,
no selftest asserts it, and `--version` still answers, just with the wrong number.

That is not theoretical. `session.py` was authored at `4.2.0` on a branch that stayed open while
main released `4.3.0`; it reached the branch review still reporting `4.2.0`, under a comment that
read *"tracks the plugin"*. The only thing that caught it was a human reading the whole branch diff
at [`/specs:conclude`](../workflows/plan-lifecycle.md) — which is exactly the class of miss a
long-lived branch produces and no checker covers.

The rule, stated so a future plugin-side-only tool inherits it:

- A tool that ships in the plugin but is never installed into a target **stays out of the six**.
  Adding it would make `drift` compare a version no target holds.
- It **carries a `VERSION` anyway**, because `--version` is part of the uniform tool contract
  (`0` ok · `1` findings · `2` refusal, `--json` everywhere) that every tool here answers to.
- It is bumped **with the six, at the same moment** — `/specs:conclude` step 5, per §*When the bump
  happens* above — and §*Verifying* reads it back like the others. Since nothing enforces it, the
  bump is a discipline, and a stale value survives until somebody reads the file. That is precisely
  how `4.2.0` survived: the conclude that should have carried it was still open.

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

The lockstep is checked by reading every version surface back and confirming one value — the four
the six resolve to, plus the plugin-side-only tool above, which no checker will catch:

```bash
cd plugins/quenching
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
python3 assets/bin/session.py --version        # outside the six; nothing else reads it
```

And the other end of the same rule — what a target actually holds, in both directions, with the
wiring question answered:

```bash
python3 assets/bin/skills.py drift --json      # 0 ok · 1 findings · 2 refused to guess
```

The broader "did I break the shipped skeleton" gate is
[bundle-verification.md](../quality/bundle-verification.md) and
[surface-verification.md](../quality/surface-verification.md).
