---
name: quenching-git-pr-review
description: "Fetch a pull request's unresolved review threads, address each on the human's own confirmation, and mark it resolved once the fix is committed. Use when the user asks to \"resolve PR comments\", \"address the review feedback\", \"fix what the reviewer flagged\", or \"work through the open review threads\". Not for: opening the PR in the first place → quenching-git-pr-create; merging it once every thread is clear → quenching-git-merge."
---

<!-- GENERATED FROM plugins/quenching/commands/git/pr/review.md -->


# quenching-git-pr-review — work through a PR's unresolved threads

**Input**: `$ARGUMENTS` — a PR number. Omitted → the PR open for the current branch.

Reads **unresolved review threads** specifically — not every comment, and not ones already marked
resolved — because that resolution state is exactly what a reviewer uses to track what still needs
a look, and re-surfacing settled threads trains the human to stop trusting the list.

## Workflow

### 1. Resolve the PR and the repo
```bash
gh repo view --json owner,name -q '.owner.login + " " + .name'
gh pr view <$ARGUMENTS, or the current branch's PR> --json number -q .number
```
No PR resolves for the current branch and none was given → say so and stop. **Done when:** the
owner, repo and PR number are all known.

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
```
Filter to `isResolved: false`. None → report the PR is clear and stop. **Done when:** the list of
unresolved threads (id, path, line, the comment chain) is in hand.

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
```
A thread that was skipped stays unresolved — resolving it would tell the reviewer it was handled
when it was not. **Done when:** every fixed thread's `isResolved` reads back `true`, and every
skipped one is named in the report as still open.

### 5. Report
State how many threads were unresolved at the start, how many were fixed and resolved, how many
were skipped and why, and the commit(s) that carried the fixes. **Done when:** all four are named.

## Invariants

- Never resolve a thread that was skipped rather than fixed.
- Never batch-apply every thread's fix before any confirmation — one thread, one yes.
- Never invent a fix for a thread whose ask is unclear — ask the human instead.
