---
description: >-
  Publish everything accumulated on the integration branch as a deliberate release — the
  local `develop → main` merge, the plugin's seven-artifact version lockstep, the git tag,
  and the push to origin. Use when the user asks to "publish a release", "cut a release",
  "ship what's on develop", "release this", "is it time to release", or "publish the
  plugin". Judges patch/minor/major from what actually accumulated and asks for
  confirmation before touching anything; when develop carries exactly one merge since the
  last release, asks once whether this is a release or a habit. When it finishes: `main`
  and its new tag exist locally and on origin, pointing at the same commit. Not for:
  concluding or merging ONE spec into the integration branch → /specs:conclude.
argument-hint: [version — optional, skips the proposal and confirms this exact X.Y.Z]
allowed-tools: Bash(git:*), Bash(python3:*), Read, AskUserQuestion
---

# /release — publish what develop accumulated

**Input**: `$ARGUMENTS` (optionally an exact `X.Y.Z` version; omitted → the command proposes one
from what accumulated and confirms it with you).

This repository separates integration from publication —
[docs/standards/git/branching.md](/docs/standards/git/branching.md): the integration branch
(`develop` by default) is where specs merge; the release branch (`main` by default) only ever
receives a deliberate `develop → main` merge, which is also the only moment the plugin's seven
version-carrying artifacts move
([docs/standards/ci-cd/versioning-release.md](/docs/standards/ci-cd/versioning-release.md)) and a
tag is created. This command is that deliberate act. The mechanical half — the seven-artifact
bump, the commit, the tag — is `plugins/quenching/assets/bin/specs.py release <version>`, already
implemented and self-tested; this command judges *whether* and *what*, gets it confirmed, performs
the merge, and publishes the result.

**Always the LOCAL copy of the tool, never the installed plugin.** Every git command and every
`specs.py` call below uses the path **relative to this repository's own root**
(`plugins/quenching/assets/bin/specs.py`) — never `${CLAUDE_PLUGIN_ROOT}`. A release packages what
is actually on this checkout's `develop`; resolving through the installed plugin could run the
tool from a different, possibly older, copy than the one being released — the exact risk this
repository's own memory already names as the plugin cache lagging the repo source.

## Workflow

### 1. Resolve the branches and where the release branch lives
```bash
python3 plugins/quenching/assets/bin/specs.py config --json
git worktree list --porcelain
```
Take `integrationBranch`/`releaseBranch` from the config payload, defaulting to `develop`/`main`
when either is absent. Find which checkout holds the release branch. **None does** → stop without
merging, name the release branch and that nothing has it checked out, and name the fix — check it
out, or add a worktree of it. Never manufacture a temporary checkout
([plan-git-record.md](/docs/standards/workflows/plan-git-record.md) §The merge runs in the
checkout that already holds the base is the same rule, applied here to the release branch instead
of a spec's base).
**Done when:** both branch names are known and a checkout holding the release branch is found, or
the run has stopped and said why.

### 2. Read what accumulated, and ask "release or habit?" at exactly one
```bash
git log --oneline --merges <releaseBranch>..<integrationBranch>
```
This is every spec merged into the integration branch since the release branch last moved —
equivalent to "since the last release" without depending on tag history, since the release branch
only ever advances by this same command. **Zero** → nothing to publish; report that and stop.
**Exactly one** → ask, once, with **AskUserQuestion**: "develop carries one merge since the last
release — is this a release, or is it habit?" (the mitigation
[branching.md](/docs/standards/git/branching.md) §O gatilho é a demanda names: nothing else
pushes back on turning every single spec into its own release). Answering habit stops the run
cleanly — nothing is written. Two or more → proceed without asking.
**Done when:** the count is known and, if it was exactly one, answered.

### 3. Propose the version, show the whole plan, gate on ONE confirmation
Read `plugins/quenching/VERSION` for the current version. Show the merge commit subjects from step
2 to the human, propose a patch/minor/major bump with the reasoning drawn from what actually
changed (a new command or a new capability → minor; a fix or a doc/prose-only change → patch; a
breaking change to an installed consumer's contract → major) — **never invent a versioning
policy**: this is human judgment the command conducts, per
[versioning-release.md](/docs/standards/ci-cd/versioning-release.md)'s own boundary. If
`$ARGUMENTS` already named an exact version, skip the proposal and confirm that one instead.

Present ONE plan and wait for it: the proposed version, "merge `<integrationBranch>` into
`<releaseBranch>` (local, `--no-ff`, never a pull request)", "bump the seven version artifacts and
tag `<version>`", and "push `<releaseBranch>` and the tag `<version>` to origin" — the push is
part of this same plan, not a second confirmation, because an unpushed release reaches nobody who
installs via the marketplace. **Done when:** the human has confirmed one exact `X.Y.Z`, or declined
— a decline stops the run with nothing written.

### 4. Merge, bump, tag, and push
```bash
git -C <checkout from step 1> merge --no-ff <integrationBranch> -m "release: merge <integrationBranch> into <releaseBranch>"
git -C <checkout from step 1> log -1 --format=%H
```
Then, from that **same checkout**:
```bash
python3 plugins/quenching/assets/bin/specs.py release <version> --json
```
Exit **0** → the seven artifacts moved, the commit landed, the tag exists at that commit. Exit
**2** → the merge already happened but the bump did not; report the refusal's `message` plainly —
this is recoverable (fix what it names, typically a lockstep already drifted, then re-run this same
`specs.py release <version>` command by hand from that checkout; the merge does not need repeating)
but it is **never retried automatically** and the checkout is **never reset**. On exit 0, push:
```bash
git -C <checkout from step 1> push origin <releaseBranch> <version>
```
**Done when:** `specs.py release` exited 0 and the push succeeded, or the run has stopped naming
exactly which of the three steps failed.

### 5. Self-check and report
```bash
git -C <checkout from step 1> rev-parse <releaseBranch>
git -C <checkout from step 1> rev-parse <version>
```
The two must be equal — the release branch's tip is the tag. Report the old and new version, the
seven artifacts that moved (from step 4's JSON `artifacts`), the tag, and that both are on origin.
**Done when:** the two revisions match and the report names what changed, or names the mismatch as
a finding rather than claiming success.

## Not published until step 4 exits 0

Steps 1–3 read and ask; nothing is written before the plan in step 3 is confirmed, and nothing
reaches origin before `specs.py release` itself succeeds. A decline at step 3, or a "habit" answer
at step 2, leaves every branch exactly as it was.
