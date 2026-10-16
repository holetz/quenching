---
name: quenching-git-cleanup
description: "Prune merged or gone branches and orphan worktrees from `cq git stale`. Use for \"clean up old branches\", \"prune stale branches\". Not for: isolation → quenching-git-branch."
---

<!-- GENERATED FROM plugins/quenching/commands/git/cleanup.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Never use gpt-6-luna for product code or import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-cleanup — prune what `cq git stale` already found

**Input**: `$ARGUMENTS` — optional `remote:<name>`; omitted → `origin`. This command always starts
from a fresh report for the selected remote.

## Workflow

### 1. Ask the tool for the current report
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git stale --remote <remote> --json
```
The report contains local `staleBranches` (removable), `keptBranches` (staying, with reasons), fetched `remoteBranches` from `<remote>`, registered
`orphanWorktrees`, and unregistered `unregisteredWorktrees` siblings with their path, branch and
size. All four lists empty → say so and stop; there is nothing to prune. Do not fetch or run `git
remote prune` here: if the caller needs newer remote facts, it must fetch explicitly and start a
fresh cleanup run. The report's `remote` must equal the selected remote. **Done when:** all four
lists and the selected remote are in hand.

### 2. Let the human pick what to prune
Show every local stale branch with its reason(s), every remote branch as `<remote>/<branch>` with
its reason(s), and every orphan worktree with its path and branch. Show each `keptBranches` entry with its reasons (`open-pr`, `worktree`,
`unmerged-commits`) as information under "kept — not removable", and do not include it in the prune choices. Show each `unregisteredWorktrees`
finding with its path, branch and size as information, but do not include it in the prune choices.
Put ONE decision sheet ([specs-develop/questions.md](../../references/specs-develop/questions.md) §1) that ends the turn; its decision lists the local
branches and live worktrees as numbered items and accepts several of them in the reply
(`D1 1,3`), or `none` — option A (recommended) is `none`, never "all". An unclear reply is asked again. Show the exact local actions in those choices:
`git branch -d <branch>` or `git worktree remove <path>`, which `cq git prune` runs. **Done when:** the local selection is
settled.

For any remote branch in the fresh `remoteBranches` list, show its exact destructive action
`git push <remote> --delete <branch>`, which `cq git prune --remote-branch` runs, and put it as its own decision on the sheet (`D2`, `none` recommended). A remote branch is never
included in the local confirmation. **Done when:** the remote selection is settled and every selected
item has one explicit action.

### 3. Delete the chosen branches
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git prune --branch <branch> --json
```
The verb re-reads the stale report and acts only on a branch it still lists (exit 2 otherwise);
git refusing (`error: the branch '<branch>' is not fully merged`, exit 1) → report why and leave it standing;
this command never escalates to `-D`. **Done when:** every chosen branch is deleted, or its refusal
is reported.

### 4. Remove the chosen worktrees
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git prune --worktree <path> --json
```
Worktree removal is **never --force**. A refusal (modified or untracked files inside) is reported with git's own
message, and that worktree is left standing. **Done when:** every chosen worktree is
removed, or its refusal is reported.

### 5. Delete the chosen remote branches
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git prune --remote-branch <branch> --remote <remote> --json
```
Run this only for a selected item from the fresh `remoteBranches` list, after the separate remote
confirmation. The command is an external write: report its exact remote/branch and its output. A
refusal leaves the server branch standing; never retry with another command or infer success from a
local remote-tracking ref. **Done when:** every selected remote branch was deleted, or its refusal
was reported.

### 6. Report
State what was deleted, what was refused (and why), and what was left untouched because it was
never chosen. Separate local branches, remote branches, and worktrees in the report. **Done when:**
the three outcome classes are named.

## Invariants

- Never prune a branch or worktree `cq git stale` did not report.
- Never offer `keptBranches` for pruning: each is listed with the reason it stays.
- Never offer `unregisteredWorktrees` for pruning: `git worktree remove` does not act on an
  unregistered directory, and this class carries no action.
- Never delete a remote branch that `cq git stale` did not report in `remoteBranches`.
- Use only the selected remote (`origin` when omitted); a branch reported by another remote is not
  a candidate for this run.
- Never pre-select "all" in the prune offer — every item is the human's own pick.
- Never fetch or run `git remote prune` implicitly; the report is the fresh fact this run acts on.
- Never `git branch -D`, `git push --force`, or `git worktree remove --force`; a refusal is
  reported and the target is left standing for that specific refusal.
