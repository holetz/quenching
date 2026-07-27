---
type: standard
title: Command surface naming
description: How the plugin's commands are named and namespaced — one file per entry point, where the path is the identity
resource: plugins/quenching/commands/**
tags: [naming, commands, taxonomy]
timestamp: 2026-07-26
audience: both
authority: current
source: rename-command-surface change (2026-07-21) + the specs-native refactor (2026-07-24) + collapse-skills-into-commands (2026-07-26)
maintainer: quenching
---

# Command surface naming

How the `quenching` plugin names its commands.

## The path IS the identity

**One file per entry point.** Claude Code merged custom commands into skills, so
`commands/<front>/[<object>/]<verb>.md` carries both the description that routes to it and the
body that runs. It is invocable as `/<front>:[<object>:]<verb>` — the `:` separator, one per path
segment — and by that same name through the Skill tool, prefixed by the plugin
(`quenching:docs:align`).

- `commands/docs/add.md` → `/docs:add`
- `commands/specs/develop.md` → `/specs:develop`
- `commands/docs/documentation/build.md` → `/docs:documentation:build`

There is **no second name**. The `quenching-<front>-<object>-<verb>` skill name this standard once
mandated existed to be *mirrored* by a command path; with nothing to mirror, it is retired, and
with it the bijection rule, the mirroring requirement, and the two root exceptions that needed
`sk-path-mismatch` recorded as intended. Nothing derives a name that could disagree with the path,
so nothing checks that they agree.

## Namespaces are honest by artifact

The surface is partitioned by the artifact each command touches:

- **`/docs:`** — the OKF `docs/` bundle.
- **`/specs:`** — the native spec-driven workspace.
- **`/skill:`** — the target repo's `.claude/` automation surface.
- **root `/align` and `/align-and-update`** — deliberately outside the three namespaces, because
  they are the two commands that span all three fronts. Under the old rule these were exceptions
  the linter had to be told about; now they are simply two commands at the top of the tree.

A command's namespace MUST match what it touches: a command that mints commands lives under
`/skill:`, never `/docs:`; a command that reads or writes the bundle lives under `/docs:`.

## Verb-first names that reveal the action

A command name is a verb (or verb-object) that names its action, so the `/` menu tells the story
without the description. A name MUST NOT be a bare noun that reads as a query, a jargon term when
a plain verb exists, or a name whose apparent object differs from what it acts on (a name that
lies). The object is named when the verb alone is ambiguous
(`glossary-backfill`, not `knowledge-scan`).

This rule also governs directory names, which is why the collapse left no `skills/` directory
holding no skills: a name that lies is forbidden of the surface this standard governs.

## The surface invariant, and clean renames

- **Every command carries a non-empty `description`, and no two resolve to the same `/` path.**
  That is the whole invariant, and it is what replaced the bijection. `skills.py doctor --json`
  decides it; the **count is not written down here**, because a number transcribed into prose goes
  stale the first time a command is minted. This standard once said "27 skills, 27 wrappers" while
  the surface carried 28, which is the whole argument.
- **`commands/**` is the only tree Claude Code registers**, so nothing that is not an entry point
  lives under it — see [../architecture/plugin-layout.md](../architecture/plugin-layout.md).
- A rename is **clean** — no compatibility aliases, no dual-registered names. A blast-radius sweep
  updates every reference (branch names, CI, scripts) and a rename reaching product code gets its
  own confirmation. The collapse took this literally at the largest scale the repo has seen: no
  `skills/` shim, no dual registration, no transitional period.

## Why there is no longer a wrapper

This standard used to carry a §*Why the wrapper still exists*, arguing that the mandatory 1:1
wrapper bought exactly one thing — the `:`-namespaced `/` tree — at a measured cost of ~2,072
characters always in context, and closing with an explicit revisit trigger:

> reconsider it when `skills.py budget` shows wrapper descriptions displacing skill descriptions.

**That trigger fired, from the other side.** The question was never whether the wrapper displaced
the skill description; it was that the *skill* description was the redundant one. Collapsing into
the wrapper's file keeps the entire discovery story — same `/` tree, same paths, same namespaces —
and deletes the other description outright. Always-on metadata fell from 30,705 characters to
2,069.

**What that saving cost, and what it did not.** The deleted description is where the quoted
trigger phrases and the `Not for:` boundary lived, so every command now reports
`sk-trigger-position` and `sk-no-boundary` against a description written as a `/`-menu label.
Both are warnings, so no gate catches it — which is why it is recorded here instead.

**Spoken routing was measured, not assumed, and it survived.** On 2026-07-26, three natural
phrases with no `/` typed each reached their command by description alone in a fresh `claude -p`:
*"park a spec for later…"* and *"capture this for the backlog…"* both reached `/specs:capture`,
and *"add a standard: we always use snake_case…"* reached `/docs:add`. So a description naming
only the action **does** still route — the claim that it would not is contradicted by the
measurement.

What remains is a **thinner margin**, not a broken surface: routing now rests on the model
inferring intent from a short action label rather than matching a verbatim trigger the author
chose, and no description states which adjacent command owns the neighbouring job. That is a
structural risk the three probes cannot rule out — they show the common phrasings work, not that
every phrasing does. Restoring triggers and boundaries is **available headroom, not a defect to
repair**: it would cost characters the collapse just freed, and it should be decided on measured
should-trigger / should-not-trigger rates, per [../automation/context-budget.md](../automation/context-budget.md).

## Canonical English surface

Command paths, folder names, frontmatter keys, and `type` values are canonical English (cross-repo
greppable). Body prose may follow the repo's language; identifier-derived slugs stay verbatim.
