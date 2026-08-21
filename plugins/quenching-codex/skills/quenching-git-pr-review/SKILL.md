---
name: quenching-git-pr-review
description: "Fetch a pull request's unresolved review threads, address each on the human's own confirmation, and mark it resolved once the fix is committed, on GitHub or Azure DevOps. Use when the user asks to \"resolve PR comments\", \"address the review feedback\", \"fix what the reviewer flagged\", or \"work through the open review threads\". Not for: opening the PR in the first place → quenching-git-pr-create; merging it once every thread is clear → quenching-git-merge."
---

<!-- GENERATED FROM plugins/quenching/commands/git/pr/review.md -->


# quenching-git-pr-review — work through a PR's unresolved threads

**Input**: `$ARGUMENTS` — a provider PR number/id. Omitted → the active PR open for the current
branch.

Reads **unresolved review threads** specifically — not every comment, and not ones already marked
resolved — because that resolution state is exactly what a reviewer uses to track what still needs
a look, and re-surfacing settled threads trains the human to stop trusting the list.

## Workflow

### 1. Resolve the provider, PR and repository
```bash
# Read `backend` from this result before choosing a host CLI.
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs config --json
git remote get-url origin
# github
gh repo view --json owner,name -q '.owner.login + " " + .name'
gh pr view <$ARGUMENTS, or the current branch's PR> --json number -q .number
# azure-boards
az repos pr list --status all --top 1 --detect true --output json
az repos pr show --id <id> --detect true --output json
az repos pr list --source-branch "$(git branch --show-current)" --status active \
  --detect true --output json
```
Run only the probe for the configured provider, after confirming the origin host matches it. On
Azure, an explicit argument goes to `show`; with no argument, `list` is filtered to the current
branch. No PR resolves for the current branch and none was given → say so and stop. More than one
active Azure PR → show the ids and ask which one to work. **Done when:** the provider, repository
and PR number/id are known.

### 2. Fetch every unresolved thread
```bash
gh api graphql -f query='
  query($owner:String!,$repo:String!,$n:Int!){
    repository(owner:$owner,name:$repo){
      pullRequest(number:$n){
        reviewThreads(first:100){
          nodes{ id isResolved path line
            comments(first:10){ nodes{ body author{login} } } } } } } }' \
  -F owner=<owner> -F repo=<repo> -F n=<number>
# azure-boards — use the repository/project ids from `az repos pr show`.
az devops invoke --area git --resource pullRequestThreads \
  --route-parameters project=<project-id> repositoryId=<repository-id> pullRequestId=<pr-id> \
  --api-version 7.1 --output json
```
For GitHub filter to `isResolved: false`. For Azure filter to non-terminal thread `status` values
(normally `active`/`pending`; omit `fixed`, `closed`, `wontFix` and `byDesign`). None → report the
PR is clear and stop. Preserve each thread's id, file/line context and comment chain. **Done
when:** the list of unresolved threads is in hand.

### 3. Work each thread, on its own confirmation
For each unresolved thread, in the order returned: show the file, line, and comment chain, propose
a fix (or ask what the human wants instead), and apply it only on a yes — a review thread is
someone's specific ask, and batching every thread into one silent sweep is how a wrong fix for
thread 3 hides inside a commit that also fixed threads 1 and 2 correctly. **Done when:** every
thread has either been fixed and staged, or explicitly skipped with a stated reason.

### 4. Commit and resolve
Once at least one thread's fix is staged, commit it — `quenching-git-commit` owns the subject and
the hygiene rules this command does not restate. Then, per thread actually fixed:
```bash
gh api graphql -f query='mutation($id:ID!){resolveReviewThread(input:{threadId:$id}){thread{isResolved}}}' -F id=<thread id>
# azure-boards — `repository.url` comes from the PR JSON returned in step 1.
az rest --method patch \
  --url "<repository.url>/pullRequests/<pr-id>/threads/<thread-id>?api-version=7.1" \
  --body '{"status":"fixed"}' --output json
```
A thread that was skipped stays unresolved — resolving it would tell the reviewer it was handled
when it was not. Verify GitHub's `isResolved: true` or Azure's `status: fixed` after the update.
**Done when:** every fixed thread reads back resolved/fixed, and every skipped one is named in the
report as still open.

### 5. Report
State how many threads were unresolved at the start, how many were fixed and resolved, how many
were skipped and why, and the commit(s) that carried the fixes. **Done when:** all four are named.

## Invariants

- Never resolve a thread that was skipped rather than fixed.
- Never batch-apply every thread's fix before any confirmation — one thread, one yes.
- Never invent a fix for a thread whose ask is unclear — ask the human instead.
- Never route an Azure PR through GitHub GraphQL, or a GitHub PR through Azure REST.
