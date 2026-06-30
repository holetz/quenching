# Dimension 1 — CLAUDE.md / context budget

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **the always-loaded map and context-budget pruning**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

- **R5 · Progressive disclosure / context budget** — dimension 1 (CLAUDE.md)
  stops being "≤150 lines + link" and gains the **context budget** axis: the
  CLAUDE.md is **always-loaded** (consumes fixed budget on every session) vs.
  everything that is **on-demand** (skills/sub-CLAUDE.md/`docs/` — only loaded
  when relevant). Three verifiable instruments: the **per-line pruning criterion**
  *"if I remove this line, would Claude make a mistake?"* (cut or convert:
  mandatory rule→hook, procedure→skill, volatile detail→link); the official
  **include/exclude table** (7×7 categories); the gotcha **`@import` does not
  save context** (expands inline). Two new smells — **rule that survives the
  pruning criterion** (model default/style-in-linter/obvious practice) and
  **context rot / fossil** (directive describing a pattern already replaced,
  loaded every session). Cross-cutting item **1b** in `detection-and-smells.md`
  (greps that only *list candidates* for cutting/conversion + cross-read with
  dimension 2 for the fossil). Owner: `/sync-claude-md` (prunes/repoints the
  map); the fossil crosses with dimension 2. (round 5)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 5 — 2026-06-28 · boundary: Progressive disclosure / context budget

- **Change:** refined **dimension 1 (Map — CLAUDE.md)** in `dimensions-template.md`
  and added cross-cutting item **1b** in `detection-and-smells.md`. The "What good
  looks like" stops being just "≤150 lines + short directive + link" and gains the
  **context budget** axis: the CLAUDE.md is **always-loaded** (enters every session
  before the first message, consumes fixed budget) vs. everything that is
  **on-demand** (skills, sub-CLAUDE.md of sub-folder, `docs/` — only enters when
  relevant). Three verifiable instruments enter: (a) the **per-line pruning
  criterion** — *"if I remove this line, would Claude make a mistake?"* (if not,
  **cut**; or **convert**: mandatory rule → hook, "when I do X I follow Y"
  procedure → skill, detail that always changes → link); (b) the official
  **include/exclude table** (7 ✅ / 7 ❌ categories) that says what belongs in the
  map; (c) the gotcha **`@import` does not save context** (expands inline, counts
  the same — serves only human maintenance). Two new smells: **rule that survives
  the pruning criterion** (model default / style already in linter / obvious
  practice) and **context rot / fossil** (directive describing a pattern **already
  replaced**, loaded every session). In `detection-and-smells.md`, the **1b** brings
  greps that **only list candidates** (obvious-practice, mandatory-rule-as-prose
  candidate for hook, use of `@import`) + the fossil check as a **cross-read with
  dimension 2** (is the pattern cited still the active one in `docs/arquitetura/`?).
  Conceptual diff: dimension 1 stops being "size + link" and gains a **nameable
  pruning test** and the **always-loaded × on-demand boundary** as a lens — and
  "context budget" enters as **cross-cutting 1b** (mirrors 6b/12), without becoming
  a new dimension (stays at 15).
- **Why:** "size of SKILL.md/CLAUDE.md" was being treated as loose numbers (≤150 in
  dim 1, <500 in dim 6) without the **criterion** that the official docs canonise or
  the **always-loaded × on-demand boundary** that decides the home of each line —
  the root of progressive disclosure. The repo **lives** by this: the root CLAUDE.md
  is already a map-with-link and has a **150-line hook** (memory `project_…`), but
  the method was missing the per-line pruning test and the **fossil** smell (map
  directive pointing to a pattern that `docs/arquitetura/` has already superseded —
  a concrete risk in a repo in active schema/catalogue refactor). It was the highest-
  value, most-anchored candidate boundary in the catalogue (`07`/`04`, multiple
  official Anthropic sources).
- **Sources:** [Best practices for Claude Code — Claude Code Docs](https://code.claude.com/docs/en/best-practices)
  (accessed 2026-06-28, ⚠️ verified by WebFetch) — states **verbatim** the pruning
  criterion *"Keep it concise. For each line, ask: 'Would removing this cause Claude
  to make mistakes?' If not, cut it. Bloated CLAUDE.md files cause Claude to ignore
  your actual instructions!"*, the **include/exclude table** (7×7 categories), the
  boundary **"CLAUDE.md is loaded every session… For domain knowledge or workflows
  that are only relevant sometimes, use skills instead. Claude loads them on demand
  without bloating every conversation"**, and **"context window is the most important
  resource to manage"**; [Effective context engineering for AI agents — Anthropic
  Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents)
  (2025-09-29) — *smallest high-signal set*, context rot, hybrid CLAUDE.md
  pre-loaded + just-in-time retrieval. Catalogue: `research/07-context-engineering.md`
  (context rot on the knowledge surface; 3-level progressive disclosure) and
  `research/04-claude-md-memory.md` (pruning criterion; CLAUDE.md=guidance vs
  hook=enforcement; ⚠️ gotcha **`@import` expands inline and does NOT save context**,
  source alexop.dev verified).
- **Rejected/superseded:** discarded creating a **new dimension** "context budget"
  — it is a refinement of existing dimension 1, and the cross-cutting axis enters as
  **1b** (like 6b/12), keeping 15 dimensions (Simplicity First, no inflation of the
  count). Discarded importing **community empirical numbers** (~50 system-prompt
  slots, 60-120 lines, +10% SWE-Bench from Arize, 10x semantic search) into the
  template — they live only in the catalogue; the template anchors **only what the
  official docs state** (pruning criterion, include/exclude table, always-loaded×on-
  demand). Discarded proposing the **evolutionary Stop hook** (reads transcript →
  proposes CLAUDE.md delta) in this round — it belongs to dimension 8 (hooks) and
  has its own theme (went to the backlog), would dilute the single evolution.
  Discarded refining **dim 6 (SKILL.md size)** again — already received R4; the
  budget axis enters in dim 1, the home of always-loaded.
- **Next candidate:** "Skills vs sub-agents vs commands — selection guide"
  (dim 6/7/9 — catalogue `02-subagents.md`/`05-slash-commands.md`/`09-building-effective-agents.md`)
  or "Evolutionary Stop hook / continuous audit" (dim 8 — catalogue `04-claude-md-memory.md`).
