---
type: standard
title: Surface translation — Claude and Codex coexistence
description: A repository may carry Claude and Codex surfaces together; Claude owns configuration and deterministic translation keeps their command, reference, and harness artifacts aligned
resource: plugins/quenching/assets/bin/quenching/components/commands/translate.py, plugins/quenching/assets/translation/codex-adaptation.json, .agents/plugins/marketplace.json
tags: [architecture, claude-code, codex, translation, surfaces]
timestamp: 2026-10-22
audience: both
authority: current
source: alinhar-plugin-a-agents-md spec, tasks 2.1–2.4 (2026-08-18)
maintainer: quenching
---

# Surface translation — Claude and Codex coexistence

<!-- rules -->

This marketplace repository publishes and checks its generated Codex plugin under
`plugins/quenching-codex/`, registered in `.agents/plugins/marketplace.json`. Regenerate it with
`python3 scripts/sync_codex_plugin.py --write`; the translator also remains a capability
for target repositories. A repository may expose `.claude/` and `.agents/` at the same time. They are paired surfaces,
not alternatives: Claude remains the authoritative source for configuration and the translator
generates the Codex representation deterministically.

The package's platform, identity, manifest and catalog are declared in `assets/modules.json` under
`distributions`. Publication and the isolated marketplace upgrade check are governed by
[versioning-release.md](../ci-cd/versioning-release.md); translation drift alone does not prove
that an installed consumer can discover or upgrade the package.

## What translates

`cq components translate --source <repo> --target <repo>` maps each
`.claude/commands/<path>.md` to `.agents/skills/<path>/SKILL.md`, preserving the command body
while adapting platform vocabulary and retaining only frontmatter Codex can use. It also copies
and adapts `.claude/references/**` to `.agents/references/**`, so translated skills retain valid
local citations, and maps the root `CLAUDE.md` harness to `.agents/AGENTS.md` when it exists.

The translator owns only those generated artifacts. Existing Codex configuration, including
`.agents/plugins/marketplace.json`, stays in place and is excluded from translation-drift checks.

The generated `.agents/.generated-from.json` and `.generated-files.json` record the generated set
and one sha256 per generated file. They deliberately carry no aggregate source digest: it changed
on every unrelated edit and made every parallel PR conflict on one line. Freshness is a byte
comparison, not a stamp. A check compares the deterministic result to that set without changing either
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

## Codex runtime policy

Runtime adaptation is generated from `assets/translation/codex-adaptation.json` and
`components/commands/translate.py`, never edited in generated skills or an installed cache.
The project's role mapping is `opus` → `gpt-6-astra`, `sonnet` → `gpt-6.1-sol`, and
`haiku` → `gpt-6-luna`; these are project routing choices, not measured model equivalence.
Declared efforts survive. Luna writes product code only on ONE task whose
`cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` — an executable
`verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context
at or under 80k — the same conditions as `haiku` (ADR 0014); a failed `verify:` returns the task
to the session model. Judgment roles and import-memory classifiers/executors never use Luna.
Source Claude model pins remain intact.

A Codex run delegates exclusively through the Codex host's subagent tools, with explicit
models and role protocols. It must never launch Claude CLI or fall back to Claude models.
Claude workflows may still delegate development to Codex, and may also ask Codex for an
independent review of their own work. That review runs only as `codex exec` under the bypass with
`--ignore-user-config` and no native sandbox, a git guard proving the tree unchanged, and runs in parallel with the Claude review, by default when quota is
available. When Codex is unavailable or out of quota the workflow reports the fallback and keeps
the Claude review rather than skipping the step in silence. A Codex run never launches Codex or
Claude CLI, so the review step belongs to the Claude surface and is absent from the generated
Codex surface; this grants no new `allowed-tools` or `tools:`. Host capabilities determine
spawn, messaging, interruption and completion mechanics; unavailable independent delegation
is reported rather than replaced by self-review. Token usage is reported per model and role
only when the Codex host exposes it, otherwise `not measured`; Claude transcript telemetry
cannot measure a Codex run. Shared `.claude/quenching.json` remains the configuration home.

Model adaptation applies to executable Markdown prose and agent frontmatter, while fenced
fixtures and copied Python implementation remain data. Existing general platform/path
translation is separate from the runtime model pass.

The generated surface-load adapter exits 2 (inconclusive) until a Codex capture harness exists;
it never runs the Claude harness. Generated `cq components session cost` likewise refuses
with `se-codex-telemetry-unavailable`. Import-memory may read existing Claude-format memory
files as data, with the original source path explicit; translation invents no Codex memory layout.
Generated runtime prefixes are excluded from reverse body reconciliation and cannot be edited
from the generated side to change source policy.
