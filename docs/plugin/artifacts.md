# Bundled artifacts

Everything the method can install lives inside the skill, under
[`assets/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets).
These payloads are **inert** in the plugin (not auto-discovered) and are
**copied and adapted** into a target repo's `.claude/`/`docs/` during
installation — that is what makes the method a *self-contained installer*
rather than a delegator.

| Category | Path | What it installs |
| --- | --- | --- |
| **Template skills** | `assets/skills/` | `quenching-map`, `quenching-docs`, `quenching-standards`, `quenching-announcement`, `quenching-skills`, `quenching-config`, `quenching-guardrails`, `quenching-roadmap` — generic, portable skills the target adapts |
| **Worker sub-agents** | `assets/agents/` | `quenching-auditor` (read-only audit fan-out) and `quenching-writer` (parallel `standards/` authoring) |
| **Command** | `assets/commands/quenching-reaudit/` | the on-demand re-audit (installs as a skill, with `context: fork`) |
| **Hooks** | `assets/hooks/` | 6 lifecycle/tool-event hooks + `hooks-config.json` + a `settings.snippet.json` to merge |
| **`docs/` skeletons** | `assets/docs/` | the canonical `docs/` taxonomy homes (only the ones that apply) |
| **`scripts/` scaffold** | `assets/scripts/` | the purpose-based `scripts/` organization (README-map + placeholders, never concrete scripts) |
| **Frontmatter templates** | `assets/templates/` | `claude/`, `docs/` and `memory/` frontmatter/body templates |

## The 6 hooks

| Hook | Event | Role | Blocks? |
| --- | --- | --- | --- |
| `propose-knowledge-delta.py` | `Stop` | proposes a CLAUDE.md/memory delta at end of turn | no |
| `reinject-conventions.py` | `SessionStart` (compact/clear/resume) | re-injects conventions that `/compact` would erase | no |
| `audit-config-change.py` | `ConfigChange` | records who/when changed the surface (append-only) | no |
| `propose-docs-home.py` | `PostToolUse` (Write\|Edit) | proposes the canonical home for a doc written outside it | no |
| `protect-generated.py` | `PreToolUse` (Write\|Edit) | **blocks** editing of generated target artifacts | **yes** |
| `run-validation.py` | `Stop` | calls the target's validation script on changed files and proposes the result | optional |

Each hook only runs if it is **wired** in `settings.json` (the snippet is a
fragment to *merge*, never to clobber). All hooks are **portable by
construction**: their target-specific inputs are derived in Step 1, and an empty
input makes the hook inert.

The full payload manifest and the gap → payload mapping are in the skill's
[`assets/README.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md)
and [`references/installation.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md).
