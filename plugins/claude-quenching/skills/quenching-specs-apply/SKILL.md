---
name: quenching-specs-apply
description: >-
  Builds a spec in ready/ and proves each task — refuses a dirty tree, offers branch or worktree
  isolation, reads the touched subjects' docs/standards/ as binding contracts, then per task:
  writes the code, runs its verify under the spec's declared policy, self-reviews the diff, and
  commits that task alone. Use when the user asks to "apply the spec", "build it", "implement
  this", "start implementing", or "work through the tasks". Boxes flip via specs.py task --check;
  a task that stops converging is written `- [!] <id> <title> — blocked: <reason>` straight into
  ## Tasks, visible to whoever unblocks it, and next skips it — there is no hidden attempt
  counter. Durable rules go into docs/standards/, authority-graded honestly, and discoveries into
  ## Discoveries. Offers the whole-branch review and chains into archiving at 100%. Not for:
  filling a spec's sections -> quenching-specs-develop; interrogating it -> quenching-specs-refine;
  closing it out -> quenching-specs-archive.
when_to_use: >-
  implementing, verifying, and committing the tasks of a spec in ready/.
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Task, Skill
user-invocable: false
---

# quenching-specs-apply — implement a plan's tasks

Implement the tasks of a **plan** — verifying each one, reviewing its diff, and committing it —
writing the plan's durable rules into the OKF `docs/` bundle as they are proved.

A task is not done when the code is written. It is done when it **ran**, its diff was
**reviewed**, and it is **committed** on its own. The mechanics of that — the verification policy,
the failure budget, the four-item diff self-review, the per-task commit, and the rules for
delegating an executor — live in [references/execution.md](references/execution.md), which this
body cites and never restates.

The spec-driven facts — the `specs/` layout, the plan artifact graph, the artifact formats,
the `specs.py` tool surface, and the `specs/` ↔ `docs/` boundary — live in
[../quenching-specs-develop/references/spec-driven.md](../quenching-specs-develop/references/spec-driven.md).
The OKF insert procedure for the docs a plan writes lives in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md).

## Resolving the tool

Resolve `specs.py` by the fallback in
[../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md)
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
   pick. Announce: "Using plan: `<name>`" and how to override (e.g. `/specs:apply <other>`).

2. **Require a clean tree, then offer to isolate (recommended, never imposed)**

   **Precondition first.** Run `git status --porcelain`. If it is non-empty, **refuse to start**
   and say why: this skill commits one task at a time, and a commit cannot tell the task's diff
   from an unrelated edit that was already in the tree. Offer to commit or stash first. The human
   may override — then the first commit carries the pre-existing changes and the report says so.
   ([execution.md](references/execution.md) §The precondition.)

   Then offer to isolate the work so the plan can be built, reviewed, and merged (or discarded) as
   a unit — this replaces the delta-spec bookkeeping the old front used; real branches give
   history, merge, and reversion. Use **AskUserQuestion**:
   - **Branch** (default) — `git checkout -b plan/<name>` off the current branch;
   - **Worktree** — `git worktree add ../<repo>-<name> -b plan/<name>` for a separate checkout;
   - **On main** — the human declines isolation and works in place.

   Not a git repo → no isolation and no commits; say so once and run the loop normally. Never
   force isolation, never `git init` on the human's behalf, and never rewrite history.

3. **Read the plan state**
   ```bash
   specs.py status --spec "<slug>" --json
   ```
   Parse the artifact `state`s, the ready gate, the resolved `## Tasks` path, task progress,
   the blocked tasks, and **`verification`** — the plan's declared policy (`per-task` /
   `per-section` / `end-of-plan`), which decides when the suite runs so this skill never has to.
   - If not the ready gate (missing `proposal`/`tasks`): show the message, suggest
     `/specs:develop <name>` to finish generating the artifacts, and stop.
   - If every task is already `- [x]`: congratulate, offer to chain into `/specs:archive`
     (step 9).
   - If the spec carries `[!]` tasks, name those tasks and their last error up front — they are
     tasks already written `[!]`, not tasks nobody has tried.
   - Otherwise proceed.

   the ready gate is a **floor, not a verdict**. Mention any open `specs.py validate` warning once
   (`sp-unrefined` — nobody has interrogated this plan; `sp-impact-uncovered` — a declared
   standard no task writes) and offer `/specs:refine` before building. Never gate on it.

4. **Read the plan's artifacts**

   Read `## Problem`/`## Proposal`, `## Design` (if present), and `## Tasks` at the paths `status` resolved —
   never assume filenames. `## Impact` in the proposal names the `docs/standards/` paths and code
   this plan is expected to touch; `## Tasks` is the checklist to walk.

5. **Read the relevant OKF standards (the OKF bridge)**

   If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), read the
   `docs/standards/<subject>/` docs for the subjects the tasks touch (naming, architecture, code,
   data-modeling, …). They are the binding contracts for HOW the implementation is built,
   complementing the plan's artifacts (WHAT to build). If a task conflicts with a standard,
   pause and surface it (step 7) instead of silently picking a side. No bundle → skip silently.

6. **Show current progress** — the plan name, "N/M tasks complete", the remaining tasks, and the
   next action from `specs.py next --spec "<slug>"`.

7. **Implement tasks (loop until done or blocked)**

   Ask the tool for the next task — never pick one by reading the file:
   ```bash
   specs.py next --spec "<slug>" --json
   ```
   It returns the task's `verify`, `files`, `pattern`, `parallel` and the plan's `verification`
   policy, and it **skips `[!]` blocked tasks** (`action: "blocked"`
   when every remaining task has). Then, for that task:

   a. **Show which task is being worked on**, with its declared `files:` and `verify:` if any.

   b. **Write the code** — minimal and focused, scoped to the task's declared files. A task that
      declares `files:` and writes nothing under `docs/` **may** be handed to an executor
      sub-agent; the orchestrator keeps every confirmation, every checkbox, every `docs/` write
      and the pause decision ([execution.md](references/execution.md) §Delegating an executor —
      including why this is **not** `context: fork` and leaves that rule untouched).

   c. **When the task writes a durable rule** (a `docs/standards/` item from `## Impact`), write
      that doc into its home under the insert procedure in
      [../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md),
      stamping `authority` **honestly**: `current` when the plan has actually proved the rule
      (implemented and verified), `background` when it is agreed but not yet proven. Self-check
      the new doc against
      [../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md).
      **This one is never delegated** — the orchestrator writes every `docs/` file itself.

   d. **Verify, per the plan's policy** ([execution.md](references/execution.md) §The validation
      loop). On failure, record the attempt mechanically and fix:
      ```bash
      specs.py task --spec "<slug>" --block <id> --reason "<why, one line>"
      ```
      Re-read the task and the current diff from scratch after **two consecutive failures**; stop
      at **five** and report the task blocked. Never weaken the check to make it pass.

   e. **Self-review the task's diff** — the four items (reuse · useless defense · obvious comment
      · dead code) — and fix what it finds *before* committing.

   f. **Commit that task alone**:
      ```bash
      git add -A && git commit -m "plan/<name>: <id> <task title>"
      ```
      Never `--no-verify`, never `--no-gpg-sign`, never amend an earlier task's commit.

   g. **Tick the checkbox mechanically**, never by string surgery:
      ```bash
      specs.py task --spec "<slug>" --check <id>
      ```

   **Pause if:**
   - a task is unclear → ask for clarification;
   - implementation reveals a design issue → suggest `/specs:develop`;
   - a task conflicts with a `docs/standards/` contract → surface it and let the human pick
     (revise the standard via `quenching-docs-add`, or revise the plan via
     `/specs:develop`);
   - further attempts stop converging → report it blocked and move to the next task;
   - an error or blocker → report and wait;
   - the user interrupts.

8. **Offer the end-of-plan review**

   With every task done, **offer** one review of the whole branch diff (`git diff <base>...HEAD`).
   This is a different thing at a different scale from step 7e's per-task check
   ([execution.md](references/execution.md) §The end-of-plan review): only the whole diff shows
   two tasks that solved the same problem twice, an abstraction that wanted extracting once the
   third caller appeared, or a `## Impact` path nothing ever wrote. Offer it once; a declined
   offer is a complete answer.

9. **On completion or pause, show status — and offer to chain**

   Run `specs.py status --spec "<slug>" --json` and display tasks completed this session, overall
   progress, any blocked tasks with their last error, and the standards written.

   **At 100%**, offer to chain straight into `quenching-specs-archive` (the `Skill` tool) so
   the plan's by-products reach `docs/` in the same run — the archive-time distillation is the
   irreducible value of the ritual, and it is what gets skipped when the human is told to run
   another command later. Offer it; on decline, name `/specs:archive` and stop.

   If paused, explain why and wait.

**Output During Implementation**

```
## Implementing: <plan-name>

Working on task 3/7: <task description>
[...implementation happening...]
✓ verify: pnpm test middleware/ — passed (attempt 1)
✓ self-review: clean
✓ committed a1b2c3d  plan/<name>: 3.2 <task title>
✓ Task complete (checked 3.2)
```

**Output On Completion**

```
## Implementation Complete

**Plan:** <plan-name>   **Isolation:** branch plan/<name> (or worktree / main)
**Progress:** 7/7 tasks complete ✓   **Verification:** per-section
**Commits:** 7 (one per task)
**Standards written:** docs/standards/<subject>/<concept>.md (authority: current), …
**Blocked:** none

Review the whole branch diff before archiving? Then: archive this plan (/specs:archive).
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

**Hard rules — no exceptions, and no "just this once"**

These are the ways an implementation ships a lie with a green checkbox. Each is absolute:

- **Never disable, skip, `xfail`, or delete a test** to make a task pass.
- **Never edit the `verify:` command, the test, or the assertion** so it stops failing. Change the
  code, or report the task blocked.
- **Never `git commit --no-verify`.** A failing commit hook is a finding to report, not an
  obstacle to route around. Same for **`--no-gpg-sign`**.
- **Never amend or rewrite an earlier task's commit**, and never force-push.
- **Never tick a checkbox for work that was not verified** — if nothing could verify it, say so in
  the report rather than implying the task was proved.

**Guardrails**
- Require a clean tree before the first code change; offer isolation, recommend it, never impose
  it.
- Keep going through tasks until done or blocked; read the artifacts and the relevant standards
  before starting.
- Drive off `specs.py status`/`next`/`task` and its exit codes — never assume artifact paths,
  never choose the next task by reading `## Tasks` yourself, and never hand-edit the spec's frontmatter
  attempt state.
- Verify per the plan's **declared** `verification` policy; never decide mid-implementation when
  to test, and never ask the human to decide it then.
- Tick each checkbox with `specs.py task --check <id>` **after** the task verified, self-reviewed,
  and committed; never hand-edit the `- [ ]`/`- [x]` character.
- A task written `[!]` is **blocked, not failed-forever** — report it with its reason and move on.
  changing something.
- Delegate an executor only under [execution.md](references/execution.md) §Delegating an executor
  (task declares `files:`, touches no `docs/`, pinned to the session model — never `haiku`), and
  run two tasks in parallel only when `specs.py parallel` reports the `[P]` group eligible.
- Write a plan's durable rules **directly** into `docs/standards/` (`authority` graded
  honestly) under the insert procedure — there is no delta and nothing to sync.
- Keep code changes minimal and scoped to each task; pause on errors, blockers, or unclear
  requirements — don't guess.
- **Route other durable learning to its OKF home**: an insight worth keeping beyond this plan (a
  gotcha, a domain understanding, a term) goes through `quenching-docs-learn` /
  `quenching-docs-add` / `quenching-docs-define` — offer the capture, don't auto-write it, and
  never leave it in loose code comments or the tasks file.
