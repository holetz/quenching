---
name: quenching-specs-plan-apply
description: >-
  Implements the tasks of a plan — first offers to isolate the work on a git branch or
  worktree (recommended, never imposed), reads the touched subjects' docs/standards/ as binding
  contracts, then works through tasks.md checkbox by checkbox until done or blocked, ticking
  each with specs.py task --check. Use when the user asks to "apply the plan", "implement the
  plan", "start implementing", "continue implementation", or "work through the tasks". A plan's
  durable rules are written straight into docs/standards/ under the OKF insert procedure,
  authority-graded honestly (current when proved, background when agreed-but-unproven); other
  durable learning routes to quenching-docs-learn/quenching-docs-add, never into loose comments.
  Not for: creating the plan and its artifacts → quenching-specs-plan-propose; revising planning
  artifacts without touching code → quenching-specs-plan-update; archiving a finished plan →
  quenching-specs-plan-archive.
when_to_use: >-
  implementing the tasks of an existing plan. Creating artifacts is
  quenching-specs-plan-propose; planning-only revisions are quenching-specs-plan-update;
  archiving is quenching-specs-plan-archive.
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion
user-invocable: false
---

# quenching-specs-plan-apply — implement a plan's tasks

Implement the tasks of a **plan**, writing its durable rules into the OKF `docs/` bundle as
they are proved.

The spec-driven facts — the `specs/` layout, the plan artifact graph, the artifact formats,
the `specs.py` tool surface, and the `specs/` ↔ `docs/` boundary — live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md).
The OKF insert procedure for the docs a plan writes lives in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md).

## Resolving the tool

Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Why `Bash` is unrestricted here.** This is the one `quenching-specs-*` skill that runs the
repo's own toolchain — build, tests, linters, migrations, and `git` for the isolation offer — as
part of implementing a task. Its siblings are scoped to `python3`/`py` because they only ever
talk to `specs.py`.

**Input**: Optionally a plan name. If omitted, infer from conversation context; if only one
active plan exists, auto-select it; if vague or ambiguous you MUST prompt.

**Steps**

1. **Select the plan**

   If a name is provided, use it. Otherwise infer from context, or auto-select when a single
   active plan exists, or run `specs.py list --json` and use **AskUserQuestion** to let the user
   pick. Announce: "Using plan: `<name>`" and how to override (e.g. `/specs:plan:apply <other>`).

2. **Offer to isolate the implementation (recommended, never imposed)**

   Before touching code, offer to isolate the work so the plan can be built, reviewed, and
   merged (or discarded) as a unit — this replaces the delta-spec bookkeeping the old front
   used; real branches give history, merge, and reversion. Use **AskUserQuestion**:
   - **Branch** (default) — `git checkout -b plan/<name>` off the current branch;
   - **Worktree** — `git worktree add ../<repo>-<name> -b plan/<name>` for a separate checkout;
   - **On main** — the human declines isolation and works in place.

   If the repo is not a git repo, or the working tree is dirty, say so and let the human decide
   (commit/stash first, or proceed on main). Never force isolation, and never rewrite history.

3. **Read the plan state**
   ```bash
   specs.py status --plan "<name>" --json
   ```
   Parse the artifact `state`s, `applyReady`, the resolved `tasks.md` path, and task progress.
   - If not `applyReady` (missing `proposal`/`tasks`): show the message, suggest
     `/specs:plan:propose <name>` to finish generating the artifacts, and stop.
   - If every task is already `- [x]`: congratulate, suggest `/specs:plan:archive`.
   - Otherwise proceed.

4. **Read the plan's artifacts**

   Read `proposal.md`, `design.md` (if present), and `tasks.md` at the paths `status` resolved —
   never assume filenames. `## Impact` in the proposal names the `docs/standards/` paths and code
   this plan is expected to touch; `tasks.md` is the checklist to walk.

5. **Read the relevant OKF standards (the OKF bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), read the
   `docs/standards/<subject>/` docs for the subjects the tasks touch (naming, architecture, code,
   data-modeling, …). They are the binding contracts for HOW the implementation is built,
   complementing the plan's artifacts (WHAT to build). If a task conflicts with a standard,
   pause and surface it (step 7) instead of silently picking a side. No bundle → skip silently.

6. **Show current progress** — the plan name, "N/M tasks complete", the remaining tasks, and the
   next action from `specs.py next --plan "<name>"`.

7. **Implement tasks (loop until done or blocked)**

   For each pending task, in order:
   - Show which task is being worked on.
   - Make the code changes — minimal and focused.
   - **When the task writes a durable rule** (a `docs/standards/` item from `## Impact`), write
     that doc into its home under the insert procedure in
     [../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md),
     stamping `authority` **honestly**: `current` when the plan has actually proved the rule
     (implemented and verified), `background` when it is agreed but not yet proven. Self-check
     the new doc against
     [../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md).
   - Tick the checkbox **mechanically**, never by string surgery:
     ```bash
     specs.py task --plan "<name>" --check <id>
     ```
   - Continue to the next task.

   **Pause if:**
   - a task is unclear → ask for clarification;
   - implementation reveals a design issue → suggest `/specs:plan:update`;
   - a task conflicts with a `docs/standards/` contract → surface it and let the human pick
     (revise the standard via `quenching-docs-add`, or revise the plan via
     `/specs:plan:update`);
   - an error or blocker → report and wait;
   - the user interrupts.

8. **On completion or pause, show status**

   Run `specs.py status --plan "<name>" --json` and display tasks completed this session, overall
   progress, and — if all done — a suggestion to archive (`/specs:plan:archive`); if paused,
   explain why and wait.

**Output During Implementation**

```
## Implementing: <plan-name>

Working on task 3/7: <task description>
[...implementation happening...]
✓ Task complete (checked 3.2)
```

**Output On Completion**

```
## Implementation Complete

**Plan:** <plan-name>   **Isolation:** branch plan/<name> (or worktree / main)
**Progress:** 7/7 tasks complete ✓
**Standards written:** docs/standards/<subject>/<concept>.md (authority: current), …

All tasks complete. Ready to archive this plan (/specs:plan:archive).
```

**Output On Pause**

```
## Implementation Paused

**Plan:** <plan-name>   **Progress:** 4/7 tasks complete

### Issue Encountered
<description>

**Options:**
1. <option 1>
2. <option 2>
3. Other approach

What would you like to do?
```

**Guardrails**
- Offer isolation before the first code change; recommend it, never impose it.
- Keep going through tasks until done or blocked; read the artifacts and the relevant standards
  before starting.
- Drive off `specs.py status`/`next` and its exit codes — never assume artifact paths.
- Tick each checkbox with `specs.py task --check <id>` immediately after finishing the task;
  never hand-edit the `- [ ]`/`- [x]` character.
- Write a plan's durable rules **directly** into `docs/standards/` (`authority` graded
  honestly) under the insert procedure — there is no delta and nothing to sync.
- Keep code changes minimal and scoped to each task; pause on errors, blockers, or unclear
  requirements — don't guess.
- **Route other durable learning to its OKF home**: an insight worth keeping beyond this plan (a
  gotcha, a domain understanding, a term) goes through `quenching-docs-learn` /
  `quenching-docs-add` / `quenching-docs-define` — offer the capture, don't auto-write it, and
  never leave it in loose code comments or the tasks file.
