# Persistent memory management for agents (Anthropic)

> Covers official cross-session memory primitives (Memory Tool, Auto Memory, compaction, context editing), memory hygiene (dedup, expiration, provenance, scope), and the boundary "each piece of information has a unique home"; primarily serves dimension 10 (memory) and the memory hygiene boundary of the `quenching-management` skill.

## Synthesis

Anthropic consolidated, between September 2025 and April 2026, a persistent memory model for agents structured around three complementary primitives: **Memory Tool** (cross-session persistence via files in `/memories`), **Context Editing / Tool Result Clearing** (surgical removal of obsolete tool_result blocks from the active context) and **Compaction** (server-side summarization of conversation history). The published performance data are significant: the combination of all three primitives delivers 39% improvement on complex multi-step tasks, context editing alone delivers 29%, and in web research workflows with 100 turns there was an 84% reduction in token consumption — what previously resulted in total failure now completes successfully. The unifying principle is "find the smallest set of high-signal tokens that maximizes the probability of the desired outcome", treating context as a finite resource with diminishing returns (*context rot*: measurable degradation of recall as context grows, amplified by the "lost-in-the-middle" effect with a drop of over 30% accuracy for information buried in the middle of long conversations).

The **Memory Tool** operates client-side: Claude emits file operation requests (view, create, str_replace, insert, delete, rename), and the application executes against developer-controlled storage (local filesystem, database, cloud storage). The system prompt is automatically injected with the instruction "ALWAYS check your memory directory before anything", ensuring the agent retrieves previous state at the start of each task. The recommended organization pattern is hierarchical: a progress file (what was done, what comes next), a feature checklist with status flags, and topic files by domain. What **not** to store: raw conversation transcripts, literal tool outputs (re-fetchable), intermediate reasoning steps (transient). Hygiene requires using `str_replace` to update existing records instead of accumulating duplicates, expiration of unaccessed files, size control, and mandatory path traversal protection on every command.

In **Claude Code** specifically, the memory surface has two pillars: CLAUDE.md (written by the user, rules and persistent instructions, versioned in the repo) and Auto Memory (written by Claude during sessions, in `~/.claude/projects/<project>/memory/`, machine-local). Auto Memory uses an index file `MEMORY.md` (200-line / 25KB limit at initial load) as an entry point, with topic files loaded on demand. The four types of Auto Memory entries are: **user** (user behavioral preferences), **feedback** (response style guidance), **project** (project context and constraints) and **reference** (lookup facts). The critical boundary is: CLAUDE.md contains what any team member would need to know (versioned, shared via git); Auto Memory contains what the agent discovered during work (local, auditable, editable). Information that already exists in the repository should not be duplicated in memory — it should be referenced via link or `@path` import. Instructions in CLAUDE.md should be specific and verifiable (target: fewer than 200 lines per file); behaviors that must run at fixed lifecycle events belong in hooks, not in CLAUDE.md instructions.

**Memory hygiene** is the most fragile boundary of the system. The smells identified by the literature: (1) accumulation of duplicates — corrected with `str_replace` instead of `create`; (2) memory as a duplicated repo — the same information in CLAUDE.md and in the code; (3) entries without provenance — no date, no origin session, no reliability indication; (4) degraded freshness — expired facts that poison future context ("context poisoning by staleness"); (5) silent conflict between contradictory entries — invisible last-write-wins; (6) incorrect scope — per-workspace memory leaking between agents. The Claude Code Auto Dream system implements automated cyclic hygiene: trigger at 24h + 5 new sessions, converts vague temporal references to exact dates, resolves contradictions, removes obsolete entries and maintains the index within the limit. This process is the analog, on the memory plane, of what the `quenching-management` skill does on the repository plane.

For a **knowledge surface audit skill** for a repository, the implications are direct: (a) the boundary "each piece of information has a unique home" should include a specific smell — "does this memory entry replicate something that already exists in the repo?" — with a verifiable criterion; (b) dimension 10 (memory) needs a cyclic hygiene protocol with checklist: dedup, expiration, provenance, scope; (c) CLAUDE.md should be treated as a context resource with token cost (target: fewer than 200 lines per file, specific and verifiable instructions); (d) the distinction CLAUDE.md-for-team-rules vs. Auto-Memory-for-agent-learnings must be documented as boundary doctrine; and (e) hooks are the correct mechanism for behaviors that must run at fixed lifecycle events — not instructions in CLAUDE.md.

## Sources

**[Memory tool — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)** — _official-anthropic · accessed 2026-06-28_

Complete official Memory Tool documentation: how it works (client-side, commands view/create/str_replace/insert/delete/rename), file organization pattern, automatically injected system prompt, security (path traversal), integration with compaction and context editing, multi-session pattern for software development, and SDKs with helpers (BetaLocalFilesystemMemoryTool).

- **Key techniques:**
  - `/memories` file as client-side developer-controlled storage
  - Auto-injection of "view memory before any task" instruction in system prompt
  - Multi-session pattern: initializer session + progress log + feature checklist
  - `str_replace` for dedup-free updates; `delete`/`rename` for hygiene
  - `exclude_tools: ['memory']` in context editing to not clear memory results
  - Mandatory path traversal protection on every command
  - Periodic expiration of unaccessed files
- **Notable:** The injected system prompt says: "ASSUME INTERRUPTION: Your context window might be reset at any moment, so you risk losing any progress that is not recorded in your memory directory." — operational reinforcement that memory is the only durable state between sessions.
- Feeds: dimension 10 (memory), memory hygiene boundary, dimension 12 (boundaries)

---

**[Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — _engineering-anthropic · accessed 2026-06-28_

Anthropic engineering blog article defining context engineering as the evolution beyond prompt engineering for sophisticated agents. Covers context rot, Goldilocks zone of the system prompt, just-in-time context retrieval, structured note-taking, compaction, sub-agents with clean context, and the "smallest set of high-signal tokens" principle.

- **Key techniques:**
  - Context rot: recall degradation as context grows (mechanism: n² pairwise relationships in transformers)
  - Just-in-time context retrieval: keep lightweight identifiers (paths, URLs) and load data on demand
  - Structured note-taking with external NOTES.md file not in context
  - Compaction for conversational workflows; note-taking for iterative development; multi-agent for parallel research
  - Sub-agents return condensed 1000-2000 token summaries to coordinator
  - System prompt in the Goldilocks zone: neither too rigid nor too vague
- **Notable:** Published principle: "find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome" — directly applicable to CLAUDE.md and MEMORY.md design.
- Feeds: dimension 10 (memory), dimension 7 (sub-agents), memory hygiene boundary

---

**[Context engineering: memory, compaction, and tool clearing — Claude Cookbook](https://platform.claude.com/cookbook/tool-use-context-engineering-context-engineering-tools)** — _official-anthropic · accessed 2026-06-28_

Official cookbook with complete code examples for the three primitives: compaction (`compact_20260112`, minimum 50K token trigger, custom instructions), tool result clearing (`clear_tool_uses_20250919`, keep N most recent, `exclude_tools`), and memory tool (complete Python handler with path traversal protection). Includes diagnostic table for when to use each primitive and a well-structured memory file template.

- **Key techniques:**
  - Compaction with custom instructions: specify what to preserve (quantitative data, architectural decisions)
  - `exclude_tools: ['memory']` to not clear memory results in clearing
  - Division of responsibilities: clearing for re-fetchable, compaction for dialogue/reasoning, memory for cross-session persistence
  - Memory file template: Status, Findings by Topic, Unresolved sections
  - What NOT to write: literal tool outputs, intermediate reasoning steps, redundant copies
  - Diagnostic table: observation → root cause → solution
- **Notable:** Published performance numbers: memory + context editing = 39% boost; context editing alone = 29%; 84% token reduction in a 100-turn web search evaluation.
- Feeds: dimension 10 (memory), memory hygiene boundary, dimension 8 (hooks/context management)

---

**[Managing context on the Claude Developer Platform — Anthropic News](https://claude.com/blog/context-management)** — _official-anthropic · accessed 2026-06-28_

Official announcement of context management tools (context editing + memory tool). Details what to store in memory (critical insights, debugging decisions, architectural findings, intermediate results, project state) vs. what to keep in the active context (active conversation, current tool interactions).

- **Key techniques:**
  - Explicit separation: memory = what must survive between sessions; context = what is needed now
  - Use cases: long coding tasks, research with accumulated knowledge base, workflows that exceed token limits
  - Client-side architecture: developer controls storage backend
- **Notable:** Real adoption results: Netflix, Rakuten, Wisedocs, Ando; Rakuten and Wisedocs reported 97% reduction in first-pass errors — evidence that memory prevents repeated errors more than it stores static information.
- Feeds: dimension 10 (memory), memory hygiene boundary, dimension 12 (boundaries)

---

**[Context windows — Claude Platform Docs](https://platform.claude.com/docs/en/docs/build-with-claude/context-windows)** — _official-anthropic · accessed 2026-06-28_

Official documentation on context windows: definition of context rot, behavior of progressive token accumulation, management with compaction (primary approach) and context editing (specialized), context awareness in Sonnet 4.6/4.5/Haiku 4.5 models.

- **Key techniques:**
  - Context rot: more context is not automatically better — accuracy degrades with growth
  - Context awareness: Claude Sonnet 4.6+ receives token budget updates after each tool call via `<system_warning>`
  - Thinking blocks are automatically stripped from context in subsequent turns (no token cost)
  - Compaction as primary approach; context editing for specialized needs
- **Notable:** Claude Sonnet 4.6 receives remaining budget after each tool call — context awareness as a native feature that allows the agent to self-manage context.
- Feeds: dimension 10 (memory), memory hygiene boundary

---

**[How Claude remembers your project — Claude Code Docs](https://code.claude.com/docs/en/memory)** — _official-anthropic · accessed 2026-06-28_

Official Claude Code documentation on the two-layer memory system: CLAUDE.md (written by user, rules and instructions, versioned) and Auto Memory (written by Claude, learnings and patterns, machine-local). Details scopes, hierarchical loading rules, `.claude/rules/` with path-specific rules via YAML frontmatter, 200-line / 25KB limit for MEMORY.md, and the `/memory` command for auditing.

- **Key techniques:**
  - CLAUDE.md: target fewer than 200 lines per file; specific and verifiable instructions
  - Auto Memory in `~/.claude/projects/<project>/memory/` with MEMORY.md as index (200 lines / 25KB)
  - Four types of Auto Memory: user, feedback, project, reference
  - Path-specific rules via YAML frontmatter in `.claude/rules/`
  - HTML comments `<!-- -->` in CLAUDE.md are stripped before injecting into context (notes for maintainers without token cost)
  - `claudeMdExcludes` to skip CLAUDE.md from other teams in monorepos
  - Hooks are the correct mechanism for behaviors that must run at fixed events — not instructions in CLAUDE.md
- **Notable:** Critical boundary documented: CLAUDE.md contains what any team member would need to know (shared via git); Auto Memory contains what the agent discovered (local, auditable). Duplicating between the two is a smell.
- Feeds: dimension 10 (memory), dimension 1 (CLAUDE.md as map), memory hygiene boundary, dimension 8 (hooks)

---

**[Effective harnesses for long-running agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** — _engineering-anthropic · accessed 2026-06-28_

Engineering article on harnesses for long-running agents. Recommends a two-phase pattern: Initializer Agent (sets up memory infrastructure the first time) and Coding Agent (executes with state recovery). Details progress log, JSON feature checklist, startup protocol, and incremental commit requirement.

- **Key techniques:**
  - Initializer session: sets up memory files before any substantive work
  - Progress log as recovery mechanism: each session reads the log to restore state without re-exploring codebase
  - JSON feature checklist with status flags: work on one feature at a time
  - Standardized startup protocol: pwd, progress log, git history, feature file, basic tests
  - Git commits with descriptive messages as complement to memory
- **Notable:** A feature is only marked complete AFTER end-to-end verification, not when the code is written — prevents inaccurate progress log between sessions.
- Feeds: dimension 10 (memory), memory hygiene boundary, dimension 9 (commands)

---

**[Scaling Managed Agents: Decoupling brain from hands — Anthropic Engineering](https://www.anthropic.com/engineering/managed-agents)** — _engineering-anthropic · accessed 2026-06-28_

Article on Managed Agent architecture with brain/hands/session separation. The session functions as an append-only log external to the context window — durable, queryable via `getEvents()` with positional slices. p50 time-to-first-token reduced 60%, p95 reduced >90%.

- **Key techniques:**
  - Session as external context store: append-only log outside the context window
  - `wake(sessionId)` + `getSession(id)` for harness failure recovery
  - Separation of concerns: harness performs context transformations; session ensures durability
  - Uniform tools interface: `execute(name, input) -> string` for sandboxes, MCP servers and custom tools
  - Vault pattern: credentials outside the sandbox where Claude's code executes
- **Notable:** The session as external log is the production implementation of the "context is finite" principle — no information is lost even with context reset.
- Feeds: dimension 7 (sub-agents), dimension 10 (memory), dimension 8 (hooks)

---

**[Claude Code MEMORY.md Spec: The 4 Frontmatter Types Decoded](https://harrisonsec.com/blog/claude-code-memory-simpler-than-you-think/)** — _community · accessed 2026-06-28_

Detailed analysis of the four types of Auto Memory frontmatter (user, feedback, project, reference) and architectural limitations: 5-file retrieval cap, index truncated at 200 lines/25KB, grep-only retrieval without semantic search.

- **Key techniques:**
  - Four frontmatter types: user (preferences), feedback (response style), project (context/constraints), reference (lookup facts)
  - 5-file limit per query — smell: critical memories may not load
  - Grep-only: "frontend unit tests" does not retrieve "React testing patterns" — semantic gap
  - Upgrade: local embeddings with SQLite-vec while maintaining markdown readability
  - Verify loaded memories against current codebase state before applying
- **Notable:** The 5-file per query limit and the semantic gap are the main production smells of the current system — an audit skill can verify whether critical memories are referenced in the MEMORY.md index.
- Feeds: dimension 10 (memory), memory hygiene boundary

---

**[Claude Code Memory System: 4 Layers, 5 Limits, and a Fix](https://milvus.io/blog/claude-code-memory-memsearch.md)** — _community · accessed 2026-06-28_

Analysis of the 4 layers (CLAUDE.md, Auto Memory, Auto Dream, KAIROS) and 5 structural limits of Claude Code's memory system. Auto Dream is the cyclic hygiene process that converts vague temporal references to exact dates, resolves contradictions, and maintains the index within the limit.

- **Key techniques:**
  - Auto Dream: trigger = 24h elapsed AND 5+ new sessions, or manual command
  - Auto Dream operations: exact timestamps, contradiction elimination, obsolete removal, maintenance of 200-line limit
  - MEMORY.md structure: pointers < 150 characters per entry, topic files separated by category
  - Hygiene smells: vague temporal references, entries without dates, silent contradictions
- **Notable:** Auto Dream is the analog of the "quenching-management" process applied to memory — automated cyclic auditing that keeps the surface clean. Can serve as a model for a skill audit command.
- Feeds: dimension 10 (memory), memory hygiene boundary

---

**[Anthropic's Managed Agents Memory: what it changes](https://usewire.io/blog/anthropic-managed-agents-memory-context-engineering/)** — _community · accessed 2026-06-28_

Critical analysis of the four design problems of persistent memory in production: scope (visibility must be declared at write time, not retrieval), freshness (expired facts cause "context poisoning by staleness"), conflict resolution (silent last-write-wins creates undetectable behavioral changes), and trust/provenance.

- **Key techniques:**
  - Scope declared at write: per-agent, per-workspace, per-user — scope errors cause most production failures
  - Explicit freshness model: without it, memory becomes "a slow source of context poisoning"
  - Conflict resolution visible to the agent: avoid silent last-write-wins
  - Mandatory provenance: each entry needs source attribution for the agent to evaluate reliability
  - Design deletion paths before implementation, especially for per-user memory with compliance obligations
- **Notable:** The four problems (scope, freshness, conflict, trust) are a direct audit checklist for dimension 10 — a skill can verify whether each memory entry has declared scope, date, and source.
- Feeds: memory hygiene boundary, dimension 10 (memory), dimension 12 (boundaries)

## How it feeds the method evolution

- **Dimension 10 (memory) — new cyclic hygiene checklist:** Introduce in the skill a MEMORY.md audit protocol with six verifiable smells: (1) entry without date/provenance; (2) entry duplicating something already in the repo/CLAUDE.md; (3) entry with vague temporal reference ("recently", "last time") instead of exact date; (4) entry contradicting another more recent entry (silent last-write-wins); (5) topic file not referenced in the MEMORY.md index (invisible to loading); (6) entry with incorrect scope (per-workspace when it should be per-agent). The detection command is `/memory` to list + manual review of the MEMORY.md index.

- **Memory hygiene boundary — smell "memory as duplicated repo":** Add to the method the criterion: "does this memory entry replicate something that already exists in the repository (code, CLAUDE.md, architecture docs)?" — if so, the memory entry should be replaced by a reference (`@path` or link). This is the application of the boundary doctrine of dimension 12 to the memory plane: each piece of information has a unique home.

- **Dimension 1 (CLAUDE.md as map) — sharpened quality criterion:** Official documentation establishes that CLAUDE.md should have fewer than 200 lines per file, specific and verifiable instructions, and should not contain multi-step procedures (which belong in skills) or instructions that only apply to part of the codebase (which belong in `.claude/rules/` with path-specific frontmatter). The skill can add these as smells: CLAUDE.md > 200 lines, vague non-verifiable instructions, multi-step procedure embedded instead of as a skill.

- **Dimension 8 (hooks) — sharper instruction vs. hook boundary:** Official documentation is explicit: "if an instruction is something that must run at a specific point — such as before every commit or after each file edit — write it as a hook instead. Hooks execute as shell commands at fixed lifecycle events and apply regardless of what Claude decides to do." The skill can add the smell: "instruction in CLAUDE.md that should be a hook" — detected when the instruction uses fixed-event language ("before committing", "after each edit", "whenever X").

- **Dimension 10 (memory) — CLAUDE.md vs. Auto Memory distinction as boundary doctrine:** Document as explicitly verifiable doctrine: CLAUDE.md = rules that any team member needs to know, versioned in the repo; Auto Memory = learnings the agent discovered during work, local and auditable via `/memory`. The smell is: presence of operational learnings (e.g., "discovered that test X fails with Y") in CLAUDE.md instead of MEMORY.md, or presence of team conventions in MEMORY.md instead of CLAUDE.md.

- **Dimension 10 (memory) — session initialization protocol as workflow step:** Incorporate into the method the Anthropic Engineering session initialization pattern: (a) check progress log, (b) review recent git history, (c) read feature file/backlog, (d) verify basic stability before new work. This protocol is the operational equivalent of the auto-inject "view memory before any task" — it should be documented as a recommended step at the start of work sessions in the repository.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **8**.

The set of 11 sources is of generally high quality: all URLs were verified as accessible and publishers are correct. The six official Anthropic sources (docs + engineering blog) and the three confirmed community sources cover the topic coherently and without gross fabrications. The three problems found are editorial in nature — two cases of mischaracterization (adoption data attributed to the wrong post; frontmatter taxonomy attributed to official documentation instead of a community source) and one malformed URL with a double '/docs/' segment that resolves via redirect but is fragile. No source appears fabricated or completely nonexistent.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://claude.com/blog/context-management | `mischaracterized` | The summary attributes to this post real customer adoption data (Netflix, Rakuten, Wisedocs, Ando; 97% reduction in first-pass errors; 30% speed increase). The WebFetch of the URL confirmed that the page exists but does NOT contain these company names — these numbers belong to the separate 'Memory for Managed Agents' announcement (April 23, 2026). The summary mixes two distinct announcements into one. |
| https://platform.claude.com/docs/en/docs/build-with-claude/context-windows | `recheck` | Malformed URL: contains duplicated segment '/docs/en/docs/' instead of the canonical path '/docs/en/build-with-claude/context-windows'. The page loaded via redirect and the content is correct, but the URL listed in the catalog is wrong and may break in direct linking or future validation. |
| https://code.claude.com/docs/en/memory | `mischaracterized` | The summary claims this official Claude Code documentation describes 'four types of Auto Memory: user, feedback, project, reference'. The actual official documentation does not enumerate these 4 frontmatter types — it describes the memory directory with MEMORY.md as index and optional topic files, without naming categories by frontmatter. These 4 types were identified in source code analysis by a community researcher, not in the official docs. |
