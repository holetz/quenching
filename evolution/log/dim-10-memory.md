# Dimension 10 — memory (Auto Memory)

> Part of the `quenching-management` evolution log. Index, anchor state, and backlog: [../README.md](../README.md). ID convention (R*/Rev*) and routing: [README.md](README.md).
>
> This file collects the rounds (`R*`) and revisions (`Rev*`) that touched **memory hygiene: load ceiling, CLAUDE.md boundary, smells**.

## Current state

> Active summary of each boundary in this dimension (what is valid today). Detail and rationale are in the history below.

- **R3 · Memory hygiene** — dimension 10 (Auto Memory) stops being a generic
  "index × files" check and gains: the **real load ceiling** (200 lines / 25 KB of
  `MEMORY.md`; content beyond that does not load; topic file on demand); the
  **official CLAUDE.md × Auto Memory boundary** (team-versioned × agent-local); the
  **4 prefix types** (`user_`/`feedback_`/`project_`/`reference_`, derived from
  the repo); and a **6-smell verifiable checklist** (index-orphan · duplicates-repo ·
  vague-date · silent-conflict/last-write-wins · stale-freshness · wrong-type/scope)
  with greps that list candidates. No owner (signals only). (round 3)

## Round and revision history

> Most recent rounds at the top. Revisions (`Rev*`) are nested under the round they refine.

### Round 3 — 2026-06-28 · boundary: Memory hygiene

- **Change:** refined **dimension 10 (Memory / Auto Memory)** in
  `dimensions-template.md` and in `detection-and-smells.md`. The "What good looks like"
  moves from the generic ("index, frontmatter, no duplicates") to **verifiable**
  criteria: (a) the **real load ceiling** — only the first **200 lines / 25 KB** of
  `MEMORY.md` enter the session; anything beyond that **does not load**, and detail
  goes to **topic files** (read on demand); (b) the **official CLAUDE.md × Auto
  Memory boundary** — CLAUDE.md = what *any team member needs to know* (versioned),
  Auto Memory = what *the agent learned* (machine-local, auditable via `/memory`);
  (c) the **4 prefix types** the repo already uses (`user_`/`feedback_`/`project_`/
  `reference_`). "Smells" becomes a **6-item verifiable checklist**: index-orphan ·
  duplicates-repo · vague temporal reference (vs. exact date) · silent conflict
  (*last-write-wins*; entry marked "WRONG/CORRECTED/superseded" that should be
  **pruned**) · stale freshness (*context poisoning by staleness*) · wrong
  type/scope. In `detection-and-smells.md` the cross-cutting item 10 gains **greps
  that list candidates** (index orphan, `wc -l` against ceiling, vague-temporal-term
  regex, obsolescence-marking regex, date regex for provenance) with the caveat that
  (2) duplicates-repo and (6) type/scope are **comparative reads, without grep**.
  Conceptual diff: dimension 10 stops being "cross index × files" and gains a
  **numerical ceiling, a named boundary and an auditable checklist** — while never
  writing memory.
- **Why:** dimension 10 was the vaguest after 12, and the repo **lives** by this —
  there are ~40 Auto Memory files already organised by the 4 prefixes, and
  `MEMORY.md` itself shows real smells: `project_validacao_pec_asr_and4_vs_or` is
  marked "⚠️ CORRECTED/WRONG: ... was false; see E2 ASR legacy below" (silent
  conflict/staleness — a superseded entry that should be pruned, smells 4/5), and
  there are v1/v2 pairs (`...reestruturacao_atraso` × `...ap_reestruturacao_atraso_v2`)
  as dedup candidates. The method was missing the official load ceiling and the
  checklist to confront this.
- **Sources:** [How Claude remembers your project — Claude Code Docs](https://code.claude.com/docs/en/memory)
  (accessed 2026-06-28) — confirms the ceiling **"first 200 lines or 25KB"** of
  `MEMORY.md` ("Content beyond that threshold is not loaded at session start";
  topic files do not load on startup), the boundary table **CLAUDE.md (You /
  Instructions and rules / coding standards, workflows, architecture) × Auto memory
  (Claude / Learnings and patterns / build commands, debugging insights, preferences
  Claude discovers)**, and `/memory` as an audit command; [Memory tool — Claude
  Platform Docs](https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool)
  (accessed 2026-06-28) — official hygiene: **"keep its content up-to-date, coherent
  and organized... rename or delete files that are no longer relevant. Do not create
  new files unless necessary"**, "cap how large a file can grow", "periodically
  delete memory files that haven't been accessed". Catalogue:
  `research/11-memory-management.md` (6-smell checklist; *context poisoning by
  staleness*; silent *last-write-wins*; 4 frontmatter types).
- **Rejected/superseded:** discarded citing off the top "4 types of Auto Memory" as
  if they were from the official docs — the ⚠️ catalogue verification note signals
  that the Claude Code docs **do not** enumerate these 4 types by frontmatter (they
  come from community analysis / code-spelunking); the template anchors them in what
  is **verifiable in this repo** (the `user_`/`feedback_`/`project_`/`reference_`
  prefixes actually used in the file names), not in the docs. Discarded proposing an
  automated **"Auto Dream" command/hook** (cyclic pruning) — out of scope for
  read-only and Simplicity First; the method signals, the pruning stays in the memory
  flow (`/memory`). Discarded refining **dimension 1 (CLAUDE.md <200 lines)** in this
  round despite the same source touching it — it is a different dimension and would
  dilute the single evolution (the repo already has a 150-line hook; reserved for its
  own round if reopened).
- **Next candidate:** "Progressive disclosure / context budget" (sharper size
  criterion for SKILL.md/CLAUDE.md — catalogue `07-context-engineering.md`) or
  "Skills vs sub-agents vs commands — selection guide" (dim 6/7/9 — catalogue
  `02-subagents.md`/`05-slash-commands.md`/`09-building-effective-agents.md`).
