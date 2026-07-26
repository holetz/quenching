---
type: standard
title: Command surface naming
description: How the plugin's skills and command wrappers are named, namespaced, and paired one-to-one
resource: plugins/claude-quenching/skills/*/SKILL.md, plugins/claude-quenching/commands/**
tags: [naming, commands, skills, taxonomy]
timestamp: 2026-07-26
audience: both
authority: current
source: rename-command-surface change (2026-07-21) + the specs-native refactor (2026-07-24)
maintainer: claude-quenching
---

# Command surface naming

How the `claude-quenching` plugin names its skills and the command wrappers that expose them.
This standard **supersedes** the earlier `openspec/specs/command-naming` spec: the `opsx:`
namespace and the "preserve the upstream `openspec-*` skill names" rule are retired, because the
spec-driven front is now fully native (no external OpenSpec CLI to align with).

## One taxonomy for every skill

Every skill is named `quenching-<front>-<object>-<verb>` — the front it acts on, then (when the
verb needs it) the object, then the verb. The name is a **flattened path**, and it is mirrored
**one-to-one** by a command wrapper at `commands/<front>/[<object>/]<verb>.md`, invocable as
`/<front>:[<object>:]<verb>` (the `:` separator, one per path segment).

- `quenching-docs-add` → `commands/docs/add.md` → `/docs:add`
- `quenching-specs-develop` → `commands/specs/develop.md` → `/specs:develop`
- `quenching-specs-triage` → `commands/specs/triage.md` → `/specs:triage`

## Namespaces are honest by artifact

The surface is partitioned by the artifact each command touches:

- **`/docs:`** — the OKF `docs/` bundle.
- **`/specs:`** — the native spec-driven workspace, with the plan lifecycle nested under
  `/specs:plan:*` and the task inbox under `/specs:backlog:*`.
- **`/skill:`** — the target repo's `.claude/` automation surface.
- **root `/align` and `/align-and-update`** — deliberately outside the three namespaces, because
  they are the two commands that span all three fronts.

A command's namespace MUST match what it touches: a command that mints skills lives under
`/skill:`, never `/docs:`; a command that reads or writes the bundle lives under `/docs:`.

## Verb-first names that reveal the action

A command name is a verb (or verb-object) that names its action, so the `/` menu tells the story
without the description. A name MUST NOT be a bare noun that reads as a query, a jargon term when
a plain verb exists, or a name whose apparent object differs from what it acts on (a name that
lies). The object is named when the verb alone is ambiguous
(`glossary-backfill`, not `knowledge-scan`).

## Bijection and clean renames

- **One skill ↔ one wrapper**, always: no skill without a wrapper, no wrapper without a skill.
  The **count is not written down here** — `skills.py doctor --json` reports it (`bijection.skills`,
  `bijection.wrappers`, `bijection.holds`), and a number transcribed into prose goes stale the
  first time a skill is minted. This standard said "27 skills, 27 wrappers" while the surface
  carried 28, which is the whole argument.
- Two deliberate exceptions to the mirroring, both at the root: **`/align`** →
  `quenching-align-all` and **`/align-and-update`** → `quenching-align-and-update-all`. They sit
  outside the three namespaces because they are what crosses them, so their wrapper path does not
  flatten to their skill's name. `doctor` reports each as `sk-path-mismatch` (a warning, not an
  error) — recorded here as intended, so the finding reads as known rather than new.
- A rename is **clean** — no compatibility aliases, no dual-registered names. A blast-radius sweep
  updates every reference (branch names, CI, scripts) and a rename reaching product code gets its
  own confirmation.

## Why the wrapper still exists

Claude Code merged custom commands into skills: `.claude/commands/x.md` and
`.claude/skills/x/SKILL.md` both produce `/x`. So the mandatory 1:1 wrapper now buys exactly one
thing — the `:`-namespaced `/` tree, where `/` + tab walks the surface in folder order and the
namespace tells you which artifact a command touches before you read its description.

That is a real discovery story, and its cost is measured rather than assumed: **2,072 characters**
of wrapper descriptions always in context across this plugin's 28 wrappers, about 6% of the
surface's total metadata (see [../automation/context-budget.md](../automation/context-budget.md)).

The wrapper stays, and this is a **trade-off with a revisit trigger**, not a structural given:
reconsider it when `skills.py budget` shows wrapper descriptions displacing skill descriptions —
that is, when the surface is against its ceiling and the wrapper half is what would have to give.
Until that measurement exists, navigability wins.

## Canonical English surface

Skill names, command paths, folder names, frontmatter keys, and `type` values are canonical
English (cross-repo greppable). Body prose may follow the repo's language; identifier-derived
slugs stay verbatim.
