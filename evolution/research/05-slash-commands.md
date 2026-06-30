# Custom Slash Commands in Claude Code

> Covers the technical mechanism of commands and skills invocable via `/name`, their frontmatter fields, argument substitution, namespacing, and the decision boundary commands vs. skills vs. sub-agents vs. hooks — directly feeds Dimension 9 (commands) and boundary 12 (each piece of information with one canonical home).

## Synthesis

Custom slash commands in Claude Code are Markdown files that create shortcuts invocable with `/name`. The legacy format uses `.claude/commands/<name>.md`; the current recommended format uses `.claude/skills/<name>/SKILL.md`. Both produce the same `/name` command and the CLI continues to support both — the difference is that skills add a support directory (scripts/, references/, assets/), richer frontmatter, and the capability of automatic invocation by model judgment. For a knowledge surface audit skill, the skills format is superior: it can be invoked directly by the user (`/audit-surface`) or by the model when it detects a relevant context, and can reference auxiliary files without inflating the main SKILL.md.

YAML frontmatter (delimited by `---`) is the central configuration mechanism. The most important fields for an audit skill are: `description` (the automatic activation trigger — should include literal phrases the user would type, e.g., «Use when asked to audit CLAUDE.md, verify the knowledge surface or diagnose conflicts between mechanisms»), `allowed-tools` (restricts tools without prompt, e.g., `Read Glob Grep`), `disable-model-invocation: true` (makes the skill exclusively manual — ideal for workflows with side effects or critical operations like deployment), `argument-hint` (autocomplete hint, e.g., `[--fix] [dimension]`), and `model` (can select a more capable model for complex audit tasks). Extra fields supported by Claude Code beyond the Agent Skills standard include `context: fork` (executes the skill in an isolated sub-agent, returning only the final result), `user-invocable: false` (hides from the `/` menu but allows model invocation), `paths` (restricts automatic activation to file glob patterns) and `effort`.

Arguments are passed after the command name and substituted in the body. `$ARGUMENTS` captures everything as a free string (ideal for Unix-style flags that the LLM parses). `$0`, `$1`, `$2` are zero-indexed positionals for typed and ordered arguments. Named arguments (`arguments: [dimension, mode]` in frontmatter) create self-explaining slots (`$dimension`, `$mode`). Dynamic context injection via `` !`command` `` executes shell before the model reads the skill, embedding the output inline — essential for an audit skill that needs the actual repo state (e.g., `` !`find .claude -name "*.md" | head -40` ``). The `@file` syntax embeds file content directly. All these substitutions occur at load time, not during execution. Critical note: `$ARGUMENTS` is case-sensitive; `$args` or `$arguments` fail silently.

Namespacing uses two mechanisms: subfolders and plugins. Subfolders in `.claude/commands/frontend/component.md` appear in the description as context, but the command is invoked simply as `/component` (duplicate names in different subfolders collide). Skills in plugin subfolders use colon notation: a skill inside a monorepo subfolder creates `/apps/web:deploy` to differentiate from the root skill `/deploy`. The priority hierarchy is: enterprise > personal (`~/.claude/`) > project (`.claude/`) > plugin.

The commands vs. skills vs. sub-agents vs. hooks boundary is the most critical architectural decision for the `quenching-management` skill. Anthropic's published golden rule: CLAUDE.md for always-relevant facts; skills for on-demand procedures; hooks for deterministic guarantees; sub-agents for isolated work that shouldn't pollute the main context. For knowledge surface auditing, the ideal pattern is a skill with `context: fork` (isolation) that scans dimensions, detects smells (procedures in CLAUDE.md, duplicated instructions across mechanisms, skills without `description`, obsolete commands) and returns a structured report without expanding the main conversation context. The skill description is the retrieval vector: matching is done by pure linguistic model judgment (no algorithm), so vague descriptions leave the skill dormant regardless of body quality. The Agent Skills open standard (agentskills.io), created by Anthropic and adopted by 30+ tools (Cursor, GitHub Copilot, Gemini CLI, JetBrains Junie, Databricks Genie Code, etc.), ensures cross-tool portability.

## Sources

**[Slash Commands in the SDK - Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/slash-commands)** — _official-anthropic · accessed 2026-06-28_

Official SDK documentation describing built-in and custom slash commands: how to discover available commands via system/init message, send commands via SDK, create custom commands in `.claude/commands/` with frontmatter (allowed-tools, description, model, argument-hint), use `$ARGUMENTS` and `$0`/`$1` positionals, bash injection via `` !` ``, file references via `@`, and subfolder namespacing. Explicitly documents that `.claude/commands/` is the legacy format and `.claude/skills/` is the recommended one.

- **Key techniques**: Frontmatter: allowed-tools, description, model, argument-hint; `$ARGUMENTS` for free string capture; `$0`/`$1` for positionals; dynamic injection via `` !`command` ``; file reference via `@path`; subfolder namespacing; project vs. personal scope; discovery via `message.slash_commands`.
- **Notable**: If a custom command has the same name as a bundled skill (e.g., code-review), the custom one overrides and the name appears only once in the `slash_commands` list.
- Feeds: Dimensions 9, 6, 7, 12

---

**[Extend Claude with skills - Claude Code Docs](https://code.claude.com/docs/en/skills)** — _official-anthropic · accessed 2026-06-28_

Complete official documentation on skills: unification of commands and skills (both create `/name`), SKILL.md format with rich frontmatter (`disable-model-invocation`, `user-invocable`, `context: fork`, `agent`, `paths`, `effort`, `hooks`), automatic invocation by model judgment vs. manual invocation, execution in sub-agent via `context: fork`, dynamic context injection, and the Agent Skills open standard.

- **Key techniques**: `disable-model-invocation: true` for manual skills with side effects; `user-invocable: false` for model-only skills; `context: fork` for isolated sub-agent execution; `paths: glob` for automatic activation restricted to specific files; `effort: low|medium|high|xhigh|max`; progressive disclosure (metadata ~100 tokens; body <5000 tokens recommended); `CLAUDE_SKILL_DIR` variable for portable paths.
- **Notable**: Skills follow the Agent Skills open standard (agentskills.io) — the same skill works in Claude Code, Cursor, GitHub Copilot, Gemini CLI, and others without modification.
- Feeds: Dimensions 6, 7, 9, 12, 14

---

**[Agent Skills Specification - agentskills.io](https://agentskills.io/specification)** — _spec-standard · accessed 2026-06-28_

Complete specification of the Agent Skills open standard format: directory structure (skill-name/SKILL.md + scripts/ + references/ + assets/), mandatory frontmatter fields (`name`: max 64 chars, lowercase+hyphens; `description`: max 1024 chars), optional fields (`license`, `compatibility`, `metadata`, `allowed-tools` experimental), naming conventions, size recommendations (SKILL.md <500 lines; body <5000 tokens), and `skills-ref` validation tool.

- **Key techniques**: `name` must match the parent directory name; `description` must include «when to use» — it is the activation trigger; `metadata` for implementor extra fields; `compatibility` for environment requirements; validation via `skills-ref validate ./my-skill`.
- **Notable**: The standard was created by Anthropic and adopted by 30+ agent tools (Cursor, GitHub Copilot, Gemini CLI, OpenHands, JetBrains Junie, Databricks Genie Code, etc.).
- Feeds: Dimensions 6, 9, 12

---

**[Steering Claude Code: skills, hooks, rules, subagents and more](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)** — _engineering-anthropic · accessed 2026-06-28_

Official Anthropic post describing the seven Claude Code instruction mechanisms and the decision between them: CLAUDE.md (always-resident facts), rules (path-scoped constraints), skills (on-demand procedures), sub-agents (isolated work with separate window), hooks (deterministic guarantees), output styles, system prompt appending.

- **Key techniques**: CLAUDE.md <200 lines for always-relevant facts; `rules/` with `paths:` for path-scoped constraints; skills for procedures; `agents/` for isolated work; hooks for deterministic guarantees; anti-pattern: procedures in CLAUDE.md (belong in skills).
- **Notable**: «Skills: model judgment — behavior is likely but not guaranteed. Hooks: harness enforcement — behavior is certain.» This distinction is the central criterion of the boundary.
- Feeds: Dimensions 1, 2, 6, 7, 8, 9, 12, 14

---

**[disable-model-invocation - DevelopersIO (Classmethod)](https://dev.classmethod.jp/en/articles/disable-model-invocation-claude-code/)** — _community · accessed 2026-06-28_

Article focused on the `disable-model-invocation` frontmatter field: what it does (prevents the model from loading the skill automatically), when to use it (deploy, release, commit — workflows with side effects where the user wants to control timing), how to verify via `/context` which skills are loaded vs. disabled.

- **Key techniques**: `disable-model-invocation: true` — skill only invocable manually via `/name`; verify active skills via `/context`; pattern for critical operations: deploy, commit, send-slack-message, release; benefit: reduces unnecessary context consumption.
- **Notable**: The skill still appears in the manual suggestion list (when typing `/`), but is not loaded automatically during conversations — timing control without sacrificing discoverability.
- Feeds: Dimensions 6, 9, 12, 14

---

**[Claude Code Skills: Complete Technical Reference - hidekazu-konishi.com](https://hidekazu-konishi.com/entry/claude_code_skills_complete_guide.html)** — _community · accessed 2026-06-28_

Complete technical reference with all Claude Code frontmatter fields (including non-standard-spec fields): `name`, `description`, `when_to_use`, `argument-hint`, `arguments`, `disable-model-invocation`, `user-invocable`, `allowed-tools`, `disallowed-tools`, `model`, `effort`, `context`, `agent`, `hooks`, `paths`, `shell`. Documents the three invocation modes (automatic, direct, sub-agent preload), the decision matrix between skills vs. CLAUDE.md vs. hooks vs. sub-agents vs. MCP, and the `context: fork` pattern.

- **Key techniques**: Complete frontmatter table with 15+ fields; `arguments: [name1 name2]` for named arguments; `context: fork + agent: Explore` for isolated sub-agent execution; `disallowed-tools` to remove tools from the pool; `paths: glob` for restricted automatic activation; scope hierarchy: enterprise > personal > project > plugin.
- **Notable**: «The description is the trigger mechanism — a vague description leaves the skill dormant regardless of body quality.» This is the most common cause of «my skill doesn't work».
- Feeds: Dimensions 6, 7, 9, 12, 14

---

**[Claude Code Skills: Technical Architecture (first-principles deep dive)](https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/)** — _community · 2025-10-26_

Technical analysis of the internal skills architecture: the dual-channel injection mechanism (visible metadata message + hidden instruction `isMeta: true`), how the model does skill matching by pure linguistic forward-pass (no embeddings, classifiers or algorithmic pattern matching), how `allowed-tools` and `model` are dynamically modified during skill execution and reverted after, and the organization of support files.

- **Key techniques**: Skill matching: pure linguistic model judgment — the description is the retrieval vector; dual injection: metadata (visible) + instruction (`isMeta: true`, invisible to user); tool permissions dynamically modified during skill and reverted after; `scripts/` for executable code; `references/` for docs loaded into context; `assets/` for templates referenced by path; do not use hardcoded absolute paths — use `${CLAUDE_SKILL_DIR}`.
- **Notable**: There is no algorithmic skill selection — all matching is done by the transformer during the forward pass. This means description quality directly determines whether the skill will be correctly activated.
- Feeds: Dimensions 6, 7, 9, 12

---

**[Custom Slash Commands - Build This Now](https://www.buildthisnow.com/blog/guide/mechanics/claude-code-custom-slash-commands)** — _community · accessed 2026-06-28_

Practical guide with the three argument mechanisms (`$ARGUMENTS`, positionals `$0`/`$1`, named via `arguments:`), the project vs. personal scope distinction, subfolder namespacing, bash injection with `` !` `` and `` ```! `` block for multi-line, and the progression command → skill → sub-agent.

- **Key techniques**: `$ARGUMENTS` is case-sensitive — `$args` fails silently; quoted args preserve spaces; `` ```! `` block for multi-line bash injection; subfolders: command name doesn't change, avoid basename duplicates across subfolders; command must be restarted after editing .md (read at session startup).
- **Notable**: `$ARGUMENTS` is case-sensitive: `$args` or `$arguments` fail silently without error — easy to violate, hard to diagnose.
- Feeds: Dimensions 9, 12

---

**[Slash Command Flags: 4 Patterns - TECHSY](https://techsy.io/en/blog/how-to-add-flags-to-claude-code-slash-commands)** — _community · accessed 2026-06-28_

Catalog of 4 flag patterns for slash commands: (1) boolean flag `--dry-run` via `$ARGUMENTS`; (2) value flag `--filter <pattern>` via `$ARGUMENTS`; (3) required positional + optional flag (`$1` + `$ARGUMENTS`); (4) strict typed positionals (`$0`/`$1` or named `arguments:`). Includes decision matrix and critical implementation rules.

- **Key techniques**: Hybrid pattern (3) — `$1` required + `$ARGUMENTS` for optional flags — is the most balanced design; `allowed-tools:` space-separated (not comma); restart Claude Code after editing .md; LLM is genuinely good at extracting flags from free strings.
- **Notable**: The hybrid pattern (3) is described as «what we use most in our own command library» — the most balanced design for commands that have one required argument plus optional flags.
- Feeds: Dimensions 9, 12

---

**[Anatomy of the .claude Folder - codewithmukesh.com](https://codewithmukesh.com/blog/anatomy-of-the-claude-folder/)** — _community · accessed 2026-06-28_

Complete map of the `.claude/` folder: CLAUDE.md (high priority, survives compaction), `rules/` (modular path-scoped instructions), `skills/` (reusable workflows), `commands/` (legacy format), `agents/` (sub-agents with separate window), `docs/` (on-demand reference), `settings.json` (allow/deny/env), `settings.local.json` (gitignored), `memory/` (cross-session auto-memory). Loading priority: managed > CLI args > settings.local > settings > user settings.

- **Key techniques**: CLAUDE.md <200 lines; modular `rules/` with path-scoped; `agents/`: sub-agents with separate window — cannot spawn other agents; `settings.json`: deny-first; `memory/`: MEMORY.md index (first 200 lines or 25KB) loaded every session; `worktrees/` for branch isolation.
- **Notable**: Agents cannot spawn other agents (no sub-agent recursion) — which makes the skill with `context: fork` pattern the correct alternative for isolated sub-tasks that need their own context.
- Feeds: Dimensions 1, 6, 7, 8, 9, 10, 12

---

**[I Asked Claude Code to Audit My Own Setup - cjonsystems.substack.com](https://cjonsystems.substack.com/p/i-asked-claude-code-to-audit-my-own)** — _community · accessed 2026-06-28_

Real knowledge surface audit use case: the author built `/audit-claude-md` to detect conflicts between CLAUDE.md, `.claude/rules/`, skills, commands, and global memory, remove obsolete instructions (that newer models already do by default), and migrate procedures from CLAUDE.md to skills. Combines with `/insights` (Anthropic feature) for behavioral analysis of sessions.

- **Key techniques**: `/audit-claude-md`: detects conflicts, obsolete instructions, procedures in the wrong place; `/insights`: analyzes real behavioral patterns from sessions; quarterly loop: insights → audit → removal of obsolete instructions; smell: procedure in CLAUDE.md that should be a skill.
- **Notable**: Distinguishes two types of auditing: `/audit-claude-md` audits configuration (static instructions); `/insights` audits real behavior (executed sessions). Together they reveal gaps between intention and execution.
- Feeds: Dimensions 1, 2, 4, 6, 9, 12

---

**[Essential Claude Code Skills and Commands - batsov.com](https://batsov.com/articles/2026/03/11/essential-claude-code-skills-and-commands/)** — _community · 2026-03-11_

Practical guide of the most valuable production skills: `/simplify` (3 parallel agents via `context: fork`), `/review` (correctness and bugs), `/batch` (migrations in parallel worktrees). Frontmatter best practices: `disable-model-invocation` for operations with side effects, `user-invocable: false` for background conventions.

- **Key techniques**: `/simplify` with `context: fork` — 3 parallel agents in isolated sub-contexts; `/batch` for migrations in parallel worktrees (inadequate for architectural redesigns requiring coherence); `user-invocable: false` for background conventions (model invokes, user doesn't see in menu); verify loaded context via `/context`.
- **Notable**: `/batch` decomposes work into 5-30 independent units in separate worktrees — ideal for repetitive migrations, but inadequate for architectural redesigns that require coherence between parts.
- Feeds: Dimensions 6, 7, 9, 12

## How it feeds the method evolution

- **Dimension 9 (commands) — sharpen the format criterion**: The current smell is using `.claude/commands/*.md` (legacy). The sharper «good» criterion is: every new command is born as `.claude/skills/<name>/SKILL.md`; existing commands/ are only migrated when they need file support, automatic invocation, or rich frontmatter. The audit skill should check whether there are `.md` files in `commands/` that should have become skills (criterion: has more than 50 lines, references external files, or was copied to several projects).

- **Boundary 12 (single canonical home for each piece of information) — new detection smell**: A procedure in CLAUDE.md is a smell of a violated boundary — it belongs in a skill. The audit skill should run `` !`grep -n "step\|first\|1\.\|workflow" .claude/CLAUDE.md | head -20` `` to detect disguised procedures, and flag each occurrence with the correct target dimension (skill, hook, or sub-agent).

- **Dimension 6 (skills) — sharpen description field as trigger**: The description is the model's retrieval vector (pure linguistic matching, no algorithm). The «good» criterion is: description should be written in third person, include literal phrases the user would type, and have the main use case in the first 100 characters. The audit skill should check each SKILL.md and flag descriptions with less than 50 chars or without the «Use when» clause as a weak activation smell.

- **Dimension 9 + 12 — new detection step**: The audit skill can use `` !`find .claude -name "*.md" -o -name "SKILL.md" | sort` `` to map the entire command/skill surface, compare with dimensions 1-14, and identify dimensions with no representation (e.g., no skill for dimension 5 ADRs, no skill for dimension 4 backlog, etc.) — revealing knowledge surface coverage gaps.

- **Boundary skills vs. hooks (Dimensions 8 and 9) — operational criterion**: The sharp good criterion is: if the consequence of the model not executing the step is an inconvenience → skill; if it's a security, correctness, or compliance failure → hook. The audit skill should list all commands marked with `disable-model-invocation: true` and verify whether they should be hooks in settings.json instead of skills (operations that MUST always run, not just when the user invokes).

- **Dimension 9 — new quarterly audit step**: Incorporate the `/insights` → `/audit-claude-md` loop as a recurring backlog item (Dimension 4): (1) run `/insights` on recent sessions to identify where model and operator clash; (2) check whether CLAUDE.md instructions became obsolete with newer models; (3) remove skills not invoked in 90 days; (4) verify whether skill descriptions still match real usage triggers. This loop closes the cycle between intention (configuration) and behavior (execution).

---

## ⚠️ Verification notes (anti-hallucination)

> Automatic adversarial verification of sources in this angle (workflow `deep-research`, 2026-06-28). Confirmed sources: **9**.

The set of 12 sources is of above-average quality for a corpus of research about Claude Code slash commands/skills: all URLs exist and are accessible, publishers are correct, and no source appears fabricated. The four problems found are characterization issues — wrong numbers (~100 tokens vs. 1536 chars), a citation presented as literal but not in the original text, and two cases of real facts attributed to sources that don't document them. The official sources (code.claude.com, agentskills.io, claude.com/blog) are all accessible and updated to 2026-06-28, with no signs of stale content.

Flagged sources (review before citing):

| Source | Verdict | Issue |
| --- | --- | --- |
| https://code.claude.com/docs/en/skills | `mischaracterized` | The summary states that metadata loads «~100 tokens» in the progressive disclosure mechanism. The actual documentation specifies truncation at 1536 characters (description + when_to_use combined), not ~100 tokens. The value is not even a reasonable approximation of the actual limit. Also, the actual doc explicitly mentions CLAUDE_SKILL_DIR as an environment variable for portable paths — dat... |
| https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more | `mischaracterized` | The summary attributes to the post the exact citation: «Skills: model judgment — behavior is likely but not guaranteed. Hooks: harness enforcement — behavior is certain.» This citation does not appear in the article. The actual text uses distinct functional language («hooks are user-defined commands [...] that provide more deterministic control», «code that the harness runs rather than instructions to Claude») without this f... |
| https://leehanchung.github.io/blogs/2025/10/26/claude-skills-deep-dive/ | `mischaracterized` | The summary lists «Do not use hardcoded absolute paths — use ${CLAUDE_SKILL_DIR} or relative paths» as a key_technique documented by the article. Confirmed via fetch: the article does not mention CLAUDE_SKILL_DIR at any point — only references paths like ~/.config/claude/skills/ and .claude/skills/. The CLAUDE_SKILL_DIR data is real (the variable exists in official docs), but the attribution of... |
| https://batsov.com/articles/2026/03/11/essential-claude-code-skills-and-commands/ | `mischaracterized` | The summary states the article recommends «verify via /context and /compact before switching work phase». The article only recommends /compact proactively before a new phase; /context is only described functionally (shows colored grid of context usage) without a strategic timing recommendation. Including /context in the same recommendation is an unsupported addition. |
