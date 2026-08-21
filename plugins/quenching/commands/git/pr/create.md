---
description: >-
  Push the current branch and open a pull request through the repository's provider — GitHub or
  Azure DevOps — against the resolved base, linking the named issue/work item natively. Use when
  the user asks to "open a PR", "create a pull request", "push and open a PR", or "submit this
  for review". Given a spec slug it derives title, body and the provider locator from the spec and
  stamps its write-many `pr:` record. Not for: merging an already-open PR → /quenching:git:merge;
  resolving PR review comments → /quenching:git:pr:review.
argument-hint: [slug-or-title]
allowed-tools: Bash(git push:*), Bash(git remote get-url:*), Bash(gh repo view:*), Bash(gh pr create:*), Bash(az repos pr:*), Bash(python3:*), Read, AskUserQuestion
---

# /quenching:git:pr:create — push and open the pull request

**Input**: `$ARGUMENTS` — a spec slug (derives title, body and the provider's issue/work-item
link), or free text to use as the PR title. Omitted → ask.

Opens the PR and **stops there** — merging is `/quenching:git:merge`'s, on its own confirmation.
The route follows `cq specs config --json`: `github` uses `gh`, `azure-boards` uses `az repos`; an
unknown or unauthenticated provider has no route here and stops plainly, rather than being treated
as a GitHub repository.

## Workflow

### 1. Confirm the route exists, and resolve the base
```bash
# Read `backend` from this result before choosing a host CLI.
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq specs config --json
git remote get-url origin
gh repo view --json name 2>&1 || echo "NO-ROUTE"
az repos pr list --status all --top 1 --detect true --output json 2>&1 || echo "NO-ROUTE"
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git base --json
```
Run only the probe for the configured provider, after confirming the origin host matches it:
`github` → `gh repo view`; `azure-boards` → `az repos pr list --status all --top 1 --detect
true`. A missing/mismatched origin, `NO-ROUTE`, or an unauthenticated host CLI → say plainly there
is no PR route here and stop; this is the ordinary case on a provider that is not available, never
a finding.
`cq git base --json` supplies the base and `isDefault`. **Done when:** the provider route and base
branch are resolved.

### 2. Resolve title, body and the provider link
A spec slug in `$ARGUMENTS` → `cq specs status --spec "<slug>" --json`; its `path` is the provider
locator. On `github`, the trailing number is an issue `<n>` and the body gets `Closes #<n>`. On
`azure-boards`, the trailing number is a work item `<n>` and the link is passed as
`--work-items <n>` to Azure; do not invent a `Closes #<n>` sentence. Free text → that text is the
title; ask for a body and, when applicable, whether an issue/work item should be linked. **Done
when:** the title, body, provider-native link (or its absence), and base are fixed.

### 3. State the link's real effect before pushing
For `github`, **measured**: `Closes #<n>` populates `closingIssuesReferences` only when the PR's
base **is** the repository's own default branch; otherwise it cross-references the issue but does
not close it on merge. State that case from `isDefault`. For `azure-boards`, state that the native
`--work-items <n>` association will be attached to the PR; `--transition-work-items true`, when
chosen, asks Azure to transition linked work items when the PR is completed; and
`--delete-source-branch true` asks Azure to delete the source branch after the PR is completed and
merged. **Done when:** the provider-native link and branch-deletion effects are stated before
publication.

### 4. Push and open, on one confirmation
Show the remote, the branch name it pushes under, and the title/body, and ask with
**AskUserQuestion** — this publishes to a remote host, which nothing before this step has done:
For Azure, show the work item id, that `--delete-source-branch true` is included, and whether
`--transition-work-items true` is included in the command the human is confirming.
```bash
git push -u origin <branch>
# github
gh pr create --base <base> --title "<title>" --body "<body>"
# azure-boards
az repos pr create --detect true --source-branch <branch> --target-branch <base> \
  --title "<title>" --description "<body>" --delete-source-branch true [--work-items <n>] \
  [--transition-work-items true] --output json
```
The host-specific command is selected from the configured provider. The target branch is explicit
on both routes: `--base` for GitHub and `--target-branch` for Azure; neither may be omitted. Read
the created PR's number/id and URL from the JSON/CLI result. **Done when:** the PR exists, or the
push/create failed and its error is reported verbatim.
[plan-git-record.md](/.knowledge/standards/workflows/plan-git-record.md) §Three frontmatter
records.

### 5. Stamp, with a slug
```bash
cq specs record "<slug>" pr --set number=<provider-pr-id> --set url=<provider-url> --set date=<today>
```
`pr:` is **write-many** — a later PR on the same spec (closed and reopened, or force-pushed to a
fresh number) is a new fact, not a correction of this one, which is why it carries its own `date`.
No slug → nothing to stamp; report the PR number and URL only. **Done when:** the record is stamped
(with a slug) or the report carries the PR's own facts (without one).

### 6. Report
State the provider, PR number/id, URL, base it targets, and the effect of the native issue/work-item
link (step 3). **Done when:** all four facts are named.

## Invariants

- Never route an Azure repository through `gh`, or a GitHub repository through `az`.
- Never omit `--base` on `gh pr create` or `--target-branch` on `az repos pr create`.
- Always pass `--delete-source-branch true` on `az repos pr create`, so Azure removes the source
  branch after the PR is completed and merged.
- Never push or open a PR without the human's confirmation on the exact remote, branch and title
  shown.
- Never claim a provider-native issue/work-item link closes or transitions anything beyond the
  host CLI's documented effect; report the provider and the selected base plainly instead.
