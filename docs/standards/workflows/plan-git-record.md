---
type: standard
title: Plan git record contract
description: How a plan's work is recorded in git — the commit subject as the task→commit anchor, the branch and merge frontmatter records, why every record is written before the thing it describes, the squash caveat, the merge that runs via git -C in the base's own checkout and the worktree removed after it, and the read-if-present contract for a target's own docs/standards/git/
resource: plugins/quenching/assets/references/specs-isolate/git.md, plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/isolate.md, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/conclude.md
tags: [workflows, specs, git, commits, records]
timestamp: 2026-07-28
audience: both
authority: current
source: specs-flow-consolidation plan (sections 2-3); rewritten around the subject anchor by the move-conclude-merge-last plan (task 5.1); the git -C merge and the post-merge worktree removal added by the prefer-worktree-isolation plan (task 4.1)
maintainer: quenching
---

# Plan git record contract

What links a plan's checkboxes to the commits that implemented them, which git facts are recorded
in the spec, and whose conventions govern the commits themselves. The procedures implementing this
live in `assets/references/specs-isolate/git.md` and `.../specs-execute/execution.md`; this
standard is the contract they answer to.

## Every record is written before the thing it describes

This is the rule the rest of the file follows from. A record pointing at a commit can only be
written *after* that commit if it names something the commit alone can produce — and a sha is
exactly that. Naming the **subject** instead inverts the dependency, because the subject is chosen
by whoever is about to commit.

Two consequences, and they are why the anchor changed:

- **`/specs:execute` ticks the box before committing**, so the checkbox travels inside the commit
  that implements it. One task is exactly one commit, and the per-task bookkeeping commit is gone.
- **`/specs:conclude` stamps `merge:` on the work branch**, so the merge is the last action of the
  run and **nothing is ever committed to the base branch after it**. One merge carries the code,
  the emergent docs, the archived spec and the distillation; reverting it reverts the spec's whole
  footprint.

A record that cannot be written beforehand is a record that forces a write afterwards, and a write
after the merge lands where the spec's own branch cannot account for it.

## The task→commit link is the commit's own subject

Each completed task line carries the subject of the commit that implements it, in the metadata
grammar `files:` and `verify:` already use:

```markdown
- [x] 3.2 Validate the token
      files: src/auth.py
      verify: pytest tests/auth
      subject: plan/session-tokens: 3.2 Validate the token
```

Written mechanically by `specs.py task --check <id> --subject <line>` — never by string surgery —
and only **after** the task verified and self-reviewed, **before** its commit. It resolves by
substring match:

```bash
git log --grep="<the recorded subject>" --fixed-strings
```

The link is still **not a trailer and not a machine-readable anchor bolted into the message**. It is
the subject the target repo's own convention produced, recorded verbatim: Conventional Commits,
ticket prefixes and required sign-offs all keep working, and the link still resolves. What changed
is only *which* fact about the commit is stored — never who decides the message.

**Two forms are read, forever.** A spec built before this change carries `commit: <sha>` and
resolves by sha. Neither form is backfilled and neither is an error: a recorded sha describes a
commit that exists, and rewriting an archived spec to modernise it would falsify when the record
was made. Tools read both; only `subject:` is ever written.

### Where the subject can fail

A `commit-msg` hook that **replaces** the subject outright breaks the link. Substring matching
survives every hook that merely *adds*, which is nearly all of them. `/specs:execute` compares
`git log -1 --format=%s` against what it recorded and **reports a mismatch as a finding, writing
nothing** — correcting it after the commit would restore the ordering this contract removed.

## Two frontmatter records carry the underivable git facts

Both belong to the record vocabulary in [plan-lifecycle.md](plan-lifecycle.md) and pass the same
admission test — a fact no derivation can reproduce:

- **`branch: {base, work}`** — stamped by `/specs:isolate`, write-once, at the moment isolation is
  taken. `work` is derivable while the branch is checked out; `base` is not — **after the merge,
  git cannot say what the branch was cut from**, which is the whole reason the record exists and
  why it is captured while still true. Work done in place stamps nothing: a record whose `base`
  equals its `work` states no fact. A later run reads the record; a current branch that disagrees
  with `work` is a finding to report, never a value to correct.
- **`merge: {strategy, subject}`** — stamped by `conclude`, write-once, **on the work branch before
  the merge**. The strategy was a human choice and the subject names the merge it will produce.
  Under `rebase` and `fast-forward` no merge commit exists, so the subject is an explicit none;
  `specs.py validate` reports a record that gets this backwards either way, as `sp-bad-merge`.

**The record is never the signal.** A human may cut `plan/<slug>` by hand and stamp nothing, and a
record outlives the branch it names. Anything asking whether a spec is in flight asks git for a
live ref — which is what `specs.py next --front` does, and why `/specs:continue` demotes a spec
whose branch is alive but checked out elsewhere.

## The squash caveat, and what rebase no longer costs

The four merge strategies differ in one dimension that matters here — what happens to the commits
the recorded subjects resolve against:

| Strategy | The per-task subjects |
| --- | --- |
| merge commit *(default)* | resolve from the base branch forever |
| fast-forward | unchanged — nothing rewritten, nothing added |
| squash | **resolve only from the branch** — deleting it strands every record |
| rebase | **survive**: the rewrite carries the message, so every record still resolves |

A squash is a common house style and is not argued against — but its consequence is said out loud:
when squash is chosen, `conclude` records it in `merge:`, states it in `## Outcome`, and offers
**not** to delete the branch, the only way the archived spec's `subject:` fields stay resolvable.

**Rebase is no longer the strategy that destroys the record.** Under the sha anchor it rewrote every
recorded commit and left the archived spec pointing at commits that no longer existed — the one
strategy that made the record strictly worse rather than merely narrower. A subject is carried by
the rewrite, so rebase now sits on the same footing as the others. The old warning applies only to
specs still carrying the sha form.

## The merge runs in the checkout that already holds the base — never `git checkout`

A plan's merge is performed **into** the base's checkout, from wherever the run happens to be
standing:

```bash
git worktree list --porcelain                    # which checkout holds <base>
git -C <that path> merge --no-ff plan/<slug> -m "plan/<slug>: merge (<strategy>)"
```

`git checkout <base>` is **never** how a plan comes home. From inside a worktree it does not merely
misbehave, it fails outright — `fatal: '<base>' is already used by worktree at …`, exit 128 — so
that form is broken for precisely the isolation this repo recommends. `git -C` is one path rather
than two special cases: from a worktree it names the main checkout, and from the main checkout it
names itself.

**When no checkout holds the base, the run stops without merging.** It names the base it wanted,
says nothing has it checked out, and names the fix — check the base out, or add a worktree of it.
It never manufactures a temporary checkout. This costs nothing, because `merge:` is stamped
*before* the merge: the run resumes with no record falsified.

## A worktree is removed after a successful merge, and never forced

Isolation that is not cleaned up accumulates: directories beside the repo, each pointing at a
branch already integrated, none of them obviously safe to delete. So once the merge exits 0,
`/specs:conclude` removes the worktree — run from the base's checkout, because nothing removes the
tree it is standing in:

```bash
git -C <the base's checkout> worktree remove <the worktree path>
```

**`--force` is never passed on this command.** `git worktree remove` refuses a tree holding
modified or untracked files by itself (`contains modified or untracked files`, exit 128), which is
exactly the irreversible case worth fearing — the safety is already git's, so no confirmation
prompt would buy anything a human would not answer "yes" to every time. A clean tree leaves the
disk silently; a refusal is reported with the path and git's own output, and the worktree stays.

Three bounds keep this from being destructive: it runs **only** after a merge verified at exit 0,
it **never** runs for an abandoned plan, and it does **not** delete the branch — that stays the
separate, offered decision it already was.

## The target's git conventions win — read if present, never installed

Before the first commit of a run, `docs/standards/git/` is checked **once**. Anything found there
governs verbatim; partial coverage splits (the target's docs for what they cover, the plugin
defaults for the rest); an `authority: background` git standard still wins over the defaults. The
report states which one governed.

With nothing declared, the plugin's defaults apply — branch `plan/<slug>`, one commit per task with
the subject `plan/<slug>: <id> <title>`, `plan/<slug>: merge (<strategy>)` for a merge, and
`plan/<slug>: record …` for the bookkeeping that remains. That bookkeeping is now only what a
commit genuinely cannot carry ahead of itself — `## Handoff`, which describes the tree *after* the
last commit — and no longer includes a ticked box or a stamped `merge:` record.

**Never install `docs/standards/git/**` into a target.** A default written into the repo stops
being a default: it converts an offer into a rule the repo now declares, which then wins forever
without anyone having agreed to it. A target that wants its conventions written down routes
through `/docs:add`, on its human's word. The same restraint bars inferring house style from
`git log` — a guess that looks deliberate is worse than the stated default.
