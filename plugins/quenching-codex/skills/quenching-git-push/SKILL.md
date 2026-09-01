---
name: quenching-git-push
description: "Publish a local branch to a named remote without opening or changing a pull request. Use when the user asks to \"push this branch\", \"publish the branch\", \"send these commits to the remote\", or \"push a checkpoint\". It resolves the exact destination, upstream state and commits ahead before one confirmation. Not for: opening or updating a PR → quenching-git-pr-create; syncing or resolving divergence → quenching-git-sync; merging → quenching-git-merge."
---

<!-- GENERATED FROM plugins/quenching/commands/git/push.md -->


# quenching-git-push — publish one branch, without opening a PR

**Input**: `$ARGUMENTS` — omitted means the current branch on `origin`; one positional argument
names a branch; `--remote <remote> [branch]` names the remote and optionally the branch. A branch
name is never interpreted as a remote. This command publishes only; it does not open or update a
pull request.

## Workflow

### 1. Resolve the destination and local preconditions

Read the current branch, working-tree status, remotes, remote URL and the base from:

```bash
git status --porcelain --untracked-files=all
git branch --show-current
git remote -v
git remote get-url <remote>
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git base --json
```

Refuse a dirty tree, detached HEAD, missing remote, missing branch, or target equal to the resolved
base. The default remote is `origin`; an alternate remote requires `--remote`. **Done when:** the
remote URL, local branch, target ref and base comparison are known, or the refusal names its cause.

### 2. Measure upstream, divergence and commits to publish

Resolve the local branch and its upstream with `git rev-parse`; inspect the remote ref with
`git ls-remote`; when it exists, measure ahead/behind with `git rev-list --left-right --count` and
list the commits to publish with `git log`. A branch behind or divergent from its remote is a
refusal for `quenching-git-sync`; an absent remote branch is a new upstream candidate. No commits
ahead is an informational no-op. **Done when:** the exact refspec, upstream action and commit list
are known, or publication is refused without a push.

### 3. Prepare the normal push command

Use the explicit refspec `HEAD:refs/heads/<branch>`. If no upstream exists, use `git push --set-upstream
<remote> HEAD:refs/heads/<branch>`; otherwise use `git push <remote> HEAD:refs/heads/<branch>`. Never
add a force option, bypass a hook, fetch, stage, commit, rebase, reset, or alter the refspec to
work around a refusal. **Done when:** one normal push command is fixed, or the no-op/refusal is
reported.

### 4. Show the write and ask once

Show the remote URL, local branch, destination branch, upstream action, ahead/behind counts and
every commit that will be sent. Ask with **AskUserQuestion** for confirmation of exactly that
normal push. A changed destination, branch, remote URL or commit list requires a fresh run and a new
confirmation. **Done when:** the human confirms or declines the exact publication.

### 5. Publish and report

Run only the confirmed normal `git push` command. Preserve Git's failure and output verbatim; do
not retry with a stronger option. On success, report the new upstream and pushed commits, then name
`quenching-git-pr-create` as a possible later action without invoking it. **Done when:** the push
succeeded with its remote facts, or its refusal/failure is reported and no bypass was attempted.

## Invariants

- Publish only the selected local branch to the selected remote; never open, edit or merge a PR.
- Refuse dirty trees, detached HEAD, base branches, missing remotes, behind/divergent upstreams and
  force requests before any push.
- Never fetch, stage, commit, rebase, reset, amend, bypass hooks or rewrite the refspec.
- Never infer success from local refs; report the push command's own result.
