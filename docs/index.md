# claude-quenching

**Portable, self-contained knowledge-management method + installer for the Claude Code surface of *any* repository.**

`claude-quenching` is a Claude Code plugin that packages a single skill,
**`quenching-management`**. Point it at a repository and it:

1. **derives the repo's current shape** (read-only) — language, taxonomy, where each knowledge layer lives;
2. confronts it with a template of **15 dimensions** (CLAUDE.md, docs, vision, backlog, ADRs, skills, sub-agents, hooks, commands, memory, catalog, boundaries, conventions, guardrails, MCP);
3. delivers a **prioritized gap report** (Present / Partial / Drifted / Absent, with `file:line` evidence);
4. and — **with confirmation, item by item** — **installs the artifacts it carries** into the target's `.claude/` and `docs/`.

## Why it's different

- **Self-contained** — everything it needs to audit and install ships inside the skill. No external dependency; runs on a repo from scratch.
- **Portable** — it adapts artifacts to the repo's own conventions; where the repo already has a convention, the repo wins.
- **Installer, not delegator** — it installs a single versioned source and flags pre-existing equivalents as **deprecable**; never duplicates silently, never removes without an OK.
- **Diagnosis-first** — the report always comes first; installation is an explicit second step.

## Quick start

```bash
claude --plugin-dir ./plugins/claude-quenching
```

Then describe the task (*"audit this repo's knowledge base"*, *"prepare this repo for Claude Code"*) or invoke the skill by name:

```
/claude-quenching:quenching-management
```

## Where to go next

| You want… | Read |
| --- | --- |
| The full picture of what it is and the scenarios | [Method → Overview](method/overview.md) |
| How the parts fit together as a system | [Method → Architecture](method/architecture.md) |
| The coverage checklist | [Method → The 15 dimensions](method/dimensions.md) |
| What the agent actually runs | [Method → The 8-step workflow](method/workflow.md) |
| Install and use the plugin | [Plugin → Install & use](plugin/install.md) |
| What ships in the package | [Plugin → Bundled artifacts](plugin/artifacts.md) |
| How the method itself evolves | [Evolving the method](evolving/index.md) |
