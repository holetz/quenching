# Anthropic Agent Skills — authorship, structure and progressive disclosure

> Covers the anatomy of SKILL.md (frontmatter, body, references, scripts), the three-layer loading mechanism, and trigger optimization techniques — directly feeds Dimension 6 (skills) and the «progressive disclosure / context budget» and «trigger optimization (subtrigger)» boundaries of the `quenching-management` skill.

## Synthesis

Anthropic's Agent Skills system implements a three-layer loading mechanism that is fundamental for any repository-audit skill: (1) only the YAML frontmatter (name + description, ~100 tokens per skill) is pre-loaded into the system prompt at every startup; (2) the full body of the SKILL.md enters context only when the skill is activated; (3) reference files and scripts are loaded on demand as Claude references them during execution. This «progressive disclosure» model — or «progressive discovery» in Phil Whittaker's reformulation, which emphasizes Claude's active agency in navigating the filesystem — makes it economically viable to keep dozens of skills installed simultaneously without a context penalty. For a skill that audits a repository's knowledge surface, this means the entire architectural documentation, indexes, and audit checklists can exist as reference files at zero cost until consulted.

The `description` field is the most critical mechanism in the stack. It is the only signal the model has to decide whether and when to invoke a skill — there is no external classifier, embeddings, or regex; it is just the transformer forward pass over the description text compared to the current task. Official documentation and community literature converge on four principles for effective descriptions: (a) always write in third person, since the text is injected into the system prompt; (b) combine *what* the skill does with *when* to use it (including concrete trigger phrases); (c) be «a little pushy», as Claude has a measurable tendency to under-trigger skills; (d) add explicit exclusion clauses («Do NOT use for...») to avoid conflict between overlapping skills. The 1536-character combined limit between `description` and `when_to_use` in Claude Code requires prioritizing the most discriminating trigger phrases at the start of the text.

The full anatomy of SKILL.md in Claude Code exposes frontmatter fields beyond the two mandatory fields of the open standard (agentskills.io): `allowed-tools` and `disallowed-tools` (granular per-skill tool control, supporting patterns like `Bash(git *)`), `disable-model-invocation` (for skills that should only be invoked by the user via `/name`), `user-invocable: false` (background knowledge that only Claude should load), `context: fork` with `agent:` (executes the skill in an isolated sub-agent), `paths` (activates the skill only for files matching globs), `model` and `effort` (per-skill model/effort override), and `hooks` (lifecycle hooks scoped to the skill). The `` !`command` `` field supports dynamic context injection — Claude Code executes the command before passing the content to the model, allowing an audit skill to automatically inject the current diff, git status, or the result of a validation script.

The comparison between Skills, MCP, and sub-agents reveals complementary boundaries: Skills package *procedural knowledge and domain context* as filesystem artifacts that Claude discovers and loads autonomously; MCP provides *integration with external tools* (servers with a standardized protocol); sub-agents are *parallel model instances* orchestrated programmatically or via `context: fork`. Skills and sub-agents compose: a sub-agent can have skills pre-loaded in its context (the `skills` field in the sub-agent definition), and a skill can launch a sub-agent via `context: fork`. For the knowledge management skill, this suggests a three-layer architecture: the root skill (SKILL.md with a precise description and a reference index), per-domain reference files (current architecture, backlog, ADRs, etc.), and automated detection scripts that return only the relevant output.

The 14-pattern catalog documented by the community (Generative Programmer) reveals the most common smells in audit skills: instruction without reasoning («MUST» without the «because»), absence of an exclusion clause in the description, undocumented known gotchas, and absence of a self-correction loop for verifications that can fail. The «Known Gotchas Pattern» — a dedicated section of concrete failures previously observed — is described as «the most valuable content of a mature skill». For the `quenching-management` skill, this implies documenting explicitly the cases where the audit produces a false positive (e.g., CLAUDE.md with a link to the architecture does not imply the doc exists at the referenced path) and the cases where it under-triggers (e.g., a task of «verify if the backlog is up to date» may not match the description if it doesn't contain the right trigger phrase).

## Sources

### **[Skill authoring best practices — Claude Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices)** — _official-anthropic · accessed 2026-06-28_

Complete normative authoring guide: concision principles (context is a public resource), calibration of freedom degree (high/medium/low freedom for low/medium/high fragility), gerund naming (`processing-pdfs`, `analyzing-spreadsheets`), frontmatter validation rules (name max 64 chars lowercase-hyphen, description max 1024 chars, no XML tags, no reserved words «anthropic»/«claude»), writing descriptions in third person with trigger phrases, three progressive disclosure patterns (high-level guide with references, domain-specific, conditional details), maximum reference depth (one level from SKILL.md), TOC in files >100 lines, body <500 lines, workflows with copyable checklist, self-correcting loop (validate→fix→repeat), template pattern in two flavors (strict vs flexible), examples pattern (input/output pairs), conditional workflow pattern, iterative development Claude A (author) × Claude B (tester), evaluations before extensive documentation.

**Key techniques:**
- Third-person description with `what + when` including concrete trigger phrases (examples provided)
- SKILL.md body <500 lines; reference files max 1 hop depth (avoid nesting)
- Evaluation-driven development: create 3 evals before writing documentation
- Claude A × Claude B iteration with observation of real behavior on tasks (not test scenarios)
- Known Gotchas pattern: section of concrete failures previously observed
- MCP tools with fully qualified name `ServerName:tool_name` to avoid «tool not found»

**Notable:** «The name and description in your Skill's metadata are particularly critical. Claude uses these when deciding whether to trigger the Skill.» + recommends descriptions «a little pushy» as Claude has a measurable tendency to under-trigger.

Feeds: Dimension 6 (skills); boundaries «progressive disclosure / context budget» and «trigger optimization (subtrigger)»

---

### **[Agent Skills — Claude Platform Docs (Overview)](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview)** — _official-anthropic · accessed 2026-06-28_

Architectural overview: three content types (instructions, code, resources) × three loading levels with documented cost (Level 1 ~100 tokens always; Level 2 <5k tokens on trigger; Level 3 effectively unlimited since scripts never load code into context, only output). Canonical directory structure, required SKILL.md fields, comparison between surfaces (claude.ai, API, Claude Code), sharing scope, runtime environment constraints (API without network and without package install; Claude Code with full network access), available pre-built skills, open-source skills in the github.com/anthropics/skills repository.

**Key techniques:**
- Cost table: Level 1 ~100 tokens, Level 2 <5k tokens, Level 3 zero cost until read
- Scripts executed via bash: only output enters context (script code never loads)
- `allowed-tools` in frontmatter works only in CLI, not in SDK
- Skills directory in Claude Code: `~/.claude/skills/` (personal) or `.claude/skills/` (project)

**Notable:** The diagram confirms that Claude navigates the skill directory as filesystem via bash Read tools — there is no special injection mechanism; it is standard filesystem access of the execution environment.

Feeds: Dimension 6 (skills); Dimension 7 (sub-agents); boundary «progressive disclosure / context budget»

---

### **[Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)** — _engineering-anthropic · accessed 2026-06-28_

Technical engineering post describing the design philosophy: progressive disclosure as a foundational principle (analogy with manual TOC→chapters→appendix), skills as composable capabilities that transform generic agents into specialists, complementary integration with MCP (skills teach complex workflows involving MCP tools), future vision of agents creating and refining skills autonomously (codification of patterns observed in behavior).

**Key techniques:**
- Skills = workflow knowledge; MCP = tool integration (complementary, not competing)
- «Start with evaluation» pattern: run agent on real tasks before creating a skill
- Audit code, scripts, and network instructions before installing a skill from an unknown source
- Vision of agents creating skills autonomously as distillation of observed patterns

**Notable:** «Skills will complement MCP servers by teaching agents more complex workflows that involve external tools and software» — delimits the architectural boundary between Skills and MCP.

Feeds: Dimension 6 (skills); Dimension 7 (sub-agents); Dimension 12 (boundary doctrine)

---

### **[Introducing Agent Skills — Claude Blog](https://claude.com/blog/skills)** — _official-anthropic · 2025-10-16_

Official launch announcement with December 18, 2025 update publishing the open standard at agentskills.io. Skills are described with four characteristics: composable, portable (cross-platform via open standard), efficient (load on demand), powerful (execute code). Announces partner ecosystem (Box, Canva, Notion, Rakuten) and org-wide management.

**Key techniques:**
- agentskills.io open standard for cross-platform portability
- Pre-built skills for PowerPoint/Excel/Word/PDF already in use in Claude apps
- Org-wide skill management as an enterprise feature

**Notable:** The agentskills.io open standard allows skill portability across AI tools — direct implication for the knowledge management skill working beyond Claude Code.

Feeds: Dimension 6 (skills); Dimension 13 (house conventions)

---

### **[Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)** — _official-anthropic · accessed 2026-06-28_

Canonical documentation of skills in Claude Code with all frontmatter fields documented. Key fields beyond the two mandatory ones: `when_to_use` (appended to description, both truncated at 1536 chars); `disable-model-invocation: true` for workflows with side effects; `user-invocable: false` for background knowledge; `allowed-tools`/`disallowed-tools`; `model`/`effort` override; `context: fork` with `agent:`; `paths` glob for path-conditional activation; `hooks` lifecycle scoped to the skill; `` !`command` `` for dynamic context injection. Also documents: skill content lifecycle (5000 tokens per skill on compaction, total budget 25000 tokens), override hierarchy (enterprise > personal > project > plugin), live change detection, nested skills in monorepos with qualified namespace.

**Key techniques:**
- `when_to_use`: supplementary field for trigger phrases, truncated together with description at 1536 chars
- `disable-model-invocation: true` for deploy, commit — skills with side effects controlled by user
- `user-invocable: false` for background knowledge (e.g., `legacy-system-context`)
- `paths:` activates skill only for files matching glob — scoping by module in monorepos
- `` !`command` `` injects shell output before Claude sees the content (preprocessing, not execution)
- Skill on compaction: keeps 5000 tokens per skill, shared total budget of 25000 tokens

**Notable:** Golden rule for separating CLAUDE.md from skill: «Create a skill when a section of CLAUDE.md has grown into a procedure rather than a fact.» Defines the boundary: procedure (skill) vs. fact (CLAUDE.md).

Feeds: Dimension 1 (CLAUDE.md as map); Dimension 6 (skills); Dimension 8 (hooks); boundaries «progressive disclosure» and «trigger optimization»

---

### **[Agent Skills in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/skills)** — _official-anthropic · accessed 2026-06-28_

Documentation of skills in the Claude Agent SDK: skills are filesystem artifacts (not programmatic), discovered via `settingSources`, controlled via the `skills` option in the query. `allowed-tools` from frontmatter does NOT work in SDK — use `allowedTools` in query config. `skills: []` disables all discovered skills.

**Key techniques:**
- SDK: `allowed-tools` from frontmatter ignored — use `allowedTools` in query config
- `skills: []` is a context filter, not a sandbox: files still accessible via Read/Bash
- Plugin skills: `plugin:skill` namespace to avoid name collisions
- `settingSources` must include `'user'` or `'project'` for discovery to work

**Notable:** «The skills option is a context filter, not a sandbox» — disabling a skill does not prevent direct reading of SKILL.md via filesystem, critical for security auditors.

Feeds: Dimension 6 (skills); Dimension 7 (sub-agents); Dimension 14 (behavioral guardrails)

---

### **[Skill Authoring Patterns from Anthropic's Best Practices — Generative Programmer](https://generativeprogrammer.com/p/skill-authoring-patterns-from-anthropics)** — _community · accessed 2026-06-28_

Catalog of 14 authoring patterns organized in 5 groups: Discovery & Selection (Activation Metadata, Exclusion Clause), Context Economy (Context Budget, Progressive Disclosure), Instruction Calibration (Control Tuning, Explain-the-Why, Template Scaffold, In-Skill Examples, Known Gotchas), Workflow Control (Execution Checklist, Self-Correcting Loop, Plan-Validate-Execute), Executable Code (Utility Bundle, Autonomy Calibration).

**Key techniques:**
- Exclusion Clause: «Do NOT use for...» as the most important line of the description for large collections
- Explain-the-Why: rule + reason so Claude generalizes unforeseen cases
- Known Gotchas: «most valuable content of a mature skill»
- In-Skill Examples: 2-3 I/O pairs embedded (few-shot inside the skill)
- Autonomy Calibration: `allowed-tools` declared explicitly (Read/Grep/Glob for readonly auditing)

**Notable:** The Exclusion Clause is described as «the single most important line in the description» for repositories with many skills — directly applicable to repos with 20+ skills.

Feeds: Dimension 6 (skills); boundaries «trigger optimization» and «boundary doctrine»

---

### **[The SKILL.md Pattern: How to Write AI Agent Skills That Actually Work — Medium](https://bibek-poudel.medium.com/the-skill-md-pattern-how-to-write-ai-agent-skills-that-actually-work-72a3169dd7ee)** — _community · accessed 2026-06-28_

Practical analysis focused on the description↔activation relationship. Central insight: «If your skill does not trigger, it is almost never the instructions. It is the description.» Documented anti-pattern table. Non-activation debugging order: description specificity → file paths → YAML syntax → session state.

**Key techniques:**
- Description must include phrases that match how users naturally request the task
- Debug in the right order: description first, instructions last
- XML brackets in frontmatter can inject unintended instructions into the system prompt
- Explicit activation via `/name` works even with a bad description — but auto-trigger does not

**Notable:** The debugging priority (description before instructions) is counterintuitive but confirms that 30 tokens of poorly written description completely breaks automatic activation.

Feeds: Dimension 6 (skills); boundary «trigger optimization (subtrigger)»

---

### **[Progressive Discovery: A Better Mental Model for Agent Skills — DEV Community](https://dev.to/phil-whittaker/progressive-discovery-a-better-mental-model-for-agent-skills-51bd)** — _community · accessed 2026-06-28_

Reformulation of «progressive disclosure» as «progressive discovery»: Claude is the active agent discovering skills (not the skills revealing information). Shifts focus from «what to reveal when» to «can Claude find what it needs here?». Practical threshold: monolithic SKILL.md works up to ~500 lines / 5000 tokens; above that, index-plus-references.

**Key techniques:**
- Per-layer design question: «Can Claude find what it needs and decide whether to go deeper?»
- Claude navigates conditionally (not sequentially) through the levels of a skill
- Section headings must be scannable enough for Claude to decide whether to read the content
- Inflection threshold: 500 lines / 5000 tokens

**Notable:** «Disclosure» implies skill as active emitter; «discovery» places Claude as active navigator — the difference changes how you write the section structure (scannability > completeness).

Feeds: Dimension 6 (skills); boundary «progressive disclosure / context budget»

---

### **[Claude Agent Skills: A First Principles Deep Dive — Lee Han Chung](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)** — _community · 2025-10-26_

First-principles analysis of the internal architecture: dual-channel communication (isMeta:true for instructions hidden from Claude, isMeta:false for status visible to user), contextModifier function for pre-approval of tools and model switching, selection by pure LLM reasoning with no external classifier. Token budget: 15000 chars for skill listing in context. `when_to_use` field as an unofficial supplement to description.

**Key techniques:**
- Pure LLM reasoning: no regex/embedding/classifier — only transformer forward pass
- 15000 chars total budget for listing available skills in context
- `when_to_use` appends to description in skill listing (Claude Code documents it officially)
- isMeta:true/false: dual channel for UI transparency + private instruction to the model

**Notable:** «There is no algorithmic skill selection at the code level» — confirms that 30 tokens of poorly written description completely break activation, as it is the only selection mechanism.

Feeds: Dimension 6 (skills); boundaries «trigger optimization» and «behavioral guardrails»

---

### **[What Is SKILL.md in Claude Skills? Structure, Resources & Loading — Skywork.ai](https://skywork.ai/blog/ai-agent/claude-skills-skill-md-resources-runtime-loading/)** — _community · accessed 2026-06-28_

Introductory article documenting the conventional directory structure (resources/, templates/, scripts/) and the three-stage runtime loading mechanism. Notes that until October 2025 Anthropic did not enumerate hard size limits — the practical limits (<500 lines, <5000 tokens) came from later official guidance.

**Key techniques:**
- Conventional layout: `resources/` for references, `templates/` for prompts, `scripts/` for executables
- Thematic organization enables selective loading by domain
- Practical limits are guidance, not hard system constraints

Feeds: Dimension 6 (skills); boundary «progressive disclosure / context budget»

---

## How it feeds the method evolution

- **Dimension 6 / smell «weak description»:** Add to the method a verifiable description criterion: (a) contains third person? (b) has explicit `what + when`? (c) has at least one literal trigger phrase that a user would naturally use? (d) has an exclusion clause «Do NOT use for...»? A description that fails any of these four points is an auditable smell — the `quenching-evolutionist` can list all skills in the repo, extract the 1536 chars of description+when_to_use and check each criterion with a simple prompt.

- **Dimension 6 / smell «absence of Known Gotchas»:** Mature skills have a section of concrete failures observed («the most valuable content of a mature skill»). The method can add this as a maturity criterion: a skill without a gotchas section = a skill not validated in production. For `quenching-management`, document explicitly the audit false positives (a link to an existing file does not imply that the file has the expected content) and the activation false negatives (a valid task that doesn't match the description).

- **Dimension 1 × 6 / CLAUDE.md vs. skill boundary:** The canonical rule («Create a skill when a section of CLAUDE.md has grown into a procedure rather than a fact») is a concrete audit criterion. The method can include a CLAUDE.md scan step to identify sections that have become procedures (>5 sequential lines with numbered steps or action bullets) and flag them as candidates for migration to a skill.

- **Dimension 6 / progressive disclosure:** Any skill with SKILL.md >500 lines or references at more than one level of depth is a smell of «flat disclosure» — the method should include this threshold as a structural audit criterion. The section heading scannability criterion (Phil Whittaker) is also auditable: can Claude decide whether to read a section from the heading alone?

- **Dimension 6 / underused frontmatter fields:** The method can audit whether skills with side effects declare `disable-model-invocation: true` (deploy, commit, send-message), whether background context skills declare `user-invocable: false`, and whether read-only skills declare `allowed-tools: Read Grep Glob` for adherence to the least-privilege principle. These fields are grep-verifiable in SKILL.md.

- **Dimension 12 / Skills vs. MCP vs. sub-agents boundary:** Add to the method the classification criterion: (a) skill = workflow knowledge + domain context packaged as a filesystem artifact; (b) MCP = integration with an external system via a standardized protocol; (c) sub-agent = parallel model instance. A backlog item that does all three is a candidate for decomposition. The `quenching-evolutionist` can audit whether the repository has skills trying to be MCP (making HTTP calls) or skills trying to be sub-agents (instructing Claude to spawn agents instead of using `context: fork`).

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **10**.

Set of 11 sources of generally high quality: all URLs exist and are accessible, publishers and dates are correct, and the technical summaries are accurate in 10 of 11 entries. The only problem found is a fabricated phrase in the «notable» field of the official Anthropic source (best-practices), where the expression «a little pushy» is attributed to the documentation without appearing in the actual text — low risk for the integrity of the set because the rest of that source is correct. The community sources (Generative Programmer, Medium, DEV Community, leehanchung, Skywork) are legitimate, published in 2025-2026, and their summaries reflect the actual content with good fidelity. No fabricated URLs or fake publishers.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://platform.claude.com/docs/en/agents-and-tools/agent-skills/best-practices | `mischaracterized` | The «notable» field attributes to the documentation the expression «a little pushy» to describe how to write skill descriptions — this phrase does not appear anywhere in the actual document. The official text says only «Make sure they clearly describe what the Skill does and when it should be used.» The citation that DOES appear verbatim («The name and description in your Skill's metadata are particularly cr...») |
