---
name: quenching-specs-plan-update
description: >-
  Revises an existing plan's planning artifacts (proposal.md, design.md, tasks.md) and keeps
  them coherent with one another — never edits code. Use when the user asks to "update the
  plan", "revise the proposal/design/tasks", "fold this decision into the plan", "make the
  plan's artifacts coherent", or "reconcile the artifacts after an edit". Reads the plan's state
  via specs.py status --plan <n> --json, applies the requested edit, checks every other existing
  artifact against it in any direction, and confirms each revision before writing; edits only
  files that already exist. Not for: creating a missing artifact or a new plan →
  quenching-specs-plan-propose; carrying a revised plan into code → quenching-specs-plan-apply;
  a durable rule/decision straight into docs/ → quenching-docs-add/quenching-docs-learn.
when_to_use: >-
  revising an existing plan's planning artifacts and keeping them coherent. Creating artifacts
  is quenching-specs-plan-propose; implementing is quenching-specs-plan-apply.
allowed-tools: Bash(python3:*), Bash(py:*), Read, Glob, Grep, Write, Edit, AskUserQuestion
user-invocable: false
---

# quenching-specs-plan-update — revise a plan's planning artifacts

Revise a plan's existing planning artifacts and keep them coherent. **Never edit code.**

The spec-driven facts — the `specs/` layout, the plan artifact graph, the artifact formats,
the `specs.py` tool surface, and the `specs/` ↔ `docs/` boundary — live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md).
The per-artifact authoring doctrine (what belongs in each file) lives in
[../quenching-specs-plan-propose/references/artifacts.md](../quenching-specs-plan-propose/references/artifacts.md).

## Resolving the tool

Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Input**: Optionally a plan name. If omitted, infer from conversation context; if vague or
ambiguous you MUST prompt.

**Steps**

1. **If no plan name provided, prompt for selection**

   Run `specs.py list --json` for the active plans sorted by `lastModified`. Use
   **AskUserQuestion** to let the user pick, presenting the top 3–4 most recently modified:
   - plan name;
   - task progress (e.g. "0/5 tasks", "complete", "no tasks");
   - how recently modified.

   Mark the most recently modified "(Recommended)". **Do NOT guess or auto-select.**

2. **Get the plan's artifacts**
   ```bash
   specs.py status --plan "<name>" --json
   ```
   Parse the JSON: each artifact's `state` (`done` / `ready` / `blocked`), `applyReady`, and the
   **resolved file paths**. The files to edit are the concrete paths `status` reports as existing
   on disk — never assume repo-local paths, and never write to a path for an artifact that does
   not yet exist. The three artifacts are `proposal`, `design` (optional), `tasks`; a `design.md`
   the plan deliberately omitted is a valid absent state, not a file to create.

3. **Understand the request**
   - A specific revision ("the design now uses X") → that is the starting edit.
   - Just "update" / "make this coherent" → treat it as a coherence review: read the existing
     artifacts and check them against each other for contradictions, gaps, and duplication.

4. **Read and reconcile**
   - Read the artifact(s) the request touches and the plan's other existing artifacts.
   - Apply the requested edit, then check every other **existing** artifact against it in ANY
     direction: an edit to `tasks.md` may require revising `proposal.md`, not only the reverse.
     Build order is a useful reading order, not a constraint on which artifacts may be revised.
   - Note everything now inconsistent, missing, or contradictory.
   - Revise only files that already exist. Do NOT create a missing artifact (e.g. a `design.md`
     the plan never had, or a `tasks.md` that was never generated) — note it and point the user
     to `/specs:plan:propose <name>`.
   - If the plan is already coherent, say so and make no edits.

5. **Confirm and apply, one artifact at a time**
   - Show each proposed revision and why. Write only after the user confirms.
   - If the user rejects a revision, do not write it — leave that artifact unchanged.
   - Keep each artifact in its format per
     [../quenching-specs-plan-propose/references/artifacts.md](../quenching-specs-plan-propose/references/artifacts.md)
     (proposal `## Why`/`## What Changes`/`## Impact`; design `## Context`/`## Decisions`/`## Risks`;
     tasks as dependency-ordered checkboxes). When a revision adds or removes a task checkbox by
     hand-editing `tasks.md`, that is fine here — but to flip an existing box's *done* state,
     prefer `specs.py task --plan "<name>" --check|--uncheck <id>` so the change stays mechanical.

6. **Point to the next step (guidance only — NEVER act on it)**
   - An artifact still missing → suggest `/specs:plan:propose <name>` to create it.
   - Plan already implemented (tasks checked off / code written) → the code may no longer match
     the revised plan; suggest `/specs:plan:apply` to carry the revised plan into code.
   - Everything done and implemented → suggest `/specs:plan:archive`.

**Output**

After each invocation, show:
- Which artifacts were revised (and which proposed revisions were rejected)
- Anything deferred to `/specs:plan:propose` (not-yet-created artifacts)
- Where the plan stands (from `specs.py status`) and the recommended next command

**Guardrails**
- Planning artifacts only — **NEVER edit implementation code.** If the revised plan implies code
  changes, stop and point to `/specs:plan:apply`.
- Use the artifact `state`s and resolved paths from `specs.py status --json`; branch on its exit
  codes, never on prose, and never assume artifact paths.
- Edit only files that already exist; do not advance the build frontier — creating a missing
  artifact is `/specs:plan:propose`'s job.
- Confirm every edit with the user before writing.
- If the request changes the plan's *intent* rather than refining it, recommend starting fresh
  with a new `/specs:plan:propose` (the "Update vs. Start Fresh" heuristic).
- A revision that surfaces durable knowledge (a rule/decision beyond this plan → a `standard`,
  a generic understanding → `knowledge/`) routes to `quenching-docs-add`/`quenching-docs-learn` —
  this skill never writes into `docs/`, and there is no delta spec or sync in this front.
