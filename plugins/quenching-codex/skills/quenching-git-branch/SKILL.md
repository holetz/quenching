---
name: quenching-git-branch
description: "Take isolation for a piece of work — a worktree, a plain branch, or in place — recommending a worktree by default, stating its cost, and stamping what was taken. Use when the user asks to \"isolate this work\", \"cut a branch for this\", \"take a worktree before I start\", or \"set up isolation for this build\". Given a spec slug it also stamps that spec's `branch:` record and marks the branch's own `quenching-slugs:` description line. Not for: pruning branches/worktrees already merged or gone → quenching-git-cleanup."
---

<!-- GENERATED FROM plugins/quenching/commands/git/branch.md -->


# quenching-git-branch — take isolation before writing code

**Input**: `$ARGUMENTS` — optionally a spec slug (stamps that spec's `branch:` record and its
`quenching-slugs:` marking) or a short name for standalone work with no spec behind it. Omitted →
ask what the isolation is for.

Cuts a worktree or branch **before the first line of code**, the same offer
`quenching-specs-execute` makes inline on its own way into a build. The mechanics — the offer's
shape, the default names, `worktreeSetup`, and the two records a taken isolation leaves behind —
are owned by
[git/isolation.md](../../references/git/isolation.md), cited below rather
than restated; this command is its standalone entry point for a caller with no build loop of its
own to hang the offer on.

`allowed-tools` grants bare `Bash` because step 4 runs a target-declared `worktreeSetup` — an
arbitrary command this file cannot scope in advance — beside `git worktree`/`git checkout`,
`cq specs record` and `cq git slugs`, which share no one prefix to scope to instead.

## Workflow

### 1. Load the rules and the state in one read
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/git/isolation.md \
  --sections "§Isolation happens on the way into a build" --sections "§Branch and worktree names" \
  --sections "§Recording the isolation"
git status --porcelain
git branch --show-current
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git base --json
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs config --json        # `worktreeSetup`, or null — exit 0 either way
```
`git status --porcelain` non-empty → refuse, name the offending paths, and stop; isolating a dirty
tree carries whatever was already sitting there into the first commit on the new ref, silently.
**Done when:** the rules are loaded, the tree is confirmed clean, and the base branch is resolved.

### 2. Resolve the slug, when one was given
`$ARGUMENTS` naming a spec → `cq specs status --spec "<slug>" --json` and read its `records.branch`.
Already stamped → report it (`base`, `work`) and **stop**; a second isolation for an already-isolated
spec is a no-op, not a re-offer. No record → continue to the offer below, carrying the slug through
to step 4. `$ARGUMENTS` naming no spec (or empty) → continue with no slug; nothing gets stamped in
step 4, only the branch or worktree itself. **Done when:** the slug (or its absence) and any
existing `branch:` record are resolved.

### 3. Offer isolation, worktree leading
State the base branch (from step 1), the branch name that would be cut (`plan/<slug>` with a slug,
else a kebab-case name derived from `$ARGUMENTS` or asked for), the worktree path, and —
`worktreeSetup` non-null — the setup command **verbatim**. Then ask with **AskUserQuestion**:

- **Worktree** *(default, recommended)* — `git worktree add ../<repo>-<name> -b <branch>`.
- **Branch** — `git checkout -b <branch>`, work continues in this checkout.
- **In place** — declines isolation; nothing is created.

Worktree leads unconditionally, per §Isolation happens on the way into a build already loaded — its
cost (no installed dependencies, no `.env`, no venv) is stated in the same block as the ask, which
**is** the consent for the setup command shown beside it. **Done when:** the human has chosen one of
the three, or the run stops on a git error from the chosen form.

### 4. Take it, run the setup, and stamp
Run the one command for the chosen form; a failure (name taken, dirty path, locked worktree) is
reported verbatim and nothing is stamped. On **Worktree** with `worktreeSetup` declared, run it once
with cwd inside the new worktree; a failing setup does not undo the worktree — report both facts
separately. Then, only with a slug from step 2:
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs record "<slug>" branch --set base=<base> --set work=<branch>
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git slugs <branch> --add "<slug>" --json
```
**In place** stamps `work` equal to `base` instead of skipping the record — §Recording the isolation
draws that distinction; nothing is marked on the branch description under **In place**, since this
command controls no branch of its own in that case. **Done when:** the chosen form exists on disk
(or **In place** was chosen), the setup ran and was reported (worktree only), and — with a slug —
`branch:` and the `quenching-slugs:` marking are stamped or explicitly skipped (**In place**).

### 5. Report
State which form was taken (or declined), the branch name, the worktree path (if any), the setup's
result (if run), and what was stamped. **Done when:** the summary names every fact step 4 produced.

## Invariants

- Never isolate over a dirty tree — refuse and name the paths.
- Recommend Worktree; never impose it, and never choose it by sniffing the target repo.
- Stamp `branch:` only once per slug — a record already present is read, never overwritten.
- Never install `.knowledge/standards/git/**` into the target; a repo's own conventions are read,
  never written, by this command.
