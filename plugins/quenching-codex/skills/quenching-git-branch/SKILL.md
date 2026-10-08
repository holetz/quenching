---
name: quenching-git-branch
description: "Take isolation for a piece of work: worktree, plain branch or in place, stamped. Use for \"isolate this work\", \"cut a branch for this\", \"take a worktree\". Not for: pruning → quenching-git-cleanup."
---

<!-- GENERATED FROM plugins/quenching/commands/git/branch.md -->


# quenching-git-branch — take isolation before writing code

**Input**: `$ARGUMENTS` — optionally a spec id (stamps that spec's `branch:` record and its
`quenching-specs:` marking) or a short name for standalone work with no spec behind it. Omitted →
ask what the isolation is for.

Cuts a worktree or branch **before the first line of code**. The mechanics — the offer's shape,
the default names, `worktreeSetup`, and the two records a taken isolation leaves behind — are owned by
[git/isolation.md](../../references/git/isolation.md), cited below rather
than restated; this command is its standalone entry point for a caller with no build loop of its own.

**Grants.** `allowed-tools` holds only the `cq` verbs the `git-steward` also holds: a skill's grant widens the `tools:` of the subagent that runs it, so a wider one here would reopen what the steward's `tools:` closes. A `worktreeSetup`, `git checkout -b` and the `cq specs record` stamps go through the normal permission prompt.

## Workflow

### 1. Load the rules and the state in one read
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/git/isolation.md \
  --sections "§Isolation happens on the way into a build" --sections "§Branch and worktree names" \
  --sections "§Recording the isolation"
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/git/conventions.md \
  --sections "§The declared-directive layer" --sections "§The read-if-present rule"
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git conventions --json   # `config.branchName`, or absent
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git state --json           # `branch`, `status` (porcelain), `staged`, `remotes`
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git base --json
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs config --json        # `worktreeSetup`, `sharedPaths`, or their empty values — exit 0 either way
```
`status` non-empty → refuse, name the offending paths, and stop; isolating a dirty
tree carries whatever was already sitting there into the first commit on the new ref, silently.
**Done when:** the rules are loaded, the tree is confirmed clean, and the base branch is resolved.

### 2. Resolve the ID, when one was given
`$ARGUMENTS` naming a spec → `cq specs status --spec "<id>" --json` and read its `records.branch`.
Already stamped → report it (`base`, `work`) and **stop**; a second isolation for an already-isolated
spec is a no-op, not a re-offer. No record → continue to the offer below, carrying the ID through
to step 4. `$ARGUMENTS` naming no spec (or empty) → continue with no ID; nothing gets stamped in
step 4, only the branch or worktree itself. The word `autonomous` beside the ID is a conductor's
pre-answer to step 3's ask, given by a run launched with `--autonomous`: see step 3. **Done when:** the ID (or its absence) and any
existing `branch:` record are resolved.

### 3. Offer isolation, worktree leading — only from the base
If the current branch is already different from the resolved base, report that the checkout is
already isolated and carry it forward; do not offer a second branch or worktree. If it is the base,
continue with the offer below.
State the base branch (from step 1), the branch name that would be cut — `config.branchName` from
step 1 governs it where declared, else the target's docs, else `plan/<id>-<handle>` with an ID and a
kebab-case name derived from `$ARGUMENTS` or asked for without one — the worktree path, and —
`worktreeSetup` non-null — the setup command **verbatim**; `sharedPaths` non-empty — the declared
paths **verbatim**. Then ask with **AskUserQuestion**:

- **Worktree** *(default, recommended)* — `cq git worktree add --path ../<repo>-<name> --branch <branch> --base <base>`.
- **Branch** — `git checkout -b <branch>`, work continues in this checkout.
- **In place** — declines isolation; nothing is created.

**With `autonomous` in the input**, ask nothing: the form is **Worktree**, the one this step
recommends, and nothing else is granted. A non-null `worktreeSetup` is **not run**, because its
consent is the verbatim display this ask carries and no human sees it; step 5 reports
`setup: skipped (autonomous)`. Step 4 cuts the worktree from the remote base, never the local one.

Worktree leads when the current checkout is the base. Its
cost (no installed dependencies, no `.env`, no venv) is stated in the same block as the ask, which
**is** the consent for the setup command shown beside it. **Done when:** the human has chosen one of
the three (under `autonomous`, Worktree was taken unasked), or the run stops on a git error from
the chosen form.

### 4. Take it, run the setup, and stamp
Run the one command for the chosen form; a failure (name taken, dirty path, locked worktree) is
reported verbatim and nothing is stamped. **The Worktree cut starts from the remote base**, because
a PR merged through `gh` moves no local ref and the local `<base>` may miss the dependency the run
waited on:
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git worktree add --path <path> --branch <branch> --base <base> --json
```
The verb fetches `origin <base>`, cuts `<branch>` from the fetched tip resolved to a commit — so
the branch has no upstream and a push without an explicit destination never targets the base —
and links the declared shared paths inside the new worktree. A fetch error is exit 2 and stops the
run; only a missing `origin` falls back to the local `<base>` (`fromRemote: false`, the
`NO-REMOTE` line), and the report says so. A link failure is exit 1 with `linkRefusal`: it does not
undo the worktree, and it stops this flow before running `worktreeSetup`. When the
link succeeds, run a declared `worktreeSetup` once with cwd inside the new worktree; a failing
setup does not undo the worktree — report both facts separately. **A worktree outside the project
directory is not the shell's cwd:** the harness may return the cwd to the base checkout after every
command, so from here on each command carries the worktree explicitly — `cd <worktree> && …` in
the same call, `git -C <worktree>`, `cq --root <worktree>` — or a cwd-dependent tool (`cq` without
`--root`, `git diff`, tests) reads the base checkout and reports green over a tree that did not
change. `cq git …` takes no `--root`
(`git declares no --root`): it always runs as `cd <worktree> && cq git …`. Then, only with an ID from step 2:
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs record "<id>" branch --set base=<base> --set work=<branch>
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" git specs <branch> --add "<id>" --json
```
**In place** stamps `work` equal to `base` instead of skipping the record — §Recording the isolation
draws that distinction; nothing is marked on the branch description under **In place**, since this
command controls no branch of its own in that case. **Done when:** the chosen form exists on disk
(or **In place** was chosen), the setup ran and was reported (worktree only), and — with an ID —
`branch:` and the `quenching-specs:` marking are stamped or explicitly skipped (**In place**).

### 5. Report
State which form was taken (or declined), the branch name and **which layer governed it**, the
worktree path (if any), the setup's result (if run), and what was stamped. **Done when:** the summary
names every fact step 4 produced.

## Invariants

- Never isolate over a dirty tree — refuse and name the paths.
- Recommend Worktree; never impose it, and never choose it by sniffing the target repo — only the
  `autonomous` input word takes it unasked.
- Stamp `branch:` only once per id — a record already present is read, never overwritten.
- Never install `docs/standards/git/**` into the target, and never write `gitConventions` into its
  `.agents/quenching.json`; a repo's own conventions are read, never written, by this command.
