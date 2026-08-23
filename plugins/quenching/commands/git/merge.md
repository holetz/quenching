---
description: >-
  Merge a branch home into its base — one of four strategies, offered and never chosen for the
  human, run in the checkout that already holds the base and never by `git checkout`ing it. Use
  when the user asks to "merge this branch", "land this work", "merge it into develop/main", or
  "bring this branch home". Given a spec id it stamps the write-once `merge:` record and removes
  the worktree afterward. Not for: opening a pull request first → /quenching:git:pr:create; pruning
  branches already merged → /quenching:git:cleanup.
 argument-hint: [id-or-branch]
allowed-tools: Bash(git worktree:*), Bash(git merge:*), Bash(git rebase:*), Bash(git branch:*), Bash(python3:*), Read, AskUserQuestion
---

# /quenching:git:merge — bring a branch home, on the human's own strategy

**Input**: `$ARGUMENTS` — a spec id (its `branch.work`/`branch.base` records name the branch and
target) or a bare branch name to merge into the resolved base. Omitted → ask.

The four strategies, the squash caveat and the post-merge worktree removal are owned by
[git/merge.md](${CLAUDE_PLUGIN_ROOT}/assets/references/git/merge.md), cited below rather than
restated.

## Workflow

### 1. Load the rules and resolve branch, base and checkout
```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git/merge.md \
  --sections "§Merge strategies" --sections "§The squash caveat" \
  --sections "§The worktree is removed after a successful merge"
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git base --json
git worktree list --porcelain
```
An ID in `$ARGUMENTS` → `cq specs status --spec "<id>" --json`, its `branch.work` is the branch
to merge and `branch.base` the target (falling back to `cq git base`'s answer where absent). A bare
branch name → merge it into `cq git base`'s answer. No checkout in the worktree list holds the base
→ **stop without merging**, naming the base and the fix (check it out, or add a worktree of it).
**Done when:** the branch, the base, and the checkout that holds it are all resolved, or the run has
stopped for lack of one.

### 2. Offer the strategy, and the branch's fate under squash
Show the trade in one line each, from §Merge strategies, and ask with **AskUserQuestion**:

- **merge commit** *(default)* — every per-section commit stays on the base, one extra commit.
- **squash** — one commit on the base; the per-section commits survive only on the branch itself.
- **rebase** — linear history, per-section commits preserved through the rewrite.
- **fast-forward** — nothing rewritten or added; only possible when the base has not moved.

**Squash chosen → offer, separately, not to delete the branch** — deleting it strands every commit
subject the archived record resolves against. **Done when:** the strategy is chosen, and, under
squash, whether the branch survives is decided too.

### 3. Run it in the base's own checkout
```bash
git -C <the checkout from step 1> <the chosen strategy's command>
```
Never `git checkout <base>` — from inside a worktree it fails outright
(`fatal: '<base>' is already used by worktree at …`, exit 128), which is exactly the isolation this
plugin recommends. A failure is reported verbatim; nothing downstream runs. **Done when:** the
merge command exits 0, or the run has stopped on its failure.

### 4. Stamp, with an ID
```bash
cq specs record "<id>" merge --set strategy=<strategy> --set subject=<the merge commit's subject, or "none — <why>" under fast-forward/rebase>
```
Write-once — a record already present is read, never overwritten. No ID → nothing to stamp.
**Done when:** the record is stamped (with an ID) or explicitly skipped (without one).

### 5. Remove the worktree, only after a verified merge
Only when step 1's worktree list held a **separate** worktree for the merged branch (not the base's
own checkout) and step 3 exited 0:
```bash
git -C <the base's checkout> worktree remove <the worktree path>
```
**Never `--force`.** `git worktree remove` refuses a tree holding modified or untracked files on its
own — the one case worth fearing, and git already declines it; report the refusal and leave the
worktree standing. Never runs for a merge that did not happen, and never deletes the branch itself —
that stays step 2's separate, offered decision. **Done when:** the worktree is removed, refused with
its own error reported, or the step was skipped because there was none to remove.

### 6. Report
State the strategy, the merge commit (or the explicit none), what was stamped, and the worktree's
fate. **Done when:** all four are named.

## Invariants

- Never `git checkout <base>` to reach the checkout that merges — always `git -C`.
- Never merge without a checkout that already holds the base; never manufacture one.
- Never `--force` a worktree removal, and never remove one before a merge verified at exit 0.
- Offer the strategy; never choose it for the human.
