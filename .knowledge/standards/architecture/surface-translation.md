---
type: standard
title: Surface translation — Claude and Codex coexistence
description: A repository may carry Claude and Codex surfaces together; Claude owns configuration and deterministic translation keeps their command, reference, and harness artifacts aligned
resource: plugins/quenching/assets/bin/quenching/components/commands/translate.py, plugins/quenching/assets/translation/codex-adaptation.json
tags: [architecture, claude-code, codex, translation, surfaces]
timestamp: 2026-08-18
audience: both
authority: background
source: alinhar-plugin-a-agents-md spec, tasks 2.1–2.4 (2026-08-18)
maintainer: quenching
---

# Surface translation — Claude and Codex coexistence

A repository may expose `.claude/` and `.agents/` at the same time. They are paired surfaces,
not alternatives: Claude remains the authoritative source for configuration and the translator
generates the Codex representation deterministically.

## What translates

`cq components translate --source <repo> --target <repo>` maps each
`.claude/commands/<path>.md` to `.agents/skills/<path>/SKILL.md`, preserving the command body
while adapting platform vocabulary and retaining only frontmatter Codex can use. It also copies
and adapts `.claude/references/**` to `.agents/references/**`, so translated skills retain valid
local citations, and maps the root `CLAUDE.md` harness to `.agents/AGENTS.md` when it exists.

The translator owns only those generated artifacts. Existing Codex configuration, including
`.agents/plugins/marketplace.json`, stays in place and is excluded from translation-drift checks.

The generated `.agents/.generated-from.json` and `.generated-files.json` record the source digest
and generated set. A check compares the deterministic result to that set without changing either
surface.

## What never translates

`.claude/quenching.json` is the single configuration home. The Codex surface does not receive a
second copy, so coexistence cannot create two independently editable configurations.

The translator's adaptation map and implementation ship inside the Claude plugin under `assets/`.
An installed plugin can therefore perform the same translation in a target repository; the
marketplace repository's root `scripts/` directory is not a runtime dependency.

## Direction and authority

This initial implementation proves the Claude-to-Codex generation path and the coexistence rule,
but not yet the reverse reconciliation path. Accordingly this standard is `background` until the
hash-based reverse direction and its tests are delivered. A future proven rule may graduate it to
`current`; it must retain Claude as the authority for configuration and for source forms that
cannot round-trip without loss.
