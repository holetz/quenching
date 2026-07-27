# Change log — `standards/`

History of the standards bundle, most recent first. Each entry is grouped under a
`## YYYY-MM-DD` heading and prefixed `**Creation**` / `**Update**` / `**Deprecation**`.

## 2026-07-26

**Creation**: [Plugin layout — what may live under `commands/`](/docs/standards/architecture/plugin-layout.md) — `commands/**` is the only tree Claude Code registers, so everything that is not an entry point lives under `assets/` and is cited by `${CLAUDE_PLUGIN_ROOT}` absolute path (`authority: current` — the collapse migration proved it).

**Update**: [Command surface naming](/docs/standards/naming/command-surface.md), [Command authoring and alignment](/docs/standards/automation/skills.md), [Always-on context budget](/docs/standards/automation/context-budget.md) — the skill↔wrapper pair is retired; the command path is the identity. §Why the wrapper still exists is replaced by the trigger it fired, and the budget is re-derived at 2,083 characters from the collapsed surface.

**Update**: `resource` globs repointed off the deleted `plugins/quenching/skills/` tree in [skill-evaluation.md](/docs/standards/automation/skill-evaluation.md), [bundle-verification.md](/docs/standards/quality/bundle-verification.md), [plan-artifacts.md](/docs/standards/workflows/plan-artifacts.md) and [task-execution.md](/docs/standards/workflows/task-execution.md) — the validator reported all four as `resource-unresolved`.

## 2026-07-06

**Creation**: `standards/` home scaffolded by `quenching` — subject subfolders
established, `index.md` seeded with the derived-listing markers.
