---
name: quenching-standards
description: >-
  Builds OR updates the ENTIRE `standards/` layer from the repository +
  external references — derives which topics apply, fan-outs a `quenching-writer`
  sub-agent PER TOPIC in parallel (each in a clean context), then REGENERATES
  `INDEX.md` deterministically from disk. Distinct from `quenching-docs`, which
  edits ONE doc. Use when the user asks to "build/update the standards structure",
  "generate the current-standards layer", "document the repo standards", "populate
  docs/standards", or "synchronize the standards index".
when_to_use: >-
  build/rebuild the entire `standards/` layer (all applicable topics) from the
  repo + references, with parallel fan-out per topic and index regenerated from
  disk.
allowed-tools: Read, Grep, Glob, Edit, Write
---

# `standards/` layer — parallel builder/updater

> Skill-template of the `quenching-management` method. Generic and portable:
> fix the real path of `docs/standards/` as derived in the repo where it is
> installed. This skill **orchestrates**; the workers (`quenching-writer`) **write**.

## What this skill is (and is not) — anti-bloat boundary

- **`quenching-docs`** = authoring **ONE** doc (any home: standards,
  backlog, ADR, direction, domain), with index synchronization for that home.
- **`quenching-standards`** = **ORCHESTRATES** the build/refresh of the
  `standards/` layer **ENTIRELY**, in **parallel** (one worker per topic), and
  **synchronizes the index** by regenerating it from disk.

This skill **COMPOSES** with `quenching-docs` (the workers follow its authoring
discipline — one standard per file, frontmatter, kebab-case, no duplication),
**not duplicates it**. If the request is "write/adjust **one** standard", use
`quenching-docs`. If it is "build/update the **entire** layer", use this.

## Procedure

1. **Derive the topics that APPLY.** From the nine canonical ones (`architecture` ·
   `code` · `naming` · `data-modeling` · `ci-cd` · `workflows` · `mlops` ·
   `quality` · `platform` — see `references/docs-taxonomy.md`), select **only
   those that fit** the repo (repo without ML → no `mlops/`; without data → no
   `naming/`/`data-modeling/`). Completeness of **what fits**, not a blind
   checklist. **Effort scale:** few topics → few agents (fan-out proportional to
   scope, not fixed).

2. **Fan-out: ONE `quenching-writer` per topic, IN PARALLEL.** Fire the workers
   in a **single message with multiple sub-agent invocations** — each in its own
   **clean context**. Standards topics are **intrinsically independent**
   (`code` ≠ `naming` ≠ `platform`); running them in parallel is the recommended
   case per official docs (*"Research the … modules in parallel using separate
   subagents"*; *"the lead agent spins up 3-5 subagents in parallel rather than
   serially"*). Caveats governing the fan-out:
   - **Concerns that CITE each other stay in the orchestrator, sequential** —
     topics *"that require all agents to share the same context … are not a good
     fit"* for parallelism. Reconciliation of two cross-cutting topics is yours,
     not the worker's.
   - **Each worker returns ONLY the condensed summary** — *"Running many subagents
     that each return detailed results can consume significant context"*.
   - **Parallelism ≈ 15× tokens** (*"multi-agent systems use about 15× more
     tokens than chats"*): it's a purchase of **quality/latency**, not savings.
     In a **large repo**, run **one slice** (one topic) first to calibrate before
     opening the full fan-out.

3. **(Quality, optional) Adversarial review in fresh context** before merging: a
   sub-agent that sees only the diff and the criterion (*"A reviewer running in a
   fresh subagent context sees only the diff and the criteria you give it"*) and
   checks **the anti-fabrication INVARIANT** — no unimplemented best-practice
   asserted as `current`; **every** current rule anchored at `file:line`.

4. **Collect condensed returns** and **expose the gaps** that workers proposed as
   **PROPOSED** items in `backlog/` / `decisions/`. **Proposes, does not impose** —
   the operator confirms (method's deprecation/confirmation doctrine).

5. **Regenerate `INDEX.md` DETERMINISTICALLY from disk.** The index is a **DERIVED
   artifact**, never hand-edited ("X defines Y" rule; structural drift becomes
   impossible by construction):
   - **Scan** `docs/standards/**/*.md` (ignore `INDEX.md` itself and
     home/subfolder `README.md` files).
   - From each file, **read the frontmatter** `title:` / `updated:` / `status:`.
   - **Rebuild the list** in the index **BETWEEN the markers**
     `<!-- BEGIN GENERATED -->` … `<!-- END GENERATED -->`, **preserving the
     authored preamble above** (do not discard the prose to "be deterministic" —
     the generated zone is only the list).
   - **Order by topic-subfolder** (deterministic, e.g., alphabetical by
     `<topic>/<file>`), with a **light optional override** (`order:` in the doc
     frontmatter) when the repo wants to fix an order.
   - The index eliminates **structural drift** (the list lying about which files
     exist) — it does **not** validate that each `status: current` is still true
     (content drift stays with the standard's owner and the method's drift audit).

6. **Report per topic:** `built` / `updated` / `drifted-corrected` /
   `not-applicable` + the **proposed gaps** (with the source for each). Semantic
   identifiers, never the dump.

## Guardrails

- **Never** asserts an unimplemented best-practice as `current`; **current** is
  anchored at `file:line`.
- **Never** edits a generated artifact (AUTO-GENERATED catalog, manifests, job
  YAML) — "X defines Y" rule.
- **Proposes gaps, does not impose** — each proposal is a `backlog/`/`decisions/`
  item for the operator to confirm.
- **`INDEX.md` is derived** — regenerated from disk between the markers, never
  hand-edited.
- The canonical tree specification and the boundary between topics live in
  `references/docs-taxonomy.md` of the method.
