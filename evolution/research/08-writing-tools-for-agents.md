# Writing effective tools for agents (Anthropic)

> Covers tool/skill design as a trigger contract, token efficiency in return values, actionable error messages, and agent-guided evaluation — directly feeds dimensions 6 (skills) and 7 (subagents) of the knowledge surface audit skill.

## Synthesis

The core of Anthropic's doctrine for agent tools can be summarized in one sentence: **descriptions are prompts, names are trigger contracts, and responses are tokens.** Every word in the name, description, and parameter documentation shapes whether the agent will call the right tool, at the right time, with the correct arguments. The official documentation recommends treating the description as the text you would write for a new team member — making implicit context explicit: specialized query formats, domain terminology, relationships between underlying resources. For a skill that **audits the knowledge surface of a repository**, this translates directly: each skill/tool exposed to the curator agent needs a description that precisely declares when it should be activated, which scenarios it covers, and which it does not.

The **description-as-trigger-contract** pattern also appears in the Agent Skills architecture: the `description` field of a `SKILL.md` YAML frontmatter is the only fragment loaded into the system prompt during startup (~100 tokens per skill). It is this text that Claude reads to decide whether to activate the skill — the equivalent of `tool.description` in the API. The progression is identical: lightweight metadata always present, full body only when activated, supplementary resources only when referenced. For the knowledge audit skill, this implies that the description must be a precise "trigger contract": listing the 14 surface types it knows, the linguistic signals that indicate the user wants to audit vs. edit vs. merely consult, and the limits of what it does not do.

Token efficiency is the second critical axis. The "Advanced Tool Use" post demonstrates that loading 5 MCP servers upfront consumes ~55k tokens before the first message. The solution — Tool Search with `defer_loading: true` — reduces this to ~500 tokens, preserving 95% of the context window. The same principle applies to any set of tools: pagination and filtering in return parameters, truncation with a notice, and the `response_format` enum pattern (CONCISE/DETAILED) allow the agent to control verbosity depending on the stage of the task. For the curator agent, which traverses multiple files and dimensions in sequence, this is fundamental: file-reading tools should return only the high-entropy fields (name, last modification, size, presence of key sections), not the full content.

Tool consolidation is the third principle. Instead of `read_claude_md`, `read_architecture_doc`, `read_skill_file` as separate tools, the canonical model groups them into a single tool with a `resource_type` parameter (enum). Fewer tools means less selection ambiguity. The opposite mistake — creating one tool per database action or per file type — produces "toolset bloat" that confuses the agent and wastes definition tokens. For the audit skill, the ideal design is to have a few powerful tools: one that reads any knowledge artifact with a section filter, one that checks for the presence/absence of elements, and one that produces the gaps report.

Actionable error messages are the fourth, often neglected, pillar. Instead of `ERROR: INVALID_INPUT`, the Anthropic pattern is to return: "Invalid date format. Use YYYY-MM-DD. Example: 2024-01-15." This eliminates an extra round of inference where the agent must self-correct. For audit tools, an error such as "Dimension 'ADR' not found in docs/adr/ — directory missing or empty" is orders of magnitude more useful than a stack trace. The same applies to empty results: include the narrowing suggestion.

Finally, the agent-guided evaluation cycle closes the loop: using Claude itself to analyze run transcripts and refactor descriptions. The "Writing tools for agents" post reports a 40% reduction in task completion time after a test agent rewrote descriptions to eliminate failure modes. For the knowledge management skill, this means building an evaluation harness with 3–5 realistic scenarios (repository without CLAUDE.md, skill without frontmatter, ADR implemented but not removed, boundaries dimension without a single home) and measuring hit rate, tokens consumed, and parameter error rate — iterating on descriptions until the numbers converge.

## Sources

**[Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)** — _engineering-anthropic · accessed 2026-06-28_

Anthropic Engineering's canonical post on designing tools for agents in production. Covers the central thesis that descriptions are prompts, and every word shapes agent behavior. Presents the complete cycle: service-prefix naming, description as contract, return format with configurable verbosity, actionable error messages, consolidation of multi-step operations, and iterative agent-guided evaluation.

- **Key techniques**:
  - Service prefix in name: `github_list_prs`, `slack_send_message` — no domain ambiguity
  - Description as onboarding guide: what it does, when to use it, when not to use it, what it returns — minimum 3–4 sentences
  - `response_format` enum CONCISE/DETAILED: ~1/3 token reduction in concise mode
  - Actionable error messages: "Use YYYY-MM-DD. Example: 2024-01-15" instead of opaque codes
  - Pagination with default 50 items; truncation with narrowing notice
  - Consolidate 5 specialized tools into 1 with an `action` parameter
  - Test agent that rewrites descriptions — 40% reduction in completion time

- Notable: "Namespacing choices have non-trivial effects on tool-use evaluations" — test variants before fixing the pattern.

Feeds: Dimension 6 (skill design as contract), 7 (subagent return format), 12 (boundary: each tool has a declared scope), 14 (guardrails: actionable error prevents self-correction loops)

---

**[Define tools — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/implement-tool-use)** — _official-anthropic · accessed 2026-06-28_

Official documentation for client-side tool definition: full schema (name, description, input_schema, input_examples), description best practices, `strict: true` field for guaranteed schema compliance, and `tool_choice` to control when tools are called. Includes contrasting examples of good vs. bad descriptions for the same tool.

- **Key techniques**:
  - `input_examples`: array of schema-validated objects — resolves complex format ambiguities
  - `strict: true`: guarantees the agent never generates parameters outside the defined schema
  - `additionalProperties: false` required for strict tools
  - Return semantic slugs/UUIDs, not opaque internal IDs
  - `tool_choice: auto/any/tool/none` — control the granularity of when tools are activated
  - Use Claude Opus for complex/ambiguous tools; Haiku for simple and deterministic tools

- Notable: `input_examples` cost 20–50 tokens for simple cases and 100–200 tokens for nested objects — use surgically only where there is real format ambiguity.

Feeds: Dimensions 6 (tool contract), 7 (subagent parameter schema)

---

**[Introducing advanced tool use on the Claude Developer Platform](https://www.anthropic.com/engineering/advanced-tool-use)** — _engineering-anthropic · accessed 2026-06-28_

Introduces three mechanisms for scale: Tool Search Tool (`defer_loading: true`) that reduces 55k definition tokens to ~500 tokens with a 49%→74% accuracy gain; Programmatic Tool Calling (20 calls in 1 code block, 37% fewer tokens); and Tool Use Examples (72%→90% accuracy on complex parameters). Defines the strategy of keeping 3–5 tools always loaded and deferring the rest.

- **Key techniques**:
  - `defer_loading: true`: tool excluded from system prompt; loaded only when Tool Search discovers it
  - Tool Search: 85% reduction in definition tokens; 95% of the context window preserved for real work
  - Programmatic Tool Calling: intermediate results stay in the execution environment, not in context
  - 1–5 realistic examples covering minimal/partial/full specification — +18pp accuracy
  - `allowed_callers`: restrict a tool to be callable only by code (code_execution) or directly

- Notable: 5 traditional MCP servers = ~55k tokens before the first message; with Tool Search + defer_loading = ~3k tokens for the tools relevant to the current context.

Feeds: Dimensions 6 (toolset efficiency), 7 (subagent loading architecture), 8 (tool discovery hooks)

---

**[Agent Skills — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)** — _official-anthropic · accessed 2026-06-28_

Official Agent Skills documentation: SKILL.md structure with YAML frontmatter (name + description required, max 1024 chars), 3-level progressive disclosure architecture (metadata ~100 tokens always; SKILL.md body only on activation; resources/scripts only when referenced), difference between skills and CLAUDE.md (skills cost ~100 tokens until activated — feasible to have 50 installed), and filesystem-based model where scripts execute without entering context.

- **Key techniques**:
  - YAML frontmatter: `description` must include WHAT it does AND WHEN to activate — trigger contract up to 1024 chars
  - Level 1 metadata (~100 tokens): only name + description — always loaded
  - Level 2 instructions (on demand): SKILL.md body < 5k tokens — only when activated
  - Level 3 resources (when referenced): scripts execute via bash without entering context
  - CLAUDE.md is always loaded; SKILL.md only when relevant — cost vs. specialization
  - Scripts are more efficient than instructions: only the output enters context, not the code

- Notable: The `description` in SKILL.md is the only text Claude reads to decide whether to activate the skill — it is equivalent to `tool.description` in the API. It must be as precise as a trigger contract.

Feeds: Dimensions 1 (CLAUDE.md vs Skills: what goes where), 6 (skill design), 7 (progressive disclosure), 12 (boundary: each level with its own cost and purpose)

---

**[Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)** — _engineering-anthropic · accessed 2026-06-28_

Engineering post on the design rationale for Agent Skills: the onboarding guide metaphor for a new team member, separation into three content types with differentiated loading, description as trigger contract, and best practices for iterative creation with Claude.

- **Key techniques**:
  - Onboarding guide metaphor: make implicit domain context explicit
  - Trigger contract: name + description are the only signal the agent uses to decide activation
  - Separate content into instructions (flexible), code (deterministic), resources (factual reference)
  - Start with an assessment of real gaps — do not create speculative skills
  - Iterate with Claude: monitor actual usage and adapt the description based on observed failures

- Notable: The amount of context embedded in a skill is effectively unlimited because files do not load until referenced — the real limit is what Claude needs to complete the task.

Feeds: Dimensions 6 (iterative skill design), 7 (discovery and progressive loading), 14 (design guardrails)

---

**[Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — _engineering-anthropic · accessed 2026-06-28_

Guide on context management for long tasks: toolset bloat as a common failure mode, the high-entropy return principle, just-in-time context loading, history compaction, and multi-agent architecture with subagents returning condensed 1–2k token summaries to the orchestrator.

- **Key techniques**:
  - Toolset bloat: if the engineer cannot define which tool to use in a given scenario, the agent will not be able to either
  - High entropy: return only what the agent needs to decide the next step
  - Just-in-time loading: keep lightweight identifiers (paths, UUIDs) and retrieve via tool calls
  - Compaction: preserve architectural decisions and unresolved bugs; discard redundant outputs
  - Subagents return condensed 1–2k token summaries to the orchestrator — not the full context
  - System prompts at the "right altitude": specific enough to guide, flexible enough not to constrain

- Notable: The tool usability test: if engineers cannot definitively specify which tool applies to a situation, the AI agent will fail in the same way.

Feeds: Dimensions 6 (toolset design), 7 (subagent return format), 12 (boundary: single home for each piece of information)

---

**[How we built our multi-agent research system — Anthropic Engineering](https://www.anthropic.com/engineering/multi-agent-research-system)** — _engineering-anthropic · accessed 2026-06-28_

Practical account of Anthropic's multi-agent research system: poor tool descriptions sent agents down wrong paths; a test agent rewrote descriptions yielding a 40% reduction in completion time; a filesystem artifact system for subagents to pass lightweight references; and explicit task instruction format for each subagent.

- **Key techniques**:
  - Test agent that uses tools and rewrites descriptions to eliminate failure modes — 40% reduction
  - Artifact system: subagents create outputs on the filesystem and pass lightweight references to the orchestrator
  - Subagents return a condensed 1–2k token summary — not the entire explored context
  - Task instructions must include: objective, output format, tools to use, task boundaries
  - Vague instructions cause subagents to duplicate work or misinterpret tasks
  - Parallelism: 3–5 simultaneous subagents with parallel tool calling (3+ tools at a time)

- Notable: The subagent's return format to the orchestrator must be explicitly specified in the task instruction — condensed summary + reference to the persisted artifact, never a full context dump.

Feeds: Dimensions 7 (subagent return format), 6 (tool description design), 12 (boundary: artifact vs. reference)

---

**[Structured outputs — Claude Platform Docs](https://platform.claude.com/docs/en/build-with-claude/structured-outputs)** — _official-anthropic · accessed 2026-06-28_

Documentation on structured outputs for agents: JSON Outputs via constrained sampling guarantees schema compliance without retries; `strict: true` on tools guarantees parameter validation; practical limits (20 strict tools, 24 optional parameters, 16 with union types); and recommended tool result pattern.

- **Key techniques**:
  - JSON Outputs: constrained sampling — eliminates retries due to schema violations
  - `strict: true` in tool definitions — Claude never generates parameters outside the schema
  - `additionalProperties: false` required for strict tools
  - Tool result pattern: `{success: bool, data: dict, error: str|null, metadata: dict}`
  - Grammar cache: first compilation adds latency; 24h cache on subsequent requests
  - SDKs automatically transform Pydantic/Zod to the supported subset

- Notable: Changes only to a tool's name or description do NOT invalidate the compiled grammar cache — only changes to the schema structure invalidate it. Useful for iterating on descriptions without latency penalties.

Feeds: Dimensions 6 (tool schema), 7 (guaranteed subagent return format)

---

**[Code execution with MCP: building more efficient AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/code-execution-with-mcp)** — _engineering-anthropic · accessed 2026-06-28_

Pattern of replacing direct MCP calls with code execution that processes data locally: real example of 150k → 2k tokens (98.7% reduction). Progressive tool discovery via filesystem; sensitive data stays in the sandbox; loops and conditionals in native code instead of tool call chains.

- **Key techniques**:
  - Code instead of direct tool calls: filter 10,000 lines locally, only the relevant ones enter context
  - Progressive tool discovery: agent navigates filesystem structure to find relevant tools
  - Sensitive data stays in the sandbox — PII never enters the model's context
  - Loops and conditionals in native code — more efficient than tool call chains
  - 150k tokens → 2k tokens in the Google Drive + Salesforce example

- Notable: This pattern is the extreme of the high-entropy principle: no intermediate data pollutes the context — only the filtered, relevant result is returned to the model.

Feeds: Dimensions 6 (toolset design with filtering), 7 (subagent returns only what is relevant), 8 (sandbox execution pattern)

---

**[Tool reference — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/tool-reference)** — _official-anthropic · accessed 2026-06-28_

Complete reference for optional tool properties: `cache_control`, `strict`, `defer_loading`, `allowed_callers`, `input_examples`, `eager_input_streaming`. Table of Anthropic tools with versions (`_YYYYMMDD`) and execution mode (server vs. client). Explains how `defer_loading + cache_control` are complementary.

- **Key techniques**:
  - `defer_loading: true` + `cache_control`: deferred tools do not appear in the cached prefix — adding new tools does not invalidate the existing cache
  - `allowed_callers: ['code_execution_20260120']`: tool only callable by code, not directly by the model
  - Versioning `_YYYYMMDD`: old versions keep working; new version only when behavior/schema changes
  - `eager_input_streaming`: fine-grained streaming of tool inputs while Claude is still generating the response

- Notable: `defer_loading + cache_control` is the ideal pattern for large toolsets in production: add hundreds of tools with no initial token cost and without invalidating the existing cache.

Feeds: Dimensions 6 (advanced toolset configuration), 7 (control over which tool each caller can invoke), 8 (cache hook integration)

---

**[Building Effective AI Agents — Anthropic Research](https://www.anthropic.com/research/building-effective-agents)** — _official-anthropic · accessed 2026-06-28_

Guide to effective agent patterns: ACI (Agent-Computer Interface) deserving the same design rigor as HCI, poka-yoke in tool arguments (switching from relative to absolute paths eliminated an entire class of errors), format close to the web's natural structure, and the principle of starting simple.

- **Key techniques**:
  - ACI (Agent-Computer Interface) deserves the same design rigor as HCI
  - Poka-yoke: restructure arguments to make errors harder (e.g., absolute vs. relative filepath)
  - Format close to the web's natural structure — minimum cognitive overhead for the model
  - Test tools with multiple sample inputs and iterate based on observed errors
  - Start simple: add complexity only when demonstrably necessary

- Notable: Switching from relative to absolute filepath as a tool parameter eliminated an entire class of errors — parameter design, not just the description, directly affects the agent's error rate.

Feeds: Dimensions 6 (parameter design), 7 (subagent design), 14 (poka-yoke error guardrails)

---

**[Token-saving updates — Anthropic](https://claude.com/blog/token-saving-updates)** — _official-anthropic · accessed 2026-06-28_

Token efficiency updates for tool use: token-efficient tools (header `token-efficient-tools-2025-02-19`) reduces output tokens by up to 70% (average 14% observed in production); `text_editor` tool for surgical edits that reduces tokens and latency vs. full rewrites.

- **Key techniques**:
  - Header `token-efficient-tools-2025-02-19`: up to 70% reduction in output tokens for tool use
  - `text_editor` tool: surgical edits instead of full rewrites — lower cost and latency
  - Combined strategy: prompt caching + token-efficient tools + cache-aware rate limits

- Notable: The average reduction observed in production was 14% — the 70% figure is the theoretical ceiling. Plan for the average case when projecting token budgets.

Feeds: Dimensions 6 (toolset efficiency in production), 7 (cost of subagents with tools)

## How this feeds the method's evolution

- **Dimension 6 — Description as trigger contract**: Introduce a specific smell to audit skills: "description without a clause for when NOT to use". Every audit skill must explicitly declare the limits of its scope (e.g., "does not cover VISION or open ADRs"). The quality criterion for "good" is: the description allows the agent to decide activation without reading the skill body.

- **Dimension 7 — Subagent return format**: Add to the method the canonical return pattern: `{success, data, error|null, metadata}` with a condensed 1–2k token summary + reference to a persisted artifact. No subagent should return a full context dump. Detect violations by comparing the size of the subagent's output with the total size of the context it consumed.

- **Dimension 12 — Boundary: single home for each piece of information**: The toolset bloat test becomes an audit criterion: "if two files on the knowledge surface answer the same question, there is a boundary violation". Tools with overlapping scope are the toolset equivalent of information duplication across dimensions.

- **Dimension 6 — Agent-guided evaluation cycle**: Add to the method's evolution workflow an evaluation harness step with 3–5 realistic scenarios, measuring hit rate, tokens consumed, and parameter error rate. The curator agent must be evaluated with the same rigor as any production tool. Minimum metrics: accuracy per audited dimension, tokens per dimension, false-negative rate (undetected gaps).

- **Dimension 1 — CLAUDE.md as map vs. Skills as specialization**: The method must include an explicit criterion for where each type of knowledge goes: CLAUDE.md is always loaded (~fixed cost), skills are loaded on demand (~100 fixed tokens + body when activated). Knowledge the agent needs for every task goes in CLAUDE.md; domain-specific knowledge goes in a skill. Audit whether there is content in CLAUDE.md that should be in a skill (indicates the map is bloated).

- **Dimension 14 — Guardrails: actionable error as tool quality standard**: Introduce the "actionable error" test as a tool quality guardrail: simulate every possible invalid parameter and verify whether the returned error message allows the agent to self-correct without calling the tool again. Opaque errors (codes, stack traces) are a smell of a poorly designed tool that generates costly retry loops.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of the sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **10**.

The set is of generally high quality: 10 of the 12 sources are accessible, exist, and faithfully reflect their content. All Anthropic Engineering and platform.claude.com URLs are working and recent (2024–2025). The two issues found are partial mischaracterization, not fabrication: the Agent Skills overview page is broader than the summary suggests, and the tool result pattern is presented as recommended when it is merely an illustrative example. No source was identified as fabricated, stale, or with a non-existent URL.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview | `mischaracterized` | The summary describes the page as focused on Claude Code Agent Skills with SKILL.md/YAML frontmatter and 3-level progressive disclosure, but the overview page is much broader: it covers pre-built skills (PowerPoint, Excel, Word, PDF), integration via API, claude.ai, and Claude Code, and the filesystem/VM architecture. The 3-level structure described in the summary is correct for Claude Code, but the ... |
| https://platform.claude.com/docs/en/build-with-claude/structured-outputs | `mischaracterized` | The summary presents the tool result pattern '{success, data, error?, metadata}' as a canonical recommendation from the documentation, but the page does not recommend it as a standard — it only displays an example use case with similar fields (status/data/errors/metadata), which differs from what the summary claims. The field name output_config.format is correct. The limits (20 strict tools, 24 optional params, 16... |
