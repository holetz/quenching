---
description: Build a sourced documentation plan for the /.knowledge/documentation home, with reader journeys and six output contracts. Triggers on "plan the documentation", "diagnose the docs structure", or "design the documentation architecture". Not for: writing pages → /quenching:knowledge:documentation:write; scoring pages → /quenching:knowledge:documentation:review; configuring or building the site → /quenching:knowledge:documentation:build; conducting the complete run → /quenching:knowledge:documentation:produce.
argument-hint: [optional-source-paths-or-scope]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), Bash(rg:*), Write
---

# /quenching:knowledge:documentation:plan — diagnose sources and record the documentation plan

**Input**: `$ARGUMENTS` (optional source paths or a scope; omit to inspect the target repository's
README, legacy docs, code, specs and `/.knowledge/standards/`).

This planning pass reads sources and writes only the plan-of-record at
`${CLAUDE_PROJECT_DIR}/.quenching/documentation/plan.md`. The six contracts, the architecture rules
and reader journeys live in
[knowledge-documentation/architecture.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-documentation/architecture.md);
source provenance is defined by
[knowledge-documentation/quality.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-documentation/quality.md).

## Doctrine

- **Sources are evidence.** Inventory before interpreting; cite a file, code location, provided official document, user link or marked inference.
- **Contracts precede prose.** Produce diagnosis, journeys, IA, visual, LLM-readability and execution contracts in that order.
- **Gaps stay visible.** Every unsupported claim is `source gap: <what's missing>`, never an invention.
- **The plan is outside `docs_dir`.** `.quenching/` is never a documentation page; if the target
  does not ignore it yet, say so and route the entry to `build` (`site-scratch-tracked`).
- **One OK gates the plan.** Show the complete table and wait for confirmation before writing the record.

## Workflow

### 1. Confirm the target and inventory sources

Resolve the repository root, verify `/.knowledge/index.md` and the `documentation/` home, then
collect source paths, heading skeletons, links, existing nav/config and relevant code/specs with
read-only tools. **Done when:** the source inventory names each path and its audience, or records
the missing bundle/home as a handoff to `/quenching:knowledge:align`.

### 2. Diagnose faults and truth risks

Classify audience, site state, orphan/duplicate/weak-title/wall/dump faults, claims without an
origin and visual opportunities. Keep evidence as file paths or line references. **Done when:**
the Diagnosis contract is filled and every uncertain claim is a `source gap:`.

### 3. Compose the six contracts

Fill the exact templates in `architecture.md`: three end-to-end journeys, an intent-based nav and
source→destination map, a visual plan, an agent-readability plan and an execution plan listing
extensions, risk and validation. **Done when:** all six contract headings exist in order and no
placeholder is silently guessed.

### 4. Present the plan and obtain one OK

Show the inventory findings, six contracts, proposed files, page intents, extensions and source
gaps as one reviewable plan. Wait for the user's confirmation; revise the plan if it is declined.
**Done when:** one explicit OK is recorded, or the run stops with no file written.

### 5. Write the plan of record

Create `.quenching/documentation/plan.md` with the contracts, source ledger seeds, page assignments,
open gaps and the accepted execution order. **Done when:** the plan exists outside the docs home,
contains all six contracts and can be handed to `write` without re-reading the raw inventory.

### 6. Self-check the record

Re-read the written plan, check that every destination has one intent and that every claim has an
allowed origin or `source gap:`. **Done when:** the record is internally consistent and the report
lists its path, assignments and remaining gaps.

## Invariants to never violate

- Never write a documentation page in this pass.
- Never fabricate a fact, source, statistic, quote, title or destination.
- Keep the plan at `.quenching/documentation/plan.md`, never under `/.knowledge/documentation/`.
- A declined OK leaves the target unchanged.
