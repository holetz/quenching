# Dimension 7 — sub-agents

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **sub-agents: home/tool-inheritance choice and return contract**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

- **R6 · Skills vs sub-agents vs commands — selection guide** — dimension 7
  (sub-agents) stops being "complete frontmatter + minimal tools + return format"
  and gains the **home-choice criterion** (sub-agent × skill × command × hook):
  **sub-agent** when the intermediate output would flood the context with results
  that will not be re-referenced (deep search / log / dependency audit) **or** the
  same worker is spawned repeatedly; **skill** when the operator needs to see and
  steer each step in the main thread; **command** = manual shortcut; **hook** =
  deterministic enforcement (not judgment). Critical new smell: **`tools` omitted**
  ⇒ the sub-agent **inherits all parent tools** (breaks least-privilege — a read-only
  auditor gains `Edit`/`Write`/`Bash`/MCP); + read-only audit profile (`Read,Grep,Glob`
  / `haiku` / `permissionMode: plan`) and the fact that **Explore/Plan skip CLAUDE.md**
  (weighs on the dim 1 budget). Cross-cutting item **7b** in `detection-and-smells.md`
  (grep for agent without-tools / without-model + the home-choice as a 4-question
  read). Owner: `skills-skill-creator` (agent authoring); the **home choice** stays
  in the core (dimension 12 applied to mechanisms, mirrors 6b/1b). (round 6)

- **R9 · Sub-agents — return contract (condensed summary × dump)** — dimension 7
  (sub-agents) gains the **return contract** that makes "explicit return format"
  *good*: the sub-agent runs in its own window **so the parent receives only the
  high signal** — the task instruction fixes (a) **condensed summary** (~1-2k tokens,
  only high-entropy fields for the next step), **never the dump** of the consumed
  context; (b) **semantic identifiers** (`file:line`/slug/name), **not** opaque
  UUID/hash/internal ID (resolving a cryptic ID to interpretable language **reduces
  hallucination** in retrieval); (c) optional verbosity axis summary×detail.
  **Violation detector by proportion:** return whose size is close to the **consumed
  context** ⇒ became a read proxy, isolation broken. New smells: **flooding-return**
  (task that instructs returning what it read / return as large as what was read) and
  **opaque-identifier in return**. Complements **7b** (R6 covered tool-inheritance
  and home-choice; R9 covers the return contract) with greps that only list
  candidates (body that instructs "return content/log", UUID/hash use, absence of
  "Return format" block). Authoring exits `quenching-skills`; the flood detector stays
  in the core. (round 9)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 9 — 2026-06-29 · boundary: Sub-agents — return contract (condensed summary × dump)

- **Change:** refined **dimension 7 (sub-agents)** in `dimensions-template.md` and
  complemented cross-cutting item **7b** in `detection-and-smells.md`. The "What good
  looks like" had "body = role + inputs + steps + **explicit return format**" without
  saying **what makes that format *good*** — it now gains the **return contract**: the
  sub-agent runs in its own window *precisely* so the parent receives **only the high
  signal**, so the task instruction fixes (a) a **condensed summary** (target ~1-2k
  tokens, only the high-entropy fields for the parent's next step), **never the
  dump** of the context it consumed; (b) **semantic identifiers** that the parent
  understands — `file:line`/slug/name — and **not** opaque IDs/UUID/hash (the
  official docs show that resolving cryptic IDs to interpretable language **reduces
  hallucination** in retrieval); (c) optionally a verbosity axis (summary ×
  detail-on-request). The **violation detector is by proportion**: if the return is
  of a magnitude close to the **context the sub-agent consumed** (it returned almost
  everything it read), the isolation was broken — it became a read proxy, not a worker
  that condenses. New smells: **flooding-return** (task that instructs returning the
  read content/log, or return as large as what was read) and **opaque-identifier in
  return** (UUID/hash instead of `file:line`/slug). In `detection-and-smells.md`, the
  **7b** gains greps that **only list candidates** (body that instructs "return
  content/files/log"; UUID/hash use; absence of "Return format"/"condensed summary"
  block) + the contract read as a complement. Conceptual diff: dimension 7 stops
  **mentioning** the return format and gains a **verifiable contract** (high entropy +
  semantic ID + token ceiling) with a **flood detector by proportion** — reinforcing
  the sub-agent's reason to exist (isolate the verbose/disposable, dim 12 applied to
  the context flow). Stays at 15 dimensions.
- **Why:** after R6 refined dimension 7 on **least-privilege** (`tools` omitted →
  inheritance) and **home-choice**, the "explicit return format" field continued to
  **mention without defining** — the most expensive half of a poorly-made sub-agent
  (returning the dump cancels the gain of the isolated window that justified the
  sub-agent). It is the highest-value axis still open and the most anchored in the
  catalogue (`08-writing-tools-for-agents.md`, **10 confirmed sources** in the anti-
  hallucination check), pointed out as feeding dimension 7 in almost all sources. The
  method **lives** by this: the package itself carries `quenching-auditor` (a read-only
  sub-agent that returns condensed evidence) — the return contract is now an auditable
  criterion, not an assumption, and the `evolucionista` depends on the auditor **not**
  flooding the parent's context.
- **Sources:** [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  (accessed 2026-06-29, ✅ verified by WebFetch) — states **verbatim** *"tool
  implementations should take care to return only high signal information back to
  agents. They should prioritize contextual relevance over flexibility, and eschew
  low-level technical identifiers (for example: `uuid`, `256px_image_url`,
  `mime_type`)"*; *"merely resolving arbitrary alphanumeric UUIDs to more semantically
  meaningful and interpretable language (or even a 0-indexed ID scheme) significantly
  improves Claude's precision in retrieval tasks by reducing hallucinations"*; and the
  `response_format` enum *"allowing your agent to control whether tools return
  `"concise"` or `"detailed"` responses"* (concise = *"~⅓ of the tokens"*).
  Catalogue: `research/08-writing-tools-for-agents.md` (high entropy in return;
  sub-agents return **condensed summary of 1-2k tokens** to the orchestrator, never
  the full context — artifact system passes a light reference; 10 confirmed sources).
- **Rejected/superseded:** discarded **creating a new dimension** "toolset efficiency
  / token budget" — it is a refinement of existing dim 7; the axis enters as a
  complement to **7b** (as the method already does in 6b/8b/9b), keeping 15 dimensions
  (Simplicity First). Discarded importing the **`{success, data, error, metadata}`
  tool result pattern** as a canonical contract — the ⚠️ catalogue verification note
  marks that attribution as `mischaracterised` (the *Structured outputs* docs **do
  not** recommend it as a standard, only show it as an example); the template anchors
  only what the official source states (high-entropy + semantic ID + configurable
  verbosity). Discarded importing **empirical numbers** ("40% completion time
  reduction" from the test-agent, "~55k→500 tokens" from Tool Search, `token-efficient-tools`
  header) into the template — they live only in the catalogue; the template uses the
  **~1-2k token target** (which the context engineering docs publish for sub-agent
  return) and the **proportion detector** (verifiable without a magic number).
  Discarded opening the **skill consolidation/toolset-bloat** axis (dim 6/12 — "if
  an engineer can't say which skill to use, the agent can't either") in this round:
  it is its own boundary from the same catalogue, would dilute the single evolution
  — reserved as **next candidate**.
- **Next candidate:** "Skill surface consolidation / toolset-bloat" (dim 6/12 —
  catalogue `08-writing-tools-for-agents.md`: overlapping-scope skills = toolset
  bloat, consolidate instead of proliferate; the catalogue axis not yet attacked) or
  "Normative reference completeness / reconstruction test" (dim 2 — reopen with the
  right source, R2 deferred due to `mischaracterised` attribution).

### Round 6 — 2026-06-28 · boundary: Skills vs sub-agents vs commands — selection guide

- **Change:** refined **dimension 7 (sub-agents)** in `dimensions-template.md` and
  added cross-cutting item **7b** in `detection-and-smells.md`. The "What good looks
  like" stops being just "complete frontmatter + minimal tools + return format" and
  gains the **home-choice criterion** (sub-agent × skill × command × hook), the rule
  that decides where a flow lives (aligned with dimension 12, each purpose → one
  home): **sub-agent** when the intermediate output would *flood* the main context
  with results that will not be re-referenced (deep search / log analysis / dependency
  audit) **or** when the same worker is spawned repeatedly with the same instructions;
  **skill** when the procedure must happen *in the main thread* so the operator **can
  see and steer each step**; **command** when it is just a manual invocation shortcut;
  **hook** when the action must be guaranteed **deterministically** (enforcement, not
  judgment — dim 8). Critical new smell: **`tools` omitted** ⇒ the sub-agent
  **inherits all tools** from the parent session (breaks least-privilege — a
  read-only auditor gains `Edit`/`Write`/`Bash`/MCP). Also added: the **read-only
  audit profile** (`tools: Read, Grep, Glob` / `model: haiku` / `permissionMode:
  plan`, in the image of the built-ins Explore/Plan) and the fact that
  **Explore/Plan skip CLAUDE.md** (weighs on the dim 1 budget). In
  `detection-and-smells.md`, the **7b** brings greps that **only list candidates**
  (agent without `tools`/`disallowedTools`; agent without `model`) + the **home
  choice as a 4-question read** (no grep, it is the criterion). Conceptual diff:
  dimension 7 stops being "frontmatter anatomy" and gains a **nameable criterion for
  when something should be a sub-agent** and a **detector of implicit tool
  inheritance** — and the home choice is classified as **dimension 12 applied to
  mechanisms** (core decides the home; `skills-skill-creator`/`update-config` do the
  authoring), mirroring 6b/1b. Stays at 15 dimensions.
- **Why:** dimension 7 was the **least operational** after those already refined —
  it only described the frontmatter anatomy, without the criterion for *when* a task
  should become a sub-agent or the least-privilege smell. The repo **lives** by this:
  it has 2 sub-agents (`diagnoser-run`, `quenching-evolutionist`) — both today
  with explicit `tools`, but the method had no way to **flag** a third one born
  without `tools` (implicit inheritance = real risk). And the home-choice boundary
  was a recurring candidate (pointed out as next in R3, R4, and R5) and the most
  anchored in the catalogue (`02-subagents.md` with 7 verified sources + `05-slash-commands.md`).
- **Sources:** [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
  (accessed 2026-06-28, ⚠️ verified by WebFetch) — states **verbatim** the criterion
  *"Use one when a side task would flood your main conversation with search results,
  logs, or file contents you won't reference again: the subagent does that work in
  its own context and returns only the summary. Define a custom subagent when you
  keep spawning the same kind of worker with the same instructions"*, the frontmatter
  table **"`tools` … Inherits all tools if omitted"** + *"If you keep all tools
  selected, the subagent inherits all tools available to the main conversation"*,
  `tools`=allowlist / `disallowedTools`=denylist (denylist applied first), and the
  built-ins **Explore/Plan read-only (Write/Edit denied), Haiku, which "skip your
  CLAUDE.md files … to keep research fast and inexpensive"**; [Steering Claude Code:
  skills, hooks, rules, subagents and more — Claude Blog](https://claude.com/blog/steering-claude-code-skills-hooks-rules-subagents-and-more)
  (accessed 2026-06-28, ⚠️ verified by WebFetch) — **verbatim** *"Use a subagent when
  a side task like deep search, a log analysis pass, or a dependency audit would
  clutter your main conversation with intermediate results you won't reference again.
  Use a skill when you want the procedure to play out inside the main thread so you
  can see and steer each step"* and the CLAUDE.md(facts) × skills(procedures: *"deploy
  workflows, release checklists … belong in a skill rather than in CLAUDE.md"*)
  boundary. Catalogue: `research/02-subagents.md` (read-only audit profile
  `Read,Grep,Glob`/haiku/plan; tool-inheritance anti-pattern; fork × named) and
  `research/05-slash-commands.md` (golden rule CLAUDE.md/skill/hook/subagent; legacy
  command × skill).
- **Rejected/superseded:** discarded citing off the top the phrase *"Skills: model
  judgment — behavior is likely but not guaranteed. Hooks: harness enforcement —
  behavior is certain"* attributed to the Steering post — the ⚠️ catalogue
  verification note (and WebFetch) confirms that **this literal quote is not in the
  article**; the template uses only the language the official source **actually**
  publishes (the functional distinction skill=judgment × hook=deterministic already
  lives in dim 8/6, without an invented citation). Discarded **importing the
  agent-teams algorithm / Dynamic Workflows / the numbers "3-5 teammates", "~7x
  tokens"** — the catalogue marks those attributions as `mischaracterised` (not found
  in the official sources) and they fall outside the read-only/Simplicity First scope
  (the method audits the surface, not orchestrating teams). Discarded **creating a
  new dimension** "mechanism choice" — it is a refinement of dim 7 and the cross-
  cutting axis enters as **7b** (like 6b/1b), keeping 15 dimensions. Discarded
  refining **dim 9 (commands)** with the "legacy command → migrate to skill" criterion
  in this round — it touches the repo (4 commands in `.claude/commands/`, some
  mirroring owner skills) but is its own boundary; would dilute the single evolution
  (stays in the backlog).
- **Next candidate:** "Evolutionary Stop hook / continuous audit" (dim 8 — catalogue
  `04-claude-md-memory.md`/`03-hooks.md`: Stop hook that reads the transcript and
  proposes a CLAUDE.md delta) or "Legacy command → skill" (dim 9 — catalogue
  `05-slash-commands.md`: migrate `.claude/commands/*.md` to `.claude/skills/`).
