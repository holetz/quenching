# Evolution boundaries → sources (map for the `quenching-evolutionist` agent)

> This is the catalog entry file. The [`quenching-evolutionist`](../../.claude/agents/quenching-evolutionist.md) agent makes **one** evolution per round and requires **≥1 citable source (URL + date)**. Here each candidate boundary from the [spine](../README.md) points to the catalog file(s) and anchor sources (prioritized by official tier). **Read the source before citing it** — adversarial verification (notes at the end of each angle file) has already flagged inaccurate characterizations.


## Candidate boundaries (from the evolution backlog) → catalog


### MCP Coverage

- **What to extract:** New dimension/check for connected MCP servers (`.mcp.json`, local/project/user scopes, tool allowlist, server instructions, security/prompt-injection).
- **Catalog files:** [06-mcp.md](06-mcp.md)
- **Anchor sources:**
  - [Connect Claude Code to tools via MCP — Claude Code Docs](https://code.claude.com/docs/en/mcp) — _Official Anthropic · accessed 2026-06-28_
  - [Control MCP server access for your organization — Claude Code Docs](https://code.claude.com/docs/en/managed-mcp) — _Official Anthropic · accessed 2026-06-28_
  - [Security — Claude Code Docs](https://code.claude.com/docs/en/security) — _Official Anthropic · accessed 2026-06-28_

### Trigger optimization (subtrigger)

- **What to extract:** How to measure and write the `description` to fire on the right phrases; evals/variation; exclusion clauses; delegating to `skills-skill-creator`.
- **Catalog files:** [13-skill-description-evals.md](13-skill-description-evals.md) · [01-agent-skills.md](01-agent-skills.md)
- **Anchor sources:**
  - [Skill authoring best practices - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — _Official Anthropic · accessed 2026-06-28_
  - [Agent Skills overview - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — _Official Anthropic · accessed 2026-06-28_
  - [Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills) — _Official Anthropic · accessed 2026-06-28_

### Skills vs sub-agents vs commands — decision guide

- **What to extract:** When to use each artifact; context isolation; composition (`context: fork`, sub-agent with pre-loaded skills).
- **Catalog files:** [02-subagents.md](02-subagents.md) · [05-slash-commands.md](05-slash-commands.md) · [01-agent-skills.md](01-agent-skills.md) · [09-building-effective-agents.md](09-building-effective-agents.md)
- **Anchor sources:**
  - [Create custom subagents — Claude Code Docs (official)](https://code.claude.com/docs/en/sub-agents) — _Official Anthropic · accessed 2026-06-28_
  - [Orchestrate teams of Claude Code sessions — Agent Teams Docs (official)](https://code.claude.com/docs/en/agent-teams) — _Official Anthropic · accessed 2026-06-28_
  - [Steering Claude Code: skills, hooks, subagents and more — Anthropic Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — _Official Anthropic · accessed 2026-06-28_

### Boundary detection by heuristic

- **What to extract:** Transform dimension 12 (comparative reading) into concrete checks; DRY/single-source-of-truth applied to docs; one canonical home per piece of information.
- **Catalog files:** [12-knowledge-architecture-external.md](12-knowledge-architecture-external.md) · [07-context-engineering.md](07-context-engineering.md)
- **Anchor sources:**
  - [Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — _Anthropic Engineering · 2025-09-29_
  - [Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — _Anthropic Engineering · 2025-10-16_
  - [Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents) — _Anthropic Engineering · 2024-12-19_

### Memory hygiene

- **What to extract:** Persistent memory criteria: dedup, what to (not) store, indexing, frontmatter, structured note-taking.
- **Catalog files:** [11-memory-management.md](11-memory-management.md)
- **Anchor sources:**
  - [Memory tool - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) — _Official Anthropic · accessed 2026-06-28_
  - [Context engineering: memory, compaction, and tool clearing - Claude Cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — _Official Anthropic · accessed 2026-06-28_
  - [Managing context on the Claude Developer Platform - Anthropic News](https://claude.com/blog/context-management) — _Official Anthropic · accessed 2026-06-28_

### Progressive disclosure / context budget

- **What to extract:** Sharper 'good' criterion for SKILL.md/CLAUDE.md size and when to split into `references/`; just-in-time vs pre-load; context rot.
- **Catalog files:** [07-context-engineering.md](07-context-engineering.md) · [01-agent-skills.md](01-agent-skills.md) · [04-claude-md-memory.md](04-claude-md-memory.md)
- **Anchor sources:**
  - [Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — _Official Anthropic · accessed 2026-06-28_
  - [Introducing Agent Skills — Claude Blog](https://claude.com/blog/skills) — _Official Anthropic · 2025-10-16_
  - [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) — _Official Anthropic · accessed 2026-06-28_

### AGENTS.md / cross-tool interoperability

- **What to extract:** Dimension for Codex/Gemini/Cursor via `claude-to-agents`; symlink/copy/inline-chain strategies; single source across tools.
- **Catalog files:** [10-agents-md-interop.md](10-agents-md-interop.md) · [04-claude-md-memory.md](04-claude-md-memory.md)
- **Anchor sources:**
  - [How Claude remembers your project — Claude Code Docs (official)](https://code.claude.com/docs/en/memory) — _Official Anthropic · accessed 2026-06-28_
  - [Best practices for Claude Code — Claude Code Docs (official)](https://code.claude.com/docs/en/best-practices) — _Official Anthropic · accessed 2026-06-28_
  - [Set up Claude Code in a monorepo or large codebase — Claude Code Docs (official)](https://code.claude.com/docs/en/large-codebases) — _Official Anthropic · accessed 2026-06-28_

### OKF — catalog as compliant bundle + knowledge interop (not just behavior)

- **What to extract:** Make `docs/catalog/` (already concept-per-file + identity-by-path) an **OKF-compliant bundle** — additive `type`/`resource`/`timestamp` in the `_table`/`_schema`/`_system` molds, `log.md` for history; classify frontmatter of docs as REQUIRED×RECOMMENDED and **preserve unknown keys**; `quenching-to-okf` export payload (analogue of `claude-to-agents`, but for knowledge/world-state). Sharp boundary doctrine: **prescriptive on contract/interop, permissive on the rest** (AGENTS.md=behavior × OKF=world-state). **Limit:** do not dilute the canonical taxonomy (OKF does not resolve cross-producer semantics); no dependency on Google tooling; OKF is a moving target v0.1.
- **Catalog files:** [15-okf-google.md](15-okf-google.md) · [12-knowledge-architecture-external.md](12-knowledge-architecture-external.md) · [10-agents-md-interop.md](10-agents-md-interop.md)
- **Anchor sources:**
  - [knowledge-catalog/okf/SPEC.md — GoogleCloudPlatform (spec v0.1)](https://github.com/GoogleCloudPlatform/knowledge-catalog/blob/main/okf/SPEC.md) — _Official/open spec · accessed 2026-06-29_
  - [How the Open Knowledge Format can improve data sharing — Google Cloud Blog](https://cloud.google.com/blog/products/data-analytics/how-the-open-knowledge-format-can-improve-data-sharing) — _Official Google Cloud · 2026-06-12_
  - [OKF FAQ — okf.md/faq (OKF × AGENTS.md × llms.txt × MCP)](https://okf.md/faq/) — _Primary · accessed 2026-06-29_


## Inverted index — Dimension (1–14) → sources that inform it

> Derived from the `feeds_frontiers` field of each source. Useful when a round wants to sharpen a specific template dimension.


**Dimension 1 — Map (CLAUDE.md)** (3 source(s))
  - [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) — _Official Anthropic_ · angle `agent-skills`
  - [How Claude remembers your project - Claude Code Docs (Memory)](https://code.claude.com/docs/en/memory) — _Official Anthropic_ · angle `memory-management`
  - [Steering Claude Code: skills, hooks, subagents and more - Claude Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — _Official Anthropic_ · angle `skill-description-evals`

**Dimension 2 — Current architecture** (0 source(s))
  - _no direct source in this catalog (candidate for next enrichment)._

**Dimension 3 — Direction (VISION)** (0 source(s))
  - _no direct source in this catalog (candidate for next enrichment)._

**Dimension 4 — Backlog** (0 source(s))
  - _no direct source in this catalog (candidate for next enrichment)._

**Dimension 5 — ADR** (0 source(s))
  - _no direct source in this catalog (candidate for next enrichment)._

**Dimension 6 — Skills** (17 source(s))
  - [Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — _Official Anthropic_ · angle `agent-skills`
  - [Agent Skills — Claude Platform Docs (Overview)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — _Official Anthropic_ · angle `agent-skills`
  - [Introducing Agent Skills — Claude Blog](https://claude.com/blog/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Agent Skills in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Steering Claude Code: skills, hooks, subagents and more - Claude Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — _Official Anthropic_ · angle `skill-description-evals`

**Dimension 7 — Sub-agents** (5 source(s))
  - [Agent Skills — Claude Platform Docs (Overview)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — _Official Anthropic_ · angle `agent-skills`
  - [Agent Skills in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — _Anthropic Engineering_ · angle `agent-skills`
  - [Effective context engineering for AI agents - Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — _Anthropic Engineering_ · angle `memory-management`
  - [Scaling Managed Agents: Decoupling brain from hands - Anthropic Engineering](https://www.anthropic.com/engineering/managed-agents) — _Anthropic Engineering_ · angle `memory-management`

**Dimension 8 — Hooks** (5 source(s))
  - [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Context engineering: memory, compaction, and tool clearing - Claude Cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — _Official Anthropic_ · angle `memory-management`
  - [How Claude remembers your project - Claude Code Docs (Memory)](https://code.claude.com/docs/en/memory) — _Official Anthropic_ · angle `memory-management`
  - [Agent Skills overview - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — _Official Anthropic_ · angle `skill-description-evals`
  - [Scaling Managed Agents: Decoupling brain from hands - Anthropic Engineering](https://www.anthropic.com/engineering/managed-agents) — _Anthropic Engineering_ · angle `memory-management`

**Dimension 9 — Commands** (1 source(s))
  - [Effective harnesses for long-running agents - Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — _Anthropic Engineering_ · angle `memory-management`

**Dimension 10 — Memory** (11 source(s))
  - [Memory tool - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) — _Official Anthropic_ · angle `memory-management`
  - [Context engineering: memory, compaction, and tool clearing - Claude Cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools) — _Official Anthropic_ · angle `memory-management`
  - [Managing context on the Claude Developer Platform - Anthropic News](https://claude.com/blog/context-management) — _Official Anthropic_ · angle `memory-management`
  - [Context windows - Claude Platform Docs](https://platform.claude.com/docs/en/docs/build-with-claude/context-windows) — _Official Anthropic_ · angle `memory-management`
  - [How Claude remembers your project - Claude Code Docs (Memory)](https://code.claude.com/docs/en/memory) — _Official Anthropic_ · angle `memory-management`
  - [Effective context engineering for AI agents - Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — _Anthropic Engineering_ · angle `memory-management`

**Dimension 11 — Data/domain catalog** (0 source(s))
  - _no direct source in this catalog (candidate for next enrichment)._

**Dimension 12 — Boundary doctrine** (7 source(s))
  - [Memory tool - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool) — _Official Anthropic_ · angle `memory-management`
  - [Managing context on the Claude Developer Platform - Anthropic News](https://claude.com/blog/context-management) — _Official Anthropic_ · angle `memory-management`
  - [Agent Skills overview - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) — _Official Anthropic_ · angle `skill-description-evals`
  - [Steering Claude Code: skills, hooks, subagents and more - Claude Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more) — _Official Anthropic_ · angle `skill-description-evals`
  - [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills) — _Anthropic Engineering_ · angle `agent-skills`
  - [Skill Authoring Patterns from Anthropic's Best Practices — Generative Programmer](https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics) — _Community_ · angle `agent-skills`

**Dimension 13 — Conventions** (4 source(s))
  - [Introducing Agent Skills — Claude Blog](https://claude.com/blog/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Skill authoring best practices - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices) — _Official Anthropic_ · angle `skill-description-evals`
  - [Agent Skills specification - agentskills.io](https://agentskills.io/specification) — _Spec / open standard_ · angle `skill-description-evals`
  - [The SKILL.md Pattern: How to Write AI Agent Skills That Actually Work](https://bibek-poudel.medium.com/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-72a3169dd7ee) — _Community_ · angle `skill-description-evals`

**Dimension 14 — Behavioral guardrails** (2 source(s))
  - [Agent Skills in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills) — _Official Anthropic_ · angle `agent-skills`
  - [Claude Agent Skills: A First Principles Deep Dive — Lee Han Chung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/) — _Community_ · angle `agent-skills`


## How to run a round using this catalog

1. Open the spine (`../README.md`), read the `current-round` anchor and the exclusion list.
2. Choose a boundary **not yet addressed** above. Open the catalog file(s) pointed to.
3. **Read** the anchor sources (do not cite from memory). Check the «⚠️ Verification notes» at the end of the angle file.
4. Make **one** surgical evolution in `SKILL.md`/template; record the round with URL + date.
5. If the research is outdated, **enrich** the catalog (see `README.md`) before evolving.
