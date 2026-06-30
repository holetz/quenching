# Skill description/trigger optimization and evaluation

> This angle covers how a skill's `description` functions as an activation conditional (trigger), how to measure and optimize firing accuracy, and how to structure evals to separate description problems from instruction problems. It primarily feeds **Dimension 6 (skills)** and the candidate boundary **"Trigger optimization (subtrigger)"**.

---

## Synthesis

The description of a skill in the SKILL.md standard is not documentation for humans: it is the activation conditional that the agent evaluates on every conversation turn to decide whether or not to load the full skill body. The three-level progressive-loading mechanism (metadata always; SKILL.md only when activated; reference files only when needed) makes the description the only text always visible to the model — it consumes approximately 100 tokens per skill in the context window from startup, and the combined description+when_to_use limit is 1,536 characters in Claude Code. The practical consequence is that a vague description ("helps with documents") never fires correctly, while a well-constructed description includes the domain, the offered capabilities, and explicit trigger phrases that mirror how the user would actually formulate the request. The empirical rule consolidated by the official docs: "If the skill does not trigger automatically but works when invoked directly, the body is correct and the description is the problem."

The `when_to_use` field, exclusive to Claude Code, functions as an extension of the description: it is appended to it in the skill listing and counts toward the same 1,536-character limit. This creates a two-plane authoring strategy — the description describes the "what" and the when_to_use lists concrete trigger phrases, examples of literal requests, and contexts in which the skill should be preferred. At the same time, the `disable-model-invocation: true` field removes the description from context entirely, reserving the skill for human invocation via `/name` — useful for workflows with side effects (deploy, commit, sending a message) where timing must be controlled by the user, not the model. The `user-invocable: false` field does the opposite: the skill is invisible in the `/` menu but continues to be automatically invoked by the model — suitable for background context (e.g., "legacy-system-context") that the model should consult but which is not a meaningful action for the user to trigger.

The skill-creator plugin (launched by Anthropic in 2025, updated in March 2026) automates the complete description evaluation and optimization cycle. The description tuning flow generates approximately 20 synthetic prompts — half designed to trigger the skill, half deliberately similar to the domain but requiring something else (intentional false positives). Each prompt is tested three times to absorb the model's stochastic variation; the skill only counts as "fires correctly" if it activates in at least 2 out of 3 runs. The prompts are split 60/40 (training/held-out) to avoid overfitting the description to known examples — a description that memorizes the training prompts but fails on the held-out set is rejected. The algorithm iterates up to 5 rounds, analyzes failure patterns (missed fires vs. false triggers), and proposes description edits until satisfactory accuracy is reached. In Anthropic's own tests with their document-creation skills, the tuner improved correct triggering in 5 of 6 public skills.

The structured eval system (evals.json, grading.json, benchmark.json) provides the quantitative feedback loop needed to know whether a skill actually adds value. The benchmark.json compares pass rate, time, and tokens across "with skill" and "without skill" configurations — a delta of +50pp in pass rate with +13s of latency is typically justifiable; +2pp with +100% tokens is not. Good assertions are verifiable and specific ("the chart has exactly 3 bars"), not vague ("the output is good"). Two systemic failure patterns reveal design problems: assertions that always pass in both configurations (the skill is not contributing) and assertions with high stddev (ambiguous instructions or flaky test prompts). The blind comparator (blind A/B) complements assertions by evaluating holistic quality — two outputs may pass all assertions but differ in organization, formatability, and usability, and the comparator captures that without bias from knowing which version is which.

For a skill that AUDITS the knowledge surface of a repository (such as quenching-management), the principles apply directly. The description must list the concrete phrases a developer would use — "audit CLAUDE.md", "verify whether the backlog is up to date", "check for unimplemented ADRs", "map the 14 dimensions", "diagnose documentation gaps" — and not just the abstract concept. The `when_to_use` should include implicit negative triggers: the skill SHOULD NOT fire when the user simply asks about one of the dimensions in isolation (e.g., "what is an ADR?") — this is a classic "should-not-trigger" that shares keywords but requires a simple answer, not a systematic audit. The `paths` field can restrict automatic activation to contexts where surface configuration files (CLAUDE.md, `docs/arquitetura/`, `.claude/skills/`) are in the working scope. Finally, the benchmark criterion for this skill must separate two metrics: (a) correct firing rate measured against a set of should-trigger/should-not-trigger prompts and (b) audited output quality measured by assertions about which dimensions were verified, which gaps were identified, and whether the recommendation is actionable.

---

## Sources

### **[Skill authoring best practices - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)**
_official-anthropic · accessed 2026-06-28_

Official normative Anthropic documentation on how to write effective skills. Covers the description as a discovery field (not metadata), naming conventions (gerund form: `processing-pdfs`, `analyzing-spreadsheets`), progressive disclosure, degrees of freedom in instructions (high/medium/low depending on task fragility), evaluation-driven development, and the Claude-A/Claude-B iteration cycle.

**Key techniques:**
- Third-person description, with what it does + when to use + specific keywords
- 1,024-character limit for the description in the SDK/API
- Create evals before writing extensive documentation (evaluation-driven development)
- Claude-A (expert who creates) / Claude-B (agent in clean context who tests) cycle
- evals.json structure: prompt + expected_output + files + verifiable assertions
- Test with all planned models (Haiku requires more detail than Opus)

**Notable:** "The description is critical for skill selection: Claude uses it to choose the right Skill from potentially 100+ available Skills."

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger), Dimension 13 (house conventions)

---

### **[Agent Skills overview - Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)**
_official-anthropic · accessed 2026-06-28_

Architectural overview of the Agent Skills system. Explains the three-level progressive loading model (Level 1: metadata ~100 tokens always; Level 2: SKILL.md <5k tokens when activated; Level 3: on-demand resources with no context cost until read).

**Key techniques:**
- Three progressive loading levels with differentiated token cost
- `name`: max 64 chars, lowercase+hyphens, no XML tags or reserved words
- `description`: max 1024 chars, required, describes what it does and when to use it
- Skills in Claude Code are filesystem-based (`.claude/skills/`)
- Runtime restrictions vary by surface (API without network access, Claude Code with full access)

**Notable:** Level table: Level 1 always ~100 tokens, Level 2 <5k tokens when activated, Level 3 effectively unlimited since it does not enter the context until read.

Feeds: Dimension 6 (skills), Dimension 12 (boundary doctrine)

---

### **[Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)**
_official-anthropic · accessed 2026-06-28_

Complete documentation for skills in Claude Code with the full frontmatter, including exclusive fields such as `when_to_use`, `disable-model-invocation`, `user-invocable`, `paths`, `skillOverrides`. Details the evaluation cycle via skill-creator and compaction behavior (first 5,000 tokens re-appended, combined budget of 25,000 tokens).

**Key techniques:**
- `description` + `when_to_use` truncated together at 1,536 chars in the skill listing
- `disable-model-invocation: true` removes the description from context entirely
- `user-invocable: false` hides from the `/` menu but maintains auto-invocation by the model
- `paths`: glob patterns that restrict automatic activation to specific file contexts
- `skillOverrides`: on / name-only / user-invocable-only / off controls visibility without editing SKILL.md
- skill-creator: ~20 should-trigger/should-not-trigger prompts, 3 runs each, 60/40 split, up to 5 iterations

**Notable:** "If a skill seems to stop influencing behavior after the first response, strengthen the skill description and instructions so the model keeps preferring it."

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger)

---

### **[Equipping agents for the real world with Agent Skills - Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)**
_engineering-anthropic · accessed 2026-06-28_

Engineering blog post describing the architecture and motivation behind Agent Skills. Emphasizes that name and description are the critical decision points for activation and recommends strategies to minimize conflicts and token consumption.

**Key techniques:**
- Name and description as critical decision points for agent activation
- Separate mutually exclusive contexts into distinct files (domain-specific organization)
- Monitor overreliance on certain sections as a signal that the content should be promoted to SKILL.md
- Ask Claude to self-reflect on what went wrong when a skill underperforms

**Notable:** Onboarding analogy: Skills are like onboarding guides organized progressively, from overview to detailed appendices — this framing helps decide what goes at which level.

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger), Dimension 12 (boundary doctrine)

---

### **[Steering Claude Code: skills, hooks, subagents and more - Claude Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)**
_official-anthropic · accessed 2026-06-28_

Anthropic blog post establishing the taxonomy of the Claude Code extension ecosystem. Distinguishes the role of skills (procedural workflows, body loads only when invoked) from the role of CLAUDE.md (facts and conventions always present).

**Key techniques:**
- Skills for procedural workflows; CLAUDE.md for facts and conventions
- Dual-trigger: user via `/name` or Claude via auto-matching the description
- Skill body loads only when invoked — long reference at no cost until used
- Oldest-drop-first during context compaction

**Notable:** "Instructions that are procedural, like deploy workflows, release checklists, or review processes, belong in a skill rather than in CLAUDE.md." — clear boundary criterion for CLAUDE.md vs. skill.

Feeds: Dimension 1 (CLAUDE.md as map), Dimension 6 (skills), Dimension 12 (boundary doctrine)

---

### **[Agent Skills specification - agentskills.io](https://agentskills.io/specification)**
_spec-standard · accessed 2026-06-28_

Open specification for the Agent Skills standard, governed as a cross-platform standard (adopted by ~40 products as of June 2026: Claude, OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI, Databricks Genie Code). Defines the normative fields and the progressive disclosure model as a spec requirement.

**Key techniques:**
- `description` must include keywords that help agents identify relevant tasks
- Progressive disclosure model: metadata ~100 tokens -> SKILL.md <5000 tokens -> on-demand resources
- SKILL.md: max 500 lines, complex content in `references/`
- `skills-ref validate ./my-skill` for spec compliance verification
- `compatibility` to indicate environment requirements (max 500 chars)

**Notable:** Cross-platform portability: a skill built for Claude Code works identically on 20+ other platforms, creating a shareable ecosystem of skills.

Feeds: Dimension 6 (skills), Dimension 13 (house conventions)

---

### **[Evaluating skill output quality - agentskills.io](https://agentskills.io/skill-creation/evaluating-skills)**
_spec-standard · accessed 2026-06-28_

Normative guide from the agentskills.io standard for evaluating skill output quality. Defines the complete eval cycle with workspace structure, JSON formats for each artifact (evals.json, grading.json, timing.json, benchmark.json), and grading principles.

**Key techniques:**
- `evals.json`: prompt + expected_output + files + verifiable assertions
- with_skill vs. without_skill cycle in clean context (subagent per test case)
- `grading.json`: PASS/FAIL with specific evidence citing the actual output
- `benchmark.json`: pass_rate + time_seconds + tokens with delta and stddev
- Assertions always passing in both configurations = remove (skill adds no value there)
- Assertions with high stddev = ambiguous instructions or flaky prompt
- Blind comparison: LLM judge without knowing which is which for holistic evaluation

**Notable:** "Require concrete evidence for a PASS. Don't give the benefit of the doubt." A vague one-sentence 'Summary' is a FAIL even with the label present.

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger)

---

### **[Improving skill-creator: Test, measure, and refine Agent Skills - Claude Blog](https://claude.com/blog/improving-skill-creator-test-measure-and-refine-agent-skills)**
_official-anthropic · 2026-03-03_

Announcement of the skill-creator plugin update with a complete eval framework and description optimization. Documents the description tuning algorithm and reports empirical results: improvement in 5 of 6 Anthropic's public document-creation skills.

**Key techniques:**
- ~20 synthetic prompts: 50% should-trigger, 50% should-not-trigger (tricky, same keywords)
- 3 runs per prompt; skill counts as "fires" if active in >=2/3 runs
- 60/40 training/held-out split to avoid description overfitting
- Up to 5 refinement iterations with failure pattern analysis (missed fire vs. false trigger)
- Blind A/B comparator: judge agent does not know which version is which
- Benchmark: pass rate + elapsed time + token usage with/without skill
- Regression detection: identifies when model updates degrade skill output

**Notable:** Empirical result: description tuner improved triggering accuracy in 5 of 6 Anthropic's public document skills after one round of optimization.

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger)

---

### **[Claude Code Skills 2.0: Evals, Benchmarks and A/B Testing](https://pasqualepillitteri.it/en/news/341/claude-code-skills-2-0-evals-benchmarks-guide)**
_community · 2026-03-07_

Detailed practical guide on skill-creator 2.0, including the 4 operational modes, the 4 parallel sub-agents in isolated contexts, and two unique detection modes: Regression and Outgrowth.

**Key techniques:**
- 4 modes: Create / Eval / Improve / Benchmark
- 4 parallel sub-agents in isolated contexts to eliminate context bleed between test cases
- Outgrowth detection: identifies when the skill has become unnecessary because the base model has improved
- HTML report for human review of results
- 60/40 split with 3 runs per prompt and 5 maximum iterations

**Notable:** Outgrowth Detection is a unique metric: it measures whether the skill is still necessary or whether the base model has already surpassed it, avoiding keeping obsolete skills that consume tokens without value.

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger)

---

### **[Claude Agent Skills 2.0: The Beginner's Guide to the Updated Skill-Creator](https://innovaitionpartners.com/blog/claude-agent-skills-2.0-the-beginners-guide-to-the-updated-skill-creator)**
_community · 2026-03-03_

Guide with a deeper explanation of the description tuning algorithm, including the "explicit exclusions" strategy for resolving false triggers without over-narrowing, and the distinction between capability uplift skills and encoded preferences skills.

**Key techniques:**
- "Explicit exclusions" in the description instead of excessive narrowing to resolve false triggers
- Should-not-trigger tricky: same keywords, similar domain, but require a different skill
- 3 runs per prompt: >=2/3 = considered to fire correctly
- Capability uplift (teaches new processes) vs. encoded preferences (encodes styles/workflows) as a category framework
- Feedback generalization: the fix must address the underlying problem, not the specific example

**Notable:** "A description might score perfectly on the training prompts by essentially memorizing them, but if it doesn't also work on the held-out test prompts, it gets rejected" — the held-out split is the safeguard against description overfitting.

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger)

---

### **[The SKILL.md Pattern: How to Write AI Agent Skills That Actually Work](https://bibek-poudel.medium.com/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-72a3169dd7ee)**
_community · 2026-02-26_

Community article with the most direct insight on triggering diagnostics and the practical description formula.

**Key techniques:**
- Description formula: what_it_does + when_to_use + literal_user_phrases
- Include phrasing variants ("write a README", "create a readme", "document this project")
- Triggering debug: test direct invocation first to isolate description vs. instructions problem
- `references/` for extensive content that should not load on every activation

**Notable:** "If your skill does not trigger, it is almost never the instructions. It is the description." — the most actionable troubleshooting diagnosis in this angle, useful as a first check in a skill audit workflow.

Feeds: Dimension 6 (skills), Trigger optimization (subtrigger), Dimension 13 (house conventions)

---

### **[Agent Skills in the SDK - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills)**
_official-anthropic · accessed 2026-06-28_

SDK documentation for using skills in programmatic agents. Explains that skills must be created as filesystem artifacts and details how to filter skills per session via the `skills` option, how to test them programmatically, and how to diagnose "Skill Not Being Used".

**Key techniques:**
- Skills filtered per session via `skills: ['name1', 'name2']` option in `query()`
- `settingSources` must include 'user' or 'project' for skill discovery
- Test: ask something that matches the description in a fresh session (clean context)
- Troubleshooting: "Check the description — ensure it is specific and includes relevant keywords"

**Notable:** The `skills` filter is a context filter, not a sandbox: skills not listed are hidden from the model but the files remain on disk and are accessible via Read and Bash.

Feeds: Dimension 6 (skills), Dimension 7 (sub-agents)

---

## How this feeds the method's evolution

- **Dimension 6 / new smell "description-as-code"**: The description is not descriptive prose, it is routing code. The quenching-evolutionist can add to the audit method the criterion: for each skill in the repository, verify whether the description passes the test "includes literal phrases the user would type" and "distinguishes itself from neighboring skills' descriptions with similar keywords". A description that fails this test is an actionable gap.

- **Dimension 6 / boundary "Trigger optimization (subtrigger)"**: Create as a sub-criterion of Dimension 6 the verification of the should-trigger/should-not-trigger pair. To audit: manually generate 3-5 prompts that SHOULD trigger and 3-5 that SHOULD NOT (tricky, similar keywords) for each critical skill, and verify behavior in a fresh session. If the skill fires on should-not-trigger prompts, it is a false positive; if it does not fire on should-trigger prompts, it is a missed fire — both are description gaps, not instruction gaps.

- **Dimension 6 / benchmark criterion**: The method can incorporate the evals.json + benchmark.json structure as a maturity standard for skills. A high-level auditable skill has: >=3 test cases in evals.json, a comparative baseline (with/without), a positive pass_rate delta, and specific, verifiable assertions. The evolutionist can add this criterion as a skill publication checklist for the repository.

- **Dimension 6 / boundary "Outgrowth detection"**: Skills should be periodically reviewed to verify whether the base model has not made them unnecessary (outgrowth). The audit method can include a step: for each existing skill, run a benchmark without the skill and verify whether the pass_rate delta still justifies the token cost. Skills with a negligible delta should be removed or merged.

- **Dimension 12 (boundary doctrine) / CLAUDE.md vs. skill**: The boundary criterion is actionable: procedural instructions (checklists, workflows, repeated processes) belong in a skill; facts and conventions belong in CLAUDE.md. The quenching-evolutionist can use this as a smell detector: any section of CLAUDE.md that describes a process with numbered steps is a candidate for extraction into a skill with `disable-model-invocation: true` if timing must be controlled by the user.

- **Dimension 6 / `paths` field as scope control**: For repository audit skills (such as quenching-management), the `paths` field allows restricting automatic activation to contexts where knowledge surface files are in scope (CLAUDE.md, `.claude/skills/`, `docs/arquitetura/`). This avoids false triggers on pure coding tasks and makes the skill fire precisely when the agent is editing the repository's own knowledge infrastructure.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of the sources in this angle (workflow `deep-research`, 2026-06-28). Sources confirmed: **11**.

The set of 12 sources is of generally high quality: all URLs exist and are accessible, the tiers are correct (official Anthropic, engineering blog, open spec, community) and the dates are accurate. Coverage of the agentskills.io ecosystem — cross-platform adoption confirmed with ~40 products including OpenAI Codex, GitHub Copilot, Cursor, Gemini CLI and Databricks Genie Code — is factual. Only one source presents a minor characterization problem: the InnovAItion Partners article does not use the terms "capability uplift" and "encoded preferences" as formal categories as described in the summary. The official Anthropic sources (platform.claude.com, code.claude.com, anthropic.com/engineering) are especially reliable and the content matches the provided summaries with precision.

Sources flagged (review before citing):

| Source | Verdict | Problem |
| --- | --- | --- |
| https://innovaitionpartners.com/blog/claude-agent-skills-2.0-the-beginners-guide-to-the-updated-skill-creator | `mischaracterized` | The summary claims the article 'distinguishes two types of skills: capability uplift (teaches new processes) and encoded preferences (encodes styles and organizational workflows)'. The verified content confirms that the article does NOT use these exact terms — it distinguishes between the skill content (the instructions) and the trigger (the description), not skill categories by type. The attribution of these two la... |
