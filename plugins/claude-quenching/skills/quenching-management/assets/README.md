# assets/ — installable payloads of the method

Everything the [`quenching-management`](../SKILL.md) method **installs** into a
target repo lives here. This is what makes the method **self-contained**: it
does not depend on any external skill — it carries its own capabilities and
stamps them into the target's `.claude/`/`docs/` (Step 5 of SKILL.md, **with
confirmation**). The gap → payload map and deprecation doctrine are in
[../references/installation.md](../references/installation.md).

> **These files are not "active" in this skill.** They live under `assets/` (≥2
> levels below), so Claude Code **does not** discover them as live skills/agents
> — they are **templates/payloads**, copied out when the method is applied.

> **Worker agents only.** The `agents/` payloads here are the method's **workers**
> (`quenching-auditor`, `quenching-writer`). The agents that develop the **method
> itself** (`quenching-evolutionist` / `quenching-reviewer`) are **maintainer
> tooling**: they are **never** shipped or installed, live at the development
> repo's root `.claude/agents/`, and are documented in that repo's
> [`CONTRIBUTING.md`](../../../../../CONTRIBUTING.md) — not here.

## Inventory

| Path | Type | Installs in | Addresses dimension |
| --- | --- | --- | --- |
| `skills/quenching-map/` | skill-template | `.claude/skills/<prefix>-mapa/` | 1 (CLAUDE.md), 13 (conventions) |
| `skills/quenching-docs/` | skill-template | `.claude/skills/<prefix>-docs/` | 2, 4, 5, 11, 13 (docs-as-code) |
| `skills/quenching-standards/` | skill-template (orchestrator) | `.claude/skills/<prefix>-standards/` | 2 (builds/updates the ENTIRE `standards/` layer: per-topic fan-out in parallel + `INDEX.md` regenerated from disk) |
| `skills/quenching-roadmap/` | skill-template (orchestrator, read-only/propositional) | `.claude/skills/<prefix>-roadmap/` | core (Step 4/8) + profiles — PRODUCES the SEQUENCED roadmap "invest first in X, then Y" (METHOD/structure investment ORDER by leverage×cost×prerequisite), reading derived shape + profile + scorecard; PROPOSES the installation order, NEVER the content; `context: fork` + `agent: quenching-auditor`; auto-trigger by description (read-only) |
| `skills/quenching-announcement/` | skill-template | `.claude/skills/<prefix>-announcement/` | 2 (directed communication — reads the channel template and fills it) |
| `skills/quenching-skills/` | skill-template | `.claude/skills/<prefix>-skills/` | 6, 7, 9 (skills/agents/commands) |
| `skills/quenching-config/` | skill-template | `.claude/skills/<prefix>-config/` | 8 (hooks), 15 (MCP) |
| `skills/quenching-guardrails/` | skill-template | `.claude/skills/<prefix>-guardrails/` | 14 (guardrails) |
| `commands/quenching-reaudit/` | command-skill | `.claude/skills/<prefix>-reauditar/` | 9 (command born as skill) + core (Step 8, trigger 3) + 7 (fork in clean context) |
| `agents/quenching-auditor.md` | sub-agent | `.claude/agents/` | 7 + audit fan-out |
| `agents/quenching-writer.md` | sub-agent | `.claude/agents/` | 2 + AUTHORING fan-out (one worker per `standards/` topic, parallel; mines repo for `current` anchored at `file:line` + researches references; unimplemented gap becomes PROPOSAL, never current) |
| `hooks/validate-claude-md.py` | hook | `.claude/hooks/` + `settings.json` | 1, 8 (CLAUDE.md ceiling) |
| `hooks/propose-knowledge-delta.py` | hook (Stop) | `.claude/hooks/` + `settings.json` | 8 (automatic freshness) + core (Step 8) — only PROPOSES (`additionalContext`), never blocks |
| `hooks/reinject-conventions.py` | hook (SessionStart) | `.claude/hooks/` + `settings.json` | 8 (compact-survival) + core (Step 8) — RE-INJECTS the stable layer that `/compact` would erase; reads from target-derived source (`conventionsFile`/CLAUDE.md root head), never a fixed list; matcher `compact\|clear\|resume`, stdout becomes context |
| `hooks/audit-config-change.py` | hook (ConfigChange) | `.claude/hooks/` + `settings.json` | 8 (audit-trail) + core (Step 8) — RECORDS who/when/what changed on the surface (settings/skills) in a target-derived log (`auditLog`), append-only, metadata only; 5 sources; OBSERVES, exit 0 always (never blocks); stdout does not become context |
| `hooks/propose-docs-home.py` | hook (PostToolUse, matcher `Write\|Edit`) | `.claude/hooks/` + `settings.json` | 8 (docs/ coverage) + 2 (taxonomy) + core (Step 8) — when a Write/Edit touches a file under `docs/`, reuses the block 2b criteria (VARIANT/TWO-HOMES/NO-HOME/NO-SIDECAR/NO-LABEL) and only PROPOSES the canonical home/slot via `additionalContext`; PostToolUse does not block (exit 0 always); stdout does not become context in this event |
| `hooks/protect-generated.py` | hook (PreToolUse, matcher `Write\|Edit`) | `.claude/hooks/` + `settings.json` | 14 (enforcement) + 8 (hooks) — runs BEFORE Write/Edit and **BLOCKS** when destination matches a GENERATED artifact pattern of the target (`protectedGlobs`, derived from target — NEVER paths from this repo; empty list = inert) via `permissionDecision: "deny"` + actionable reason pointing to the source-of-truth ("X defines Y" rule); wins even in `bypassPermissions`; legacy `exit 2`/stderr via `denyMode`. Complements `propose-docs-home` (which PROPOSES after): this one BLOCKS before |
| `hooks/run-validation.py` | hook (Stop) | `.claude/hooks/` + `settings.json` | 8 (hooks, thin-hook-calls-script) crosses `scripts/` + 14 — at END of turn **CALLS the target's DERIVED validation script** (`validateScript`/`validateCmd`, home `scripts/checks`/`ci`; empty = inert, NEVER hardcoded trio) on altered files (`git status --porcelain`, filtered by `includeGlobs`); logic lives in `scripts/`, hook is the thin trigger. Default **PROPOSES** result via `additionalContext` (exit 0; `ruff --fix`/`format` mutate code, not the base ⇒ informs, does not block); `blockOnFail:true` mode uses `decision: block`/`reason` for "mandatory/never skip". Example for Python repo: script runs `ruff check --fix` + `ruff format` + `pyright` |
| `hooks/hooks-config.json` | config | `.claude/hooks/` | 8 |
| `hooks/settings.snippet.json` | wiring | merge into `.claude/settings.json` | 8 |
| `templates/**` (12 molds — see [`templates/README.md`](templates/README.md)) | templates | stamped where missing (header: skill/agent/CLAUDE.md/ADR/backlog/memory/docs-front) or applied by `quenching-docs` (body: sidecar/area/catalog) | 1–7, 10–13 |
| `docs/README.md` | skeleton | target's `docs/` root (canonical taxonomy manifest) | 2, 12 |
| `docs/standards/` (README + INDEX + 9 subtopics) | skeleton | target's current reference (`architecture/code/naming/data-modeling/ci-cd/workflows/mlops/quality/platform`) | 2, 12 |
| `docs/decisions/README.md` | skeleton | target's ADRs (open decision; canonical, was `adr/`) | 5 |
| `docs/vision/` (README only) | skeleton | target's direction segmented by area (only with OK; template `area.md` in `templates/`) | 3 |
| `docs/backlog/README.md` | skeleton | target's backlog tree | 4 |
| `docs/guides/` (README only) | skeleton | target's how-to + tutorials; the repo creates the guides and organizes them (preferably in topic subfolders) — the skill does not ship a ready guide | 2 |
| `docs/reference/` (README + `tools/libraries/regulations/`) | skeleton | target's external reference (what we consume) | 2, 12 |
| `docs/catalog/` (README only) | skeleton | target's data/domain catalog: `<system>/<catalog>/<schema>/<table>`, detailed × consolidated, access + scripts (generated × curated; templates `system`/`schema`/`table` in `templates/`) | 11 |
| `docs/communications/` (README + `templates/` per channel `email`/`chat`/`wiki`/`markdown` + `archive/`) | skeleton | target's directed communication; the repo creates the announcements (in `archive/`) and adopts channels (template per channel) — the skill ships the STRUCTURE, not the announcements | 2 |
| `docs/presentations/` (README + `slides/diagrams/reports/`) | skeleton | target's human deliverables (via sidecar) | 2, 12 |
| `scripts/` (README-map + `ci/checks/maintenance/dev/` README-only, placeholders `<...>`) | skeleton | canonical organization of the target's repo-level **executable logic** (purpose subfolders + map + execution convention); ships the STRUCTURE, **NEVER** concrete scripts (would couple to a repo) | 8 (crosses 1/9) |

## How to install (summary)

1. **Copy** the payload to the target's destination.
2. **Rename** folder/`name` to the derived taxonomy (`<prefix>`) and **translate**
   to the repo's language if needed.
3. **Fix the internal paths** of the payload to the real layers derived in Step 0
   of [../references/detection-and-smells.md](../references/detection-and-smells.md).
4. Hooks: **register** the `command` in `settings.json` (use
   `hooks/settings.snippet.json`) and commit `hooks-config.json`; adjust
   `maxLines` to the repo's ceiling.
5. **Never** overwrite the target's generated artifacts (`*.job.yml`, manifests,
   AUTO-GENERATED catalog or equivalent).
6. If the repo already had an equivalent artifact, **deprecate it** (do not
   remove without OK) — see deprecation doctrine in
   [../references/installation.md](../references/installation.md).

## No payload (method only proposes)

Dimensions **3 (vision)**, **10 (memory)** and **12 (boundaries)** have no
content payload — they are human decisions. The `docs/vision/` skeleton (with
the `templates/docs/vision/area.md` mold) and the template
`templates/memory/memory.md` exist as a starting point, but installing/writing
them is the user's decision, not an automatic step. The method **never writes
memory**.
