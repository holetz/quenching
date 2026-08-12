---
description: Build ONE spec task by task — write, verify, self-review, tick, commit. Triggers on "execute this spec", "build it", "implement the tasks", "apply the plan", "start working on it", "continue building", "run the next task", "work through the tasks". Requires a clean tree; offers isolation inline; verifies under the spec's own declared policy; ticks each box with the subject of the commit it is about to make, so code and box land in one commit per task, squashed into one commit per section at that section's own boundary. Writes the /.docs/standards/ a task explicitly names, and records everything else the work reveals as a one-line discovery. Stops at the last commit — the branch review, the merge and the archive are a separate command. Not for: writing or sharpening a spec → /quenching:specs:develop; a version bump or other release obligation → /quenching:specs:conclude; creating one → /quenching:specs:create; reviewing the branch, merging and archiving → /quenching:specs:conclude; being told which spec to build next → /quenching:specs:continue.
argument-hint: [slug]
allowed-tools: Bash, Read, Glob, Grep, Write, Edit, AskUserQuestion, Task, Skill
model: sonnet
---

# /quenching:specs:execute — build one spec, one task at a time

**Input**: `$ARGUMENTS` — optionally a spec slug. Omitted → infer from the conversation, or
auto-select when exactly one spec is under way; vague or ambiguous → you MUST prompt.

Builds the `## Tasks` of ONE spec: writing each task, verifying it under the spec's declared
policy, reviewing its diff, and committing it alone with the box already ticked inside that commit.

**A task is not done when the code is written.** It is done when it **ran**, its diff was
**reviewed**, and it is **committed**.

**Every `§X` in this body is an address, and it is loaded as one — never by opening the file.**
The example uses `§A` / `§B` as placeholders — they are not addresses.

```bash
cq components read <the cited file> --sections "§A" --sections "§B"
```

One call, N sections, no frontmatter; a unique prefix resolves, so `§B` is enough. The reason is
this command's own cost: a preamble is re-sent every turn that follows it, so what is loaded at
turn one is paid for the length of the run — a section runs ~400 tokens against 4,600 for the
file that holds it. `--rules-only` narrows to the `<!-- rules -->` half where a section carries
the marker, and returns the whole section, saying so, where it does not.

**This command stops at the last commit.** Reviewing the whole branch, writing the `/.docs/` the work
*revealed*, merging, and archiving belong to `/quenching:specs:conclude` — [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
opens on why that split holds.

## Resolving the tool

Resolve `cq` (`cq components read` is the section reader every `§X` citation in this body resolves through)
per [align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## Workflow

### 1. Select the spec
A slug was given → use it. Otherwise infer from the conversation, auto-select when exactly one spec
is under way, or run `cq specs list --json` and pick with **AskUserQuestion**. Announce
"Building spec: `<slug>`" and how to override.
**Done when:** one spec in `plans/` is resolved.

### 2. Take the tree, the isolation and the state in one read
**The precondition comes first.** Load the rule that binds this step:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md \
  --sections "§The precondition"
```

The rest of this step is read in **one call** — the tree, the isolation ref, the spec's own state
(step 3 reads it anyway, so it is read here once), and the environment probe below:

```bash
git status --porcelain
git branch --list "plan/<slug>"
git branch --show-current
git worktree list
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null
cq specs status --spec "<slug>" --json
cq specs config --json
# and the hook probe of 2b, in this same call
```

`git status --porcelain` non-empty → **refuse to start**, per
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§The precondition. Offer to commit or stash. The human may override; then the first commit carries
the pre-existing changes and the report says so.

**Then resolve the work ref, and check before offering.** The spec's work branch is the `branch`
record's `work` when the `status` payload carries one, else `plan/<slug>` — the ref already listed.
A record naming something else costs one more `git branch --list "<work>"` to know whether it is
alive. Two outcomes end the question here:

- **This checkout is on the work ref** (`git branch --show-current` equals it) → the spec **is**
  isolated. Go straight to the loop and offer nothing; asking again buys nothing and costs the
  turns it takes.
- **The ref is alive but held elsewhere** — a `git worktree list` entry, or a checkout this one is
  not on — → it is being built somewhere else, and starting here would fork the work. Name where,
  and stop.

**A ref that merely exists is not isolation.** Standing on the base with the work ref sitting
unclaimed one branch over, a short-circuit on its *existence* would send the loop to build and
commit onto the base itself — the exact outcome the offer exists to prevent, reached by skipping
it. Anything short of being **on** the ref falls through to the branches below.

**Resolve the base branch next**, stopping at the first that answers: the spec's own `branch.base`
record, when one already exists; else the repo's own declared `integrationBranch` (already read
above, from `cq specs config --json`); else `git symbolic-ref refs/remotes/origin/HEAD` (already
read above); else `git config init.defaultBranch`, and then `main`. **The declared integration
branch is consulted before `origin/HEAD`, never after** — under the develop/main flow
(`git/branching.md`) `origin/HEAD` resolves to `main`, the publication branch, and falling through
to it first would merge an unstamped spec there by default. Left undeclared, this step answers
nothing and the chain is exactly as it was.

**Not on the base → adopt the current branch, and skip the offer.** `git branch --show-current`
disagreeing with the resolved base means the human already answered the isolation question at
checkout. Show the inference on the same line as the confirmation, before stamping —
`base: main — inferred; this branch was not cut by this command` — and stamp:

```bash
cq specs record "<slug>" branch --set base=<resolved base> --set work=<current branch>
```

Never derive `base` from `git merge-base` or `--fork-point` here: both answer a commit, not a
branch name, and a commit ancestral to three branches identifies none of them.

**On the base with the work ref alive and unclaimed → offer to take it, never to cut a second
one.** Two forms, worktree first as always: `git worktree add ../<repo>-<slug> <work ref>` beside
this checkout, or `git checkout <work ref>` in it. **Nothing is stamped** — a `branch` record, where
one exists, is write-once and already true, and a ref cut by hand with no record is the case
`base` cannot honestly be inferred for from here. Declining leaves the run on the base; say plainly
that the commits will land there.

**On the base branch, with nothing to check out → offer isolation here, inline.** Load the rules
that name the branch and record the isolation, then read what the workspace declares:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md \
  --sections "§Branch and worktree names" --sections "§Recording the isolation"
cq specs config --json        # `worktreeSetup`, or null — exit 0 either way
```

State in one block: the spec, the base branch, the branch name that will be created, the worktree
path, what will be stamped, and — when `worktreeSetup` is non-null — **the setup command verbatim**,
exactly as read, never paraphrased or reformatted. **That block is the consent.** Choosing
**Worktree** IS the OK for the command shown, and there is no second prompt and no remembered
"this repo is authorised" state: the human judges the command on the same screen where they choose
the form. Nothing declared → say nothing; an absent config is the normal case, not a finding.

Then ask with **AskUserQuestion**:

- **Worktree** *(default, recommended)* — `git worktree add ../<repo>-<slug> -b plan/<slug>`, a
  separate checkout beside the repo, leaving this one untouched. State its cost **in the offer**:
  a fresh checkout carries only what git tracks — no `node_modules/`, no `.venv/`, no `.env`, no
  build output — so a repo with installed dependencies needs them installed again there;
- **Branch** — `git checkout -b plan/<slug>`, work continues in this checkout;
- **In place** — declines isolation. Nothing is created and **nothing is stamped**.

Worktree leads **unconditionally** — never on a heuristic that sniffs the target for
`package.json` or `.venv/`. A recommendation that changes from repo to repo cannot be documented in
one sentence, and guessing somebody else's build is how the recommended path becomes a silent trap.
The cost above is stated instead, so choosing **Branch** is a decision the human read rather than a
discovery at the first `verify:` that fails.

Run the one command for the chosen form. If it fails — a name already taken, a dirty path, a locked
worktree — report the git error verbatim and stop without stamping. **Then, on a worktree with a
`worktreeSetup` declared**, run it once with **cwd inside the new worktree**, which is the whole
point: it is the tree that lacks the dependencies. Report its output and its exit code. **A failing
setup does not undo the worktree** — say plainly which of the two it is, and report a command whose
first token does not resolve inside the worktree as not run, for that reason, rather than executing
it and blaming the shell.

Then stamp what was taken:

```bash
cq specs record "<slug>" branch --set base=<what was checked out> --set work=plan/<slug>
```

`base` is captured **now**, while it is still true: after the merge git cannot say what the branch
was cut from, which is the whole reason the record exists. The record is write-once and the tool
enforces it — one already present refuses (exit 2) naming the value it holds. **Read it, never
rewrite it**, and never edit the frontmatter to get past the refusal. Stamp nothing for work done
in place, because a record whose `base` equals its `work` states no fact.

Recommend isolation before building, and never impose it. A human who declines gets no branch, no
record, and no second prompt.

Not a git repo → no isolation and no commits; say so once and run the loop normally. Never force
isolation, never `git init` on the human's behalf, and never rewrite history.

**2b. Probe the environment before writing any code.** A hook wired in `.claude/settings.json`
whose script no longer exists on disk fails *every* commit this loop makes — probe once, in the
same call as the reads above, per [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§The hook probe. Anything other than `none` → report it before the first task, name the hook and
the missing path, and let the human decide; never `--no-verify` past it. Silent when nothing wired.

**Done when:** the tree is clean (or the override is on the record), isolation has been taken,
found already held, or declined, and any unresolved hook has been reported.

### 3. Settle the approval, off the state step 2 already read
**Load the stage ladder first** — what the derived stage names and means:

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§Derived stages"
```

The `cq specs status --json` payload is **already in hand** from step 2 — do not read it again.
From it: the derived stage, the section states, task progress, the blocked tasks, the recorded
subjects, and **`verification`** — the spec's declared policy, which decides when the suite runs so
this command never has to.

- **`approved` unset** → ask for it inline, in one question showing what the spec commits to, and
  on a yes stamp it with `cq specs record "<slug>" approved --set date=<today>` — never by editing
  the frontmatter. **Never refuse over it** — refusing would rebuild the folder hop this front
  removed. A no ends the run cleanly.
- **`next` reports `write_section`** → the ready gate is not met. Name the missing or malformed
  sections and route to `/quenching:specs:develop <slug>`, then stop. The gate refuses nothing itself; the
  tool simply has no task to hand out until it is closed.
- **Every task already `- [x]`** → say so and offer to chain into `/quenching:specs:conclude` (step 7).
- **`[!]` blocked tasks** → name them and their reasons up front. They were tried and stopped, not
  skipped.

Mention any open `cq specs validate` warning **once** — `sp-unrefined` (nobody has interrogated
this spec), `sp-impact-uncovered` (a declared standard no task writes) — and offer
`/quenching:specs:develop`. Never gate on it: the ready gate is a floor, not a verdict.
**Done when:** the state is in hand, `approved` is settled, and any warning has been surfaced once.

### 4. Read what the tasks must satisfy
Ask for the `build` moment — the six sections an executor needs — never by naming them:

```bash
cq specs section "<slug>" --moment build --json
```

Branch on the payload, never the exit code. `sections[].state`, already read once in step 2, is
the same fact this call's own `absent` list repeats: a section not yet `filled` — `## Handoff`
empty on a spec's first build is the ordinary case, not a finding — is read as empty. No second
call, and no heading enumerated here to know which one that was.
The path comes from what `status` resolved; never assume filenames. `## Impact` names the
`/.docs/standards/` paths and the code this spec expects to touch.

Then, if the repo carries an OKF bundle (`/.docs/index.md` with `okf_version`), read the
`/.docs/standards/**.md` files the spec **declares** under `## Impact`, plus the ones the current
task's own text names — **never the folder** `/.docs/standards/<subject>/`, the wrong and the
expensive unit ([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§Tooling asides has the measurement). Those files are **binding contracts** for
HOW the work is built, complementing the spec's own sections (WHAT to build). A task that
contradicts one is surfaced (step 5), never silently resolved. No bundle → skip silently.

A declared bullet may carry a `§`address beside its path — `/.docs/standards/automation/skills.md
§Invocation and permission are authored decisions §The admission criterion`. With one, read
exactly those sections (`cq components read <path> --sections "§A" --sections "§B"`); with none,
read the file whole, exactly as today. The default never changes: reading less is an assertion the
spec's own author wrote, never an economy the executor takes on its own.

**No mechanical net for a contract nobody declared — deliberately.** Deciding a standard governs a
task is reading, not parsing, so nothing scans the folder to net one
([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
§Tooling asides has the failure modes this avoids). What covers the gap is one line at the
moment it shows up — `cq specs discover` records it while building, and `/quenching:specs:develop`
repairs `## Impact`.
**Done when:** the spec's sections and the declared binding standards are read.

### 5. Implement tasks — loop until done or blocked
Ask the tool for the next task; **never pick one by reading the file**:
```bash
cq specs next --spec "<slug>" --json
```
It returns that task's `verify`, `files`, `pattern` and `parallel`, plus the spec's `verification`
policy, and it **skips `[!]` blocked tasks** (`action: "blocked"` once every remaining task is).
Then, for that task:

a. **Show what is being worked on** — the id, its declared `files:` and its `verify:`.

b. **Write the code**, minimal and scoped to the declared files. A task that declares `files:` and
   writes nothing under `/.docs/` **may** go to an executor sub-agent under
   [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
   §Delegating an executor — which also explains why this is **not** `context: fork` and leaves
   that rule untouched; when it is, load the rules that bound it before dispatching:

   ```bash
   cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md \
     --sections "§Delegating an executor"
   ```

c. **Write only the `/.docs/` this task names.** When this task writes `/.docs/`, load the rule that
   draws the line between declared and emergent, and the boundary it crosses:

   ```bash
   cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md \
     --sections "§Declared versus emergent"
   cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
     --sections "§Boundary"
   ```

   A `/.docs/standards/` path declared under `## Impact` and named by this task is part of its
   deliverable — written through the insert procedure in
   [knowledge-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-add/homes.md) §The frontmatter
   stamp §Updating `index.md` §Enriching the glossary §Self-check; stamp `authority` honestly and
   self-check against [knowledge-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/knowledge-align/conformance.md)
   §Concept docs §Resource integrity. Anything else the work reveals costs one line —
   `cq specs discover "<slug>" "<finding>"` — and no authoring.

d. **On the first pass through 5d–5e, load the rules the chain runs under — once, never per
   task.** The verification policy, the validation loop, the self-review, the commit's hard rules,
   the section squash; then the git conventions that name the subject — one call per file:

   ```bash
   cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md \
     --sections "§The verification policy" --sections "§The validation loop" \
     --sections "§The diff self-review" --sections "§The commit" --sections "§The section squash"
   cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md \
     --sections "§The read-if-present rule" --sections "§Commit messages" --sections "§The subject is the anchor"
   ```

   **Self-review the task's diff** on the four items — reuse · useless defense · obvious comment ·
   dead code — and fix what it finds, on the written diff, *before* the chain below, so what the
   chain commits is already the reviewed version.

e. **Then run verify, tick and commit as ONE chained call.** Decide the subject first — it follows
   [git.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/git.md) §Commit messages, or the
   target's own convention where it declares one — and put it in both places it appears:

   ```bash
   <the task's verify:> \
     && cq specs task --check <id> --spec "<slug>" --subject "plan/<slug>: <id> <title>" \
     && git add <the task's declared files> <the spec file> \
     && git commit -m "plan/<slug>: <id> <title>" \
     && git log -1 --format=%s
   ```

   **The `&&` is the ordering**, not a shortcut around it. Every guarantee the four separate acts
   carried is still enforced, and now mechanically rather than by the body being obeyed in sequence:
   verify precedes the tick, the tick precedes the commit so the box travels *inside* the commit
   that implements it, and any link failing short-circuits every link after it. Run `verify:` only
   when the spec's declared policy says this task is a gate ([execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
   §The verification policy); otherwise the chain starts at `cq specs task`.

f. **Read the chain's tail, and act on which link broke** — per §The commit, already loaded in
   5d: `verify:` failed → nothing ticked, nothing committed; fix and retry, or block it when
   attempts stop converging. The commit failed → undo the tick, report. The recorded subject
   drifted → report it as a finding and write nothing.

g. **Announce the declared hook for this event, and move on.** Once the task has committed,
   `after_specs_execute_task` has fired: print what the config declared for it — the event's
   name, the declared command, and the prompt whoever executes the hook must follow — then move
   on. Announcing is not executing: never invoke the declared command, never wait for it, never
   integrate its result. The step-2 read already filtered `enabled: false` hooks out, so this
   announces exactly what the read returned, whether or not the hook was written for this repo
   (`automation/extension-points.md` §The body announces — name, command and prompt — and moves
   on):

   ```text
   after_specs_execute_task — declared hook: /my:security-review
     prompt: none declared
   ```

h. **On a section boundary with no `[!]`, squash and repair** — per §The section squash, loaded once alongside 5d:

   ```bash
   git reset --soft <the commit immediately BEFORE this section's first task> \
     && git commit -m "plan/<slug>: <N> <section title>"
   cq specs task --check <id> --spec "<slug>" --subject "plan/<slug>: <N> <section title>"   # per task
   ```

   A `[!]` in the section skips both calls whole; a failed squash reports as a finding and leaves
   the per-task commits untouched.

i. **On a section boundary, OFFER to stop — and keep going if nobody says otherwise.** The branch
   is already at its final shape (one commit), another section still ahead. Say it and continue:

   ```
   Section 3 of 7 done, at a clean boundary. `/quenching:specs:execute <slug>` resumes from here —
   say the word and I stop; otherwise I continue with 4.1.
   ```

   It **offers and never imposes**, never ends the run itself, and writes no state — the trail that
   makes the boundary resumable is the one step 6 already keeps. Why the trigger is that event, and
   why a section is the unit, live in [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The section boundary.

**Pause if:** a task is unclear; implementation reveals a design problem (→ `/quenching:specs:develop`); a
task contradicts a `/.docs/standards/` contract (surface it and let the human pick — revise the
standard via `/quenching:knowledge:add`, or the spec via `/quenching:specs:develop`); attempts stop converging; or the user
interrupts.
**Done when:** every task is `- [x]` or `- [!]`, or the run pauses with the reason stated.

### 6. Refresh `## Handoff` on four events, never on judgment
Rewrite the **relevant block** of `## Handoff` to the state of play a fresh executor would need
**and cannot derive** — on exactly four events:

- the run **pauses**;
- a task is written **blocked**;
- a **discovery** is recorded;
- the run's **last commit** lands.

`## Handoff` is a small evergreen **global block** plus one block per `## Tasks` `### N.` section.
A rewrite touches ONE of the two — never both, never a closed section's:

```bash
cq specs section "<slug>" Handoff --write --scope global   # the evergreen block
cq specs section "<slug>" Handoff --write --scope current  # the block of the open section
```

Everything a resumed run *can* derive — which tasks are done, which commit carried each — is
already in `git log` and in the `subjects` `status` returns, so the Handoff is not the resumption
trail and must not be rewritten as one. The global block plus the current section's block are sent
with every task, so keep both small — a section's block, once its last task commits, is never
targeted again: `--scope current` always resolves to whichever section still has open work, so
closing costs nothing extra and adds no event of its own.

**Not after every committed task, and not on a judgment call either** — both were tried and both
failed;
[execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The Handoff cadence
has the measurement. Each trigger above is a moment this body *just finished doing
something*, never one where it appraises something.

**The section-boundary offer (step 5h) adds no fifth event and writes no new state.** Accepted, it is a
pause and a last commit, which are already two of the four above; declined, nothing happened worth
recording. The trail this step already maintains — `## Handoff` plus `git log` plus the `subjects`
`status` returns — **is** what makes a fresh session resume from that boundary, and it is exactly
why stopping there is nearly free. An offer that required writing something extra would be moving
cost rather than cutting it.
**Done when:** the global block and the current section's `## Handoff` block describe the tree as
it stands after the run's last commit.

### 7. Report, and hand off

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. The single-spec header line carries overall progress; three body blocks:

1. **This session** — fixed. The isolation and its `branch` record, tasks completed, each task's
   commit and the subject recorded for it, and any subject that drifted.
2. **Blocked** — optional. Each blocked task with its reason.
3. **Written along the way** — optional. The standards written, and the discoveries recorded,
   **quoted** as `/quenching:specs:develop` quotes them: the same artifact is owed the same fidelity
   whichever command wrote it.

Close on §The next-step block, its recommended line carrying **this spec's slug**:
`/quenching:specs:conclude <slug>` at 100%, `/quenching:specs:execute <slug>` when the run paused
mid-plan.

**At 100%**, after the block, offer once to chain straight into `/quenching:specs:conclude` (the `Skill` tool, which takes
the registry name): the branch review,
the emergent `/.docs/`, the merge, and the archive-time distillation. Declined → the block already
named the command, so stop. Paused → say why and wait.
**Done when:** the summary is shown and the hand-off has been offered or declined.

## Output during the loop

Progress as it happens, not a report — the mold governs step 7, this governs the loop. Its glyphs
are §The report mold's, and mean the same. **Only the mold's own header line opens with a `##` that
carries the slug** — this banner prints plain text, never a heading, so the two can never be
confused for each other:

```
Building: <slug>

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

- Require a clean tree before the first code change; **isolated means this checkout is ON the work
  ref**, never that the ref exists somewhere — and where it is not, offer isolation inline (taking
  a live ref, or cutting one), recommend it, and never impose it. Checking the right thing is what
  keeps the offer from being asked twice *and* from being skipped onto the base.
- Drive off `cq specs status` / `next` / `task` and their exit codes. Never assume a path, never
  choose the next task by reading `## Tasks`, and never hand-edit a `- [ ]` / `- [x]` character.
- Verify per the spec's **declared** policy. Never decide mid-build when to test, and never ask the
  human to decide it then.
- Tick each box **after** the task verified and self-reviewed, and **before** its commit — with the
  subject that commit will carry, so code and box land together. Undo the tick if the commit fails.
- Never write a record after the commit it describes. A subject that drifted is reported, not
  corrected.
- Never refuse over a missing `approved`; ask inline and stamp it with `cq specs record`, never by
  editing the frontmatter.
- Stamp `branch:` only when isolation was actually taken, and never over an existing record —
  through `cq specs record`, never by editing the frontmatter.
- Write **only** the `/.docs/` a task explicitly names. Emergent findings are one `cq specs discover`
  line — never an unrequested standard, and never a loose code comment.
- Delegate an executor only under
  [execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md)
  §Delegating an executor (declares `files:`, touches no `/.docs/`, pinned to the session model —
  **never `haiku`**), and run two tasks in parallel only when `cq specs parallel` reports the `[P]`
  group eligible.
- Never review the whole branch, merge, or archive from here — that is `/quenching:specs:conclude`, and
  splitting it is what makes a half-finished build resumable.
- Keep changes minimal and scoped to each task; pause on errors, blockers, or unclear requirements
  rather than guessing.
- **Route other durable learning to its OKF home**: an insight worth keeping beyond this spec goes
  through `/quenching:knowledge:learn` / `/quenching:knowledge:add` / `/quenching:knowledge:define` — offered, never auto-written.
