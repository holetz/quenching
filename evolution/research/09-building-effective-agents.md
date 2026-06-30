# Patterns of effective agents and multi-agent systems

> Covers the workflow vs. agent distinction, the five canonical Anthropic patterns, multi-agent systems in production, and verifiable quality criteria — feeds primarily into Dimension 7 (sub-agents) and the method philosophy (goal-driven, audit+apply-with-confirmation).

## Synthesis

The fundamental distinction established by Anthropic separates **workflows** (systems where LLMs and tools are orchestrated through predefined code paths) from **agents** (systems where the LLM dynamically directs its own processes and tool usage). This distinction is not academic: it determines which of the five patterns to apply (prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer) and when the simplicity of a single LLM call with retrieval already solves the problem. The practical rule is to start simple and scale complexity only when the simpler pattern does not cover the problem's state space.

The multi-agent research system built by Anthropic (launched in April 2025, documented in June 2025) concretizes the orchestrator-workers pattern in production: a lead agent analyzes the query, develops strategy with "extended thinking", and spawns 3-5 subagents in parallel, each with isolated context, distinct objectives, and parallel calls to 3+ tools. The empirical result is a 90.2% accuracy gain over Claude Opus 4 single-agent and a 90% reduction in research time — at a cost of ~15x more tokens than a chat interaction. This highlights the central trade-off of multi-agent systems: parallelism and context isolation improve quality, but the computational cost requires that the task generate sufficient value to justify it.

The documented production failures reveal the smells of a poorly designed multi-agent system: subagents with vague instructions duplicate work, lead agents without effort-scaling rules spawn 50 subagents for simple queries, ambiguous tool descriptions cause wrong tool selection, and accumulated context ("context rot") degrades retrieval precision quadratically. The countermeasure is defensive design: explicit scaling rules (simple fact-finding = 1 agent, 3-10 calls; complex research = 10+ subagents), clear task boundaries for each subagent, and output via artifacts on the filesystem (avoiding copying large outputs through conversation history). Recent academic research (arXiv 2604.02460) reinforces that, under equal reasoning token budgets, single-agent systems match or outperform multi-agent — the real advantage of multi-agent emerges when the single agent's context deteriorates or when the task is intrinsically parallel and breadth-first.

For a skill that audits a repository's knowledge surface, the most relevant patterns are: (a) **orchestrator-workers** as the mental model for the skill itself — a curator agent delegates point audits to subagents specialized by dimension; (b) **evaluator-optimizer** as a quality criterion — the skill must have a verifiable criterion of "good" for each audited dimension, not merely detect presence/absence; (c) **context engineering** as an operational constraint — CLAUDE.md must contain only what the agent needs without degrading attention, and sub-CLAUDE.md files per subfolder carry context just-in-time. The harness pattern for long-running agents (feature list in JSON, progress file, git history, startup verification protocol) maps directly to how the skill should track its state between method evolution rounds.

The **Agent Skills** dimension (opened as a standard in December 2025) introduces an architectural primitive that closes the loop: skills are folders of instructions + scripts + resources that agents discover and load dynamically, with YAML metadata that triggers automatic activation. This means the knowledge management skill itself can be delivered as a SKILL.md — activated when relevant, without occupying context in every conversation. The recommended defensive design (careful name and description to avoid unintended activation, code dependency auditing, iterative refinement based on observed behavior) are criteria directly applicable to method evolution.

## Sources

**[Building Effective Agents](https://www.anthropic.com/research/building-effective-agents)** — _official-anthropic · December 2024_

Foundational document that defines workflows vs. agents and describes the five canonical patterns: prompt chaining, routing, parallelization (sectioning + voting), orchestrator-workers, and evaluator-optimizer. Establishes the simplicity-first philosophy and provides criteria for when to use agents versus workflows.

- **Key techniques**:
  - Workflow (predefined code paths) vs. agent (LLM directs dynamically) distinction
  - Five patterns: prompt chaining, routing, parallelization, orchestrator-workers, evaluator-optimizer
  - Evaluator-optimizer requires verifiable "clear evaluation criteria"
  - Agents preferred for open-ended problems with unpredictable number of steps
  - Simplicity: start with single call + retrieval before scaling
- **Notable**: Explicit verifiable criterion — coding agents verify solutions via automated tests; customer support measures resolutions quantitatively, never subjectively.
- **Feeds**: Dimensions 7, 12, 14, 6

---

**[How we built our multi-agent research system](https://www.anthropic.com/engineering/multi-agent-research-system)** — _engineering-anthropic · June 2025_

Technical account of the multi-agent research system launched in April 2025. Describes orchestrator-workers architecture with a lead agent (extended thinking + planning) and 3-5 parallel subagents, each with distinct objectives, specific output formats, and parallel calls to 3+ tools. Documents production failures, prompt strategies, observability, and zero-downtime deployment of running agents.

- **Key techniques**:
  - Lead agent with extended thinking for strategic planning
  - Parallel subagents with isolated contexts and distinct objectives
  - Explicit effort-scaling rules (1 agent / 2-4 / 10+ subagents)
  - Start broad then narrow: short, general queries, progressively focused
  - Artifact system: subagents write directly to the filesystem, passing lightweight references to the lead
  - Rainbow deployments to avoid interrupting running agents
  - LLM-as-judge with 5 criteria: factual accuracy, citation accuracy, completeness, source quality, tool efficiency
- **Notable**: Token usage explains 80% of performance variance in browsing tasks; multi-agent systems use ~15x more tokens than chat — the advantage is quality, not cost.
- **Feeds**: Dimensions 7, 9, 12, 14

---

**[Best practices for Claude Code](https://code.claude.com/docs/en/best-practices)** — _official-anthropic · accessed 2026-06-28_

Official best-practices guide for Claude Code as an agentic coding environment. Covers effective CLAUDE.md (concise, auditable, prunable), subagents for isolated investigation, Writer/Reviewer pattern with parallel sessions, verification by objective criteria (tests, build, screenshot), headless harness (-p flag), fan-out via bash loop, skills, and deterministic hooks.

- **Key techniques**:
  - CLAUDE.md: include only what causes errors if removed; exclude conventions Claude already follows
  - Subagents for investigation without polluting main context
  - Writer/Reviewer pattern: separate sessions, reviewer has clean context
  - Verification by objective criterion (test suite, build exit code, screenshot diff)
  - Plan mode (Explore > Plan > Implement > Commit) for multi-file changes
  - Fan-out: bash loop with claude -p per file for large-scale migrations
  - Hooks: deterministic, guarantee action (vs CLAUDE.md which is advisory)
- **Notable**: CLAUDE.md pruning rule: "For each line, ask: would removing this cause errors?" If not, cut it. Files that are too long cause Claude to ignore important instructions.
- **Feeds**: Dimensions 1, 6, 7, 8, 13

---

**[Writing effective tools for AI agents—using AI agents](https://www.anthropic.com/engineering/writing-tools-for-agents)** — _engineering-anthropic · accessed 2026-06-28_

Guide to tool design for agents: selection by impact (not quantity), namespacing with prefix/suffix, descriptions treated as prompt engineering, high signal-to-noise responses, token optimization via pagination/truncation, and evaluation with realistic multi-step tasks.

- **Key techniques**:
  - Consolidate related operations into a single tool
  - Namespacing by prefix/suffix to group related tools
  - Replace UUIDs with semantic fields in responses (reduces hallucinations)
  - Response format enums (detailed/concise) for agent to control verbosity
  - Held-out test sets to avoid overfitting in tool evaluations
  - Agent as engineer: use Claude Code to analyze transcripts and auto-improve tool descriptions
- **Notable**: A tool-testing agent that iteratively refined descriptions reduced task completion time by 40% — prompt engineering of tool descriptions is a greater lever than code changes.
- **Feeds**: Dimensions 7, 9, 6

---

**[Effective context engineering for AI agents](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — _engineering-anthropic · accessed 2026-06-28_

Treats context as a finite resource: "context rot" (degradation with volume) is real (n² relationships in the transformer), and the goal is "the smallest possible set of high-signal tokens that maximize the probability of the desired outcome". Describes three compression strategies: compaction (summarize), structured note-taking (external NOTES.md), and sub-agent architectures (fresh context per specialist).

- **Key techniques**:
  - Just-in-time retrieval: load data via tools instead of pre-processing everything
  - Compaction: summarize completed phases preserving architectural decisions and open issues
  - NOTES.md as persistent agent memory across sessions
  - Sub-agents with fresh context for focused tasks, returning condensed summaries
  - Start with minimal prompt on a capable model, add instructions based on failure modes
- **Notable**: "Context rot" formalized — retrieval performance degrades with volume because transformers have less training experience with long sequences, not solely due to absolute size.
- **Feeds**: Dimensions 1, 7, 10, 12

---

**[Effective harnesses for long-running agents](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents)** — _engineering-anthropic · accessed 2026-06-28_

Describes harness infrastructure for agents operating across multiple context windows: two-agent architecture (Initializer + Coding Agent), three critical state artifacts (feature list in JSON, progress file, git history), startup protocol for each session, and one-feature-at-a-time discipline to avoid partial implementations.

- **Key techniques**:
  - Feature list in JSON (more resistant to inappropriate model edits than Markdown)
  - Progress file: cross-session activity log for fast ramp-up of new context
  - Startup protocol: verify working dir, read git log + progress file + feature list, run init.sh
  - Browser automation (Puppeteer) for end-to-end verification, not just unit tests
  - One-feature-at-a-time: prevents agent from attempting to one-shot the app and running out of context
  - Commit after each session with a descriptive message, leaving the codebase in a clean state
- **Notable**: Without explicit verification, agents "would fail to recognize that the feature didn't work end-to-end" — the verifiable criterion is what closes the autonomy loop.
- **Feeds**: Dimensions 7, 9, 14

---

**[Equipping agents for the real world with Agent Skills](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)** — _engineering-anthropic · December 2025_

Introduces Agent Skills as an architectural primitive: folders with SKILL.md (YAML frontmatter + main content + supplementary resources) that agents discover and load dynamically. Skills package instructions + scripts + resources; metadata lives in the system prompt for triggering; main content loads on-demand. Complementary to MCP (tools) vs. Skills (complex workflows).

- **Key techniques**:
  - Three-tier structure: metadata (YAML, pre-loaded), primary content (SKILL.md, on-demand), supplementary files (on-demand)
  - Evaluation-first: identify capability gaps by executing representative tasks before building the skill
  - Name and description as activation triggers — careful wording prevents misuse
  - Deterministic scripts packaged in the skill for context-free operations
  - Iterative refinement based on observed real behavior
- **Notable**: Open standard published at agentskills.io (December 2025); 40+ compatible products in June 2026 including Databricks Genie Code — cross-platform portability.
- **Feeds**: Dimensions 6, 7, 12, 13

---

**[Our framework for developing safe and trustworthy agents](https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents)** — _official-anthropic · April 2026_

Framework of five principles for trustworthy agents: keeping humans in control, aligning with human values, protecting privacy, maintaining transparency, and securing interactions. Defines a four-layer architecture (model, harness, tools, environment) and a graduated permission hierarchy. Plan Mode as a UX pattern to reduce approval fatigue.

- **Key techniques**:
  - Four-layer model: model + harness + tools + environment — each layer can be exploited independently
  - Tiered trust: persistent permissions for trusted routine tasks; manual approval for consequential actions
  - Plan Mode: strategic visibility instead of per-action confirmation
  - Layered defenses against prompt injection: model-level + traffic monitoring + external red-teaming
  - Cross-context information isolation: sensitive data does not leak between interactions
- **Notable**: "No single line of defense is enough to guarantee protection" — defense in depth is the only viable model for agents in production.
- **Feeds**: Dimensions 7, 8, 14, 12

---

**[Measuring AI agent autonomy in practice](https://www.anthropic.com/research/measuring-agent-autonomy)** — _official-anthropic · accessed 2026-06-28_

Empirical analysis of ~400,000 interactive sessions from ~235,000 Claude Code users between October 2025 and April 2026. Documents how autonomy emerges from co-construction between model behavior, user strategy, and product design. Experienced users increase auto-approve to 40%+ but also interrupt more, reflecting a transition from per-action approval to strategic monitoring.

- **Key techniques**:
  - Post-deployment monitoring infrastructure is essential — pre-deploy evaluations do not capture real-world patterns
  - Agent-initiated stops (clarification pauses) are more frequent than human interruptions in complex tasks
  - 80% of tool calls have safeguards; 73% have a human in the loop; only 0.8% are irreversible
  - Models must recognize uncertainty and signal proactively (complements external safeguards)
- **Notable**: The 99.9th percentile turn duration in Claude Code nearly doubled (25 > 45 min) between October 2025 and January 2026 — smooth growth between releases suggests a deployment gap, not a capability gap.
- **Feeds**: Dimensions 7, 8, 14

---

**[Single-Agent LLMs Outperform Multi-Agent Systems on Multi-Hop Reasoning Under Equal Thinking Token Budgets](https://arxiv.org/abs/2604.02460)** — _academic-other · April 2026_

Controlled study with Qwen3, DeepSeek-R1-Distill, and Gemini 2.5 demonstrating that, under equal reasoning token budgets, single-agent matches or outperforms multi-agent on multi-hop reasoning. The advantage frequently attributed to multi-agent systems stems from "unaccounted computation and context effects". Multi-agent wins when the single context deteriorates or when substantially more computation is allocated.

- **Key techniques**:
  - Control total token budget for fair comparisons across architectures
  - Data Processing Inequality as theoretical framework for information efficiency
  - Multi-agent is competitive only when single context deteriorates or budget is asymmetric
  - Coordination has real overhead — it is not free
- **Notable**: Practical implication — adopting multi-agent by default without controlling total coordination cost is a fallacy; the decision criterion should be "does the single context deteriorate for this task?"
- **Feeds**: Dimensions 7, 12

---

**[How and when to build multi-agent systems](https://www.langchain.com/blog/how-and-when-to-build-multi-agent-systems)** — _community · accessed 2026-06-28_

Practical article on decision criteria for multi-agent systems: tasks heavy on parallelization, breadth-first exploration, and interfaces with complex tools are a good fit. Tasks with high interdependency or real-time coordination are a poor fit. Distinguishes read-heavy (easy to parallelize) from write-heavy (write conflicts are worse than read conflicts).

- **Key techniques**:
  - Context engineering is "the #1 job of the engineer building AI agents"
  - Read vs. Write: read-heavy systems are significantly easier to parallelize
  - Durable execution: recovery from specific checkpoints, not full restart
  - LLM-as-judge with ~20 initial datapoints representative of real usage
  - Economic evaluation: value generated must justify increased computational cost
- **Notable**: Coding tasks are explicitly cited as a poor fit for multi-agent today — high interdependency and coordination make parallelization counterproductive.
- **Feeds**: Dimensions 7, 12

---

**[Trustworthy agents in practice](https://www.anthropic.com/research/trustworthy-agents)** — _official-anthropic · accessed 2026-06-28_

Details trust mechanisms in agents: Plan Mode as a UX pattern (upfront plan vs. step-by-step), intent alignment failures (agent does not distinguish information gaps from decisions requiring user input), prompt injection, and approval fatigue. Recommends standardized benchmarks for injection resistance.

- **Key techniques**:
  - Plan Mode: strategy approval instead of individual action approval
  - Constitutional AI to reinforce pausing, clarification, and refusal in ambiguous scenarios
  - Three lines of defense against injection: model-level, production monitoring, external red-team
  - MCP donated to Linux Foundation — decoupling agent quality from integration control
- **Notable**: Per-action approval generates "approval fatigue" that causes oversight disengagement — Plan Mode is the UX solution: one strategic decision, not hundreds of micro-approvals.
- **Feeds**: Dimensions 7, 8, 14

## How this feeds method evolution

- **Dimension 7 (sub-agents) — new orchestration pattern**: The quenching-evolutionist skill should explicitly adopt the orchestrator-workers pattern: a curator agent delegates per-dimension audits to subagents with fresh context. Detectable smell: the current skill performs monolithic auditing in a single accumulated context — fragmenting into subagents per dimension reduces context rot and improves precision.

- **Dimension 12 (boundary doctrine) — multi-agent decision criterion**: Add to the method the empirical rule for when NOT to use multi-agent: tasks with high interdependency across dimensions (e.g., CLAUDE.md and sub-CLAUDE.md) should remain in the main agent; only parallelize intrinsically independent dimensions (e.g., verifying each skill in isolation). The arXiv 2604.02460 paper provides the formal criterion: "does the single context deteriorate for this task?"

- **Dimension 6 (skills) — SKILL.md structure as first-class citizen**: The knowledge management skill should be delivered as a valid SKILL.md conforming to the agentskills.io standard — with YAML frontmatter (name + description as activation triggers) and content divided into three levels (metadata / primary / supplementary). This allows the skill to be activated automatically when relevant without occupying context in every conversation.

- **Dimension 14 (behavioral guardrails) — mandatory verifiable criterion**: Incorporate into the method the requirement that each audited dimension has a verifiable criterion of "good" (not just presence/absence). Inspired by the evaluator-optimizer pattern and the empirical finding that agents without a verifiable check only stop when something "looks done" — equivalent to an audit that declares OK without evidence.

- **Dimension 1 (CLAUDE.md as map) — pruning by failure mode**: Add to the CLAUDE.md maintenance process an active pruning protocol: for each line, verify whether removing it would cause observed errors. Lines that pass the test are candidates for removal or migration to skills (on-demand loading). Health metric: CLAUDE.md below 150 lines with coverage verified by real failure modes.

- **Dimension 7 (sub-agents) — adversarial review as workflow step**: Add to the method evolution cycle a "reviewer subagent" step with clean context that verifies the diff of each evolution against the target dimension's criteria — equivalent to the Writer/Reviewer pattern documented in the official Claude Code guide. The reviewer should report only gaps that affect correctness, not style preferences.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources for this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **10**.

The set is of generally high quality: 10 of the 12 sources exist, are accessible, have correct dates and publishers, and the summaries reflect the actual content with good fidelity. The problems are concentrated in the pair of Anthropic sources on 'trustworthy agents', where apparent cross-contamination of attributes occurred: concepts from the 'trustworthy-agents' article (Plan Mode, four-layer model) were inadvertently described in the summary of 'our-framework', which in reality presents five distinct principles without those elements. The date of 'our-framework' is also wrong (August 2025, not April 2026). The academic and third-party sources (arXiv 2604.02460, LangChain) were verified and are correct. The Agent Skills article has a partially imprecise date in the catalog (published in October/December 2025, not just 'December 2025'), but the substantive facts about agentskills.io and adoption by 40+ platforms check out.

Flagged sources (review before citing):

| Source | Verdict | Problem |
| --- | --- | --- |
| https://www.anthropic.com/news/our-framework-for-developing-safe-and-trustworthy-agents | `mischaracterized` | Wrong date and content mismatch: the article was published in August 2025, not April 2026. More critically: the source does NOT contain the 'four-layer model (model, harness, tools, environment)' or 'Plan Mode' as a UX pattern — both are concepts from other Anthropic documents (likely from 'trustworthy-agents'). The summary for this source describes content that is simply not on the page. |
| https://www.anthropic.com/research/trustworthy-agents | `recheck` | The summary attributes 'Plan Mode' and the 'four-layer model' to this source — which are precisely the concepts ABSENT from 'our-framework'. There is attribution overlap between the two Anthropic sources on trustworthy agents. The actual content of the page (published in April 2026) covers Plan Mode and prompt injection, but the item 'Constitutional AI to reinforce pausing, clarification, and refusal' is a... |
