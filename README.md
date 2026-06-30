# claude-quenching

> **Portable, self-contained knowledge-management method + installer for the Claude Code surface of *any* repository.**

This repository is **two things at once**:

1. A **Claude Code plugin marketplace** ([`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json)) hosting the single plugin **`claude-quenching`**.
2. The **development workspace** for that plugin — its evolution log, maintainer agents, and documentation source.

The distributed plugin lives entirely under [`plugins/claude-quenching/`](plugins/claude-quenching/); everything else in this repo (`evolution/`, `.claude/agents/`, `docs/`) is **maintainer tooling that is never shipped to users**.

## What the plugin does

Point it at a repository and it reads what already exists (`CLAUDE.md`, `docs/`, skills, subagents, hooks, commands, memory, catalog, MCP), confronts it with a template of **15 dimensions**, hands back a **prioritized gap report**, and — **with confirmation, item by item** — **installs the artifacts it carries** into the target's `.claude/` and `docs/`.

- **Self-contained** — everything the method needs to audit and install lives inside the skill, under [`assets/`](plugins/claude-quenching/skills/quenching-management/assets/). It depends on no external skill and runs on a repo from scratch.
- **Portable** — it first derives the target repo's shape (language, prefix taxonomy, where each layer lives) and adapts the artifacts to it.
- **Installer, not delegator** — where the repo already has an artifact doing the same job, it installs the package's single source and flags the pre-existing one as **deprecable**; it never duplicates silently and never removes without an explicit OK.
- **Diagnosis-first** — the report always comes first; installation is a separate, explicit, confirmed step.

## Documentation

The full, navigable method documentation (overview, architecture, the 15 dimensions, the 8-step workflow, and how the method evolves) is published as a **MkDocs Material** site, built from [`docs/`](docs/). The toolchain is managed with [`uv`](https://docs.astral.sh/uv/) and pinned in [`pyproject.toml`](pyproject.toml)/`uv.lock`:

```bash
make docs-serve     # sync + serve with live reload at http://127.0.0.1:8000
make docs-build     # strict static build into ./site
make docs-deploy    # publish to GitHub Pages (gh-pages branch)
make docs-update    # upgrade the pinned docs dependencies
```

`make help` lists every script. Each target runs through `uv` (e.g. `uv run mkdocs serve`), so no global Python install is touched. While this repository is **private**, GitHub Pages publishing is gated; the site always builds and serves locally.

## Quick start (local)

Load the plugin straight from this repo:

```bash
claude --plugin-dir ./plugins/claude-quenching
```

Then trigger it by describing the task (*"audit this repo's knowledge base"*, *"prepare this repo for Claude Code"*) or invoke the skill by name:

```
/claude-quenching:quenching-management
```

Run `/help` to confirm **only** `quenching-management` is listed as an active skill (the bundled payloads under `assets/` are not auto-discovered). After edits, reload with `/reload-plugins`.

## Install from the marketplace

This repo doubles as its own marketplace. Once you have access to it on GitHub:

```
/plugin marketplace add israelholetz/claude-quenching
/plugin install claude-quenching@claude-quenching
```

Refresh later with `/plugin marketplace update claude-quenching`.

## Repository layout

| Path | Shipped? | What it is |
| --- | --- | --- |
| [`plugins/claude-quenching/`](plugins/claude-quenching/) | ✅ **yes** | The distributed plugin: manifest + the `quenching-management` skill (`SKILL.md` + `references/` + `assets/` payloads) |
| [`.claude-plugin/marketplace.json`](.claude-plugin/marketplace.json) | — | Marketplace catalog (`source: "./plugins/claude-quenching"`) |
| [`evolution/`](evolution/) | ❌ no | The method's R&D log — evolution rounds + research notes ([spine](evolution/README.md)) |
| [`.claude/agents/`](.claude/agents/) | ❌ no | The maintainer meta-agents (`quenching-evolutionist`, `quenching-reviewer`) that evolve the method in *this* repo |
| [`docs/`](docs/) | ❌ no | Source of the MkDocs documentation site |

Because the marketplace `source` points only at `plugins/claude-quenching/`, the `evolution/`, `.claude/agents/` and `docs/` siblings are **versioned in the repo but never delivered to a user**.

## For maintainers

The method is **alive** — it is improved over time by two meta-agents, with a traceable log:

- **[`quenching-evolutionist`](.claude/agents/quenching-evolutionist.md)** advances the frontier (one new round at a time).
- **[`quenching-reviewer`](.claude/agents/quenching-reviewer.md)** critiques and refines what already exists.

The full evolution doctrine, the round/research log, and how to run the eval fixtures are in [`CONTRIBUTING.md`](CONTRIBUTING.md) and the [`evolution/`](evolution/) spine. **Do not edit the method by hand outside this flow** — it would break the log that keeps the method from re-attacking solved problems.

## Authors

- **Israel Holetz**
- **Gabriel Groehs** — <https://gabriel-groehs.github.io/>

## License

[MIT](LICENSE) © 2026 Israel Holetz and Gabriel Groehs.
