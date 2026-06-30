# Context engineering for agents (Anthropic)

> This angle covers the set of strategies for designing, selecting, and organizing the context of an LLM agent as a finite resource — context rot, progressive disclosure, compaction, note-taking, sub-agent isolation and token budget. Directly feeds the «progressive disclosure / context budget» boundaries and dimensions 1 (CLAUDE.md as map), 6 (skills) and 7 (sub-agents).

## Synthesis

Context engineering is the discipline of designing, selecting, and organizing all information an LLM receives during inference — system prompt, conversation history, tool results, retrieved documents. Anthropic formalized the concept in September 2025 with the article «Effective Context Engineering for AI Agents», defining the central question of agent development: «What context configuration maximizes the probability of the desired behavior?». Context is not just the prompt: it is the most critical finite resource of the agent, and mismanaging it is the most silent way to destroy reliability in production. Tool results alone can consume over 50,000 tokens before the agent processes the user's first request; multi-agent systems use up to 15x more tokens than simple chat interactions.

The phenomenon of «context rot» — progressive degradation of precision as context grows — is architectural: the n² attention relationships of transformers disperse over long sequences. Chroma research showed that adding full history of ~113k tokens can drop accuracy by 30% compared to a focused 300-token version. Information position matters: content in the middle of a long context suffers a ~15% accuracy drop vs. start/end («lost in the middle» effect, Liu et al. 2023). These empirical findings underpin three Anthropic-recommended anti-rot strategies: (1) compaction — summarize conversation history as the limit approaches, starting by clearing old tool results; (2) structured note-taking — the agent writes external files (NOTES.md, TODO.md) as persistent memory and re-reads them as needed, never keeping everything in the window; (3) multi-agent architectures — sub-agents with clean, isolated context windows do focused work, returning condensed 1,000-2,000 token summaries to the orchestrator.

The «smallest high-signal set» principle — the smallest possible set of high-relevance tokens that maximizes the desired outcome — guides all context decisions. It manifests in three arenas: (a) system prompt design at the optimal altitude (specific but not brittle, flexible but not vague); (b) tool design with minimal overlap, unambiguous parameters and token-efficient returns (pagination, truncation, format enums); (c) just-in-time retrieval, where the agent navigates the environment on demand (glob, grep, read_file) instead of pre-loading static indexes that go stale. Claude Code exemplifies the hybrid pattern: CLAUDE.md is injected into context at startup (a pre-computed high-density drop), while exploration primitives allow lazy retrieval of any other file during execution.

The progressive disclosure pattern — formalized in Anthropic's Agent Skills (October 2025) — is the most sophisticated application of the principle. Skills are directories with SKILL.md; the system loads only the YAML frontmatter (name + description, ~80-100 tokens per skill) at startup; only when the agent determines the skill is relevant does it read the full body (typically <5k tokens); additional files (scripts, reference documents) are accessed via bash only if needed for the concrete task. The result: dozens of installed skills cost ~1,700 tokens combined in idle state; without progressive disclosure, the same set would consume hundreds of thousands of tokens in the system prompt. Scripts executed via bash never enter the context window — only the output enters, eliminating a huge token inflation vector.

For auditing the knowledge surface of a repository with Claude Code, these principles translate into verifiable criteria. A healthy CLAUDE.md functions as a map (what each file contains and where to go), not an encyclopedia — it should itself follow the smallest high-signal set principle, delegating details to referenced architecture docs. Repository skills should have precise YAML descriptions (progressive disclosure routing depends on them) and bodies that load only what the task needs, with additional files referenced but not included in the body. Chained sub-CLAUDE.md files via @-imports perform progressive disclosure at the filesystem level: the agent only reads the sub-file when navigating to that subfolder, keeping the root context lean. Context rot in the repository manifests as CLAUDE.md growing beyond 150 lines, skills without updates that contradict the current/active code, and architecture docs describing already-replaced patterns — all «context rot» on the knowledge surface that a curator agent should detect and address.

## Sources

**[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — _engineering-anthropic · 2025-09-29_

Foundational Anthropic article that formalizes context engineering as an evolution of prompt engineering. Defines the central question («What context configuration maximizes the desired behavior?»), describes context rot, smallest-high-signal-set, system prompt altitude, token-efficient tool design, just-in-time retrieval, compaction, structured note-taking, and multi-agent architectures. Released alongside Claude Sonnet 4.5.

**Key techniques:**
- Context rot: precision degradation with context window growth
- Smallest high-signal set: smallest set of high-relevance tokens that maximizes outcome
- System prompt altitude: specific but not brittle, flexible but not vague
- Just-in-time retrieval: autonomous navigation via glob/grep/read_file instead of pre-computed indexes
- Compaction: history summarization preserving critical decisions; starts by clearing old tool results
- Structured note-taking: agent writes NOTES.md as external memory and re-reads when needed
- Multi-agent: sub-agents with isolated windows return condensed summaries (1k-2k tokens) to orchestrator
- Hybrid CLAUDE.md + exploration: pre-computed high-density drop + lazy just-in-time retrieval

**Notable:** Tool results alone can consume >50k tokens before the agent processes the first request; multi-agent systems use up to 15x more tokens than simple chat.

Feeds: dimension-1-CLAUDE.md-as-map, dimension-6-skills, dimension-7-sub-agents, boundary-progressive-disclosure, boundary-context-budget

---

**[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)** — _engineering-anthropic · 2025-10-16_

Article that formalizes the progressive disclosure pattern as a context management mechanism for Skills. Describes the three-level architecture: YAML metadata at startup (~100 tokens per skill), SKILL.md body loaded on demand (<5k tokens), and additional files accessed via bash without entering the context window.

**Key techniques:**
- Progressive disclosure: loading at three levels (metadata → instructions → resources)
- YAML frontmatter: name + description are the only fixed cost per skill in context
- Filesystem-based: skills exist as directories; Claude navigates via bash
- Scripts executed via bash: code never enters context, only the output
- Effectively unlimited context for bundled files not accessed

**Notable:** 17 official Anthropic skills cost ~1,700 tokens combined in idle state. The pattern became an open standard adopted by OpenAI, Google, GitHub and Cursor within weeks.

Feeds: dimension-6-skills, boundary-progressive-disclosure, boundary-context-budget, dimension-7-sub-agents

---

**[Agent Skills — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)** — _spec-standard · accessed 2026-06-28_

Normative Agent Skills documentation: SKILL.md structure, required YAML frontmatter fields, cost table per level (Level 1 ~100 tokens, Level 2 <5k, Level 3+ unlimited until accessed), runtime restrictions per surface.

**Key techniques:**
- YAML frontmatter: name (max 64 chars) + description (max 1024 chars) — required fields
- Description must include WHEN to use the skill for precise routing
- Level 1 (metadata): always loaded at startup; Level 2: loaded when triggered
- Level 3+ (resources/scripts): accessed on-demand; script code never enters context
- Claude Code: skills in ~/.claude/skills/ (personal) or .claude/skills/ (project)

**Notable:** Scripts executed via bash never load the code into context — only the output enters the window, eliminating token inflation from on-the-fly generated code.

Feeds: dimension-6-skills, boundary-progressive-disclosure, boundary-context-budget

---

**[Building Effective AI Agents](https://www.anthropic.com/research/building-effective-agents)** — _engineering-anthropic · 2024-12-19_

Agent architecture guide: workflow patterns (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer), when to use agents vs. workflows, tool design with comparable effort to HCI.

**Key techniques:**
- ACI (Agent-Computer Interface): invest in tool documentation as much as in HCI
- Poka-yoke in tools: design that makes incorrect use difficult (e.g., absolute paths)
- Orchestrator-workers: dynamic decomposition for unpredictable tasks
- Simplicity first: add complexity only when evaluation demonstrates necessity
- Avoid frameworks until deeply understanding the underlying mechanics

**Notable:** Tool optimization often exceeds overall prompt refinement in effort (SWE-bench experience).

Feeds: dimension-6-skills, dimension-7-sub-agents, dimension-14-guardrails, boundary-context-budget

---

**[Writing effective tools for AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)** — _engineering-anthropic · 2025-09-11_

Practical tool design guide focused on token efficiency: consolidate operations, prefix namespacing, semantically clear returns, pagination/truncation with sensible defaults.

**Key techniques:**
- Consolidate operations: schedule_event instead of list_users + list_events + create_event separately
- Prefix namespacing: asana_projects_search vs. asana_users_search to avoid ambiguity
- Semantics over technology: human-readable names instead of UUIDs/mime-types in returns
- Pagination and truncation with sensible defaults (Claude Code: 25k tokens max per response)
- Format enums: allow agent to request «concise» or «detailed»
- Actionable errors: guide agents toward token-efficient strategies in error messages

**Notable:** Selecting between prefix vs. suffix namespacing produces measurable differences in evaluations. Even small refinements in tool descriptions yield dramatic improvements.

Feeds: dimension-6-skills, boundary-context-budget, dimension-13-conventions

---

**[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)** — _engineering-anthropic · 2025-06-13_

Account of how Anthropic built their internal multi-agent research system. Describes memory checkpointing when context exceeds 200k tokens, communication via artifacts instead of coordinator routing, and scale heuristics.

**Key techniques:**
- Checkpointing: lead agent saves plan to external memory when context > 200k tokens
- Artifact-based handoff: sub-agents create outputs that persist independently, without going through coordinator
- Subagent output bypass: light references passed back instead of full outputs
- Extended thinking interleaved: sub-agents use thinking after tool results to assess quality
- Effort scaling: 1 agent/3-10 tool calls for simple facts; 10+ parallel sub-agents for complex research

**Notable:** Multi-agent with Claude Opus 4 lead + Claude Sonnet 4 sub-agents outperformed single-agent Opus 4 by 90.2% in internal evaluation, processing 67% fewer tokens.

Feeds: dimension-7-sub-agents, boundary-context-budget, boundary-progressive-disclosure

---

**[Agent Skills: Progressive Disclosure as a System Design Pattern](https://www.newsletter.swirlai.com/p/agent-skills-progressive-disclosure)** — _community · 2026-03-11_

Technical analysis of the progressive disclosure mechanism with concrete metrics: metadata ~80 tokens per skill, body between 275 and 8,000 tokens (median ~2,000). Highlights the problem of 90+ tool definitions accumulating 50k+ JSON tokens before reasoning.

**Key techniques:**
- 17 official Anthropic skills = ~1,700 tokens combined in idle state
- Fewer than 20 tools per agent recommended; accuracy degrades after 10
- YAML description quality directly impacts skill routing accuracy
- Smart caching of recently used skills to avoid context churn

**Notable:** Systems with 90+ tool definitions accumulate 50k+ tokens of JSON schemas before the agent begins reasoning — degrading attention and accuracy.

Feeds: dimension-6-skills, boundary-progressive-disclosure, boundary-context-budget

---

**[Context Engineering: A Practical Guide for AI Agents (Sourcegraph)](https://sourcegraph.com/blog/context-engineering)** — _community · 2026-05-28_

Practical guide focused on code agents: four pillars (instructions, retrieval, memory, tools), re-ranking as a central practice, code-aware retrieval via SCIP, and production metrics to monitor context health.

**Key techniques:**
- Re-ranking: cross-encoders over high-recall candidates to select precise top-k
- Code-aware retrieval: SCIP-backed lookups return definitions directly vs. probabilistic top-k
- Production metrics: context utilization rate, compression ratio, retrieval precision
- Context drift signals: re-reading already-processed files, reaffirming previous decisions
- Agent-controlled retrieval improves tool selection accuracy ~3x

**Notable:** Chroma Research: adding full history (~113k tokens) can drop accuracy by 30% vs. focused 300-token version on simple tasks.

Feeds: dimension-11-data-catalog, boundary-context-budget, dimension-7-sub-agents

---

**[Context Engineering Beyond CLAUDE.md: The 5-Layer Hierarchy (Pixelmojo)](https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md)** — _community · 2026-02-14_

Analysis of context hierarchy in code agents: enterprise policy → per-project CLAUDE.md → per-file-type rules (.claude/rules/ with glob) → conversation history. Quantifies CLAUDE.md impact on SWE Bench.

**Key techniques:**
- Four-level hierarchy: enterprise → project (CLAUDE.md) → file type → conversation
- Auto-compaction at 98% of effective window; /compact manually when quality drops
- Subagent isolation: explore agent (read-only), plan agent, domain-specific agents
- File-pattern rules: .claude/rules/ with glob to maintain context relevance by domain

**Notable:** Arize AI achieved +10% on SWE Bench only by optimizing the system prompt (CLAUDE.md) — without fine-tuning or architectural changes. Simple filesystem storage outperforms graph-based memory: 74.0% vs. 68.5% on LoCoMo benchmark.

Feeds: dimension-1-CLAUDE.md-as-map, boundary-progressive-disclosure, boundary-context-budget, dimension-7-sub-agents

---

**[Context Engineering: Gateway-Level Session Management, Compaction, and System Prompt Caching (TrueFoundry)](https://www.truefoundry.com/blog/context-engineering-gateway-session-management)** — _community · 2026-06-01_

Production infrastructure perspective: gateway-level session tracking, compaction strategies with recommended thresholds (75%), and prefix caching savings (85% cache hit rate reduces cost by ~73%).

**Key techniques:**
- Compaction threshold: 75% of model context limit; proactive, not reactive
- Do not compact conversations below ~75k tokens or before turn 10
- Prefix caching: Anthropic charges 10% on cache reads vs. 100% on input — ROI typically in weeks
- Priority: enable prefix caching → server-side compaction → session tracking → stateless chaining
- Code agents accumulate ~6k tokens per turn — predictable for threshold planning

**Notable:** Prefix caching is the highest-ROI context primitive: ~73% discount on frequent calls with long static prompt. Proactive compaction at 75% avoids reactive degradation.

Feeds: boundary-context-budget, dimension-9-commands, dimension-8-hooks

---

**[Fighting Context Rot (Inkeep Blog)](https://inkeep.com/blog/fighting-context-rot)** — _community · 2025-10-01_

Practical article about context rot with focus on finite attention and token economy. Highlights that agents have a smaller attention budget than imagined, and that five well-designed tools outperform twenty with overlap.

**Key techniques:**
- Five well-designed tools outperform twenty with overlap
- Compaction: start by clearing old tool results in message history
- Just-in-time: keep light references (file paths, queries) and retrieve dynamically
- Multi-agent: sub-agents with clean contexts return condensed 1k-2k token summaries

**Notable:** Claude playing Pokemon maintains accurate tallies for thousands of steps by writing and re-reading its own note files — concrete example of structured note-taking persisting through context resets.

Feeds: boundary-context-budget, dimension-7-sub-agents, dimension-6-skills

## How it feeds the method evolution

- **Dimension 1 (CLAUDE.md as map) — sharpen the «good» criterion:** The empirical evidence (Arize AI +10% SWE Bench) and the smallest-high-signal-set principle provide verifiable criteria: a healthy CLAUDE.md has <150 lines, functions as a map with links to architecture docs, and does not duplicate content that lives in other files. The detectable smell is «CLAUDE.md growing as an encyclopedia instead of an index» — the method can add a size and external link density check as a health metric.

- **Dimension 6 (skills) — new smell and quality criterion for YAML descriptions:** The progressive disclosure mechanism depends critically on the quality of the frontmatter description. The audit should verify whether each skill has: (a) description that includes WHEN to use (not just WHAT it does), (b) body that loads only what is needed for the task without redundancy with root CLAUDE.md, (c) additional files referenced in the body but not included in it. A skill with a vague description is the equivalent of a book index without page numbers — routing fails silently.

- **Dimension 7 (sub-agents) — artifact handoff pattern:** Anthropic's artifact-based handoff pattern (sub-agents create persistent outputs independently, passing light references to the coordinator) is an auditable criterion: repository sub-agents should return condensed summaries (1k-2k tokens) to the orchestrator, not complete traces. The method can add a verification step: «is the sub-agent returning the full output or a reference/summary?»

- **Boundary progressive disclosure / context budget — add context rot detection on knowledge surface:** Context rot is not just a runtime problem; it also exists in repo knowledge files. Context rot patterns on the surface: (a) architecture docs describing already-replaced patterns, (b) skills with instructions contradicting current/active code, (c) sub-CLAUDE.md files that duplicate content already in the root. The method can include a smell check: «does this file still describe the current state or is it a fossil?»

- **Dimension 12 (boundary doctrine) — each piece of information with one canonical home is the anti-pattern of context pollution:** The «each piece of information with one canonical home» rule already in the method is directly grounded by the context pollution principle from context engineering: redundant or conflicting information distorts reasoning. The method can add the inverse criterion as a detectable smell: «does this information appear in more than one place with a risk of diverging?»

- **Dimension 8/9 (hooks and commands) — add compaction threshold as session hygiene practice:** The 75% context utilization threshold (TrueFoundry) and the auto-compaction at 98% pattern (Pixelmojo) are production practices that the method can recommend as default harness configuration. A pre-task hook can check context utilization and trigger proactive compaction before long knowledge audit tasks.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **9**.

The set is of generally high quality: 9 of the 12 sources were verified and confirmed with accessible URL, correct publisher, correct date, and content consistent with the summary. The three primary Anthropic articles (articles 1, 2, 4) and the official documentation (article 3) are all correct. The problems found are mischaracterizations, not fabricated or inaccessible URLs: one Anthropic article has its central contribution omitted from the summary; another has an invented number («67% fewer tokens») that contradicts the article itself; and a community article has the wrong title (5 layers vs. 4 actual). No source appears fabricated or inaccessible.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://www.anthropic.com/engineering/writing-tools-for-agents | `mischaracterized` | The summary presents the article as a token-efficiency and operation-consolidation focused tool design guide, omitting the article's core: the eval-driven loop where agents (Claude Code) automatically optimize tools through systematic evaluations. The main method — using agents to analyze results and improve tools automatically — is absent from the summary... |
| https://www.anthropic.com/engineering/multi-agent-research-system | `mischaracterized` | The «notable» field claims the system «processed 67% fewer tokens» — a claim not in the article that contradicts actual content: the article says multi-agent systems use ~15x MORE tokens than simple chat and that agents consume ~4x more than chat. The number 67% does not appear in the article; possibly confused with the ~67% price reduction of Opus 4.1 to 4.5+. The «notable» intro... |
| https://www.pixelmojo.io/blogs/context-engineering-ai-coding-agents-beyond-claude-md | `mischaracterized` | The catalog entry title says «5-Layer Hierarchy», but the actual article explicitly describes a 4-level architecture (Enterprise Policy, Project Memory/CLAUDE.md, Project Rules/.claude/rules/, Conversation History). The description itself contradicts the title by saying «Four-level hierarchy». The wrong title may cause confusion when citing or searching for the content. |
