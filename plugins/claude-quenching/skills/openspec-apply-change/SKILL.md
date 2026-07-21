---
name: openspec-apply-change
description: >-
  Implements the tasks of an OpenSpec change — reads the change's artifacts plus the OKF
  bundle's relevant standards/ (the binding contracts for how we build), then works through
  tasks.md checkbox by checkbox until done or blocked. Use when the user asks to "apply the
  change", "implement the openspec change", "start implementing", "continue implementation",
  or "work through the tasks". CLI-driven: `openspec instructions apply --json` supplies the
  context files, progress, and dynamic instruction; durable learning discovered while
  implementing routes to quenching-learn/quenching-add, never into loose comments.
  Requires the openspec CLI (`@fission-ai/openspec`). Not for: creating the change and its
  artifacts → openspec-propose; revising planning artifacts without touching code →
  openspec-update-change; archiving a finished change → openspec-archive-change.
when_to_use: >-
  implementing the tasks of an existing OpenSpec change. Creating artifacts is
  openspec-propose; planning-only revisions are openspec-update-change; archiving is
  openspec-archive-change.
allowed-tools: Bash, Read, Glob, Grep, Write, Edit
user-invocable: false
metadata:
  generatedBy: "1.6.0"
---

# openspec-apply-change — implement tasks from a change

Implement tasks from an OpenSpec change.

OpenSpec facts (layout, artifact graph, formats, CLI surface) live in
[../openspec-propose/references/openspec.md](../openspec-propose/references/openspec.md).
**Store selection:** per §Store selection there.

**Input**: Optionally specify a change name. If omitted, check if it can be inferred from
conversation context. If vague or ambiguous you MUST prompt for available changes.

**Steps**

1. **Select the change**

   If a name is provided, use it. Otherwise:
   - Infer from conversation context if the user mentioned a change
   - Auto-select if only one active change exists
   - If ambiguous, run `openspec list --json` to get available changes and use the
     **AskUserQuestion tool** to let the user select

   Always announce: "Using change: <name>" and how to override (e.g., `/opsx:implement <other>`).

2. **Check status to understand the schema**
   ```bash
   openspec status --change "<name>" --json
   ```
   Parse the JSON to understand:
   - `schemaName`: The workflow being used (e.g., "spec-driven")
   - `planningHome`, `changeRoot`, and `actionContext`: planning scope and edit constraints
   - Which artifact contains the tasks (typically "tasks" for spec-driven, check status for
     others)

3. **Get apply instructions**

   ```bash
   openspec instructions apply --change "<name>" --json
   ```

   This returns:
   - `contextFiles`: artifact ID -> array of concrete file paths (varies by schema - could
     be proposal/specs/design/tasks or spec/tests/implementation/docs)
   - Progress (total, complete, remaining)
   - Task list with status
   - Dynamic instruction based on current state

   **Handle states:**
   - If `state: "blocked"` (missing artifacts): show message, suggest `/opsx:propose <name>`
     to finish generating the missing artifacts
   - If `state: "all_done"`: congratulate, suggest archive
   - Otherwise: proceed to implementation

4. **Read context files**

   Read every file path listed under `contextFiles` from the apply instructions output.
   The files depend on the schema being used:
   - **spec-driven**: proposal, specs, design, tasks
   - Other schemas: follow the contextFiles from CLI output

5. **Read the relevant OKF standards (the OKF bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), read the
   `docs/standards/<subject>/` docs for the subjects the tasks touch (naming, architecture,
   code, data-modeling, …) — they are the binding contracts for HOW the implementation is
   built, complementing the change's artifacts (WHAT to build). If a task conflicts with a
   standard, pause and surface it (see step 7's pause rules) instead of silently picking a
   side. No bundle → skip silently.

6. **Show current progress**

   Display:
   - Schema being used
   - Progress: "N/M tasks complete"
   - Remaining tasks overview
   - Dynamic instruction from CLI

7. **Implement tasks (loop until done or blocked)**

   For each pending task:
   - Show which task is being worked on
   - Make the code changes required
   - Keep changes minimal and focused
   - Mark task complete in the tasks file: `- [ ]` → `- [x]`
   - Continue to next task

   **Pause if:**
   - Task is unclear → ask for clarification
   - Implementation reveals a design issue → suggest updating artifacts
   - A task conflicts with a `docs/standards/` contract → surface the conflict, let the
     user pick (update the standard via `quenching-add`, or revise the change)
   - Error or blocker encountered → report and wait for guidance
   - User interrupts

8. **On completion or pause, show status**

   Display:
   - Tasks completed this session
   - Overall progress: "N/M tasks complete"
   - If all done: suggest archive
   - If paused: explain why and wait for guidance

**Output During Implementation**

```
## Implementing: <change-name> (schema: <schema-name>)

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete
```

**Output On Completion**

```
## Implementation Complete

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 7/7 tasks complete ✓

### Completed This Session
- [x] Task 1
- [x] Task 2
...

All tasks complete! Ready to archive this change.
```

**Output On Pause (Issue Encountered)**

```
## Implementation Paused

**Change:** <change-name>
**Schema:** <schema-name>
**Progress:** 4/7 tasks complete

### Issue Encountered
<description of the issue>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Keep going through tasks until done or blocked
- Always read context files before starting (from the apply instructions output)
- If task is ambiguous, pause and ask before implementing
- If implementation reveals issues, pause and suggest artifact updates
- Keep code changes minimal and scoped to each task
- Update task checkbox immediately after completing each task
- Pause on errors, blockers, or unclear requirements - don't guess
- Use contextFiles from CLI output, don't assume specific file names
- **Route durable learning to its OKF home**: an insight worth keeping (a gotcha, a domain
  understanding, a term, a rule beyond this change) goes through `quenching-learn` /
  `quenching-add` / `quenching-define` — not into loose code comments or the tasks
  file; offer the capture, don't auto-write it

**Fluid Workflow Integration**

This skill supports the "actions on a change" model:

- **Can be invoked anytime**: Before all artifacts are done (if tasks exist), after partial
  implementation, interleaved with other actions
- **Allows artifact updates**: If implementation reveals design issues, suggest updating
  artifacts - not phase-locked, work fluidly
