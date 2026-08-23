---
name: quenching-release
description: "Publish what the primary branch accumulated as a deliberate release — the plugin's four-artifact version lockstep, the git tag, and the push to origin. Use when the user asks to \"publish a release\", \"cut a release\", \"release this\", \"is it time to release\", or \"publish the plugin\". Judges patch/minor/major from what actually accumulated and asks for confirmation before touching anything; when the primary branch carries exactly one PR since the last release, asks once whether this is a release or a habit. When it finishes: the bump and its tag live on the primary branch's tip, on origin."
---

<!-- GENERATED FROM .claude/commands/release.md -->


# /release — publish what the primary branch accumulated

**Input**: `$ARGUMENTS` (optionally an exact `X.Y.Z` version; omitted → the command proposes one
from what accumulated and confirms it with you).

This repository publishes from a single long-lived branch —
[knowledge/standards/git/branching.md](/.knowledge/standards/git/branching.md): every spec lands on the
primary branch (`main`) through a reviewed pull request, and the release is the one deliberate act
that moves the plugin's four version-carrying artifacts
([knowledge/standards/ci-cd/versioning-release.md](/.knowledge/standards/ci-cd/versioning-release.md))
and creates a tag. This command is that deliberate act. The mechanical half — the four-artifact
bump, the commit, the tag — is `plugins/quenching/scripts/bin/cq specs release <version>`, already
implemented and self-tested; this command judges *whether* and *what*, gets it confirmed, and
publishes the result.

**Always the LOCAL copy of the tool, never the installed plugin.** Every git command and every
`cq specs` call below uses the path **relative to this repository's own root**
(`plugins/quenching/scripts/bin/cq`) — never `../..`. A release packages what
is actually on this checkout's primary branch; resolving through the installed plugin could run the
tool from a different, possibly older, copy than the one being released — the exact risk this
repository's own memory already names as the plugin cache lagging the repo source.

## Workflow

### 1. Resolve the primary branch and where its checkout lives
```bash
python3 plugins/quenching/scripts/bin/cq specs config --json
python3 plugins/quenching/scripts/bin/cq git base --json
git worktree list --porcelain
```
The primary branch is the `base` `cq git base` resolves (`origin/HEAD`, else
`init.defaultBranch`, else `main`). Find which checkout holds it — the bump runs there.
**No checkout holds the primary branch** → stop without bumping, name the branch and that nothing
has it checked out, and name the fix — check it out, or add a worktree of it. Never manufacture a
temporary checkout ([plan-git-record.md](/.knowledge/standards/workflows/plan-git-record.md)).
**Done when:** the primary branch is known and a checkout exists, or the run has stopped and said
why.

### 2. Read what accumulated, and ask "release or habit?" at exactly one
```bash
git -C <primary checkout from step 1> describe --tags --abbrev=0
git -C <primary checkout from step 1> log --oneline --merges <last-tag>..HEAD
```
The first names the last tag; the second lists every PR merged into the primary branch since it —
"since the last release", without depending on a second branch. **No tag yet** → the range is the
whole history; treat the count as "since the beginning". **Zero** → nothing to publish; report that
and stop. **Exactly one** → ask, once, with **AskUserQuestion**: "the primary branch carries one PR
since the last release — is this a release, or is it habit?" (the mitigation
[branching.md](/.knowledge/standards/git/branching.md) §O gatilho é a demanda names: nothing else
pushes back on turning every single spec into its own release). Answering habit stops the run
cleanly — nothing is written. Two or more → proceed without asking.
**Done when:** the count is known and, if it was exactly one, answered.

### 3. Propose the version, show the whole plan, gate on ONE confirmation
Read `plugins/quenching/VERSION` for the current version. Show the merge commit subjects from step
2 to the human, propose a patch/minor/major bump with the reasoning drawn from what actually
changed (a new command or a new capability → minor; a fix or a doc/prose-only change → patch; a
breaking change to an installed consumer's contract → major) — **never invent a versioning
policy**: this is human judgment the command conducts, per
[versioning-release.md](/.knowledge/standards/ci-cd/versioning-release.md)'s own boundary. If
`$ARGUMENTS` already named an exact version, skip the proposal and confirm that one instead.

Present ONE plan and wait for it: the proposed version, "bump the four version artifacts and tag
`<version>` on the primary branch", and "push the primary branch and the tag `<version>` to origin" —
the push is part of this same plan, not a second confirmation, because an unpushed release reaches
nobody who installs via the marketplace. **Done when:** the human has confirmed one exact `X.Y.Z`,
or declined — a decline stops the run with nothing written.

### 4. Bump on the primary branch, and push
The bump comes FIRST, on the primary branch's checkout — the tag points at the bump, which is what
makes the release one atomic fact on the branch that publishes
([versioning-release.md](/.knowledge/standards/ci-cd/versioning-release.md) §When the bump happens).
The `cd` in the subshell is what picks the repository — `cq specs` resolves it from the cwd, and
refuses (exit 2, `sp-release-wrong-branch`) any checkout not on the primary branch.
```bash
( cd <primary checkout from step 1> && python3 plugins/quenching/scripts/bin/cq specs release <version> --json )
git -C <primary checkout from step 1> push origin <primary-branch> <version>
```
Exit **0** on `cq specs release` → the four artifacts moved, the bump commit landed on the primary
branch, the tag points at it. Exit **2** → nothing was bumped; report the refusal's `message`
plainly — this is recoverable (fix what it names, typically a lockstep already drifted or a checkout
on the wrong branch, then re-run this same `cq specs release <version>` command by hand from the
primary branch's checkout) but it is **never retried automatically**. **Done when:** `cq specs
release` exited 0 and the push succeeded — or the run has stopped naming exactly which step failed.

### 5. Self-check and report
```bash
git -C <primary checkout from step 1> merge-base --is-ancestor <version>^{commit} <primary-branch>
git -C <primary checkout from step 1> log -1 --format=%s <primary-branch>
```
The first must exit 0 — the tag's commit (the bump) is contained in the primary branch; the second
is the tip the release published. `^{commit}` is required because the tag is annotated — bare
`rev-parse <version>` yields the tag object, never the commit. The JSON `commit` from step 4 must
also match `git -C <primary checkout> rev-parse <version>^{commit}`.
Report the old and new version, the four artifacts that moved (from step 4's JSON `artifacts`),
the tag, and that both are on origin.
**Done when:** the ancestry check passes, the JSON `commit` matches the tag's commit, and the
report names what changed — or names the mismatch as a finding rather than claiming success.

## Not published until step 4 exits 0

Steps 1–3 read and ask; nothing is written before the plan in step 3 is confirmed, and nothing
reaches origin before `cq specs release` itself succeeds. A decline at step 3, or a "habit" answer
at step 2, leaves the primary branch exactly as it was.
