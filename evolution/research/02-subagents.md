# Claude Code Subagents — design, tool scope and orchestration

> Covers how to design, configure and chain sub-agents in Claude Code: frontmatter, minimum-privilege tools, context isolation and decision criteria between sub-agent, skill, hook and agent team — feeds Dimension 7 (sub-agents) and the «skills vs sub-agents vs commands — decision guide» boundary of the `quenching-management` skill.

## Synthesis

Sub-agents in Claude Code are isolated Claude instances that the main agent delegates to for executing specific tasks. Each sub-agent runs in its own context window with its own system prompt, independent tool permissions, and a configurable model. The central isolation mechanism is that all intermediate output (logs, search results, file content) stays in the sub-agent's context; only the final summary returns to the main conversation. This is fundamental for a skill that audits knowledge surfaces: the scan and extraction work — potentially verbose — happens in isolation, and the main agent receives only the condensed diagnostic.

The anatomy of a sub-agent is defined in a Markdown file with YAML frontmatter. The mandatory fields are `name` (unique identifier in lowercase-hyphens) and `description` (the automatic delegation criterion used by Claude to decide when to trigger the sub-agent). Optional fields cover: `tools` (allowlist), `disallowedTools` (denylist), `model` (alias: `haiku`, `sonnet`, `opus`, `fable`; or full model ID; default: `inherit`), `permissionMode`, `maxTurns`, `skills` (pre-loads skill content into the sub-agent's context on initialization), `mcpServers` (scopes MCP servers exclusively to this sub-agent), `hooks` (local lifecycle), `memory` (cross-session persistence: `user`/`project`/`local`), `isolation: worktree` (isolated git clone) and `background`. The Markdown file body becomes the sub-agent's system prompt, which does *not* receive the full Claude Code system prompt — only its own prompt plus environment details.

The tool-scoping decision is the core of secure design: if `tools` is omitted, the sub-agent inherits all tools available in the parent session. For a repository audit sub-agent (reading CLAUDE.md, architecture docs, backlog, ADRs, skills), the minimum viable set is `tools: Read, Grep, Glob` without any write permissions. This implements the minimum-privilege principle and prevents accidental modifications during scanning. Sub-agents can also be nested up to 5 levels deep (from v2.1.172), allowing an orchestrator to spawn multiple specialized workers; the depth level is counted from the main conversation and is not configurable.

The boundary between sub-agents, skills, hooks, and agent teams defines the decision guide for a curator skill. Skills run in the main context and are appropriate when the operator needs to see and direct each audit step. Sub-agents are the right mechanism when the task produces verbose output that would pollute the main context (e.g., scanning 50 architecture files, listing gaps in 14 dimensions). Hooks are deterministic and non-AI — suitable for validating or blocking actions before/after tools. Agent teams (experimental) add direct agent-to-agent communication and a shared task list, with significantly higher token overhead; they only pay off when workers need to challenge each other's findings, which exceeds the scope of a standard audit. The operational rule is: start with skills for the procedure, add hooks for enforcement, use sub-agents when output volume or permission isolation matters.

For the `quenching-management` skill, the practical pattern is a scan sub-agent (`model: haiku`, `tools: Read, Grep, Glob`, `permissionMode: plan`) that receives as its task the mapping of the repository's 14 dimensions and returns a structured diagnostic. The main agent — running on Sonnet or Opus — interprets the diagnostic and decides which surgical evolutions to make. The `skills` field in the sub-agent's frontmatter allows pre-injecting the current contract of each dimension (e.g., the `arq-codebase-design` skill), preventing the sub-agent from having to rediscover the evaluation vocabulary on each run. The `memory: project` field accumulates cross-session discoveries in `.claude/agent-memory/<name>/`, building an incremental knowledge base of the repository that makes subsequent audits more accurate and faster.

## Sources

**[Create custom subagents — Claude Code Docs (official)](https://code.claude.com/docs/en/sub-agents)** — _official-anthropic · accessed 2026-06-28_

Canonical sub-agent documentation: all frontmatter fields, storage scopes, built-in sub-agents (Explore/Plan/General-purpose), invocation, nesting up to 5 levels, fork vs. named sub-agent, context return and common usage patterns.

**Key techniques:**
- `name` + `description` are mandatory; all other fields are optional
- `tools` defines allowlist; `disallowedTools` defines denylist; if both, denylist is applied first
- `model: haiku` for cheap reading; `sonnet` for analysis; `opus` for complex reasoning
- `isolation: worktree` for parallel edits without file collisions
- `skills` pre-loads skill content into the sub-agent's context on initialization (not just makes available)
- `memory: project` accumulates cross-session knowledge in `.claude/agent-memory/<name>/`
- Hooks in frontmatter (`PreToolUse`, `PostToolUse`, `Stop`) scoped to sub-agent
- `mcpServers` inline to isolate MCP servers outside the main context
- `Agent(worker, researcher)` in tools restricts which sub-agents can be spawned by the sub-agent
- Fork inherits the entire conversation and reuses parent's prompt cache; named sub-agent starts with fresh context

**Notable:** The sub-agent receives ONLY its own system prompt plus environment details — NOT the full Claude Code system prompt. Explore and Plan are the only sub-agents that skip CLAUDE.md and git status to keep research fast and cheap.

Feeds: Dimension 7 (sub-agents), Dimension 12 (boundary: skills vs sub-agents vs commands), Dimension 6 (skills), Dimension 8 (hooks)

---

**[Orchestrate teams of Claude Code sessions — Agent Teams Docs (official)](https://code.claude.com/docs/en/agent-teams)** — _official-anthropic · accessed 2026-06-28_

Official Agent Teams documentation (experimental): architectural difference between sub-agents (only report to parent) and agent teams (peer-to-peer communication, shared task list, mailbox), ideal use cases, recommended team size, and current limitations.

**Key techniques:**
- Sub-agents: results return only to parent; agent teams: direct communication between agents
- 3-5 teammates as the sweet spot; 5-6 tasks per teammate avoids excessive context switching
- Reuse of sub-agent definitions as teammate roles (`tools` + `model` applied; `skills`/`mcpServers` not)
- `TeammateIdle` hook: exit code 2 keeps teammate working (programmatic quality gate)
- Token cost scales linearly with number of active teammates

**Notable:** Agent teams add significantly higher token cost vs. sub-agents for the same results in sequential tasks; use agent teams only when workers need to challenge each other's findings (competing hypotheses, multi-lens review).

Feeds: Dimension 7 (sub-agents), Dimension 12 (decision boundary)

---

**[Steering Claude Code: skills, hooks, subagents and more — Anthropic Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)** — _official-anthropic · accessed 2026-06-28_

Official post introducing the Claude Code steering ecosystem and establishing the boundary between skills, sub-agents, and hooks.

**Key techniques:**
- Skills = procedure visible in main context; sub-agents = condensed result in isolation
- Hooks = deterministic automation; sub-agents = intelligent delegation to a separate Claude instance
- Action-oriented description is Claude's automatic routing criterion for delegation
- Sub-agents can be nested up to 5 levels deep

**Notable:** The canonical phrase for the usage criterion: «Use a sub-agent when a side task such as deep search, log analysis or dependency auditing would flood your main conversation with intermediate results you won't reference again.»

Feeds: Dimension 7 (sub-agents), Dimension 6 (skills), Dimension 12 (decision boundary)

---

**[Best practices for Claude Code sub-agents — PubNub Blog](https://www.pubnub.com/blog/best-practices-for-claude-code-sub-agents/)** — _community · accessed 2026-06-28_

Practical guide with a 3-stage pipeline (pm-spec, architect-review, implementer-tester), per-agent Definition of Done, and detailed anti-patterns.

**Key techniques:**
- 3-stage pipeline: pm-spec (criteria + open questions) → architect-review (ADR + guardrails) → implementer-tester (code + passing tests)
- HITL (human-in-the-loop): if criteria are ambiguous, sub-agent asks numbered questions and waits
- `SubagentStop` + `Stop` hooks as stage gatekeepers with human paste-through
- PM/Architect: read-heavy tools (`Read`, `Grep`, `WebSearch`); Implementer: `Edit`, `Write`, `Bash`
- Slugs in commit messages and queue statuses as audit trail

**Notable:** Critical anti-pattern: omitting `tools` in frontmatter implicitly grants all available tools — always whitelist explicitly for specialized sub-agents.

Feeds: Dimension 7 (sub-agents), Dimension 8 (hooks), Dimension 12 (decision boundary)

---

**[Claude Code Subagents: The Complete Guide to AI Agent Delegation — Medium](https://medium.com/@sathishkraju/claude-code-subagents-the-complete-guide-to-ai-agent-delegation-d0a9aba419d0)** — _community · accessed 2026-06-28_

Complete reference with examples of real definitions and a decision matrix: sub-agent vs. skill vs. hook vs. main conversation.

**Key techniques:**
- repo-explorer pattern: `tools: [Read, Grep, Glob]`, `model: haiku`, `permissionMode: plan`
- `disallowedTools: Edit, Write` to guarantee read-only in audit agents
- `memory: project` for cross-session codebase knowledge accumulation
- Sub-agents do NOT inherit skills from parent; declare explicitly in `skills` field for preloading
- Parallel research: spawn multiple sub-agents for independent modules simultaneously

**Notable:** Ideal profile for knowledge surface auditing: `tools: [Read, Grep, Glob]` + `disallowedTools: [Edit, Write, Bash]` + `model: haiku`.

Feeds: Dimension 7 (sub-agents), Dimension 12 (decision boundary), Dimension 6 (skills)

---

**[Claude Code: Hooks, Subagents, and Skills — Complete Guide — DEV Community](https://dev.to/owen_fox/claude-code-hooks-subagents-and-skills-complete-guide-hjm)** — _community · accessed 2026-06-28_

Complete guide covering all frontmatter fields with a reference table, forked sub-agents vs. named ones, and over-isolation and context bloat anti-patterns.

**Key techniques:**
- If both `tools` and `disallowedTools` are defined, denylist is applied first
- Fork inherits the entire conversation — appropriate when sub-agent would need a lot of background to be useful
- `context: fork` in skill injects content into the specified agent (inverse of `skills` field in sub-agent)
- Over-isolation anti-pattern: don't use sub-agent when task requires frequent iterative feedback
- Context bloat anti-pattern: if sub-agent summary rivals main conversation in complexity, isolation failed

**Notable:** Fork reuses parent prompt cache (first request cheaper than fresh sub-agent for tasks that need the same context).

Feeds: Dimension 7 (sub-agents), Dimension 6 (skills), Dimension 12 (decision boundary)

---

**[Claude Code Advanced Patterns: Skills, Fork, and Subagents — RanketAI](https://www.ranketai.com/en/blog/explainer-claude-code-skills-fork-subagents-2026-03-31)** — _community · 2026-03-31_

March 2026 article detailing how skills, fork, and sub-agents connect and defining the transition criterion for fork/sub-agents.

**Key techniques:**
- Adoption sequence: skills first → hooks for enforcement → sub-agents for isolation
- `context: fork` in skill = same logic running in isolated context without duplicating sub-agent file
- Transition criterion: context drift in long sessions combining exploration + implementation + review
- Slash commands and skills unified since 2026: `.claude/commands/` and `.claude/skills/` behave identically, skills take precedence

**Notable:** Confirms that the commands and skills unification in 2026 means that `initialPrompt` in sub-agents and `context: fork` in skills are the modern mechanisms for auto-invocation and isolation.

Feeds: Dimension 6 (skills), Dimension 7 (sub-agents), Dimension 12 (decision boundary), Dimension 9 (commands)

---

**[Building effective agents — Anthropic Engineering](https://www.anthropic.com/engineering/building-effective-agents)** — _engineering-anthropic · accessed 2026-06-28_

Anthropic's canonical guide on agent architecture: five workflows, when to use agents vs. simple workflows, and tool design principles.

**Key techniques:**
- Orchestrator-Workers: central LLM dynamically delegates to workers and synthesizes results
- Parallelization: sectioning (simultaneous subtasks) vs. voting (multiple perspectives for greater confidence)
- Tool engineering: extensive documentation with examples and edge cases; poka-yoke prevents incorrect use
- Exhaust simple solutions (single LLM call) before moving to agents
- Agents for open-ended problems where steps cannot be predicted in advance

**Notable:** Anthropic spent more time optimizing tools than prompts when building their SWE-bench agent — strong signal that tool documentation and design is the most critical investment in multi-agent systems.

Feeds: Dimension 7 (sub-agents), Dimension 14 (guardrails), Dimension 12 (decision boundary)

---

**[The evolution of agentic surfaces: building with Claude Managed Agents — Anthropic Blog](https://claude.com/blog/building-with-claude-managed-agents)** — _official-anthropic · accessed 2026-06-28_

Architectural vision of Claude Managed Agents: decoupled architecture (harness separate from sandbox), three primary resources, credential management via Vaults.

**Key techniques:**
- Decoupled architecture: harness (orchestrator) separate from sandbox (execution) for security
- Credentials in Vaults with envelope encryption — never in the agent's sandbox
- Sessions persist full event history with append-only log (clean pause/resume)
- Containers start in parallel while Claude begins reasoning immediately

**Notable:** The harness behavior evolves alongside model improvements — context resets designed for earlier models became unnecessary, allowing developers to focus on domain expertise.

Feeds: Dimension 7 (sub-agents), Dimension 14 (guardrails)

---

**[Claude Code Agents In 2026: Agent View, Subagents, Teams, And What Parallel Sessions Actually Cost — CloudZero](https://www.cloudzero.com/blog/claude-code-agents/)** — _community · accessed 2026-06-28_

Comparative cost and performance analysis of three parallelism modes: sub-agents, agent teams, and background agents via Agent View.

**Key techniques:**
- Dynamic Workflows (June 2026): orchestrator plans and spawns dozens-to-hundreds of sub-agents in parallel in a single session
- 3-5 concurrent sub-agents as sweet spot — beyond that, merge time exceeds parallelism savings
- Agent View: monitor for independent background sessions (different from sub-agents within a session)
- Token cost: sub-agents < agent teams (linear per teammate)

**Notable:** Dynamic Workflows of June 2026 allow the orchestrator agent to plan and spawn dozens to hundreds of sub-agents in parallel in a single session without specifying each architectural detail in advance.

Feeds: Dimension 7 (sub-agents), Dimension 12 (decision boundary)

---

**[Claude Code Subagents: How to Create, Use, and Debug Them — Builder.io](https://www.builder.io/blog/claude-code-subagents)** — _community · accessed 2026-06-28_

Practical guide with examples of complete definitions and three invocation methods with specific use cases.

**Key techniques:**
- Three invocation methods: natural language (Claude decides), @-mention (guaranteed for one task), `--agent` (session-wide default)
- `PreToolUse` hooks in frontmatter for conditional validation (e.g., block SQL writes in db-reader with exit code 2)
- `permissionMode: plan` for read-only exploration/audit sub-agents
- `disallowedTools: mcp__github` to remove all tools from a specific MCP server

**Notable:** db-reader example with PreToolUse hook validating SQL queries demonstrates how hooks in frontmatter allow fine control beyond what the `tools` field offers — useful for sub-agents with `Bash` that need to restrict specific operations.

Feeds: Dimension 7 (sub-agents), Dimension 8 (hooks), Dimension 12 (decision boundary)

## How it feeds the method evolution

- **Dimension 7 (sub-agents) — new audit sub-agent pattern**: create `.claude/agents/knowledge-auditor.md` with `tools: Read, Grep, Glob`, `model: haiku`, `permissionMode: plan`, `memory: project`, `skills: [arq-codebase-design]` and body instructing scan of the 14 dimensions with return of a structured diagnostic. The `skills` field injects the evaluation vocabulary at initialization, eliminating rediscovery per run.

- **Dimension 12 («skills vs sub-agents vs commands» boundary) — sharper decision criterion**: document the operational criterion in three questions: (1) Would intermediate output pollute the main context? → sub-agent. (2) Does the operator need to see and direct each step? → skill. (3) Must the action be deterministically blocked/validated? → hook. Add to the guide the fork vs. named sub-agent distinction: fork for tasks that need existing background (reuses prompt cache); named sub-agent for pre-defined roles with fresh context.

- **Dimension 6 (skills) — new smell of skill candidate for sub-agent**: a skill that generates verbose output (file scanning, log analysis, dependency inventory) is a candidate for `context: fork` or conversion to sub-agent. The signal is: if the intermediate result won't be referenced again in the main conversation, the work should be isolated.

- **Dimension 8 (hooks) — hooks × sub-agents integration as quality gates**: use `SubagentStart`/`SubagentStop` in `settings.json` for quality enforcement at the session level (e.g., run lint/validate at the end of each implementation sub-agent). Use `PreToolUse` in the sub-agent frontmatter for specific restrictions (e.g., block writes in audit sub-agents even if Bash is needed for other purposes).

- **Dimension 7 (sub-agents) — tool inheritance anti-pattern to document as smell**: absence of the `tools` field in a sub-agent is a critical smell — it means implicit inheritance of all parent session tools, violating least privilege. The audit skill should detect files in `.claude/agents/` without `tools` or `disallowedTools` explicitly declared and flag as risk.

- **Dimension 7 (sub-agents) — precedence hierarchy for distributed team sub-agent design**: document the model resolution order (`CLAUDE_CODE_SUBAGENT_MODEL` env > per-invocation parameter > frontmatter > inherited model) and the scope hierarchy (managed settings > CLI --agents > .claude/agents/ > ~/.claude/agents/ > plugin agents/) as part of the reproducibility contract for sub-agents versioned in the repository.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **7**.

The set has a solid foundation: 7 of the 11 sources are accessible and their summaries adequately reflect the actual content. The 4 problematic sources are not non-existent or fabricated URLs — all pages exist and are relevant to the topic — but the summaries attribute specific claims (code examples, numerical metrics, specific techniques) that do not appear in the published article, suggesting the summary was enriched with inferred content or confused between sources. The main risk in this set is mischaracterization through excessive specificity, not URL fabrication. The Anthropic Engineering source (building-effective-agents) and the two official code.claude.com docs are the most reliable and precisely verifiable.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://medium.com/@sathishkraju/claude-code-subagents-the-complete-guide-to-ai-agent-delegation-d0a9aba419d0 | `mischaracterized` | The sub-agent examples cited in the summary (repo-explorer, code-reviewer, debugger) don't match the actual article content, which uses dependency-auditor, test-runner, and researcher. The claim that «sub-agents don't inherit skills from parent» and the «decision matrix» are also not in the text. The article is real and accessible, but the summary describes different content from what is published. |
| https://www.cloudzero.com/blog/claude-code-agents/ | `mischaracterized` | The article exists (published 2026-05-18) but doesn't mention «Dynamic Workflows of June 2026» or the «3-5 sub-agents as sweet spot» threshold. The summary attributes to the article content that isn't in it — probably inferred or fabricated. What the article covers is cost comparison between modes and model tiering recommendation (Opus/Sonnet), not a parallelism threshold. |
| https://code.claude.com/docs/en/agent-teams | `mischaracterized` | The «~7x tokens vs sub-agents» overhead cited in the summary does not appear on the official page — documentation says only «significantly more tokens» without citing a multiple. The specific numerical claim appears fabricated. The rest of the summary (peer-to-peer, TeammateIdle, 3-5 teammates, skills/mcpServers not applied to teammates) is correct. |
| https://www.builder.io/blog/claude-code-subagents | `mischaracterized` | The example of «db-reader with PreToolUse hook validating SQL» doesn't appear in the actual article. The three invocation methods are mentioned partially but not as an explicitly defined set. The article uses «pr-reviewer» instead of «code-reviewer». The actual content is more restricted than the summary suggests. |
