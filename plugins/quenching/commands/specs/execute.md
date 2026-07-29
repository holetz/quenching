---
description: Build ONE spec task by task — write, verify, self-review, tick, commit. Triggers on "execute this spec", "build it", "implement the tasks", "apply the plan", "start working on it", "continue building", "run the next task", "work through the tasks". Requires a clean tree; delegates isolation to /specs:isolate; verifies under the spec's own declared policy; ticks each box with the subject of the commit it is about to make, so code and box land in ONE commit per task. Writes the docs/standards/ a task explicitly names, and records everything else the work reveals as a one-line discovery. Stops at the last commit — the branch review, the merge and the archive are a separate command. Not for: writing or sharpening a spec → /specs:develop; a version bump or other release obligation → /specs:conclude; creating one → /specs:create; taking a branch or worktree → /specs:isolate; reviewing the branch, merging and archiving → /specs:conclude; being told which spec to build next → /specs:continue.
argument-hint: [slug]
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Task, Skill
---

# /specs:execute — build one spec, one task at a time

**Input**: `$ARGUMENTS` — optionally a spec slug. Omitted → infer from the conversation, or
auto-select when exactly one spec is under way; vague or ambiguous → you MUST prompt.

Builds the `## Tasks` of ONE spec: writing each task, verifying it under the spec's declared
policy, reviewing its diff, and committing it alone with the box already ticked inside that commit.

**A task is not done when the code is written.** It is done when it **ran**, its diff was
**reviewed**, and it is **committed**. The mechanics of that — the clean-tree precondition, the
verification policy, the validation loop, the four-item diff self-review, the one commit per task,
the declared-versus-emergent `docs/` line, and the rules for delegating an executor — live in
[specs-execute/execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md),
which this body cites and never restates.

**This command stops at the last commit.** Reviewing the whole branch, writing the `docs/` the work
*revealed*, merging, and archiving belong to `/specs:conclude`. That is not tidiness: the branch
review is a different scale of judgment, the merge is a separate irreversible decision needing its
own confirmation, and a run that dies after task nine must be resumable without redoing tasks one
through eight.

The git conventions — the commit subject, the branch name, the `branch` record, the subject as the
task→commit anchor, and the **read-if-present** rule for a target's `docs/standards/git/**` — live
in [specs-isolate/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md), whose
command is `/specs:isolate`.

The spec-driven facts — the layout, the thirteen canonical sections, the derived stages, the
`specs.py` surface, the `specs/`↔`docs/` boundary — live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).
The OKF insert procedure for the docs a task writes lives in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md).

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Why `Bash` is unrestricted here.** This is the one `/specs:*` command that runs the target repo's
own toolchain — build, tests, linters, migrations, and `git` — as part of implementing a task. Its
siblings are scoped to `python3`/`py` because they only ever talk to `specs.py`.

## Workflow

### 1. Select the spec
A slug was given → use it. Otherwise infer from the conversation, auto-select when exactly one spec
is under way, or run `specs.py list --json` and pick with **AskUserQuestion**. Announce
"Building spec: `<slug>`" and how to override.
**Done when:** one spec in `plans/` is resolved.

### 2. Require a clean tree, then delegate the isolation
**The precondition comes first.** `git status --porcelain` non-empty → **refuse to start**, per
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The
precondition. Offer to commit or stash. The human may override; then the first commit carries the
pre-existing changes and the report says so.

Then **hand isolation to `/specs:isolate`** (the `Skill` tool) rather than reimplementing it: it
owns the branch and worktree forms, the `plan/<slug>` name, the `branch: {base, work}` stamp and
its write-once rule. It is not exclusive to building — a spec may already have been isolated at
creation or during development, in which case that command reports the existing branch and stamps
nothing new.

Read the result before the first task: a spec whose branch is **alive but checked out elsewhere**
is being built somewhere else, and starting here would fork the work. Say so and stop.

Not a git repo → no isolation and no commits; say so once and run the loop normally. Never force
isolation, never `git init` on the human's behalf, and never rewrite history.
**Done when:** the tree is clean (or the override is on the record), and isolation has been taken,
reported as already held, or declined.

### 3. Read the spec's state, and settle the approval
```bash
specs.py status --spec "<slug>" --json
```
Read the derived stage, the section states, task progress, the blocked tasks, the recorded subjects,
and **`verification`** — the spec's declared policy, which decides when the suite runs so this
command never has to.

- **`approved` unset** → ask for it inline, in one question showing what the spec commits to, and
  stamp `approved: {date}` on a yes. **Never refuse over it** — refusing would rebuild the folder
  hop this front removed. A no ends the run cleanly.
- **`next` reports `write_section`** → the ready gate is not met. Name the missing or malformed
  sections and route to `/specs:develop <slug>`, then stop. The gate refuses nothing itself; the
  tool simply has no task to hand out until it is closed.
- **Every task already `- [x]`** → say so and offer to chain into `/specs:conclude` (step 7).
- **`[!]` blocked tasks** → name them and their reasons up front. They were tried and stopped, not
  skipped.

Mention any open `specs.py validate` warning **once** — `sp-unrefined` (nobody has interrogated
this spec), `sp-impact-uncovered` (a declared standard no task writes) — and offer
`/specs:develop` before building. Never gate on it: the ready gate is a floor, not a verdict.
**Done when:** the state is in hand, `approved` is settled, and any warning has been surfaced once.

### 4. Read what the tasks must satisfy
Read `## Problem`, `## Proposal`, `## Design`, `## Handoff` and `## Tasks` at the path `status`
resolved — never assume filenames. `## Impact` names the `docs/standards/` paths and the code this
spec expects to touch.

Then, if the repo carries an OKF bundle (`docs/index.md` with `okf_version`), read
`docs/standards/<subject>/` for the subjects the tasks touch. Those are **binding contracts** for
HOW the work is built, complementing the spec's own sections (WHAT to build). A task that
contradicts one is surfaced (step 5), never silently resolved. No bundle → skip silently.
**Done when:** the spec's sections and the binding standards are read.

### 5. Implement tasks — loop until done or blocked
Ask the tool for the next task; **never pick one by reading the file**:
```bash
specs.py next --spec "<slug>" --json
```
It returns that task's `verify`, `files`, `pattern` and `parallel`, plus the spec's `verification`
policy, and it **skips `[!]` blocked tasks** (`action: "blocked"` once every remaining task is).
Then, for that task:

a. **Show what is being worked on** — the id, its declared `files:` and its `verify:`.

b. **Write the code**, minimal and scoped to the declared files. A task that declares `files:` and
   writes nothing under `docs/` **may** go to an executor sub-agent under §Delegating an executor —
   which also explains why this is **not** `context: fork` and leaves that rule untouched.

c. **Write only the `docs/` this task names.** A `docs/standards/` path declared under `## Impact`
   and named by this task is part of its deliverable — write it through the insert procedure in
   [docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md), stamp `authority`
   honestly, and self-check it against
   [docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md).
   Anything else the work reveals costs one line — `specs.py discover "<slug>" "<finding>"` — and
   no authoring. The line between the two, and why it falls there, is §Declared versus emergent
   `docs/`.

d. **Verify, per the spec's declared policy** (§The validation loop). On a failure that stops
   converging, write it blocked with its reason —
   `specs.py task --spec "<slug>" --block <id> --reason "<why>"` — and move on. Never weaken the
   check to make it pass.

e. **Self-review the task's diff** on the four items — reuse · useless defense · obvious comment ·
   dead code — and fix what it finds *before* committing.

f. **Decide the subject, then tick the box with it** — mechanically, never by string surgery. The
   subject follows [git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-isolate/git.md)
   §Commit messages, or the target's own convention where it declares one:
   ```bash
   specs.py task --spec "<slug>" --check <id> --subject "plan/<slug>: <id> <title>"
   ```
   The subject is known **before** the commit, which is the whole reason it is the anchor: ticking
   first means the box travels *inside* the commit it describes, and the per-task bookkeeping
   commit disappears.

g. **Commit that task alone**, staging its declared files **and the spec file**, under exactly the
   subject just recorded. One task is one commit, carrying the code and its ticked box together.

h. **Assert the subject survived**, and report rather than repair:
   ```bash
   git log -1 --format=%s        # must equal what step f recorded
   ```
   A `commit-msg` hook that only *adds* (a ticket prefix, a `Change-Id`, a sign-off) leaves the
   recorded subject resolvable as a substring — that is fine and needs nothing. A hook that
   **replaces** the subject breaks the link: **report it as a finding and write nothing.** Editing
   the record now would put a write after the commit again, which is exactly what this ordering
   removed.

   If the commit itself fails — a failing hook, nothing staged — **undo the tick**
   (`specs.py task --spec "<slug>" --uncheck <id>`) so no box claims a commit that does not exist,
   then report the failure. Never `--no-verify` your way past it.

**Pause if:** a task is unclear; implementation reveals a design problem (→ `/specs:develop`); a
task contradicts a `docs/standards/` contract (surface it and let the human pick — revise the
standard via `/docs:add`, or the spec via `/specs:develop`); attempts stop converging; or the user
interrupts.
**Done when:** every task is `- [x]` or `- [!]`, or the run pauses with the reason stated.

### 6. Refresh `## Handoff` as events, not as judgment
After each committed task, rewrite `## Handoff` to the state of play a fresh executor would need
and cannot derive. It is sent with every task, so keep it small; staleness is its failure mode, and
binding the refresh to the commit is what stops it going stale.
**Done when:** `## Handoff` describes the tree as it stands after the last commit.

### 7. Report, and hand off
Show the spec, the isolation and its `branch` record, tasks completed this session, overall
progress, each task's commit and the subject recorded for it, any subject that drifted, the blocked
tasks with their reasons, the standards written, and the discoveries recorded.

**At 100%**, offer to chain straight into `/specs:conclude` (the `Skill` tool): the branch review,
the emergent `docs/`, the merge, and the archive-time distillation. Offer it once; declined → name
the command and stop. Paused → say why and wait.
**Done when:** the summary is shown and the hand-off has been offered or declined.

## Output during the loop

```
## Building: <slug>

Task 3/7 — 3.2 <task title>
  files: src/middleware/auth.ts, src/config/limits.ts
✓ verify: pnpm test middleware/ — passed
✓ self-review: clean
✓ checked 3.2 (subject: plan/<slug>: 3.2 <task title>)
✓ committed a1b2c3d — subject matches
```

## Hard rules — no exceptions, and no "just this once"

Every way a build ships a lie with a green checkbox is enumerated in
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The commit, and
each is absolute. The three whose failure is **silent and permanent**, so they are worth having in
front of you before the loop starts:

- **Never edit the `verify:` command, the test, or the assertion** so it stops failing — and never
  disable, skip, `xfail` or delete a test. Change the code, or report the task blocked.
- **Never amend or rewrite an earlier task's commit**, and never force-push. A rewritten history
  makes every earlier record a lie at once.
- **Never tick a checkbox for work that was not verified.** The box is ticked before the commit but
  only ever *after* the task verified and self-reviewed — the commit boundary moved, the proof did
  not. If nothing could verify it, say so in the report rather than implying the task was proved.

## Invariants to never violate

- Require a clean tree before the first code change; delegate isolation to `/specs:isolate`,
  recommend it, never impose it, and never reimplement it here.
- Drive off `specs.py status` / `next` / `task` and their exit codes. Never assume a path, never
  choose the next task by reading `## Tasks`, and never hand-edit a `- [ ]` / `- [x]` character.
- Verify per the spec's **declared** policy. Never decide mid-build when to test, and never ask the
  human to decide it then.
- Tick each box **after** the task verified and self-reviewed, and **before** its commit — with the
  subject that commit will carry, so code and box land together. Undo the tick if the commit fails.
- Never write a record after the commit it describes. A subject that drifted is reported, not
  corrected.
- Never refuse over a missing `approved`; ask inline and stamp it.
- Never stamp or rewrite a `branch` record here — that record belongs to `/specs:isolate`.
- Write **only** the `docs/` a task explicitly names. Emergent findings are one `specs.py discover`
  line — never an unrequested standard, and never a loose code comment.
- Delegate an executor only under §Delegating an executor (declares `files:`, touches no `docs/`,
  pinned to the session model — **never `haiku`**), and run two tasks in parallel only when
  `specs.py parallel` reports the `[P]` group eligible.
- Never review the whole branch, merge, or archive from here — that is `/specs:conclude`, and
  splitting it is what makes a half-finished build resumable.
- Keep changes minimal and scoped to each task; pause on errors, blockers, or unclear requirements
  rather than guessing.
- **Route other durable learning to its OKF home**: an insight worth keeping beyond this spec goes
  through `/docs:learn` / `/docs:add` / `/docs:define` — offered, never auto-written.
