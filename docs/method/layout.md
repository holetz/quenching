# Repository layout

This repository is **two things at once**, and the split governs the layout:

1. a **Claude Code plugin marketplace** that hosts a single plugin,
   `claude-quenching`;
2. the **development workspace** for that plugin — its evolution log, maintainer
   agents and documentation-site source.

**The only thing ever shipped to a user is
[`plugins/claude-quenching/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching).**
The marketplace `source` points only there. Everything else —
[`evolution/`](https://github.com/holetz/claude-quenching/tree/main/evolution),
[`.claude/agents/`](https://github.com/holetz/claude-quenching/tree/main/.claude/agents),
[`docs/`](https://github.com/holetz/claude-quenching/tree/main/docs) — is
**maintainer tooling: versioned, but never delivered**.

> Every link on this page points to the **actual file or folder on GitHub**, not
> to a documentation page — this is the map of the repository as it exists on
> disk.

---

## The tree

```text
claude-quenching/
├── .claude-plugin/
│   └── marketplace.json          # marketplace manifest — source → plugins/claude-quenching/ only
├── plugins/
│   └── claude-quenching/         # ┓ THE SHIPPED PLUGIN — the only delivered artifact
│       ├── README.md             # ┃
│       └── skills/
│           └── quenching-management/
│               ├── SKILL.md      # ┃ the 8-step operational roadmap
│               ├── references/   # ┃ per-step operational detail (consulted on demand)
│               └── assets/       # ┛ inert installable payloads (skills, agents, hooks, …)
│
├── .claude/
│   └── agents/                   # ┓ MAINTAINER TOOLING — never shipped, never installed
│       ├── quenching-evolutionist.md  # ┃ advances the method one round per invocation
│       └── quenching-reviewer.md      # ┃ critiques/refines an existing definition
├── evolution/                    # ┃ the method's history (the shipped skill is present-only)
│   ├── README.md                 # ┃ the spine: anchors, exclusion index, backlog, queue
│   ├── log/                      # ┃ verbose detail, one file per dimension/theme
│   └── research/                 # ┃ cited research input (every round needs ≥1 source)
├── docs/                         # ┃ this MkDocs site source
│   ├── index.md                  # ┃
│   ├── method/                   # ┃ architecture · dimensions · workflow · this page
│   └── plugin/                   # ┃ install · bundled artifacts
│                                 # ┛
├── CLAUDE.md                     # guidance for Claude Code working in this repo
├── CONTRIBUTING.md               # canonical doctrine for evolving the method
├── README.md                     # repo entry point
├── mkdocs.yml                    # docs-site config
├── Makefile                      # docs-site scripts (uv-managed)
├── pyproject.toml / uv.lock      # pinned docs toolchain
└── .github/                      # CI (auto-deploys the docs site)
```

---

## The shipped plugin

Everything a user receives lives under
[`plugins/claude-quenching/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching).
The skill itself has three layers:

| Path | What it is |
| --- | --- |
| [`SKILL.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md) | the **operational instructions** the agent loads when the skill fires (Steps 1–8); kept present-tense and lean, with detail pushed to `references/` |
| [`references/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/references) | per-step operational detail consulted on demand (see its [`README.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/README.md)) |
| [`assets/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets) | the **inert installable payloads** the method stamps into a target (see its [`README.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/README.md)) |

### `references/` — the operational detail

| File | What it is |
| --- | --- |
| [`dimensions-template.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/dimensions-template.md) | the **15 dimensions** — purpose · "good" · detection · smells · remediation · payload |
| [`detection-and-smells.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/detection-and-smells.md) | the detection **cookbook**: adaptive globs/greps per dimension + the rule of 4 states |
| [`docs-taxonomy.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/docs-taxonomy.md) | the canonical `docs/` taxonomy (single source of home names) |
| [`scripts-taxonomy.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/scripts-taxonomy.md) | the canonical `scripts/` organization (single source of the tree) |
| [`repo-profiles.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md) | catalog of **repo profiles** (signals → emphasis) that Step 4 consults |
| [`report-format.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/report-format.md) | skeleton of the **report** (scorecard · gaps · deprecables · plan) |
| [`installation.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/references/installation.md) | the **gap → payload** map + deprecation doctrine and `docs/` convergence |

### `assets/` — the installable payloads

| Path | What it installs |
| --- | --- |
| [`skills/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/skills) | the template skills (`quenching-map`, `quenching-docs`, `quenching-standards`, `quenching-announcement`, `quenching-skills`, `quenching-config`, `quenching-guardrails`, `quenching-roadmap`) |
| [`agents/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/agents) | the **worker** sub-agents only — `quenching-auditor` and `quenching-writer` |
| [`hooks/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/hooks) | the 6 lifecycle/tool-event hooks + the `settings.json` snippet to merge |
| [`commands/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/commands) | the on-demand re-audit command (`quenching-reaudit/`, installs as a skill) |
| [`docs/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/docs) | the canonical `docs/` taxonomy skeletons (only the homes that apply) |
| [`scripts/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/scripts) | the purpose-based `scripts/` scaffold (README-map + placeholders) |
| [`templates/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/templates) | `claude/`, `docs/` and `memory/` frontmatter/body templates |

> The **maintainer agents** (`quenching-evolutionist` / `quenching-reviewer`)
> live only at [`.claude/agents/`](https://github.com/holetz/claude-quenching/tree/main/.claude/agents)
> and are **never** under `assets/` — `assets/agents/` ships only the two worker
> payloads above.

---

## The maintainer workspace (never shipped)

| Path | What it is |
| --- | --- |
| [`.claude/agents/`](https://github.com/holetz/claude-quenching/tree/main/.claude/agents) | the two **dev-only** maintainer agents — [`quenching-evolutionist.md`](https://github.com/holetz/claude-quenching/blob/main/.claude/agents/quenching-evolutionist.md) (advances the frontier) and [`quenching-reviewer.md`](https://github.com/holetz/claude-quenching/blob/main/.claude/agents/quenching-reviewer.md) (refines what exists) |
| [`evolution/`](https://github.com/holetz/claude-quenching/tree/main/evolution) | the method's **history** — [`README.md`](https://github.com/holetz/claude-quenching/blob/main/evolution/README.md) (the spine), [`log/`](https://github.com/holetz/claude-quenching/tree/main/evolution/log) (per-theme detail), [`research/`](https://github.com/holetz/claude-quenching/tree/main/evolution/research) (cited input) |
| [`CONTRIBUTING.md`](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md) | the canonical doctrine for **evolving** the method — not needed to use the plugin |
| [`docs/`](https://github.com/holetz/claude-quenching/tree/main/docs) | the source of **this site** (it documents the plugin for its users; it does not re-document the evolution flow) |

To evolve the method, invoke a maintainer agent rather than hand-editing the
skill — see [`CONTRIBUTING.md`](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md).
