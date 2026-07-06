# claude-quenching

**Portable, self-contained knowledge-management method + installer for the Claude Code surface of *any* repository.**

> *"Most agent failures, examined honestly, are configuration failures."*
> — Google, *The New SDLC With Vibe Coding* (May 2026)

## The problem

An AI coding agent is only as good as what surrounds it — its **harness**: the
CLAUDE.md it loads, the docs it reads, the skills and hooks it runs. That
surrounding knowledge is where most of the leverage lives (and where most of the
failures come from), yet in most repositories it is ad-hoc: scattered, half-stale,
duplicated across files, or simply absent. Nobody owns it, so it rots. The
[Context](context/index.md) movement makes this case in full.

## The solution

`claude-quenching` is a Claude Code plugin that packages a single skill,
**`quenching-management`**. Point it at a repository and it treats that knowledge
surface as something to be *measured and maintained*. It:

1. **derives the repo's current shape** (read-only) — language, taxonomy, where each knowledge layer lives;
2. confronts it with a template of **15 dimensions** (CLAUDE.md, docs, vision, backlog, ADRs, skills, sub-agents, hooks, commands, memory, catalog, boundaries, conventions, guardrails, MCP);
3. delivers a **prioritized gap report** (Present / Partial / Drifted / Absent, with `file:line` evidence);
4. and — **with confirmation, item by item** — **installs the artifacts it carries** into the target's `.claude/` and `docs/`.

## The basic principle

The whole method turns on one axis: **audit-by-default + install-with-confirmation**.
The report always comes first and is read-only; installation is a separate, explicit,
item-by-item step. What it installs is a **single evolved source**, *adapted to your
repo's conventions* rather than imposed — and where your repo already has an
equivalent, it flags yours as **deprecable** instead of duplicating it, never
removing anything without your OK.

- **Self-contained** — everything it needs to audit and install ships inside the skill. No external dependency; runs on a repo from scratch.
- **Portable** — it doesn't impose a foreign structure: naming and paths adapt to the repo (where the repo has a *convention*, the repo wins), but the knowledge *structure* converges to the method's standard — the `docs/` home names follow a canonical taxonomy, and the agent-facing surface stays English (only human-only material and product code keep the repo's language). This [fixed-vs-adaptive line](method/architecture.md) is explicit throughout the docs.
- **Installer, not delegator** — it installs a single versioned source and flags pre-existing equivalents as **deprecable**; never duplicates silently, never removes without an OK.
- **Diagnosis-first** — the report always comes first; installation is an explicit second step.

## Who it's for — and who it's not

**It's for you if** you are preparing or auditing a repository's Claude Code
surface — a new repo you want to set up right, or an existing one whose CLAUDE.md,
docs, skills and hooks have drifted — or if your team is practicing *agentic
engineering* and wants the harness reviewed and versioned like any other config.

**It's not for you if** the repo is a throwaway you'll vibe-code once and discard
(there's no harness worth engineering), or if you want the *content and direction*
written for you. The method installs **structure and method, never content**:
three dimensions — vision, memory, boundary doctrine — it only ever *proposes*.
You write those.

## How to read this manual

The docs are one continuous read, in three movements — front matter carries a
prev/next chain so you can go straight through:

1. **Introduction** *(this page)* — the problem, the solution, the principle, and
   who it's for.
2. **[Context](context/index.md)** — the problem in depth. Why the harness is the
   work (grounded in a recent Google report), how a repo's knowledge surface rots,
   and the [15 dimensions](method/dimensions/index.md) as an anatomy of that
   surface — each with the research that justifies it.
3. **[Technical guide](plugin/install.md)** — everything to *use* the tool:
   [install & run](plugin/install.md), the [8-step workflow](plugin/workflow.md),
   the [architecture](method/architecture.md), the [bundled artifacts](plugin/artifacts.md),
   and the [repository layout](method/layout.md).

If you only want to run it, skip to the Technical guide. If you want to understand
*why it's shaped the way it is*, read the Context movement first.

## Quick start

```bash
claude --plugin-dir ./plugins/claude-quenching
```

Then describe the task (*"audit this repo's knowledge base"*, *"prepare this repo for Claude Code"*) or invoke the skill by name:

```
/claude-quenching:quenching-management
```

Maintainers evolving the method itself:
[CONTRIBUTING.md](https://github.com/holetz/claude-quenching/blob/main/CONTRIBUTING.md).
