# claude-quenching (plugin)

> **Portable, self-contained knowledge-management method + installer for the Claude Code surface of any repository.**

This is the **distributed plugin**. It packages a single skill, **`quenching-management`**: point it at a repository and it audits the repo's knowledge surface across **15 dimensions**, returns a **prioritized gap report**, and — **with confirmation, item by item** — **installs the artifacts it carries** ([`skills/quenching-management/assets/`](skills/quenching-management/assets/)) into the target's `.claude/` and `docs/`.

## What's inside

| Path | What it is |
| --- | --- |
| [`.claude-plugin/plugin.json`](.claude-plugin/plugin.json) | Plugin manifest (identity, version, metadata) |
| [`skills/quenching-management/SKILL.md`](skills/quenching-management/SKILL.md) | The operational instructions the agent runs (the 8 audit/install steps) |
| [`skills/quenching-management/references/`](skills/quenching-management/references/) | The dense operational detail each step consults |
| [`skills/quenching-management/assets/`](skills/quenching-management/assets/) | The **installable payloads** (template skills, worker sub-agents, hooks, doc skeletons, frontmatter templates) |

The **only active surface** of this plugin is the `quenching-management` skill. The payloads under `assets/` are **inert** — they are not auto-discovered as live skills/hooks; they ship with the plugin and are copied/adapted into the target repo's `.claude/` during installation.

## Use

Load locally from the repo root:

```bash
claude --plugin-dir ./plugins/claude-quenching
```

Then describe the task (*"audit this repo's knowledge base"*) or invoke the skill by name:

```
/claude-quenching:quenching-management
```

## Full documentation

The human-facing overview, the system architecture, the 15 dimensions and the 8-step workflow live in the project's **MkDocs documentation site** (built from the repository's `docs/`). See the repository root [`README.md`](../../README.md) for how to build and serve it.
