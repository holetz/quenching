# /quenching-specs execute — step 5 d–e

Loaded only when this sub-step runs, together with the step 5 loop in [step-5-implement-tasks.md](.agents/skills/quenching-specs/references/specs-execute/step-5-implement-tasks.md); the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

d. **On the first pass through 5d–5e, load the rules the chain runs under — once, never per
   task.** The verification policy, the validation loop, the self-review, and the commit's hard rules;
   then the git conventions that name the subject — one call per file:

   ```text
   components_read(verb="read", path=".agents/quenching/references/specs-execute/execution.md", sections=["§The verification policy", "§The validation loop", "§The diff self-review", "§The commit"])
   components_read(verb="read", path=".agents/quenching/references/git/conventions.md", sections=["§The declared-directive layer", "§The read-if-present rule"])
   git_read(verb="conventions")
   components_read(verb="read", path=".agents/quenching/references/git/commit.md", sections=["§Commit messages", "§The subject is the anchor"])
   components_read(verb="read", path=".agents/quenching/references/git/isolation.md", sections=["§Marking the branch with the specs it built"])
   ```

   **Self-review the task's diff** on the four items — reuse · useless defense · obvious comment ·
   dead code — and fix what it finds, on the written diff, *before* the chain below, so what the
   chain commits is already the reviewed version.

e. **Then verify, stage, commit and confirm the spec task as ONE chained operation.**
   The subject is the one the declared-directive layer's table and
   [commit.md](.agents/quenching/references/git/commit.md) §Commit messages
   §The subject is the anchor name, resolved from what 5d already loaded — never reload
   `/quenching-git commit` per task. Execute stages only the task's declared files, commits that
   index with `git_write(verb="commit", root=<worktree>)`, which never stages, amends or skips hooks, only after
   the shell half exited 0, then sends the subject and sha it reports to `specs_write(verb="task")`:

   ```bash
   cd <worktree> \
     && <the task's verify:> \
     && git add <the task's declared files>
   ```

   ```text
   git_write(verb="commit", subject="<subject>", root="<worktree>")
   specs_write(verb="task", spec=<spec-id>, action="check", task=<task-id>, subject="<subject the commit reported>", commit="<sha the commit reported>")
   ```

   **The `verify:` runs with no pipe, or under `set -o pipefail`:** the exit that gates the chain is
   the command's own, never a `tail` or `head` stage's; shorten the output when reading it.

   **The ordering remains explicit:** verify precedes staging, staging precedes the
   commit, and the spec tick follows the commit. Any failure stops the operation. A commit that
   already succeeded is preserved when the spec write fails; report its sha and retry
   `specs_write(verb="task", action="check")` without rebuilding or amending it. Run `verify:` only
   when the spec's declared policy says this task is a gate ([execution.md](.agents/quenching/references/specs-execute/execution.md)
   §The verification policy); otherwise the chain starts at `git add`. A task with
   **no `files:` declared** — the line absent, or `files: []` — has no diff to commit, so its
   chain *ends* at the tick, run without `subject` or `commit`, and with neither `git add` nor
   the commit. **A task that runs generators writes files, so it declares their outputs in `files:`**; with `files: []` the spec-verifier fails the scope of whatever it wrote. A `branch:` record also gets the branch marked, per the rule loaded in 5d.

   **After every tick, renew the reservation:** `specs_external(verb="claim_renew", claim_id=<id>)`. Exit 0 or
   `reason: absent` (no reservation was taken in step 2) → go on; exit 2 → report it and go on.
   `reason: not-holder` → another machine took the lease: **stop** with `held-by: <holder>`, the
   commit already made kept.
