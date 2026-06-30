# assets/hooks/ — hook payloads of the method

The **hooks** the [`quenching-management`](../../SKILL.md) method installs in the
target repo live here, along with the wiring for `settings.json`. By the
doctrine of dimension 8 (and Step 8 of SKILL.md), the hook is the
**deterministic trigger** of the cycle: it **OBSERVES / PROPOSES / at-most-BLOCKS**,
but **never mutates the base on its own** (propose ≠ apply — the one that applies
is a skill/command, with human OK). It is the link that makes base freshness
**automatic** without removing the human gate.

> **Not "active" in this skill.** They live under `assets/` and only start
> running when copied to `.claude/hooks/` of the target **and** registered in
> `settings.json`. The `*.py` files here are **payloads**; any `__pycache__/`
> is local-execution garbage (ignore it).

## Inventory

| Path | Event | Installs in | Addresses / does |
| --- | --- | --- | --- |
| `validate-claude-md.py` | PostToolUse (`Write\|Edit`) + InstructionsLoaded | `.claude/hooks/` + `settings.json` | 1, 8 — **SIGNALS** (`exit 2`, actionable feedback) when the touched CLAUDE.md exceeds the line ceiling; **does not block** (PostToolUse runs after the tool) |
| `propose-knowledge-delta.py` | Stop | `.claude/hooks/` + `settings.json` | 8 + core — only **PROPOSES** freshness delta via `additionalContext`, never blocks |
| `reinject-conventions.py` | SessionStart (`compact\|clear\|resume`) | `.claude/hooks/` + `settings.json` | 8 + core — **RE-INJECTS** the stable layer that `/compact` would erase; reads from a target-derived source (`conventionsFile`/CLAUDE.md root head), never a fixed list |
| `audit-config-change.py` | ConfigChange | `.claude/hooks/` + `settings.json` | 8 + core — **RECORDS** who/when/what changed on the surface (settings/skills) in a target-derived append-only log (`auditLog`); only observes, exit 0 always |
| `propose-docs-home.py` | PostToolUse (`Write\|Edit`) | `.claude/hooks/` + `settings.json` | 8 + 2 + core — when a Write/Edit touches a file under `docs/`, **PROPOSES** the canonical home/slot (block 2b criteria) via `additionalContext`; never blocks |
| `protect-generated.py` | PreToolUse (`Write\|Edit`) | `.claude/hooks/` + `settings.json` | 14 + 8 — **BLOCKS** (`permissionDecision: "deny"`) writes to a GENERATED artifact of the target (`protectedGlobs` derived from the target; empty list = inert); reason points to the source-of-truth ("X defines Y" rule) |
| `hooks-config.json` | — (config) | `.claude/hooks/` (commit it) | 8 — target-derived parameters (`maxLines`, `conventionsFile`, `auditLog`, `protectedGlobs`, …) |
| `settings.snippet.json` | — (wiring) | merge into `.claude/settings.json` | 8 — registers the `command` for each hook on the right event |

## Doctrine: OBSERVES × BLOCKS

Only **one** hook **blocks** (PreToolUse): `protect-generated` (generated artifact) —
deterministic enforcement, wins even under `bypassPermissions`. The rest
**only observe, signal, or propose** (PostToolUse / InstructionsLoaded /
ConfigChange / SessionStart): they never interrupt work — at most they inject
context (`additionalContext`), write a log, or **signal via `exit 2`** (like
`validate-claude-md` on ceiling: `exit 2` shows the feedback to Claude **after**
the edit, not blocking it). This is the dim 14 boundary: **enforcement**
(deterministic, blocks) × **guidance** (probabilistic, signals/suggests). The
hook never writes to the knowledge base — the one that applies is a skill/command
with confirmation.

## How to install (summary)

1. **Copy** the `*.py` files to `.claude/hooks/` of the target (skip `__pycache__/`).
2. **Register** each `command` in `settings.json` using `settings.snippet.json`
   as a template; **commit** `hooks-config.json`.
3. **Derive the parameters** in `hooks-config.json` to the target: `maxLines` to
   the repo's ceiling, `conventionsFile`/`auditLog`/`protectedGlobs` to the real
   paths (Step 0). **`protectedGlobs` must point to TARGET artifacts, never to
   paths in this repo** — an empty list leaves the hook inert (safe).
4. **Test the trigger** before trusting it: an edit above the ceiling should
   signal; a write to a protected glob should deny with an actionable reason.
5. If the repo already had an equivalent hook, **deprecate** the duplicate (do
   not remove without OK) — doctrine in
   [../../references/installation.md](../../references/installation.md).
