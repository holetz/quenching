# /quenching-specs execute — 2. Take the tree, the isolation and the state in one read

Loaded only when this step runs; the flow index is [execute.md](.claude/skills/quenching-specs/references/execute.md).

**The precondition comes first.** Load the rule that binds this step:

```text
components_read(verb="read", path=".agents/quenching/references/specs-execute/execution.md", sections=["§The precondition"])
```

The rest of this step is read in **one call** — the post-merge close of whatever already merged,
the tree, the isolation ref, the spec's own state, and the environment probe below:

```text
specs_write(verb="reconcile", write=true)   # archives merged specs carrying ## Outcome
specs_read(verb="status", spec=<id>)
specs_read(verb="config")
```

```bash
git status --porcelain
git branch --list "plan/<id>-<handle>"
git branch --show-current
git worktree list
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null
# and the hook probe of 2b, in this same turn
```

`git status --porcelain` non-empty → **refuse to start**, per
[execution.md](.agents/quenching/references/specs-execute/execution.md)
§The precondition. Offer to commit or stash; do not override this precondition inside execution.

**Reserve the build before any isolation** — only the build reserves; `create`, `develop`,
`triage` and `status` never do (`/docs/standards/workflows/spec-claims.md` where the repo keeps it):

```text
specs_external(verb="claim_acquire", claim_id=<id>)
```

Exit 0 → the lease is this machine's for `shared.autonomy.claimMinutes` (45), a re-acquire by the
same machine in another session included. Exit 1 `held` → another machine is building it: **stop**
with `held-by: <heldBy.holder> until <heldBy.expires>`, cut and write nothing. Taking a live lease
(the `take` verb of `.agents/quenching/bin/cq specs claim`, run on `"<id>"`) is the human's call only, asked on a decision sheet and recorded
with `specs_write(verb="discover", spec=<id>, text="lease taken from <holder>")`; a sub-agent returns `STATE: blocked`
with `NOTE: needs-human: held-by: <holder>` and never takes. Exit 2 (git could not answer) → report
it and build without a reservation: the lease protects, and a remote that cannot answer never
blocks the build.

**Then resolve the work ref, and check before offering.** The spec's work branch is the `branch`
record's `work` when the `status` payload carries one, else `plan/<id>-<handle>` — the ref already listed.
A record naming something else costs one more `git branch --list "<work>"` to know whether it is
alive. Two outcomes end the question here:

- **This checkout is on the work ref** (`git branch --show-current` equals it) → the spec **is**
  isolated. Go straight to the loop and offer nothing.
- **The ref is alive but held elsewhere** — a `git worktree list` entry, or a checkout this one is
  not on — → it is being built somewhere else, and starting here would fork the work. Name where,
  and stop.

**A ref that merely exists is not isolation.** Anything short of being **on** the ref falls through
to the branches below.

**Resolve the base branch next**, stopping at the first that answers: the spec's own `branch.base`
record, when one already exists; else `git symbolic-ref refs/remotes/origin/HEAD` (already read
above); else `git config init.defaultBranch`, and then `main`.

**Not on the base → adopt the current branch, and skip the cut.** `git branch --show-current`
disagreeing with the resolved base means the human already answered the isolation question at
checkout. Show the inference on the same line as the confirmation, before stamping —
`base: main — inferred; this branch was not cut by this command` — and stamp:

```text
specs_write(verb="record", spec=<id>, name="branch", fields={"base": "<resolved base>", "work": "<current branch>"})
```

Never derive `base` from `git merge-base` or `--fork-point`; they answer a commit, not a branch
name.

**On the base with the work ref alive and unclaimed → take a slot over it, unasked, never a
second branch.** `git_write(verb="worktree_acquire", branch=<work ref>, base=<base>)`
switches a free slot (or a new one under `shared.worktreeSlots.max`) to the work ref, links the
declared shared paths and runs the declared `worktreeSetup` — displayed verbatim, as every cut does —
inside it. A ref already checked out in a slot returns that slot. **Nothing is stamped** — a
`branch` record, where one exists, is write-once and already true. At the ceiling the verb refuses
`git-worktree-slots-full` with each holder named: wait with `--wait`, and on
`git-worktree-slots-timeout` stop and tell the human the limit was reached — never cut a worktree
outside the slots.

**On the base branch, with nothing to check out → hand off to `/quenching-git branch`**, which
cuts the worktree from the remote base (its cost stated, `worktreeSetup`, the `branch:` record and
the branch's `quenching-specs:` marking). It is a worktree by default and asks nothing about the
form; a plain branch happens only when this run's input asked for one in the human's own words.
It is a `Skill` call, never `context: fork`:

```
Skill("quenching-git", "branch <id>")
```

When it returns, re-read the state it left:

```text
specs_read(verb="status", spec=<id>)
```

`branch.work` now set → the worktree was cut; continue the loop from the returned worktree checkout,
never from the base checkout — and carry that path on every command of the loop (`cd <worktree> &&
…` in the same call, `git -C <worktree>`, `root=<worktree>` on every `quenching` tool), because the harness may return
the shell cwd to the base checkout after each command and a cwd-dependent command would then
measure or write the wrong tree. A tool given `root=<worktree>` runs there, the `git` write verbs included. No record at all → the
git command it ran failed (a name already taken, a dirty path, a locked worktree) and nothing was
stamped — report it verbatim and stop; never fall back to a branch or the base, which is the
outcome the worktree default exists to prevent.

Not a git repo → stop before writing: this command's task/commit contract requires Git. Never force
isolation, never `git init` on the human's behalf, and never rewrite history.

**2b. Probe the environment before writing any code** — a hook wired in `.claude/settings.json`
whose script is gone fails every commit. Probe once, in the same call as the reads above, per [execution.md](.agents/quenching/references/specs-execute/execution.md)
§The hook probe. Anything other than `none` → report it before the first task, name the hook and
the missing path, and let the human decide; never `--no-verify` past it. Silent when nothing wired.

**2c. On a resume, re-run the last checked task's `verify:` before any code.** A resume is a
`status` with at least one task checked. Take the last checked task and run its `verify:` (the
`## Validation` command when it has none) from its declared `cwd:`, in the same checkout the run
builds in. Green → go on to step 3. Red → **stop**: report the task, the command and its output
and write nothing, until the cause is classified. Reproduce the failure in the base worktree
(`.quenching/red`): it reproduces there → pre-existing, and the route of **5i** applies; it does not →
the regression belongs to the task that caused it, not to the conclude gate, and nothing is fixed
here. Nothing checked yet → run the baseline once, before any code: the first task's `verify:` (the narrowest `## Validation` command when it has none), skipping a command that spends billed sessions and saying so in the report. A red there is the base's by construction (clean tree, setup already run): route **5i** directly, no `.quenching/red` worktree — unless it only names code this task itself will create, which is the task's own RED.

**Done when:** the tree is clean, the build is reserved (or stopped `held-by:`, or reported
unreserved on exit 2), the worktree (or the requested branch) has been taken or found
already held, any unresolved hook has been reported, and a resume's last checked task still
verifies.
