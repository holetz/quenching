# CLAUDE.md and Claude Code memory files

> This angle covers the hierarchy, syntax, best practices, and anti-patterns of Claude Code memory files — primarily feeds **Dimension 1 (CLAUDE.md as map)** and the **progressive disclosure / context budget** boundary.

## Synthesis

The Claude Code memory system operates on two complementary axes: **CLAUDE.md files** (written by humans, loaded every session, containing instructions) and **auto memory** (written by Claude itself, stored in `~/.claude/projects/<repo>/memory/MEMORY.md`, containing learnings). The CLAUDE.md hierarchy has four scopes in order of breadth: managed policy (org-wide, `/etc/claude-code/CLAUDE.md` on Linux, cannot be deleted), user (`~/.claude/CLAUDE.md`, personal preferences), project (`./CLAUDE.md` or `./.claude/CLAUDE.md`, shared via git), and local (`./CLAUDE.local.md`, gitignored, personal overrides per project). Within the git tree, loading follows the current directory going up to root; files in subfolders are loaded on demand when Claude reads files in those folders. This progression from general to specific allows team conventions to coexist with individual preferences without conflict.

The most important boundary for an audit skill is the separation between **always loaded** and **on demand**. Everything that goes in the root CLAUDE.md is injected at every session start, consuming context budget before the first message. The recommended limit is 200 lines (and frequently a more aggressive target of 60-120 lines in practice); beyond that, the model starts ignoring instructions due to signal dilution. Instructions don't need to all be in the root file: the `@path/to/file` mechanism imports additional files (they still count against context — they are expanded inline), and the `.claude/rules/` directory allows modular files with or without `paths:` frontmatter for conditional loading by glob. Skills (`.claude/skills/`) are the true **progressive disclosure** mechanism: they only enter context when invoked or when Claude determines relevance.

The most important operational distinction for auditing is: **CLAUDE.md = guidance, not enforcement; hooks = enforcement**. Instructions in CLAUDE.md are delivered as a user message after the system prompt, not as the system prompt itself — so Claude treats them as a guide, not an imposition. For behaviors that *must* happen (lint before commit, blocking writes to migrations), the correct mechanism is **hooks** (PreToolUse, Stop), which execute as shell commands regardless of what Claude decides. This boundary is the main detectable anti-pattern in auditing: mandatory instructions written in CLAUDE.md that should be hooks.

**Context rot** is the main smell associated with CLAUDE.md: accumulation of outdated, contradictory, or redundant instructions that silently degrade adherence. The signals are detectable: Claude ignoring existing instructions (file too large), Claude asking something already answered in CLAUDE.md (ambiguous formulation), instructions never violated (candidates for deletion — already the model's default). The operational audit criterion is: «if I removed this line, would Claude do something wrong?» — if the answer is no, delete or move to a hook. Style instructions already enforced by a linter, standard language conventions, and frequently changing content are the three most common candidates for removal.

For large repositories (monorepos, codebases with thousands of files), the canonized strategy is directory-based layering: root CLAUDE.md with global conventions (less than 80 lines), per-package/subsystem CLAUDE.md with local conventions (loaded on demand), `.claude/rules/` for instructions by file type with glob patterns, and skills for complex procedures that only matter in specific contexts. `claudeMdExcludes` in `.claude/settings.local.json` allows excluding CLAUDE.md files from other teams without altering git. The audit skill should verify whether this layered architecture is being respected or whether the root CLAUDE.md is absorbing content that belongs in subfolders or skills.

## Sources

**[How Claude remembers your project — Claude Code Docs](https://code.claude.com/docs/en/memory)** — _official-anthropic · accessed 2026-06-28_

Primary and normative reference for the Claude Code memory system. Documents the complete scope hierarchy, directory-based loading behavior, @import syntax with path resolution and maximum depth of 4 hops, CLAUDE.local.md for personal use, .claude/rules/ directory with path-scoped rules, auto memory with MEMORY.md as index (first 200 lines or 25KB), and the /memory command. Details survival through /compact: root CLAUDE.md survives, subfolder CLAUDE.md files do not (reloaded on demand). HTML comments are stripped before injection at no token cost.

- CLAUDE.md is a post-system-prompt user message — not enforcement; to guarantee action use PreToolUse hook
- claudeMdExcludes with glob patterns in settings.json, arrays merged between layers
- CLAUDE_CODE_ADDITIONAL_DIRECTORIES_CLAUDE_MD=1 to load memory from extra directories
- Auto memory is machine-local; worktrees of the same repo share a single memory folder

Feeds: Dimensions 1, 12, 8, 13

**Notable:** «Claude treats [CLAUDE.md] as context, not enforced configuration. To block an action regardless of what Claude decides, use a PreToolUse hook instead.»

---

**[Best practices for Claude Code — Claude Code Docs](https://code.claude.com/docs/en/best-practices)** — _official-anthropic · accessed 2026-06-28_

Official best practices guide. Contains the normative include vs. exclude table for CLAUDE.md and the central pruning criterion. Documents /init for initial generation and the use of IMPORTANT/YOU MUST sparingly for critical instructions. Positions the context window as the fundamental resource to manage.

- Include vs. exclude table as an audit checklist (what Claude infers from code doesn't need to be in CLAUDE.md)
- Pruning criterion: «Would removing this cause Claude to make mistakes? If not, cut it»
- Bloated CLAUDE.md causes Claude to ignore real instructions — degradation feedback loop
- Commit CLAUDE.md for team sharing; CLAUDE.local.md for personal overrides

Feeds: Dimensions 1, 12, 13, 14

**Notable:** Normative table with 7 inclusion categories and 7 exclusion categories — direct basis for an automatable audit checklist.

---

**[Set up Claude Code in a monorepo or large codebase — Claude Code Docs](https://code.claude.com/docs/en/large-codebases)** — _official-anthropic · accessed 2026-06-28_

Official guide for large codebases. Canonizes directory-based layering (root + per-package), claudeMdExcludes to exclude CLAUDE.md from other teams, Read deny rules to block reading of generated/vendored files, per-directory skills for on-demand loading, and plugins for centralized conventions. Includes a comparative table between per-directory CLAUDE.md vs. path-scoped rules in .claude/rules/ vs. skills.

- Layering: root CLAUDE.md (global, loaded at startup) + per-package CLAUDE.md (on-demand when Claude reads files there)
- Stop hook to propose CLAUDE.md updates at session end using the transcript
- Per-directory skills (.claude/skills/) for conditional loading by task relevance
- Project settings (.claude/settings.json) load ONLY from the initial directory — not inherited from parent folders

Feeds: Dimensions 1, 6, 8, 12

**Notable:** Recommends a Stop hook that reads the session transcript and proposes CLAUDE.md updates while the exposed gap is still fresh — an automated continuous evolution mechanism.

---

**[Effective context engineering for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)** — _engineering-anthropic · accessed 2026-06-28_

Engineering article positioning CLAUDE.md as a hybrid strategy: naively loaded at startup + grep/glob primitives for just-in-time retrieval of details. Defines context engineering as curating the smallest set of high-signal tokens that maximizes outcome. Documents three persistence techniques: compaction, structured note-taking, and sub-agent architectures with 1000-2000 token summaries.

- Hybrid: naive loading of CLAUDE.md + just-in-time retrieval via tools
- Sub-agents return summaries (1000-2000 tokens) instead of flooding the main context with files
- Principle: «the smallest possible set of high-signal tokens that maximize the probability of the desired outcome»
- Start with minimal prompts and add instructions based on observed failure modes

Feeds: Dimensions 1, 12, 7

**Notable:** Analogy with human cognition: we maintain organizational systems instead of memorizing entire corpora — direct principle for deciding what goes in CLAUDE.md vs. in referenced docs.

---

**[The Complete Guide to CLAUDE.md: Memory, Rules, Loading, and Cross-Tool Compression — Medium](https://medium.com/@bijit211987/the-complete-guide-to-claude-md-memory-rules-loading-and-cross-tool-compression-97cc12ed037b)** — _community · May 2026_

Technical guide that quantifies the instruction budget: ~100-150 useful slots after ~50 used by Claude Code's system prompt. Proposes 5 canonical sections and a 3-pass compression strategy. Compares CLAUDE.md with formats from other tools (AGENTS.md, copilot-instructions.md, .cursor/rules/, .windsurfrules).

- Quantified budget: ~150-200 total instructions, ~50 from system prompt, ~100-150 available
- 5 canonical sections: critical commands, architecture map, hard rules, workflow preferences, out-of-scope
- 3-pass compression: deduplication → convert to commands → separate always vs. on-demand
- Cross-tool strategy: canonical AGENTS.md with tool-specific imports

Feeds: Dimensions 1, 12, 13

**Notable:** Quantification of the budget (50 slots used by Claude Code system prompt) is the empirical basis for Anthropic's recommended 200-line limit.

---

**[Stop Bloating Your CLAUDE.md: Progressive Disclosure for AI Coding Tools — alexop.dev](https://alexop.dev/posts/stop-bloating-your-claude-md-progressive-disclosure-ai-coding-tools/)** — _community · accessed 2026-06-28_

Article about progressive disclosure as a central technique. Defines CLAUDE.md as an index of at most 50 lines with pointers to docs/. Documents the critical @import gotcha and the meta-instruction for Claude to self-direct toward relevant documentation.

- Progressive disclosure: CLAUDE.md as index (50 lines) + docs/ for details
- Meta-instruction: include instruction «identify which of the docs below are relevant and read them first»
- @import expands inline and still counts against the budget (critical gotcha — does not save tokens)
- agent_docs/ or docs/ for domain-specific gotchas and guidelines

Feeds: Dimensions 1, 12, 6

**Notable:** @import does not reduce context — files are expanded inline. Modular organization via imports only benefits human maintenance of the file, not the token budget.

---

**[The CLAUDE.md Configuration Hierarchy — AI Agent Factory (Panaversity)](https://agentfactory.panaversity.org/docs/General-Agents-Foundations/claude-code-teams-cicd/claude-md-configuration-hierarchy)** — _community · accessed 2026-06-28_

Team guide focused on diagnostics. Documents /memory as the primary hierarchy debugging tool. Contrasts CLAUDE.md (guidance) vs. settings.json (enforcement). Includes size guidelines by repository type.

- /memory command lists all files loaded in the session — real-time audit tool
- Size guidelines: 20-80 lines (lib), 80-200 lines (service), >200 migrate to .claude/rules/
- @~/.claude/my-project-instructions.md to import personal preferences from the shared CLAUDE.md
- Avoid: duplicate README, detailed architecture docs, execution plans, edge cases for rules/

Feeds: Dimensions 1, 12, 13

**Notable:** /memory command as a team audit tool: comparing output between members identifies configuration divergences (member without personal preferences, subfolder CLAUDE.md not loaded, etc.).

---

**[Writing a good CLAUDE.md — HumanLayer Blog](https://www.humanlayer.dev/blog/writing-a-good-claude-md)** — _community · accessed 2026-06-28_

Practical guide focused on auditing and maintenance. Proposes the WHAT/WHY/HOW framework and a 4-point audit checklist. HumanLayer maintains their own root CLAUDE.md in under 60 lines as a practical example.

- WHAT/WHY/HOW framework: stack+structure, component purpose, workflows+verification
- «Never send an LLM to do a linter's job» — style rules belong in the linter
- file:line references instead of code snippets (self-update when code changes)
- Audit checklist: (1) non-universal instructions, (2) linting rules, (3) redundancy with defaults, (4) outdated code snippets

Feeds: Dimensions 1, 12, 13, 14

**Notable:** 4-point audit criterion directly actionable as an automated checklist for the knowledge management skill.

---

**[Claude Code Auto Memory: How Your AI Learns Your Project — claudefa.st](https://claudefa.st/blog/guide/mechanics/auto-memory)** — _community · accessed 2026-06-28_

Technical documentation of the auto memory system. Clarifies division of responsibilities between CLAUDE.md (human instructions) and MEMORY.md (Claude's notebook). Documents structure in ~/.claude/projects/<git-root>/memory/ with index and topic files.

- MEMORY.md = index (200 lines/25KB loaded at startup) + topic files on-demand via file tools
- Auto memory is local-only and not shared via git — not for team policies
- CLAUDE_CODE_DISABLE_AUTO_MEMORY=1 for CI/automated pipelines
- Claude decides what is worth memorizing — does not save every session

Feeds: Dimensions 1, 10, 7

**Notable:** Worktrees of the same git repo share a single auto memory directory — relevant for repositories that use multiple active worktrees simultaneously.

---

**[What Is Context Rot in Claude Code? — MindStudio](https://www.mindstudio.ai/blog/what-is-context-rot-claude-code)** — _community · accessed 2026-06-28_

Article dedicated to context rot as the central anti-pattern. Defines and documents detectable signals of degradation from accumulation of instructions in CLAUDE.md.

- Context rot = outdated, contradictory, or redundant instructions that silently degrade adherence
- Signals: Claude ignores instruction (file too large), inconsistent output (contradictions), Claude asks something already in CLAUDE.md (ambiguous formulation)
- MCP overhead >10% of context indicates unnecessary servers connected
- Periodic auditing: verify whether removing the instruction would cause wrong behavior

Feeds: Dimensions 1, 12, 14

**Notable:** Testable audit signal: if Claude asks something already answered in CLAUDE.md, the instruction formulation is ambiguous; if Claude ignores an existing instruction, the file is too large or has contradictions.

---

**[Claude Code Memory Levels Explained: 6 Layers — MindStudio](https://www.mindstudio.ai/blog/claude-code-memory-levels-explained-6-layers-claude-md-cross-tool-shared-memory)** — _community · accessed 2026-06-28_

6-layer memory framework expanding beyond Claude Code's native mechanisms. Relevant for repositories with a large volume of architectural documentation that doesn't fit in the CLAUDE.md budget.

- 6 layers: CLAUDE.md files → session hooks → semantic search → verbatim recall → knowledge bases → cross-tool shared memory
- Semantic search (layer 3): ~10x token savings vs. full context dump
- Cost per layer: layers 1-2 negligible; layers 3-6 increase in overhead vs. precision
- Cross-tool memory (layer 6): SQLite/Supabase for distributed agent teams

Feeds: Dimensions 1, 7, 10, 12

**Notable:** Layer 3 (semantic search via vector databases) offers ~10x token savings versus injecting all architectural documentation into CLAUDE.md — relevant alternative for repositories with extensive architectural docs.

---

**[Using CLAUDE.MD files — Claude Blog (Anthropic)](https://claude.com/blog/using-claude-md-files)** — _official-anthropic · accessed 2026-06-28_

Official Anthropic blog post about customization via CLAUDE.md. Emphasizes the critical warning not to rely on local-only auto memory for shared project policies.

- «Do not rely on local-only memory for shared project policy» — version in git
- /init examines package files, README, config files, and code structure to generate a starter
- Complementarity: CLAUDE.md (always-loaded) + .claude/rules/ (conditional) + .claude/skills/ (on-demand)
- CLAUDE.md as evolutionary documentation — maintain and update as the project changes

Feeds: Dimensions 1, 10, 12, 13

**Notable:** Normative warning: auto memory should not be the only repository of important behaviors — team policies require files versioned in git.

## How it feeds the method evolution

- **Dimension 1 (CLAUDE.md as map) — new detectable smell**: CLAUDE.md with more than 200 lines is a candidate for context rot; with more than 120 lines should have an explicit justification. The skill can count lines and flag files above the threshold, categorizing the excess content by type (candidates for rules/, skills/, hooks, deletion).

- **Dimension 12 («one canonical home» boundary) — sharper criterion**: The CLAUDE.md (guidance) vs. hooks (enforcement) vs. settings.json (technical) distinction is a boundary formally documented by Anthropic. The skill can audit imperative instructions in CLAUDE.md that describe mandatory behaviors («always run X before committing») and flag them as candidates for PreToolUse/Stop hook — the correct canonical home.

- **Dimension 1 — context rot detection command**: /memory command within a session lists all files loaded — the skill can instrument a check that a new team member's /memory output is aligned with the expected (no other team's CLAUDE.md loaded, no missing subfolder CLAUDE.md). This becomes a verifiable onboarding step.

- **Dimension 6 (skills) — CLAUDE.md vs. skills boundary**: Instructions of the type «when doing X, follow procedure Y» are candidates for skills (`.claude/skills/`), not CLAUDE.md. Skills only enter context when relevant; CLAUDE.md enters always. The audit can detect long procedural instructions in CLAUDE.md and suggest conversion to a skill.

- **Dimension 10 (auto memory) — worktrees gotcha**: Auto memory is shared between worktrees of the same git repo (key = git root), but not between repos. The skill should check if the project uses worktrees and warn that MEMORY.md is shared — conventions written by Claude in one worktree affect all others.

- **Dimension 1 — new workflow step (evolutionary Stop hook)**: Official documentation recommends a Stop hook that reads the session transcript and proposes CLAUDE.md updates. The knowledge management skill can formalize this pattern as a continuous audit hook — each closed session generates a delta proposal for CLAUDE.md, making the knowledge surface self-evolving rather than manually-maintained.

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **10**.

The set of 12 sources is of above-average quality: 4 are official Anthropic documentation (all confirmed and accessible), and most community sources have valid URLs and content consistent with their summaries. Two problems were found: the HumanLayer article was characterized with details not in the actual text (60-line limit vs. 300, 4-point checklist not prominent); and claudefa.st inverts worktree behavior relative to official documentation. The Anthropic Engineering and Medium/Bijit Ghosh sources were confirmed with 2025-2026 dates, with no signs of staleness. The set covers the proposed angle (CLAUDE.md and Claude Code memory) well, but the worktree data at claudefa.st is a material error that may propagate misinformation about memory behavior in multi-worktree workflows.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://www.humanlayer.dev/blog/writing-a-good-claude-md | `mischaracterized` | The summary claims the framework «WHAT/WHY/HOW», a target of «less than 60 lines», and «a 4-point detectable audit checklist». The actual content uses «WHY, WHAT, HOW» (different order), recommends less than 300 lines (not 60), and does not present a 4-point audit checklist as a main resource — the focus is on good writing practices, not auditing. The characterization of «4-point audit criteria» ... |
| https://claudefa.st/blog/guide/mechanics/auto-memory | `mischaracterized` | The summary states that «worktrees of the same git repository share a single auto memory directory». The actual page content says the opposite: «Git worktrees get separate memory directories. This is intentional.» This directly contradicts the summary and also contradicts official documentation (source 1), which says worktrees share the same directory. The claudefa.st page is itself... |
