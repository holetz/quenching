---
type: decision
title: The source is written in the target dialect, and a skill per vertical or front routes to its flows
description: Why the source of quenching stopped being a plugin tree translated per harness and became one tree of router skills in the target dialect — flows as references inside each skill, shortcuts retired, one module per vertical or front, the quenching/ and integrations/ roots, and hooks installed by the deploy
resource: quenching/skills/**, quenching/references/**, quenching/assets/modules.json, quenching/assets/bin/quenching/deploy/tree.py, quenching/assets/hooks/**, docs/standards/architecture/source-layout.md, docs/standards/architecture/deploy-mode.md
tags: [decision, architecture, skills, deploy, layout]
timestamp: 2026-11-03
audience: both
authority: current
source: epic 2167 (specs 2168, 2169, 2170, 2171, 2172, 2173, 2174)
maintainer: quenching
---

# 0019 — Router skills and a source in the target dialect

[ADR 0017](0017-install-only-by-deploy.md) made `cq deploy` the only way the product reaches a
repository, and [ADR 0018](0018-retire-omnigent-and-source-manifest.md) removed the plugin-model
remnants. The source itself still had the plugin's shape: one `commands/<front>/<verb>.md` file per
command, ids written with `:` and translated at deploy, shortcuts beside them, and a
`plugins/<harness>/<name>/` layout for the satellites. This records the shape that replaced it. It
supersedes the part of 0017 that placed the satellites under `plugins/<harness>/<name>/`.

## Context

- Every `.md` under `commands/` was a command, so each flow was a registered entry that cost its
  description in the always-on listing, and the source could be loaded by no harness without a
  translation of its ids and citations.
- The deploy rewrote ids, citations and the plugin root in every body, so the bytes a reader opened
  in the source were not the bytes a target ran.
- Shortcuts (`/align`, `/specs-execute` style aliases) duplicated entries to save typing, and each
  one was a second description to carry.
- The module list stopped at `quenching-align`, which stood for two verticals that evolve apart.

## Decision

- **The source is written in the target dialect.** A body carries `/quenching-<vertical> <flow>` and
  `.agents/quenching/…` citations, with no plugin-root marker and no `:` in an id. `cq deploy`
  rewrites only the frontmatter, the generated header, the grants and the `cq.cmd` launcher, and
  refuses a source that still carries a plugin marker ([deploy-mode.md](../standards/architecture/deploy-mode.md)
  §Surface translation).
- **One router skill per vertical or front.** `skills/<name>/SKILL.md` is the only entry point and
  the skill name is the folder name. Its body picks a flow from a table and grants the union of the
  flows' `allowed-tools`.
- **Flows are references.** A flow is a file under the skill's own `references/`, cited
  `/quenching-<vertical> <flow>`; a reference two skills cite lives in the common
  `quenching/references/` ([source-layout.md](../standards/architecture/source-layout.md)).
- **Shortcuts are retired.** No alias entry stands for another entry; the router's table is the one
  place a flow is named.
- **One module per vertical and per front**, prefixed `quenching-`: `quenching-specs` (mandatory,
  with `quenching-handoff` and the root `quenching-align`), `quenching-git`, `quenching-knowledge`,
  `quenching-components` and one per front. `core` is `specs,git,knowledge,components`, and the old
  `align` is an alias for `knowledge,components`
  ([install-profiles.md](../standards/architecture/install-profiles.md)).
- **The roots are `quenching/` and `integrations/`.** `plugins/` is gone: the source is
  `quenching/`, and the satellites that install into no repository are
  `integrations/claude-hud` and `integrations/opencode-vitrine`.
- **Hooks are installed by the deploy.** The modules declare their hooks in `assets/modules.json`
  and `cq deploy` merges them into the target's `.claude/settings.json`; no manifest ships them.

## Consequences

- The listing a session pays for is one description per router, not one per flow.
- A reader of the source sees what a target runs; the translation is a thin, checkable rewrite.
- A new flow is a new reference and a new row in a router's table; a new front is a new skill, a
  new module record and an install-profile entry.
- `plugin-layout.md` became `source-layout.md` and `surface-translation.md` became a section of
  `deploy-mode.md` (spec 2174); the glossary gained Router skill, Flow, Module and Shortcut.
- What this does not change: the single editable source, deploy as the only installation, and the
  content of the flows themselves.
