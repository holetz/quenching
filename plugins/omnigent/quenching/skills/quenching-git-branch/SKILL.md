---
name: quenching-git-branch
description: "Take isolation for a piece of work: worktree or plain branch, never on the base, stamped. Use for \"isolate this work\", \"cut a branch for this\", \"take a worktree\". Not for: pruning → quenching-git-cleanup."
allowed-tools: "Bash(cq git base:*), Bash(cq git conventions:*), Bash(cq git specs:*), Bash(cq git state:*), Bash(cq git worktree add:*), Bash(cq specs config:*), Bash(cq specs status:*), Bash(cq components read:*), Read, AskUserQuestion"
---

<!-- GENERATED FROM plugins/quenching/commands/git/branch.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-git-branch — take isolation before writing code

**Input**: `$ARGUMENTS` — optionally a spec id (stamps that spec's `branch:` record and its
`quenching-specs:` marking) or a short name for standalone work with no spec behind it. Omitted →
ask what the isolation is for.

Cuts a worktree or branch **before the first line of code**. The mechanics — the offer's shape,
the default names, `worktreeSetup`, and the two records a taken isolation leaves behind — are owned by
[git/isolation.md](quenching://references/git/isolation.md), cited below rather
than restated; this command is its standalone entry point for a caller with no build loop of its own.

**Grants.** `allowed-tools` holds only the `cq` verbs the `git-steward` also holds: the steward follows this body with its own `tools:` (it holds no `Skill`), so a call outside them here would leave its `branch` step blocked. A `worktreeSetup`, `git checkout -b` and the `cq specs record` stamps go through the normal permission prompt.

## Workflow

### 1. Load the rules and the state in one read
```bash
cq() { python3 "${QUENCHING_OMNIGENT_ROOT:-$HOME/.omnigent/quenching}/scripts/cq" "$@"; }
# Read the quenching MCP resource: quenching://references/git/isolation.md?section=%C2%A7Isolation%20happens%20on%20the%20way%20into%20a%20build&section=%C2%A7Branch%20and%20worktree%20names&section=%C2%A7Recording%20the%20isolation
# Read the quenching MCP resource: quenching://references/git/conventions.md?section=%C2%A7The%20declared-directive%20layer&section=%C2%A7The%20read-if-present%20rule
cq git conventions --json   # `config.branchName`, or absent
cq git state --json           # `branch`, `status` (porcelain), `staged`, `remotes`
cq git base --json
cq specs config --json        # `worktreeSetup`, `sharedPaths`, or their empty values — exit 0 either way
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
paths **verbatim**. Then put ONE decision sheet ([specs-develop/questions.md](quenching://references/specs-develop/questions.md) §1) and end the turn (a sub-agent that holds the AskUserQuestion grant, such as the `git-steward`, carries the sheet inside one `AskUserQuestion` call instead — §1 "A sub-agent without the `AskUserQuestion` grant never asks");
an ambiguous reply is asked again, never filled in. `D1` is the isolation form:

- **A (recommended) Worktree** — `cq git worktree add --path ../<repo>-<name> --branch <branch> --base <base>`.
- **B Branch** — `git checkout -b <branch>`, work continues in this checkout.

**There is no in-place form.** Standing on the base is exactly the case this offer exists for, so
building there is never one of its answers. A reply that declines both forms stops the run: nothing
is cut, nothing is stamped, and the report says the work did not start because it would have landed
on the base.

**With `autonomous` in the input**, ask nothing: the form is **Worktree**, the one this step
recommends, and nothing else is granted. A non-null `worktreeSetup` is **not run**, because its
consent is the verbatim display this ask carries and no human sees it; step 5 reports
`setup: skipped (autonomous)`. Step 4 cuts the worktree from the remote base, never the local one.

Worktree leads when the current checkout is the base. Its
cost (no installed dependencies, no `.env`, no venv) is stated in the same block as the ask, which
**is** the consent for the setup command shown beside it. **Done when:** the human has chosen one of
the two (under `autonomous`, Worktree was taken unasked), or the run stops on a declined offer or on
a git error from the chosen form.

### 4. Take it, run the setup, and stamp
Run the one command for the chosen form; a failure (name taken, dirty path, locked worktree) is
reported verbatim and nothing is stamped. **The Worktree cut starts from the remote base**, because
a PR merged through `gh` moves no local ref and the local `<base>` may miss the dependency the run
waited on:
```bash
cq() { python3 "${QUENCHING_OMNIGENT_ROOT:-$HOME/.omnigent/quenching}/scripts/cq" "$@"; }
cq git worktree add --path <path> --branch <branch> --base <base> [--spec "<id>"] --json
```
With an ID from step 2, pass `--spec`: the verb refuses (exit 2, nothing cut) a spec that does not
exist or does not own `<branch>`, and after the cut stamps the `branch:` record itself
(`branchRecord` in the payload; a failed stamp is exit 1 and leaves the worktree). The verb fetches `origin <base>`, cuts `<branch>` from the fetched tip resolved to a commit — so
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
change. `cq git …` takes no `--root` on its write verbs
(a usage error): it always runs as `cd <worktree> && cq git …`. Then, only with an ID from step 2
(the Worktree form already stamped `branch:` through `--spec`; **Branch** form stamps it by hand):
```bash
cq() { python3 "${QUENCHING_OMNIGENT_ROOT:-$HOME/.omnigent/quenching}/scripts/cq" "$@"; }
cq specs record "<id>" branch --set base=<base> --set work=<branch>   # Branch form only
cq git specs <branch> --add "<id>" --json
```
**Done when:** the chosen form exists on disk, the setup ran and was reported (worktree only), and
— with an ID — `branch:` and the `quenching-specs:` marking are stamped.

### 5. Report
State which form was taken (or declined), the branch name and **which layer governed it**, the
worktree path (if any), the setup's result (if run), and what was stamped. **Done when:** the summary
names every fact step 4 produced.

## Invariants

- Never isolate over a dirty tree — refuse and name the paths.
- Recommend Worktree; never impose it, and never choose it by sniffing the target repo — only the
  `autonomous` input word takes it unasked.
- Never leave the work on the base — the offer has no in-place form, and a declined offer stops the
  run instead of building there.
- Stamp `branch:` only once per id — a record already present is read, never overwritten.
- Never install `docs/standards/git/**` into the target, and never write `gitConventions` into its
  `.agents/quenching.json`; a repo's own conventions are read, never written, by this command.
