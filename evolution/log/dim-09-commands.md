# Dimension 9 — commands

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **legacy commands × skills and the migration criterion**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

- **R27 · Commands as COMPOSABLE blocks invoked by the model (`SlashCommand`/Skill
  tool), not just user shortcuts** — dim 9 stops treating a command as "a shortcut
  the user types" and gains the **composability-in-workflow** axis: Claude can
  **execute** a custom command during the conversation via the programmatic invocation
  tool (`SlashCommand` in the SDK / today the *Skill tool*), so a command becomes a
  **building block** that a skill/sub-agent/method step can **chain** (e.g.,
  `/<prefix>-reaudit <dimension>` as a step in a larger flow, not just the user at
  the `/` menu). Four anchored facts: (a) **the composability trigger is the
  `description`** (*"Claude uses this to decide when to apply the skill"*) — same
  `description`/dim 6 as auto-triggering, weak description ⇒ inert building block;
  (b) **exposure control** — `disable-model-invocation: true` **removes** the command
  from the tool (*"blocks programmatic invocation"* / *"Description not in context"*),
  so a gated read-only step = **gated-composable** smell and a side-effect WITHOUT the
  flag = **auto-invocable-side-effect** smell (mirrors R18); (c) **character budget**
  — the list of descriptions available to the tool enters a budget = **~1% of the
  window** (adjustable by `skillListingBudgetFraction`/`SLASH_COMMAND_TOOL_CHAR_BUDGET`;
  each entry capped at 1,536 chars; `/doctor` reports overflow; `name-only` frees
  space) ⇒ **inflated-list/budget-overflow** smell, links to dim 1; (d) **R6
  boundary applied to the chainable step** — composable command (model invokes as
  block) × skill (operator steers in thread) × sub-agent (isolated context). The R18
  re-audit payload is re-labelled as the **example of a composable command** (read-
  only, without the flag ⇒ chainable by the model). 3 new smells in dim 9; 15
  dimensions maintained. Distinct from R8 (legacy×skill/migration) and R18 (concrete
  payload): R27 is **composability via `SlashCommand`** in the workflow. (round 27)

- **R18 · `assets/commands/` is born — first command payload in the package (on-
  demand re-audit)** — the package stops only **detecting the absence** of commands
  and starts **carrying** the first one: `assets/commands/quenching-reaudit/SKILL.md`,
  materialising **trigger (3) of Step 8** (R17). It is installed as a **skill**
  (`.claude/skills/<prefix>-reauditar/`), not a legacy command — the R8 doctrine
  ("new command is born a skill; legacy only for manual side-effect shortcut") applied
  **by construction**: the re-audit **reads and proposes** (no side effect), so it
  **keeps** auto-triggering by description (the form the user "misses"); uses
  `argument-hint` for the scope (dimension/path/empty) and `context: fork` +
  `agent: quenching-auditor` to scan in **clean context** (dim 7: fork condenses, does
  not dump). `disable-model-invocation` would be reserved for the hypothesis that
  the re-exam gains a side effect (open PR/commit). Installation map (`installation.md`),
  manifest (`assets/README.md`), and the **Payload** of dim 9 in the template updated
  to reflect that the package now carries this payload. No detection rule changed
  (harness does not run). (round 18)

- **R8 · Legacy command → skill (recommended format + migration criterion)** —
  dimension 9 (commands) stops being "`.claude/commands/*.md` with description +
  live corresponding skill" and gains the **legacy×recommended anchor fact**:
  `.claude/commands/<name>.md` is the **legacy** format, `.claude/skills/<name>/SKILL.md`
  the **recommended** — both produce the **same** `/name` and the CLI supports both,
  but only the skill adds **model-judgment auto-triggering** (the description/dim 6
  becomes a trigger) and a support directory (`references/`/`scripts/`). Hence the
  healthy state "every new command is born a skill; remains a command only the
  **manual side-effect shortcut**" + the **verifiable migration criterion**: (a) would
  benefit from auto-triggering · (b) >50 lines / references files · (c) multi-repo.
  New smells: **migratable legacy command** (passes the criterion), **basename
  collision** between subfolders (the subfolder enters the description but **not** the
  name — ambiguous `/name`) and **silent shadowing** of a bundled skill
  (`code-review`/`verify`). Cross-cutting item **9b** in `detection-and-smells.md`
  (greps that only list candidates: command >50 lines · with `@file`/`!cmd` ·
  duplicate basename · shadowing) + the command×skill×hook choice as a read. The
  home choice stays in the core (dim 12 applied to mechanisms, mirrors 7b/8b);
  authoring exits `quenching-skills`. (round 8)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 27 — 2026-06-29 · boundary: commands as COMPOSABLE blocks invoked by the model via `SlashCommand`/Skill tool (composability in the workflow)

- **Change:** refined **dimension 9 (commands)** in `dimensions-template.md` on the
  **composability** axis. The **Purpose** stops being just "shortcut/entry for flows"
  and declares that the command is invocable **by the user** (`/name`) **and by
  Claude itself** (the programmatic invocation tool — `SlashCommand` in the SDK /
  today the *Skill tool*), making it a **composable block** that a skill/sub-agent/
  method step **chains**. Four new blocks enter **"What good looks like"**: (1)
  **Composability** — Claude executes a custom command during the conversation via the
  tool (*"A few built-in commands are also available through the Skill tool"*), so a
  flow step becomes `/<prefix>-<step> <scope>` (e.g., the Step 8 re-audit as
  `/<prefix>-reaudit <dimension>`); (2) **the composability trigger is the
  `description`** (*"Claude uses this to decide when to apply the skill"*) — links to
  dim 6; (3) **exposure control** — `disable-model-invocation: true` **removes** the
  command from the tool (*"blocks programmatic invocation"*, *"Description not in
  context"*, *"removes the skill from Claude's context entirely"*), mirroring the R18
  decision (read-only ⇒ without the flag; side-effect ⇒ with the flag); (4)
  **character budget** — budget = ~1% of the window (`skillListingBudgetFraction`/
  `SLASH_COMMAND_TOOL_CHAR_BUDGET`; each entry capped at 1,536 chars; `/doctor`;
  `name-only`), links to dim 1; and the **R6 boundary applied** to the chainable step
  (composable command × skill × sub-agent). **Detection** (9b) gains "read-only
  composables improperly gated" + "list weight in the budget". **Smells** gain three:
  **gated-composable** (read-only with `disable-model-invocation` ⇒ disappears from
  the tool), **auto-invocable-side-effect** (deploy/commit/send without the flag —
  *"You don't want Claude deciding to deploy"*) and **inflated-list/budget-overflow**
  (long descriptions overflow the ~1% and `/doctor` reports truncation/dropping). The
  **Payload** re-labels the R18 command-skill as the **composable command example**
  (read-only + without the flag ⇒ chainable by the model). 15 dimensions maintained;
  no new payload; **no measured detection rule** (no Bash — 9b greps stay PENDING in
  the review queue).
- **Why:** it was the central axis of "command use in workflow" missing from dim 9
  (the user feels the method **uses** commands, not just detects them). R8 gave the
  legacy×skill fact + migration criterion; R18 carried the **concrete** re-audit
  payload; but both treat the command as a **shortcut** (the user types `/name`). The
  official docs expose a distinct and more powerful axis: the command is executable
  **by the model** as a **building block** of a larger flow — this is what makes the
  re-audit step (R18) **chainable** within a workflow instead of depending on the user
  remembering to invoke it. Anchoring the tool, the role of the `description`, the
  exposure control (`disable-model-invocation`), and the budget in one place closes
  composability.
- **Sources:** [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/slash-commands)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim**: programmatic
  invocation tool — *"A few built-in commands are also available through the Skill
  tool, including `/init`, `/review`, and `/security-review`"* and *"the ability for
  Claude to load them automatically when relevant"*; role of the description —
  *"`description` … What the skill does and when to use it. **Claude uses this to
  decide when to apply the skill.** … the combined `description` and `when_to_use`
  text is **truncated at 1,536 characters** in the skill listing to reduce context
  usage"*; exposure control — *"`disable-model-invocation: true`: Only you can invoke
  the skill"*, in the table *"Description not in context"*, and in the restriction
  section *"**Hide individual skills** by adding `disable-model-invocation: true` …
  This **removes the skill from Claude's context entirely**"* + *"Use
  `disable-model-invocation: true` to **block programmatic invocation**"*; side
  effect — *"You don't want Claude deciding to deploy because your code looks ready"*;
  **budget** — *"The budget scales at **1% of the model's context window**. When it
  overflows, **descriptions for the skills you invoke least are dropped first** … Run
  `/doctor` to see how many skill descriptions are being shortened or dropped"* and
  *"To raise the budget, set the `skillListingBudgetFraction` setting (e.g. `0.02` =
  2%) or the `SLASH_COMMAND_TOOL_CHAR_BUDGET` environment variable … set low-priority
  entries to `"name-only"` in `skillOverrides`"*. The legacy tool name (`SlashCommand`)
  and *"autonomous invocation by Claude"* appear in [Slash Commands in the SDK —
  Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/slash-commands)
  (accessed 2026-06-29, ✅ by WebFetch). Catalogue to update: `research/05-slash-commands.md`
  (covers the legacy×recommended format and `disable-model-invocation` as manual-only,
  but **not** the programmatic invocation tool nor the budget — noted in the review
  queue).
- **Rejected/superseded:** discarded **creating a new dimension** "programmatic
  invocation" — it is a refinement of existing dim 9 (15 dimensions maintained,
  Simplicity First). Discarded **creating a new payload** (a dedicated "composable"
  command-skill) — the R18 re-audit payload **already is** the composable example
  (read-only, without `disable-model-invocation`); creating another would be toolset
  bloat (dim 6/R10). Discarded **citing the name `SlashCommand` as the current term**
  — the current skills docs use *Skill tool* (the command→skill merge renamed it); the
  template cites both (`SlashCommand`/Skill tool) to avoid becoming stale or inaccurate.
  Discarded **measuring the 9b greps** (gated-composable / weight in the budget) in
  this round — no Bash in context; they stay PENDING in the review queue (like
  R22/R23/R25/R26), preferring doctrine + «good» over an unvalidated grep. Discarded
  **moving the "chainable flow step" boundary to the core/dim 12** — the mechanism
  choice already lives in the core (dim 12 applied to mechanisms, 7b/8b/9); here it
  is just the **instance** "composable step", which belongs to dim 9.
- **Next candidate:** "Outgrowth detection — skill the base model has already
  superseded" (dim 6, from the backlog) or "Event-based hook applied to `.claude/`
  (the config surface), not just `docs/`" (dim 8, from the backlog) — both in the
  axis of keeping the surface lean/alive. Or, for dim 9, measure the 9b greps against
  fixtures (review queue).

### Round 18 — 2026-06-29 · boundary: `assets/commands/` is born — first command payload in the package (on-demand re-audit)

- **Change:** created the **`assets/commands/`** folder (which did not exist) and its
  first payload, **`assets/commands/quenching-reaudit/SKILL.md`** + `assets/commands/README.md`.
  Materialises **trigger (3) of Step 8** (R17, core): the `/<re-audit>` that reruns
  Steps 1-7 on demand. Until now the package **detected** the absence of commands
  (dim 9) and **anticipated** the slot (Step 8), but **carried no command payload**
  — this round closes exactly that gap ("the method does not actually use commands").
  The payload takes the form of a **skill** (installed in `.claude/skills/<prefix>-reauditar/`),
  with description-trigger (dim 6) + `when_to_use` + `argument-hint` for the scope
  (`[dimension | path | empty]`) + `context: fork` + `agent: quenching-auditor` +
  `allowed-tools: Read, Grep, Glob, Bash` (read-only). The body reruns Step 0/1
  (derive paths), detection by dimension (or only the scope of `$ARGUMENTS`), the
  4-state score with `file:line` (hunting **Drifted**, what has aged), and returns
  only the condensed score (dim 7 return contract), without deciding
  boundaries/memory. Updated: `references/installation.md` (new gap→payload line:
  "missing the manual trigger of the recurrent cycle"), `assets/README.md` (line in
  the inventory) and the **Payload** of **dim 9** in `dimensions-template.md` (from
  "skill-template quenching-skills" to "+ ready command-skill … the package now
  **carries** the first command, not just detects the absence").
- **Why:** it was the **next candidate** pointed out by R17 and the one in the
  advancement backlog, and the concrete gap the user feels: the 10-round sequence
  (workflow+commands+hooks) culminated in R17 in a **doctrine** of cycle (Step 8)
  that **anticipated** three payloads without materialising any; the package still
  had no `assets/commands/`. This round is the **payload** of trigger (3) — distinct
  from R8 (migration criterion command→skill, no new payload) and R17 (the
  spine/doctrine of the loop, no payload). Choosing the **form** with rationale
  closed the theme: the re-audit **reads and proposes** (no side effect) and the
  operator forgets to invoke it ⇒ both command→skill migration criteria match
  (auto-trigger + portable/multi-repo), so **skill with auto-trigger**, not a legacy
  command nor `disable-model-invocation`.
- **Sources:** [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
  (accessed 2026-06-29, ✅ verified by WebFetch) — **verbatim**: *"**Custom commands
  have been merged into skills.** A file at `.claude/commands/deploy.md` and a skill
  at `.claude/skills/deploy/SKILL.md` both create `/deploy` and work the same way …
  Skills add optional features: a directory for supporting files, frontmatter to
  control whether you or Claude invokes them, and the ability for Claude to load them
  automatically when relevant"*; *"Files in `.claude/commands/` still work and support
  the same frontmatter. Skills are recommended since they support additional features
  like supporting files"*; on the manual-only field: *"**`disable-model-invocation:
  true`**: Only you can invoke the skill. Use this for workflows with side effects or
  that you want to control timing, like `/commit`, `/deploy`, or `/send-slack-message`"*
  (⇒ **not** the case of a read-only re-audit); on the fork: *"Add `context: fork`
  to your frontmatter when you want a skill to run in isolation … the built-in Explore
  and Plan agents skip CLAUDE.md and git status to keep their context small"* and
  *"`argument-hint` — Hint shown during autocomplete to indicate expected arguments"*.
  Catalogue: `research/05-slash-commands.md` (legacy×recommended format; `context:
  fork`; `argument-hint`; `$ARGUMENTS`; 9 confirmed sources).
- **Rejected/superseded:** discarded the payload as a **pure legacy command**
  (`.claude/commands/reauditar.md` with `disable-model-invocation: true`) — the
  official docs reserve `disable-model-invocation` for **side effects / timing
  control** (deploy/commit/slack), and the re-audit has **no** side effect; removing
  auto-triggering would go against the user's own gap ("the method does not use
  commands") and against the R8 doctrine. Discarded materialising **all three** Step 8
  payloads in this round (PR hook + Stop hook + command) — one surgical evolution per
  round; the PR/Stop hook remains a candidate. Discarded **doubling the existing
  auditor's function** (just saying "use the sub-agent") instead of creating the
  command — the Step 8 slot is an invocable **command** `/<re-audit>` (the user misses
  a **command**, not another agent); the command-skill **orchestrates** the auditor
  via `context: fork`/`agent:`, it does not replace it. Discarded embedding own
  `references/`/`scripts/` in the payload (Simplicity First) — it **reuses**
  `references/detection-and-smells.md` and the `quenching-auditor` agent from the package,
  without duplicating detection. Discarded hardcoding this repo's paths (portability):
  the payload derives paths in Step 0 and uses an adaptable `<prefix>`.
- **Next candidate:** "PR hook / freshness Stop hook ready in `assets/hooks/`" —
  materialise the slots of **triggers (1) and automatic freshness** from Step 8 (PR
  hook that reruns detection of the touched scope and **proposes**, does not block +
  evolutionary Stop hook that reads the transcript), with correct exit semantics
  (`exit 2`+stderr × proposal) and actionable error (R11). Or "PR `docs/` coverage
  hook (enforcement of taxonomy in PR)" — the dim 2 slice of the same trigger (1).

### Round 8 — 2026-06-29 · boundary: Legacy command → skill (recommended format + migration criterion)

- **Change:** refined **dimension 9 (commands)** in `dimensions-template.md` and
  added cross-cutting item **9b** in `detection-and-smells.md`. The "What good looks
  like" stops being "`.claude/commands/*.md` with description/allowed-tools + live
  corresponding skill" and gains the **legacy×recommended anchor fact**: **`.claude/commands/<name>.md`
  is the *legacy* format; `.claude/skills/<name>/SKILL.md` is the *recommended*** —
  both produce the **same** invocable `/name` and the CLI supports both, but only the
  skill adds **model-judgment auto-triggering** (the `description`/dimension 6 becomes
  a trigger) and a support directory (`references/`/`scripts/`/`assets/`) without
  bloating the body. Hence the healthy state "**every new command is born a skill**;
  remains a legacy command only the pure **manual side-effect shortcut** (and then the
  skill equivalent uses `disable-model-invocation: true`)", plus the **verifiable
  command→skill migration criterion**: (a) would benefit from auto-triggering (the
  user forgets to invoke by `/name`), (b) references external files / exceeded ~50
  lines (needs `references/`), (c) was copied to multiple repos (becomes a portable
  skill, Agent Skills open standard). New smells: **migratable legacy command**
  (passes the criterion), **basename collision** between subfolders (the subfolder
  appears in the description but does **not** change the name — ambiguous `/name`)
  and **silent shadowing** of a bundled skill (`code-review`/`verify` — `slash_commands`
  lists the name once only). In `detection-and-smells.md`, the **9b** brings greps that
  **only list candidates** (command >50 lines · with `@file`/`!cmd` · duplicate
  basename via `uniq -d` · bundled skill shadowing) + the command×skill×hook choice
  as a read applying the criterion. Conceptual diff: dimension 9 stops being "orphan
  command?" and gains a **format fact (legacy×recommended)**, a **nameable migration
  criterion** and a **name collision/shadowing detector** — with the home choice
  classified as **dimension 12 applied to mechanisms** (mirrors 7b/8b). Stays at 15
  dimensions.
- **Why:** dimension 9 was the **least operational** after those already refined —
  only checked "orphan command" and mentioned "migratable legacy command" **without a
  criterion** or the central fact that `.claude/commands/` is a **legacy** format
  replaced by `.claude/skills/`. It was the **leading candidate** (pointed out as next
  in R6 and R7) and the most anchored in the catalogue (`05-slash-commands.md`, 9
  confirmed sources). The repo **lives** by this: it has `.claude/commands/` with
  commands that mirror owner skills (cited in R6) — real candidates for
  migration/shadowing that the method now flags with a verifiable criterion instead
  of impression.
- **Sources:** [Slash Commands in the SDK — Claude Code Docs](https://code.claude.com/docs/en/agent-sdk/slash-commands)
  (accessed 2026-06-29, ✅ verified by WebFetch) — states **verbatim** *"The
  `.claude/commands/` directory is the legacy format. The recommended format is
  `.claude/skills/<name>/SKILL.md`, which supports the same slash-command invocation
  (`/name`) plus autonomous invocation by Claude. … The CLI continues to support both
  formats"*; the subfolder collision *"The subdirectory appears in the command
  description but doesn't affect the command name itself"*; the shadowing *"If you
  name a custom command after one of them, for example `.claude/commands/code-review.md`,
  your command shadows the bundled skill and `slash_commands` lists the name once"*;
  and the command frontmatter (`allowed-tools`/`description`/`model`/`argument-hint`,
  `$ARGUMENTS`/`$0`/`$1`). Catalogue: `research/05-slash-commands.md` (legacy ×
  recommended format; migration criterion >50 lines/references-files/multi-repo;
  command×skill×hook×subagent boundary; 9 confirmed sources in the anti-hallucination
  check).
- **Rejected/superseded:** discarded **creating a new dimension** "invocation
  mechanism choice" — it is a refinement of existing dim 9; the cross-cutting axis
  enters as **9b** (like 7b/8b/6b), keeping 15 dimensions (Simplicity First).
  Discarded importing the **complete argument algorithm** (`$ARGUMENTS` case-sensitive,
  positional `$0`/`$1`, named via `arguments:`, the 4 flag patterns, multi-line `` !`cmd` ``
  injection) into the template — it is command-authoring mechanics (lives in the
  catalogue), not an audit criterion; the template anchors only `argument-hint` as a
  signal that the command uses arguments. Discarded citing off the top the phrase
  *"Skills: model judgment … Hooks: harness enforcement — behavior is certain"*
  attributed to the Steering post — the catalogue marks that literal citation as
  `mischaracterised` (R6/R7 already recorded this); the template uses only what the
  official docs publish (auto-triggering by judgment × hook determinism, distinction
  already in dim 8). Discarded the **quarterly loop `/insights`→`/audit-claude-md`**
  as a method step — it is a recurrent maintenance workflow (recurring backlog item
  of the target repo, dim 4), not template evolution; stays outside this single round.
  **(This rejection was superseded by R17, `core-workflow.md`:** the axis was the
  right boundary, it just did not fit in a *dimension 9* round; R17 brought it to the
  correct home — the **core application workflow** (Step 8) — as cycle doctrine
  anchored in the official docs, without the literal `/insights`→`/audit-claude-md`.)**
- **Next candidate:** "Writing tools for agents / token-efficiency of the surface"
  (dim 6/11 — catalogue `08-writing-tools-for-agents.md`: tool description/output
  criterion and token consumption) or "Normative reference completeness / reconstruction
  test" (dim 2 — reopen with the right source, R2 deferred due to `mischaracterised`
  attribution).
