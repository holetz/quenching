# /quenching-specs conclude — step 8: After the merge: archive and release the worktree

**Resuming.** Already merged → run only this step. Archived → report it closed; nothing is left.
**Under `autonomous`.** No question exists: `reconcile --write` and the worktree's release run as
written; a `needs-human` row or a refusal is reported and never forced.

This step runs only once the work is merged — a conclude resumed after the merge (the "already
merged" row of the resume signals), or right after a `low` or `autonomous` hand-off whose merge already
landed. Right after `pr-create` the PR is open, nothing here applies, and the run ends at step 9.

```text
specs_write(verb="reconcile", write=true)
```

`reconcile` is the whole archive rule and this step adds none of its own: it fetches, finds every
spec whose work is merged, and archives as `done` each one carrying `## Outcome` through the same
gate `promote` applies. A row with `action: needs-human` (`## Outcome` missing, a task still open)
is reported with its `why` and never forced.

**Then bring the local base up to the remote** — the merge moved only `origin/<base>`:
`git_write(verb="refresh")`. It is fast-forward only: it never discards a commit or an uncommitted
change and never switches a branch, and a `diverged` or `merge-refused` result is reported and left as it is, never forced.

**Then give the worktree back.** A spec built in a **slot** (`../<repo>-slot-<n>`) needs nothing
more: `reconcile` already released it in the row it archived (`slot.released`) — detached at the
remote base, unlocked, its `.venv` kept warm for the next spec. A `slot.released: false` row keeps
the slot held and carries its reason (a dirty tree, ignored files no `shared.regenerablePaths`
entry covers): report it and leave the slot standing.

A spec built in a worktree that is **not** a slot (cut before slots existed) is retired instead,
with no question and no extra flag. The recorded fact is the `branch` record (`work`, `base`) and
the worktree path from `git worktree list`; skip silently when the work was done in the base
checkout or in a plain branch. Run it from the base's checkout, never from the worktree it removes:

```text
git_write(verb="worktree_retire", path="<the spec's worktree>", branch="<branch.work>", base="<branch.base>", root="<the base's checkout>")
```

`retire` fetches the remote base, requires the branch tip to be an ancestor of it, refuses a dirty
tree, and runs `git worktree remove` and `git branch -d` without `--force`. **Never pass `--force`
or `--discard-ignored`, and never `retire` a slot** — a slot is released, never removed, except by
`/quenching-git cleanup` above the floor. A refusal is information, not an obstacle — report the
`code` or `message` it printed and leave the worktree standing; it is never retried with a stronger
flag.
