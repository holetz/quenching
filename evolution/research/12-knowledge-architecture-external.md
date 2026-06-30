# Knowledge architecture and documentation (external references)

> Covers the external frameworks and standards that define how to organize, type, and maintain the knowledge surface of a repository for effective use by AI agents — feeds directly into the boundaries of dimensions 2 (current architecture), 3 (vision), 4 (backlog), 5 (ADR), 6 (skills), 12 (boundary doctrine/canonical home), and 13 (house conventions).

## Synthesis

The Diataxis framework (Procida, 2021–present) and its predecessor the Divio Documentation System offer the most solid conceptual foundation for organizing knowledge surfaces: all documentation serves one of four modes (tutorial, how-to, reference, explanation), determined by two axes — practical/theoretical content crossed with an acquisition/application objective. The critical contribution for an auditing skill is that mixing quadrants is the primary cause of useless documentation. In a 14-dimension surface like that of the `quenching-management` skill, the same principle maps directly: CLAUDE.md as a map (reference), ADRs as explanation of past decisions, current architecture docs as the canonical reference, and backlog as how-to for pending work. The auditor must detect when content from one quadrant has migrated to another unintentionally — for example, CLAUDE.md accumulating explanation that belongs in `docs/arquitetura/`.

The docs-as-code doctrine (Write the Docs) applies to repository knowledge the same principles that code already has: versioning in Git, review via pull request, CI to detect drift, and DRY via modular content. Single-source-of-truth is the direct corollary: each piece of information has a canonical home; copies are noise. For the auditing skill, this translates to "boundary doctrine" (dimension 12) — detecting duplication between CLAUDE.md, architecture docs, skills, and memory is a concrete smell. The arXiv paper 2602.20478 ("Codified Context Infrastructure") quantifies the cost: stale specs cause silent failures where the output looks correct but conflicts with recent refactors; the team reported 1–2 h/week of maintenance for ~26,200 lines of context supporting 108,000 lines of code.

Spec-Driven Development (SDD) elevates documentation to a primary artifact: the code is derived from the spec, not the other way around. The arXiv paper 2602.00180 proposes three levels of rigor (spec-first, spec-anchored, spec-as-source) and the "reconstruction test" — deleting the code and attempting to regenerate it solely from the spec reveals gaps of implicit undocumented knowledge. For the auditing skill, this suggests a completeness criterion for dimensions 2 and 5: an architecture doc or ADR is sufficient if a new agent can reproduce the decision without asking a human. Augment Code operationalizes this by distinguishing "requirement" (what) from "decision" (why, with embedded security/architecture rationale).

The three-layer architecture for agent context files (arXiv paper 2602.20478 + groff.dev) is the most actionable reference for the auditing skill: (1) hot memory / constitution — always loaded, concise, universal; (2) specialized skills/agents — loaded on demand by domain; (3) cold memory / specifications — retrieved by keyword/semantics when relevant. Claude Code (arXiv paper 2604.14228) implements this via lazy-loading: a subfolder CLAUDE.md is only read when the agent reads files in that folder. The auditable smell is when layer 1 has bloated with layer 3 content — the empirical limit of 150 lines for the root CLAUDE.md (research across 2,500+ repos) and "if AGENTS.md is bigger than the README, it's probably too long" are objective criteria.

ADRs (Nygard/MADR 4.0.0 format, September 2024) complete the architecture by separating open decisions (not yet implemented) from current architecture (already implemented and distilled into reference docs). MADR adds machine-readable YAML front matter for status, date, deciders, and roles — making the state verifiable by CI. The rule of the repository in question — "an implemented ADR leaves the tree, distils into docs/arquitetura/" — is an exact instance of boundary doctrine: the information has a single home per lifecycle phase. The AGENTS.md standard, now under the Agentic AI Foundation (Linux Foundation, December 2025) with 60,000+ adopting repos, complements CLAUDE.md as a cross-tool standard for agent context, reinforcing separation of concerns: README for humans, AGENTS.md/CLAUDE.md for agents, skills for domains, cold memory for specs.

## Sources

### **[Diataxis — A systematic framework for technical documentation](https://diataxis.fr/)** — _spec-standard · accessed 2026-06-28_

Daniele Procida's canonical framework that organizes documentation into four types crossing two axes: practical/theoretical content and a skill acquisition/application objective. Adopted by Django, Canonical, Cloudflare, Gatsby. The central premise is that mixing quadrants is the root cause of most documentation problems.

**Key techniques:**
- Map each document to the correct quadrant by the (content-axis, objective-axis) pair
- Tutorials: immersion in action without excessive theoretical explanation; assumes a zero-experience user
- How-to: assumes prior competence, focus on a specific task with a verifiable result
- Reference: neutral and structural description (like a map), without opinions
- Explanation: context and "why", may roam across topics, exists for understanding acquisition
- Start by identifying one improvable element and iterate — do not rewrite everything
- Quadrant separation prevents tutorials overloaded with theory

**Notable:** Diataxis found an unexpected "second life" — the structure that helps humans navigate also makes documentation more digestible for RAG systems and AI agents.

Feeds: dimensions 2, 3, 4, 5, 12, 13

---

### **[The Divio Documentation System](https://docs.divio.com/documentation-system/)** — _spec-standard · accessed 2026-06-28_

Predecessor to Diataxis, created by Divio and presented at PyCon AU 2017 by Procida. Establishes the same four types and the principle "there isn't one thing called documentation — there are four". Widely cited as the origin of the taxonomy that Diataxis formalized.

**Key techniques:**
- Strict separation of the four types as a quality prerequisite
- Each type requires a distinct writing mode
- Projects need all four types integrated to serve different user moments
- Simple, comprehensive, and almost universally applicable framework

**Notable:** Foundational phrase — "There isn't one thing called documentation, there are four" — serves as an auditable smell criterion when content of different types coexists in the same file.

Feeds: dimensions 2, 12, 13

---

### **[Docs as Code — Write the Docs](https://www.writethedocs.org/guide/docs-as-code/)** — _spec-standard · accessed 2026-06-28_

Canonical reference from the Write the Docs community for the docs-as-code philosophy: treating documentation with the same tools and processes as code (Git, PR review, lightweight markup, CI/CD). Promotes single-source-of-truth as a direct corollary of unified versioning.

**Key techniques:**
- Git versioning as the single source of truth for documentation
- Doc review via pull requests for transparency and feedback
- Automated CI to detect drift between code and documentation
- DRY applied to docs via modular and reusable content
- Docs required for feature merge encourages synchronous updates

**Notable:** Recommends three foundational books: "Docs Like Code" (Anne Gentle), "Modern Technical Writing" (Andrew Etter), "Crafting Docs for Success" (Diana Lakatos).

Feeds: dimensions 2, 12, 13

---

### **[Codified Context: Infrastructure for AI Agents in a Complex Codebase](https://arxiv.org/html/2602.20478v1)** — _academic-other · Feb/2025_

Empirical paper that proposes treating project documentation as load-bearing infrastructure for AI agents. Documents a three-layer architecture evaluated across 283 sessions, 2,801 human prompts, and 16,522 agent turns. Knowledge-to-code ratio of 24.2% (26,200 lines of context for 108,000 lines of code).

**Key techniques:**
- Hot memory (constitution ~660 lines): always loaded, universal rules, failure modes, orchestration protocols
- Specialized agents (19 specs of 115–1,233 lines): created reactively when failure patterns emerge
- Cold memory (34 spec docs ~16,250 lines): retrieved by keyword/MCP on demand
- Specs written for AI consumption: explicit paths, do/don't-do patterns, symptom-cause-fix tables
- Automatic routing tables: map file area to which specialist agent to invoke
- Codify repeated explanations: if you explained it twice, write it as a spec
- Stale specs cause silent failures — agents trust documentation absolutely

**Notable:** The most referenced spec appeared in 74 independent sessions with zero related bugs — concrete proof of the ROI of well-structured documentation for agents.

Feeds: dimensions 1, 2, 6, 7, 12

---

### **[Dive into Claude Code: The Design Space of Today's and Future AI Agent Systems](https://arxiv.org/html/2604.14228v1)** — _academic-other · Apr/2025_

Academic paper that analyzes the TypeScript source code of Claude Code, identifying 13 design principles derived from 5 values. Documents the four-level CLAUDE.md hierarchy, the 5-layer context compaction pipeline, and the 4 extension mechanisms (MCP, plugins, skills, hooks).

**Key techniques:**
- Root CLAUDE.md + subfolders: lazy-loading — only loaded when the agent reads files in that directory
- 4-level hierarchy: managed settings -> project-level -> directory-specific -> auto-memory
- Skills for specific domains, hooks for policy, MCP for external integrations (separation of concerns)
- 5-layer compaction pipeline: budget reduction -> snip -> microcompact -> context collapse -> auto-compact
- Subagents with isolated contexts return only a summary to the parent (no context inflation)

**Notable:** Identified tension — Claude Code amplifies short-term productivity (27% of tasks would not be attempted without the tool) but offers limited mechanisms for long-term human learning. Docs should include learning scaffolding, not just task completion.

Feeds: dimensions 1, 6, 7, 8, 14

---

### **[Implementing CLAUDE.md and Agent Skills In Your Repository](https://www.groff.dev/blog/implementing-claude-md-agent-skills)** — _community · accessed 2026-06-28_

Practical guide by Matthew Groff for the 3-layer architecture: root CLAUDE.md (<100 lines, universal rules), skills (.claude/skills/name/SKILL.md, <500 lines, domain-specific), and agent guides (docs/agent-guides/, deep reference loaded on demand). Proposes 5 essential starter skills and concrete anti-patterns.

**Key techniques:**
- Tier 1 (root): Why/What/How/Progressive Disclosure, max ~100 lines
- Tier 2 (skills): YAML frontmatter with name and description, on-demand, max ~150 lines
- Tier 3 (agent guides): deep reference material pointed to by skills
- 5 essential skills: build-test-verify, git-commit, create-pull-request, core-conventions, self-review-checklist
- Subfolder CLAUDE.md: 20–30 lines, only unique constraints for that directory
- Anti-patterns: do not auto-generate CLAUDE.md, do not use as a linter, do not duplicate across tiers

**Notable:** Code review comments are a signal of missing context — each one is an opportunity to refine the rules. Criterion: if AGENTS.md/CLAUDE.md is bigger than the README, it's probably too long.

Feeds: dimensions 1, 6, 12, 14

---

### **[Spec-Driven Development: From Code to Contract in the Age of AI Coding Assistants](https://arxiv.org/html/2602.00180v1)** — _academic-other · Feb/2025_

Paper that formalizes SDD as an inversion of the traditional flow: the spec is the maintained primary artifact, the code is derived. Defines three levels of rigor and the "reconstruction test" as a specification completeness criterion.

**Key techniques:**
- Spec-first: guides initial development, can be discarded afterwards
- Spec-anchored: evolves alongside the code, CI validates conformance via contract tests
- Spec-as-source: humans only edit specs, code is generated; comments "GENERATED FROM SPEC — DO NOT EDIT"
- Reconstruction test: delete the code, provide only the spec to a new agent; failures reveal implicit knowledge
- Specs for AI consumption: input/output, pre/post-conditions, invariants, domain-oriented language
- Use the minimum level of rigor needed to eliminate ambiguity

**Notable:** Foundational principle — "Code is the implementation detail of the specification — not the other way around." When spec and implementation diverge, the spec is authoritative.

Feeds: dimensions 2, 5, 12

---

### **[Spec-driven development: Unpacking one of 2025's key new AI-assisted engineering practices](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)** — _community · 2025_

Thoughtworks article that positions SDD as a direct response to "vibe coding" — agents that produce plausible code but drift from the real intent. Describes the use of larger contexts in modern LLMs and BDD techniques for specs.

**Key techniques:**
- Separate business requirements from technical specs into different files
- Specs should use Given/When/Then language to reduce ambiguity
- Mandatory human-in-the-loop before code generation
- Deterministic CI/CD to detect spec drift and hallucinations
- Structured input/output formats reduce model errors

**Notable:** Debate about the source of truth — some treat the spec as the primary artifact; others keep the code as the primary artifact with the spec as a driver. This distinction is relevant for deciding which document "wins" in the event of a conflict.

Feeds: dimensions 2, 5, 12

---

### **[Understanding Spec-Driven-Development: Kiro, spec-kit, and Tessl](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html)** — _community · 2025_

Critical analysis on Martin Fowler's blog of three SDD tools. Distinguishes "spec" (a feature development artifact) from "memory bank" (persistent context across sessions — rules files, architectural descriptions). Raises concerns about review overhead and the parallel with Model-Driven Development.

**Key techniques:**
- Spec vs. memory bank distinction: specs are per-feature and transient; memory bank is persistent and cross-session
- Kiro: Requirements -> Design -> Tasks as three Markdown documents
- Spec-kit (GitHub): "constitution" with immutable principles + specify/plan/tasks cycle
- Tessl: the only one with real spec-anchored/spec-as-source support; generated code marked "DO NOT EDIT"

**Notable:** Critical warning — despite detailed specs, agents frequently ignore instructions or over-interpret them ("control illusion"). Lesson from historical MDD: overhead and inflexibility are real risks that must be prevented with concise specs.

Feeds: dimensions 2, 5, 12, 14

---

### **[The Spec as Source of Truth: Why Codebases Should Be Rebuildable from Documentation](https://www.augmentcode.com/guides/spec-as-source-of-truth-rebuildable-codebase)** — _community · accessed 2026-06-28_

Augment Code guide that distinguishes "requirement" (what) from "decision" (why, with security rationale and CVE mapping). Proposes "generation-grade" specs that embed architectural rationale, security constraints, and generation metadata.

**Key techniques:**
- Requirement vs. Decision: "endpoints require auth" (req) vs. "403 not 404 to prevent enumeration" (decision)
- Generation-grade specs: business rules + enforcement level + architectural rationale + CVE/CWE mapping
- Constitutional specs: separate document of non-negotiable constraints, avoids duplication across individual specs
- OpenAPI extensions (x-business-rules, x-architectural-decisions) for embedding rationale alongside the definition

**Notable:** Teams that version generated code without versioning specs "invert the dependency that matters most". The reconstruction test operationalizes completeness: failures reveal implicit undocumented knowledge.

Feeds: dimensions 2, 5, 12

---

### **[AGENTS.md — The Universal Standard for AI Agent Context](https://agents.md/)** — _spec-standard · Dec/2025_

The AGENTS.md standard, launched by OpenAI in August 2025 and transferred to the Agentic AI Foundation (Linux Foundation) in December 2025. Open Markdown format, now with 60,000+ adopting repos. Complements README (for humans) with context specific to agents.

**Key techniques:**
- Separation of concerns: README for humans, AGENTS.md for agents
- Canonical sections: project overview, setup commands, build/test commands, code style, testing, security, PR instructions
- Multi-file in monorepos: the agent uses the closest file in the directory (proximity-based precedence)
- No required fields — adapt to the project's real needs
- Update like code: whenever build processes or conventions change
- Compatible with all major runtimes: Claude Code, Codex, Cursor, Copilot, Devin, Gemini CLI

**Notable:** Addy Osmani — "If your AGENTS.md is bigger than your README, it's probably too long" — a direct smell criterion for the auditor.

Feeds: dimensions 1, 6, 7, 13

---

### **[Architectural Decision Records (ADRs) — adr.github.io](https://adr.github.io/)** — _spec-standard · accessed 2026-06-28_

Canonical site maintained by the ADR community. Documents the Nygard format (2011: Context/Decision/Consequences) and MADR 4.0.0 (September 2024, a superset of Nygard with YAML front matter). ADRs form the project's decision log, supporting knowledge retention as the team evolves.

**Key techniques:**
- Minimum Nygard format: Title / Status / Context / Decision / Consequences
- MADR 4.0.0: machine-readable YAML front matter (status, date, deciders, consulted, informed)
- Title in the format "Use X for Y" (MADR) instead of "Decision about Y"
- Context is the most important section: includes numbers, constraints, team factors
- Superseded ADR: mark as "superseded" with a link to the new ADR
- Store alongside source code in a dedicated docs/adr/ folder
- An implemented ADR distils into architecture docs — the ADR itself can be removed or archived

**Notable:** MADR 4.0.0 (Sep/2024) makes status machine-readable via YAML front matter — allows CI scripts to verify whether open ADRs have been implemented and should be removed from the tree.

Feeds: dimensions 5, 12

---

### **[Living Architecture: Structured Architecture Documentation for AI Coding Agents](https://ceaksan.com/en/living-architecture-ai-architectural-documentation)** — _community · accessed 2026-06-28_

Proposed architecture.md template with 10 core sections and 11 optional modules activated conditionally, in 3 depth levels (L1/L2/L3) scaled by project size. Distinguishes what is auto-generated (schemas, dependency graphs via CI) from what is human-written (decisions, trade-offs via ADRs).

**Key techniques:**
- Single architecture.md file for loading at session start — reduces context overhead
- Progressive disclosure with jump-to pointers and executable search commands
- 10 core sections: Stack, Module Map, Data Flow, Route/API, Data Model, Config, Security, Constraints, Tech Debt, Hotspots
- L1/L2/L3 by project complexity (50 files -> L1; 1,200-file monorepo -> L3)
- Auto-generated vs. human-written distinction: schemas/deps via CI hooks; decisions/trade-offs via ADR
- PR Check automation: GitHub Actions mapping changed files to sections of architecture.md
- Feedback loop: daily-code-review uses architecture.md as context and feeds Tech Debt/Hotspots

**Notable:** "Update on Change" strategy estimates ~2 minutes per relevant change (new dependency, route, table) — a concrete argument that keeping docs up to date is not expensive if done incrementally.

Feeds: dimensions 2, 7, 12

## How this feeds the method's evolution

- **Dimension 12 (boundary doctrine) — new cross-quadrant smell**: Using the Diataxis taxonomy, the auditor must verify whether each knowledge file belongs to a single quadrant. Concrete smell: CLAUDE.md containing explanation (which should be in docs/arquitetura/), or an ADR containing an API reference (which should be extracted). Criterion: "if this document serves two different purposes, it has two homes, not one."

- **Dimension 1 (CLAUDE.md as map) — empirical size criterion with source**: The 150-line limit for the root CLAUDE.md and the test "if AGENTS.md is bigger than the README, it's probably too long" (Addy Osmani / groff.dev) are verifiable criteria that the auditor can apply directly. Add to the checklist: count the lines in the root CLAUDE.md and emit an alert if > 150; check whether there is cold memory content (detailed specs, long examples) that should be in skills or agent guides.

- **Dimension 5 (ADR) — machine-readable state and auditable lifecycle**: MADR 4.0.0 makes the `status` field verifiable by script. The auditor can check via `grep` or YAML parser whether there are ADRs with status "Accepted" whose implementation is already in the code but the ADR still remains in the tree (it should have been distilled into docs/arquitetura/ and removed). Detection command: `grep -r "status: Accepted" docs/adr/` followed by verification of whether the corresponding feature already exists in production.

- **Dimension 2 (current architecture) — reconstruction test as a completeness criterion**: The SDD "reconstruction test" (arXiv 2602.00180 + Augment Code) offers an objective criterion: an architecture doc is complete if a new agent can reproduce the decision without asking a human. The auditor can apply this as a heuristic: "is there implicit knowledge that lives only in developers' memory and not in docs/arquitetura/?" — identified by repeated questions to the user or code review comments on the same topic.

- **Dimension 6 (skills) — separation of concerns across tiers**: The 3-layer architecture (hot memory / skills / cold memory) from groff.dev + arXiv 2602.20478 defines where each type of knowledge should live. The auditor must verify: (a) skills with content > 500 lines likely have embedded cold memory that should be in agent guides; (b) root CLAUDE.md with domain-specific instructions that should be in subfolder skills; (c) content duplication between tiers (violation of documentary DRY).

- **Dimension 12 (boundaries) — requirement vs. decision distinction**: The Augment Code pattern — "requirement says what, decision says why with embedded rationale" — is an auditable quality criterion for architecture docs and ADRs. Current architecture docs that describe what the system does without documenting why that choice was made are candidates for enrichment. The auditor can detect docs without a "Context" or "Rationale" section and flag them as incomplete for agent consumption.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources for this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **10**.

The set is of generally good quality: 10 of the 13 sources have an accessible URL, correct publisher, and a summary faithful to the actual content. The arxiv papers (2602.20478 and 2604.14228) and the practical guides (groff.dev, writethedocs, diataxis.fr, augmentcode) were all confirmed with a high degree of fidelity. The three problems found are ones of internal characterization (authorship attribution, technique displacement between sources, and incorrect numerical thresholds), not fabricated URLs or non-existent content — which suggests the sources were read but details were mixed between them during synthesis.

Flagged sources (review before citing):

| Source | Verdict | Problem |
| --- | --- | --- |
| https://docs.divio.com/documentation-system/ | `mischaracterized` | The summary states the system was 'created by Divio and presented at PyCon AU 2017 by Procida', but the current page attributes the content to 'David Laing' (The Grand Unified Theory of Documentation — David Laing), without mentioning Daniele Procida. The historical attribution may be correct, but the publisher/author as shown on the site today does not match the description. |
| https://arxiv.org/html/2602.00180v1 | `mischaracterized` | The summary attributes the 'reconstruction test' to this paper, but the fetch and search confirm the concept does not appear in the text (neither in the abstract nor in search results about the paper). The 'reconstruction test' belongs to Source 10 (Augment Code, April 2026). The three levels of rigor (spec-first/anchored/as-source) are correct, but the attribution of the summary's central technique is wrong. |
| https://ceaksan.com/en/living-architecture-ai-architectural-documentation | `mischaracterized` | The L1/L2/L3 thresholds described in the summary ('50 files → L1; 1,200-file monorepo → L3') do not match the actual page content: L1 < 30 files, L2 between 30–200, L3 > 200. The summary's thresholds are significantly different (50 vs. 30 for L1), indicating a numerical characterization error. |
