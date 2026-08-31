---
description: >-
  Commit what is already staged under this repo's own commit convention when one is declared, the
  plugin's default subject grammar otherwise, enforcing hygiene no flag may bypass. Use when the user
  asks to "commit this", "make a commit", "commit these changes", or "wrap this up in a commit".
  Not for: staging files → the human or the owning build command; merging or pushing →
  /quenching:git:merge, /quenching:git:pr:create.
argument-hint: [subject]
allowed-tools: >-
  Bash(git status:*), Bash(git branch --show-current:*), Bash(git diff:*), Bash(git commit:*),
  Bash(git log:*), Bash(python3:*), Read
---

# /quenching:git:commit — commit what is staged, under the target's own convention

**Input**: `$ARGUMENTS` — an optional explicit commit subject. When omitted, resolve one from the
current spec/task context; never invent it from the diff and never ask for confirmation.

Commits **only what is already in the index** — never `git add -A` on the human's behalf, and
never a guess at which files belong together.

## Workflow

### 1. Read-if-present, and the staged diff
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git/conventions.md \
  --sections "§The read-if-present rule"
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git conventions --json
git diff --cached --name-only
```
Nothing staged → refuse: name that the index is empty and say what to stage. **Done when:** which convention governs (target's own, or the plugin default below)
and the staged file list are both known.

### 2. Resolve the subject
`§The read-if-present rule` governs: a target convention naming a subject format wins outright; a
target doc covering only part of it governs that part, the default below fills the rest. With
nothing declared:
```bash
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/git/commit.md --sections "§Commit messages"
```
`$ARGUMENTS` given → use it verbatim, wrapped rather than truncated past 72 characters where the
title allows; an explicit subject always wins. When it is omitted, resolve the current branch and
its `quenching-specs:` mark:
```bash
git branch --show-current
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq git specs <current-branch> --json
python3 ${CLAUDE_PLUGIN_ROOT}/assets/bin/cq specs next --spec <唯一-spec-id> --json
```
If that produces exactly one spec and one actionable task, derive the subject with the governing
convention from the spec id, task id and task title. If the execution caller already supplies a
unique spec/task pair, use that pair as the equivalent context. More than one candidate, no
candidate, or no actionable task is **ambiguous or missing context**: refuse, name the unresolved
fact, and tell the caller to supply an explicit subject or spec/task pair. Do not choose by
recency, branch order or staged-diff content. **Done when:** the exact subject string is fixed or
the refusal is reported.

### 3. Commit
```bash
git commit -m "<subject>" && git log -1 --format=%s
```
Execute immediately after the staged-diff and hygiene checks; a resolvable omitted subject does
not add a confirmation question. The command commits the existing index only — it never stages
files, amends history, or bypasses hooks.
The `commit-msg` hook only *adds* (a ticket prefix, a sign-off) still matches by substring and needs
nothing; one that **replaces** the subject outright is a mismatch, reported as a finding rather than silently accepted. **Done when:**
the commit exists and its logged subject either matches or the mismatch is reported.

### 4. Report
State the sha, the subject, and the committed files. **Done when:** all three are named.

## Invariants

- **Never `git add -A`, or any equivalent of it.** Staging is the caller's decision; this command
  commits the index exactly as it finds it.
- **Never `--no-verify` or `--no-gpg-sign`.** A rejecting hook is a finding to report, not an
  obstacle to route around.
- **Never amend or rewrite an existing commit, and never force-push.**
- **Never install `docs/standards/git/**` into the target.** A convention read here is
  followed, never written back.
