# claude-quenching

> **Portable, self-contained knowledge-management method + installer for the Claude Code surface of *any* repository.**

`claude-quenching` is a Claude Code plugin that packages a single skill, **`quenching-management`**. Point it at a repository and it:

1. **derives the repo's current shape** (read-only) — language, taxonomy, where each knowledge layer lives;
2. confronts it with a template of **15 dimensions** (CLAUDE.md, docs, vision, backlog, ADRs, skills, sub-agents, hooks, commands, memory, catalog, boundaries, conventions, guardrails, MCP);
3. delivers a **prioritized gap report** (Present / Partial / Drifted / Absent, with `file:line` evidence);
4. and — **with confirmation, item by item** — **installs the artifacts it carries** into the target's `.claude/` and `docs/`.

## Why it's different

- **Self-contained** — everything it needs to audit and install ships inside the skill. No external dependency; runs on a repo from scratch.
- **Portable** — it doesn't impose a foreign structure: naming, language and paths adapt to the repo (where the repo has a *convention*, the repo wins), while the knowledge *structure* converges to the method's standard.
- **Installer, not delegator** — it installs a single versioned source and flags pre-existing equivalents as **deprecable**; never duplicates silently, never removes without an OK.
- **Diagnosis-first** — the report always comes first; installation is an explicit second step.

## Install

This repository doubles as its own marketplace. Once you have access to it on GitHub:

```
/plugin marketplace add israelholetz/claude-quenching
/plugin install claude-quenching@claude-quenching
```

Refresh later with `/plugin marketplace update claude-quenching`.

> While the repository is **private**, only accounts with read access (and an authenticated `gh`/git locally) can add the marketplace.

To run it straight from a clone instead, load it as a local plugin directory:

```bash
claude --plugin-dir ./plugins/claude-quenching
```

## Use

Trigger the method by describing the task — *"audit this repo's knowledge base"*, *"prepare this repo for Claude Code"*, *"see what's missing from the knowledge base"* — or invoke the skill by name:

```
/claude-quenching:quenching-management
```

Run `/help` to confirm that **only** `quenching-management` is listed as an active skill. The method audits first and hands back the gap report; installation is a separate, explicit step that only touches your `.claude/`/`docs/` after your OK, item by item.

## Documentation

The full method documentation — architecture, the 15 dimensions, the 8-step workflow, the repository layout, and how to install & use the plugin — is published as a **MkDocs Material** site:

**<https://holetz.github.io/claude-quenching/>**

## Contributing

The method is **alive** — it is advanced over time through a traceable evolution log and two maintainer skills. See [`CONTRIBUTING.md`](CONTRIBUTING.md) before proposing a change.

## Authors

- **Israel Holetz**
- **Gabriel Groehs** — <https://gabriel-groehs.github.io/>

## License

[MIT](LICENSE) © 2026 Israel Holetz and Gabriel Groehs.
