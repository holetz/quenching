---
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Task, Skill
---

# /quenching-specs execute — build one spec, one task at a time

**Input**: `$ARGUMENTS` — optionally a spec id. Omitted → infer from the conversation, or
auto-select when exactly one spec is under way; vague or ambiguous → you MUST prompt.

Builds the `## Tasks` of ONE spec: writing each task, verifying it under the spec's declared
policy, reviewing its diff, committing it alone, and recording the spec task after that commit.

**This command stops at the last commit.** Reviewing the whole branch, writing the `/docs/` the work
revealed, merging, and archiving belong to `/quenching-specs conclude` — the archive only after the
merge.

`Bash` is unrestricted: the verification and Git commands are resolved from the live spec. The
commit itself is one `git_write(verb="commit", subject=…, root=<worktree>)` call, which commits the worktree's existing index.

## Resolving the tool

Resolve `cq` (`components_read(verb="read")` is the section reader every `§X` citation in this body resolves through)
per [align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Select the spec
Run it from [step-1-select-the-spec.md](.claude/skills/quenching-specs/references/execute/step-1-select-the-spec.md) — read that file whole when this step starts, and not before.
**Done when:** one spec is resolved.

### 2. Take the tree, the isolation and the state in one read
Run it from [step-2-tree-isolation-state.md](.claude/skills/quenching-specs/references/execute/step-2-tree-isolation-state.md) — read that file whole when this step starts, and not before.
**Done when:** the tree is clean, the build is reserved (or stopped `held-by:`, or reported
unreserved on exit 2), the worktree (or the requested branch) has been taken or found
already held, any unresolved hook has been reported, and a resume's last checked task still
verifies.

### 3. Settle the approval, off the state step 2 already read
Run it from [step-3-settle-the-approval.md](.claude/skills/quenching-specs/references/execute/step-3-settle-the-approval.md) — read that file whole when this step starts, and not before.
**Done when:** the state is in hand, `approved` is settled, and any warning has been surfaced once.

### 4. Read what the tasks must satisfy
Run it from [step-4-read-what-tasks-satisfy.md](.claude/skills/quenching-specs/references/execute/step-4-read-what-tasks-satisfy.md) — read that file whole when this step starts, and not before.
**Done when:** the spec's sections and the declared binding standards are read.

### 5. Implement tasks — loop until done or blocked
Run it from [step-5-implement-tasks.md](.claude/skills/quenching-specs/references/execute/step-5-implement-tasks.md) — read that file whole when this step starts, and not before.
**Done when:** every task is `- [x]` or `- [!]`, or the run pauses with the reason stated.

### 6. Refresh `## Handoff` on four events, never on judgment
Run it from [step-6-refresh-handoff.md](.claude/skills/quenching-specs/references/execute/step-6-refresh-handoff.md) — read that file whole when this step starts, and not before.
**Done when:** the global block and the current section's `## Handoff` block describe the tree as
it stands after the run's last commit.

### 7. Report, and hand off
Run it from [step-7-report-and-hand-off.md](.claude/skills/quenching-specs/references/execute/step-7-report-and-hand-off.md) — read that file whole when this step starts, and not before.
**Done when:** the summary is shown and the hand-off has been offered or declined.

## Output during the loop

Progress as it happens, not a report — the mold governs step 7, this governs the loop. Its glyphs
are §The report mold's, and mean the same. **Only the mold's own header line opens with a `##` that
carries the ID** — this banner prints plain text, never a heading, so the two can never be
confused for each other:

```
Building: <id>

Task 3/7 — 3.2 <task title>
  files: src/middleware/auth.ts, src/config/limits.ts
✓ self-review: clean
✓ chain: verify && check && commit
    verify: pnpm test middleware/ — passed
    checked 3.2 (subject: plan/<id>-<handle>: 3.2 <task title>)
    committed a1b2c3d — subject matches
```

## Hard rules — no exceptions, and no "just this once"

Every way a build ships a lie with a green checkbox is enumerated in
execution.md §The commit (loaded by step 5d), and
each is absolute. The three whose failure is **silent and permanent**:

- **Never edit the `verify:` command, the test, or the assertion** so it stops failing — and never
  disable, skip, `xfail` or delete a test. Change the code, or report the task blocked.
- **Never amend or rewrite an earlier task's commit**, and never force-push.
- **Never tick a checkbox for work that was not verified.** The spec task is ticked only after
  the task was verified, self-reviewed and committed. If nothing could verify it, say so in the
  report rather than implying the task was proved.

## Invariants to never violate

- Require a clean tree before the first code change; **isolated means this checkout is ON the work
  ref**, never that the ref exists somewhere — and where it is not, cut a worktree over a live ref
  or hand off to `/quenching-git branch` to cut one. The worktree is the default and is taken
  unasked; a plain branch only when the run's input asked for it.
- Drive off `specs_read(verb="status")` / `next` / `task` and their exit codes. Never assume a path, never
  choose the next task by reading `## Tasks`, and never hand-edit a `- [ ]` / `- [x]` character.
- Verify per the spec's **declared** policy. Never decide mid-build when to test, and never ask the
  human to decide it then.
- Tick each spec task **after** its commit succeeds — with the subject and sha that commit
  actually carried. A failed spec write leaves the commit preserved and the task unchecked for
  a retry; never rebuild or amend that commit.
- Never write an ordinary record after the commit it describes. The spec task is the explicit
  post-commit exception and carries that commit's subject and sha; no later history rewrite or
  anchor repair is part of a section close.
- Never refuse over a missing `approved`; ask inline and stamp it with `specs_write(verb="record")`, never by
  editing the frontmatter. The one exception is `autonomous`, where it is a real block.
- Stamp `branch:` once the work ref is resolved, taken or declined (`work` then equals `base`) —
  never over an existing record, through `specs_write(verb="record")`, never the frontmatter.
- Write **only** the `/docs/` a task explicitly names. Emergent findings are one `specs_write(verb="discover")`
  line — never an unrequested standard, and never a loose code comment. A pre-existing error is the
  exception (5i): a declared `[fix-preexistente]` task, or a captured spec resolved `promoted: <id>`.
- Delegate an executor only under
  execution-delegation.md §Delegating an executor (loaded by step 5b) (declares `files:`, touches no `/docs/`, pinned to the session model —
  `haiku` only on a task `specs_read(verb="estimate", task=…)` reports `smallTierEligible`), and run two tasks in parallel only when `specs_read(verb="parallel")` reports the `[P]`
  group eligible.
- Never review the whole branch, merge, or archive from here — that is `/quenching-specs conclude`.
- Keep changes minimal and scoped to each task; pause on errors, blockers, or unclear requirements
  rather than guessing.
- **Route other durable learning to its OKF home**: an insight worth keeping beyond this spec goes
  through `/quenching-knowledge learn` / `/quenching-knowledge add` / `/quenching-knowledge define` — offered, never auto-written.
