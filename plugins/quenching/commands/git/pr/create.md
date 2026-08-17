---
description: >-
  Push the current branch and open a pull request through `gh`, against the resolved base, with a
  `Closes #<n>` body when an issue is named — and report plainly whether that keyword will actually
  close the issue or only cross-reference it. Use when the user asks to "open a PR", "create a pull
  request", "push and open a PR", or "submit this for review". Given a spec slug on the `github`
  backend it derives title, body and issue from the spec and stamps its write-many `pr:` record.
  Not for: merging an already-open PR → /quenching:git:merge; resolving PR review comments →
  /quenching:git:pr:review.
argument-hint: [slug-or-title]
allowed-tools: Bash(git push:*), Bash(gh repo view:*), Bash(gh pr create:*), Bash(python3:*), Read, AskUserQuestion
---

# /quenching:git:pr:create — push and open the pull request

**Input**: `$ARGUMENTS` — a spec slug on the `github` backend (derives title, body, and the issue to
close), or free text to use as the PR title. Omitted → ask.

Opens the PR and **stops there** — merging is `/quenching:git:merge`'s, on its own confirmation.
Offered only where `gh` resolves the repository; a repo with no GitHub remote has no route here at
all, silently, which is the ordinary case rather than a finding.

## Workflow

### 1. Confirm the route exists, and resolve the base
```bash
gh repo view --json name 2>&1 || echo "NO-ROUTE"
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git base --json
```
`NO-ROUTE` (or `gh` unauthenticated) → say plainly there is no PR route here and stop; this is the
ordinary case on a host other than GitHub, never a finding. **Done when:** the route is confirmed
and the base branch (and whether it is the host's own default) is resolved.

### 2. Resolve title, body and the issue to close
A spec slug in `$ARGUMENTS` → `cq specs status --spec "<slug>" --json`; on the `github` backend its
`path` is the issue URL — the trailing number is `<n>`. Free text → that text is the title; ask for
a body and whether an issue number should be closed. **Done when:** the title, the body (with
`Closes #<n>` appended when an issue is named), and the issue number (or its absence) are fixed.

### 3. State the link's real effect before pushing
**Measured**: `Closes #<n>` only populates `closingIssuesReferences` — the link a caller can read
back — when the PR's base **is** the repository's own default branch; on any other base (a branch
in flight during a transition, whose record names a base the default no longer is) the keyword
still cross-references the issue in its timeline but does not close it on merge. Say which case
this run is, from step 1's `isDefault`, **before** asking to push — the human's confirmation covers
a PR whose real behavior they already know. **Done when:** the link's real effect has been stated,
whichever case it is.

### 4. Push and open, on one confirmation
Show the remote, the branch name it pushes under, and the title/body, and ask with
**AskUserQuestion** — this publishes to a remote host, which nothing before this step has done:
```bash
git push -u origin <branch>
gh pr create --base <base> --title "<title>" --body "<body>"
```
**`--base` is never omitted** — `gh pr create` without it targets the repository's own GitHub
default branch, which under the PR-on-primary flow is where work lands, but a spec in flight
during the transition (its `branch.base` record names `develop`) must still land on that recorded
base, and an omitted `--base` would silently target the wrong branch.
[plan-git-record.md](/.knowledge/standards/workflows/plan-git-record.md) §Three frontmatter
records. **Done when:** the PR exists, or the push/create failed and its error is reported
verbatim.

### 5. Stamp, with a slug
```bash
cq specs record "<slug>" pr --set number=<n> --set url=<url> --set date=<today>
```
`pr:` is **write-many** — a later PR on the same spec (closed and reopened, or force-pushed to a
fresh number) is a new fact, not a correction of this one, which is why it carries its own `date`.
No slug → nothing to stamp; report the PR number and URL only. **Done when:** the record is stamped
(with a slug) or the report carries the PR's own facts (without one).

### 6. Report
State the PR number, its URL, the base it targets, and whether `Closes #<n>` will actually close
the issue (step 3). **Done when:** all four are named.

## Invariants

- Never omit `--base` on `gh pr create`.
- Never push or open a PR without the human's confirmation on the exact remote, branch and title
  shown.
- Never claim `Closes #<n>` closes the issue when the base is not the host's own default — say so
  plainly instead.
