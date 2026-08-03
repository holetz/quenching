---
description: Build ONE spec task by task — write, verify, self-review, tick, commit. Triggers on "execute this spec", "build it", "implement the tasks", "apply the plan", "start working on it", "continue building", "run the next task", "work through the tasks". Requires a clean tree; delegates isolation to /specs:isolate; verifies under the spec's own declared policy; ticks each box with the subject of the commit it is about to make, so code and box land in ONE commit per task. Writes the docs/standards/ a task explicitly names, and records everything else the work reveals as a one-line discovery. Stops at the last commit — the branch review, the merge and the archive are a separate command. Not for: writing or sharpening a spec → /specs:develop; a version bump or other release obligation → /specs:conclude; creating one → /specs:create; taking a branch or worktree → /specs:isolate; reviewing the branch, merging and archiving → /specs:conclude; being told which spec to build next → /specs:continue.
argument-hint: [slug]
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Task, Skill
---

# /quenching:specs:execute — build one spec, one task at a time

**Input**: `$ARGUMENTS` — optionally a spec slug. Omitted → infer from the conversation, or
auto-select when exactly one spec is under way; vague or ambiguous → you MUST prompt.

Builds the `## Tasks` of ONE spec: writing each task, verifying it under the spec's declared
policy, reviewing its diff, and committing it alone with the box already ticked inside that commit.

**A task is not done when the code is written.** It is done when it **ran**, its diff was
**reviewed**, and it is **committed**. The mechanics of that live in
[specs-execute/execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§The precondition §The verification policy §The validation loop §The diff self-review §The commit
§Declared versus emergent `docs/` §Delegating an executor, which this body cites and never restates.

**Every `§X` below is an address, and it is loaded as one — never by opening the file.**

```bash
skills.py read <the cited file> --sections "§The verification policy" --sections "§The commit"
```

One call, N sections, no frontmatter; a unique prefix resolves, so `§The commit` is enough. The
reason is the whole of this command's own cost: a preamble is re-sent on every turn that follows
it, so what is loaded at turn one is paid for the length of the run — and `execution.md`
§The verification policy is ~400 tokens against 4,600 for the file that holds it. `--rules-only`
narrows further to the `<!-- rules -->` half where a section carries the marker, and returns the
whole section, saying so, where it does not.

**This command stops at the last commit.** Reviewing the whole branch, writing the `docs/` the work
*revealed*, merging, and archiving belong to `/quenching:specs:conclude` — [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
opens on why that split holds.

The git conventions live in
[specs-execute/git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md)
§The read-if-present rule §Branch and worktree names §Recording the isolation §Commit messages
§The subject is the anchor, whose command is `/quenching:specs:isolate`.

The spec-driven facts live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The `specs/` layout §The fourteen sections §Derived stages §The `specs.py` tool surface §Boundary.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/specs-front.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/specs-front.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

`skills.py read` — the section reader every `§X` citation above resolves through — is the same
fallback one directory over: `${CLAUDE_PLUGIN_ROOT}/assets/bin/skills.py` first, then the target's
`.claude/hooks/skills.py`. Neither resolves → read the cited file with `Read` and **say in the
report that the sections were loaded whole**.

## Workflow

### 1. Select the spec
A slug was given → use it. Otherwise infer from the conversation, auto-select when exactly one spec
is under way, or run `specs.py list --json` and pick with **AskUserQuestion**. Announce
"Building spec: `<slug>`" and how to override.
**Done when:** one spec in `plans/` is resolved.

### 2. Take the tree, the isolation and the state in one read
**The precondition comes first.** Everything this step needs is read in **one call** — the tree, the
isolation ref, the spec's own state (which step 3 reads anyway, so it is read here once), and the
environment probe below, which belongs in this same call:

```bash
git status --porcelain
git branch --list "plan/<slug>"
specs.py status --spec "<slug>" --json
# and the hook probe of 2b, in this same call
```

`git status --porcelain` non-empty → **refuse to start**, per
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§The precondition. Offer to commit or stash. The human may override; then the first commit carries
the pre-existing changes and the report says so.

**Then check before dispatching.** `branch --list plan/<slug>` printing a ref, or the `branch`
record already present in the `status` payload, means the spec **is already isolated** — go
straight to the loop and dispatch nothing. `/quenching:specs:isolate` would report the existing
branch and stamp nothing new, so the call buys nothing and costs twice: the turns, and the run's
own attribution, per
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§Isolation is somebody else's job.

**Nothing to check out → hand isolation to `/quenching:specs:isolate`** (the `Skill` tool) rather
than reimplementing it: it owns the branch and worktree forms, the `plan/<slug>` name, the
`branch: {base, work}` stamp and its write-once rule. Delegating less is not the point — checking
first is; when there is something to isolate, that command is still the only thing that takes it.

Either way, read the state before the first task: a spec whose branch is **alive but checked out
elsewhere** (`git worktree list`, or a ref this checkout is not on) is being built somewhere else,
and starting here would fork the work. Say so and stop.

Not a git repo → no isolation and no commits; say so once and run the loop normally. Never force
isolation, never `git init` on the human's behalf, and never rewrite history.

**2b. Probe the environment before writing any code.** A hook wired in `.claude/settings.json`
whose script no longer exists on disk fails *every* commit this loop makes, and it fails as a hook
error rather than as a missing file — so it gets diagnosed at the first commit, ad hoc, in about
ten calls. Ask the question once instead, in the same call as the reads above:

```bash
python3 -c "
import json, pathlib, re
p = pathlib.Path('.claude/settings.json')
d = json.loads(p.read_text()) if p.exists() else {}
cmds = [h.get('command','') for g in d.get('hooks',{}).values() for e in g for h in e.get('hooks',[])]
gone = sorted({t for c in cmds for t in re.findall(r'[\w./\$\{\}-]+\.(?:py|sh|js|ts)', c)
               if not pathlib.Path(re.sub(r'\\\$\{?CLAUDE_PROJECT_DIR\}?/?', '', t)).exists()})
print('unresolved hook targets:', gone or 'none')"
```

Anything other than `none` → **report it before the first task**, name the hook and the missing
path, and let the human decide: fix the wiring, or build knowing every commit will trip it. Never
route around it with `--no-verify`. No `.claude/settings.json`, or nothing wired → silent, and the
probe costs nothing.

**Done when:** the tree is clean (or the override is on the record), isolation has been taken,
found already held, or declined, and any unresolved hook has been reported.

### 3. Settle the approval, off the state step 2 already read
The `specs.py status --json` payload is **already in hand** from step 2 — do not read it again.
From it: the derived stage, the section states, task progress, the blocked tasks, the recorded
subjects, and **`verification`** — the spec's declared policy, which decides when the suite runs so
this command never has to.

- **`approved` unset** → ask for it inline, in one question showing what the spec commits to, and
  on a yes stamp it with `specs.py record "<slug>" approved --set date=<today>` — never by editing
  the frontmatter. **Never refuse over it** — refusing would rebuild the folder hop this front
  removed. A no ends the run cleanly.
- **`next` reports `write_section`** → the ready gate is not met. Name the missing or malformed
  sections and route to `/quenching:specs:develop <slug>`, then stop. The gate refuses nothing itself; the
  tool simply has no task to hand out until it is closed.
- **Every task already `- [x]`** → say so and offer to chain into `/quenching:specs:conclude` (step 7).
- **`[!]` blocked tasks** → name them and their reasons up front. They were tried and stopped, not
  skipped.

Mention any open `specs.py validate` warning **once** — `sp-unrefined` (nobody has interrogated
this spec), `sp-impact-uncovered` (a declared standard no task writes) — and offer
`/quenching:specs:develop` before building. Never gate on it: the ready gate is a floor, not a verdict.
**Done when:** the state is in hand, `approved` is settled, and any warning has been surfaced once.

### 4. Read what the tasks must satisfy
Ask for the `build` moment — the six sections an executor needs — never by naming them:

```bash
specs.py section "<slug>" --moment build --json
```

Branch on the payload, never the exit code. `sections[].state`, already read once in step 2, is
the same fact this call's own `absent` list repeats: a section not yet `filled` — `## Handoff`
empty on a spec's first build is the ordinary case, not a finding — is read as empty. No second
call, and no heading enumerated here to know which one that was.
The path comes from what `status` resolved; never assume filenames. `## Impact` names the
`docs/standards/` paths and the code this spec expects to touch.

Then, if the repo carries an OKF bundle (`docs/index.md` with `okf_version`), read the
`docs/standards/**.md` files the spec **declares** under `## Impact`, plus the ones the current
task's own text names — **never the folder** `docs/standards/<subject>/`, the wrong and the
expensive unit ([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§Tooling asides has the measurement). Those files are **binding contracts** for
HOW the work is built, complementing the spec's own sections (WHAT to build). A task that
contradicts one is surfaced (step 5), never silently resolved. No bundle → skip silently.

A declared bullet may carry a `§`address beside its path —
`docs/standards/automation/context-budget.md §The two caps §The per-surface ceiling`. With one,
read exactly those sections (`skills.py read <path> --sections "§A" --sections "§B"`); with none,
read the file whole, exactly as today. The default never changes: reading less is an assertion the
spec's own author wrote, never an economy the executor takes on its own.

**No mechanical net for a contract nobody declared — deliberately.** Deciding a standard governs a
task is reading, not parsing, so nothing scans the folder to net one
([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§Tooling asides has the failure modes this avoids). What covers the gap is one line at the
moment it shows up — `specs.py discover` records it while building, and `/quenching:specs:develop`
repairs `## Impact`.
**Done when:** the spec's sections and the declared binding standards are read.

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
   writes nothing under `docs/` **may** go to an executor sub-agent under
   [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
   §Delegating an executor — which also explains why this is **not** `context: fork` and leaves
   that rule untouched.

c. **Write only the `docs/` this task names.** A `docs/standards/` path declared under `## Impact`
   and named by this task is part of its deliverable — write it through the insert procedure in
   [docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md) §The frontmatter
   stamp §Updating `index.md` §Enriching the glossary §Self-check, stamp `authority` honestly, and
   self-check it against
   [docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)
   §Concept docs §Resource integrity.
   Anything else the work reveals costs one line — `specs.py discover "<slug>" "<finding>"` — and
   no authoring. The line between the two, and why it falls there, is
   [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
   §Declared versus emergent `docs/`.

d. **Self-review the task's diff** on the four items — reuse · useless defense · obvious comment ·
   dead code — and fix what it finds. This happens on the written diff, *before* the chain below,
   so what the chain commits is already the reviewed version.

e. **Then run verify, tick and commit as ONE chained call.** Decide the subject first — it follows
   [git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md) §Commit messages, or the
   target's own convention where it declares one — and put it in both places it appears:

   ```bash
   <the task's verify:> \
     && specs.py task --check <id> --spec "<slug>" --subject "plan/<slug>: <id> <title>" \
     && git add <the task's declared files> <the spec file> \
     && git commit -m "plan/<slug>: <id> <title>" \
     && git log -1 --format=%s
   ```

   **The `&&` is the ordering**, not a shortcut around it. Every guarantee the four separate acts
   carried is still enforced, and now mechanically rather than by the body being obeyed in sequence:
   verify precedes the tick, the tick precedes the commit so the box travels *inside* the commit
   that implements it, and any link failing short-circuits every link after it. Run `verify:` only
   when the spec's declared policy says this task is a gate ([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
   §The verification policy); otherwise the chain starts at `specs.py task`.

f. **Read the chain's tail, and act on which link broke:**

   - **`verify:` failed** → nothing was ticked and nothing was committed; the chain stopped at link
     one. Read the failure, change the code, run it again. When attempts stop converging, write it
     blocked with its reason — `specs.py task --spec "<slug>" --block <id> --reason "<why>"` — and
     move on. **Never weaken the check to make it pass.**
   - **The commit failed** — a rejecting hook, nothing staged — → the tick already landed, so
     **undo it** (`specs.py task --spec "<slug>" --uncheck <id>`) so no box claims a commit that
     does not exist, then report the failure. Never `--no-verify` your way past it.
   - **The final `git log -1 --format=%s` does not equal the recorded subject** → a `commit-msg`
     hook rewrote it. One that only *adds* (a ticket prefix, a `Change-Id`, a sign-off) leaves the
     recorded subject resolvable as a substring — fine, and needs nothing. One that **replaces** it
     breaks the task→commit link: **report it as a finding and write nothing.** Editing the record
     now would put a write after the commit again, which is exactly what this ordering removed.

g. **On a section boundary, OFFER to stop — and keep going if nobody says otherwise.** The event
   is exact and needs no threshold: the last task of a `## N.` section just committed, and another
   section is still ahead. Say it in one line and continue:

   ```
   Section 3 of 7 done, at a clean boundary. `/quenching:specs:execute <slug>` resumes from here —
   say the word and I stop; otherwise I continue with 4.1.
   ```

   It **offers and never imposes**, never ends the run itself, and writes no state — the trail that
   makes the boundary resumable is the one step 6 already keeps. Why the trigger is that event and
   never a window size, and why a section is the unit, live in
   [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The section boundary.

**Pause if:** a task is unclear; implementation reveals a design problem (→ `/quenching:specs:develop`); a
task contradicts a `docs/standards/` contract (surface it and let the human pick — revise the
standard via `/quenching:docs:add`, or the spec via `/quenching:specs:develop`); attempts stop converging; or the user
interrupts.
**Done when:** every task is `- [x]` or `- [!]`, or the run pauses with the reason stated.

### 6. Refresh `## Handoff` on four events, never on judgment
Rewrite `## Handoff` to the state of play a fresh executor would need **and cannot derive** — on
exactly four events:

- the run **pauses**;
- a task is written **blocked**;
- a **discovery** is recorded;
- the run's **last commit** lands.

Everything a resumed run *can* derive — which tasks are done, which commit carried each — is
already in `git log` and in the `subjects` `status` returns, so the Handoff is not the resumption
trail and must not be rewritten as one. It is sent with every task, so keep it small.

**Not after every committed task, and not on a judgment call either** — both were tried and both
failed;
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The Handoff cadence
has the measurement. Each trigger above is a moment this body *just finished doing
something*, never one where it appraises something.

**The section-boundary offer (step 5g) adds no fifth event and writes no new state.** Accepted, it is a
pause and a last commit, which are already two of the four above; declined, nothing happened worth
recording. The trail this step already maintains — `## Handoff` plus `git log` plus the `subjects`
`status` returns — **is** what makes a fresh session resume from that boundary, and it is exactly
why stopping there is nearly free. An offer that required writing something extra would be moving
cost rather than cutting it.
**Done when:** `## Handoff` describes the tree as it stands after the run's last commit.

### 7. Report, and hand off
Show the spec, the isolation and its `branch` record, tasks completed this session, overall
progress, each task's commit and the subject recorded for it, any subject that drifted, the blocked
tasks with their reasons, the standards written, and the discoveries recorded.

**At 100%**, offer to chain straight into `/quenching:specs:conclude` (the `Skill` tool): the branch review,
the emergent `docs/`, the merge, and the archive-time distillation. Offer it once; declined → name
the command and stop. Paused → say why and wait.
**Done when:** the summary is shown and the hand-off has been offered or declined.

## Output during the loop

```
## Building: <slug>

Task 3/7 — 3.2 <task title>
  files: src/middleware/auth.ts, src/config/limits.ts
✓ self-review: clean
✓ chain: verify && check && commit
    verify: pnpm test middleware/ — passed
    checked 3.2 (subject: plan/<slug>: 3.2 <task title>)
    committed a1b2c3d — subject matches
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

- Require a clean tree before the first code change; **check whether the spec is already isolated
  before dispatching**, and where it is not, delegate isolation to `/quenching:specs:isolate` —
  recommend it, never impose it, and never reimplement it here. Checking first is not delegating
  less.
- Drive off `specs.py status` / `next` / `task` and their exit codes. Never assume a path, never
  choose the next task by reading `## Tasks`, and never hand-edit a `- [ ]` / `- [x]` character.
- Verify per the spec's **declared** policy. Never decide mid-build when to test, and never ask the
  human to decide it then.
- Tick each box **after** the task verified and self-reviewed, and **before** its commit — with the
  subject that commit will carry, so code and box land together. Undo the tick if the commit fails.
- Never write a record after the commit it describes. A subject that drifted is reported, not
  corrected.
- Never refuse over a missing `approved`; ask inline and stamp it with `specs.py record`, never by
  editing the frontmatter.
- Never stamp or rewrite a `branch` record here — that record belongs to `/quenching:specs:isolate`.
- Write **only** the `docs/` a task explicitly names. Emergent findings are one `specs.py discover`
  line — never an unrequested standard, and never a loose code comment.
- Delegate an executor only under
  [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
  §Delegating an executor (declares `files:`, touches no `docs/`, pinned to the session model —
  **never `haiku`**), and run two tasks in parallel only when `specs.py parallel` reports the `[P]`
  group eligible.
- Never review the whole branch, merge, or archive from here — that is `/quenching:specs:conclude`, and
  splitting it is what makes a half-finished build resumable.
- Keep changes minimal and scoped to each task; pause on errors, blockers, or unclear requirements
  rather than guessing.
- **Route other durable learning to its OKF home**: an insight worth keeping beyond this spec goes
  through `/quenching:docs:learn` / `/quenching:docs:add` / `/quenching:docs:define` — offered, never auto-written.
