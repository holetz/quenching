---
type: standard
title: Plan git record contract
description: How a plan's work is recorded in git — the per-task commit field, the branch and merge frontmatter records, the squash caveat, and the read-if-present contract for a target's own docs/standards/git/
resource: plugins/quenching/assets/references/specs-isolate/git.md, plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/bin/specs.py, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/conclude.md
tags: [workflows, specs, git, commits, records]
timestamp: 2026-07-27
audience: both
authority: current
source: specs-flow-consolidation plan (sections 2-3)
maintainer: quenching
---

# Plan git record contract

What links a plan's checkboxes to the commits that implemented them, which git facts are recorded
in the spec, and whose conventions govern the commits themselves. The procedures implementing this
live in `assets/references/specs-isolate/git.md` and `.../execution.md`; this standard is the
contract they answer to.

## The task→commit link is stored, never inscribed

Each completed task line carries its implementing sha, in the metadata grammar `files:` and
`verify:` already use:

```markdown
- [x] 3.2 Validate the token — files: src/auth.py — verify: pytest tests/auth — commit: abc1234
```

Written mechanically by `specs.py task --check <id> --commit <sha>` — never by string surgery —
and only **after** the task verified, self-reviewed, and committed. The link lives on the task
line rather than as a trailer or anchor inside the commit message, which leaves the message format
**entirely the target repo's to decide**: Conventional Commits, ticket prefixes, and required
sign-offs all keep working, and the link still resolves.

The record cannot go stale by construction: amending an earlier task's commit and force-pushing
are both forbidden (see [task-execution.md](task-execution.md) §Hard rules), so a recorded sha
stays resolvable for the life of the branch. The one thing that can narrow it is a squash merge —
§The squash caveat below.

## Two frontmatter records carry the underivable git facts

Both belong to the record vocabulary in [plan-lifecycle.md](plan-lifecycle.md) and pass the same
admission test — a fact no derivation can reproduce:

- **`branch: {base, work}`** — stamped by `execute`, write-once, at the moment isolation is taken.
  `work` is derivable while the branch is checked out; `base` is not — **after the merge, git
  cannot say what the branch was cut from**, which is the whole reason the record exists and why
  it is captured while still true. Work done in place stamps nothing: a record whose `base` equals
  its `work` states no fact. A later run reads the record; a current branch that disagrees with
  `work` is a finding to report, never a value to correct.
- **`merge: {strategy, commit}`** — stamped by `conclude`, write-once. The strategy was a human
  choice and the sha is its result; recording both is what tells a future reader whether the
  per-task shas still resolve from the base branch.

## The squash caveat

The four merge strategies differ in exactly one dimension that matters here — what happens to the
recorded shas:

| Strategy | The per-task `commit:` shas |
| --- | --- |
| merge commit *(default)* | stay on the base branch, resolve forever |
| fast-forward | unchanged — nothing rewritten, nothing added |
| squash | **survive only on the branch** — deleting it strands every record |
| rebase | **rewritten** — every recorded sha points at a commit that no longer exists |

A squash is a common house style and is not argued against — but its consequence is said out
loud: when squash is chosen, `conclude` records it in `merge:`, states it in `## Outcome`, and
offers **not** to delete the branch, the only way the archived spec's `commit:` fields stay live.
Rebase is offered only when asked for by name, with the plain statement that it makes the record
worse rather than narrower.

## The target's git conventions win — read if present, never installed

Before the first commit of a run, `docs/standards/git/` is checked **once**. Anything found there
governs verbatim; partial coverage splits (the target's docs for what they cover, the plugin
defaults for the rest); an `authority: background` git standard still wins over the defaults. The
report states which one governed.

With nothing declared, the plugin's defaults apply — branch `plan/<slug>`, one commit per task
with the subject `plan/<slug>: <id> <title>`, and bookkeeping commits (a ticked box, a stamped
record, a regenerated listing) as `plan/<slug>: record …`. Bookkeeping commits exist because the
spec file is edited *after* a task's commit is made, and folding that edit into the task's own
commit would mean amending it.

**Never install `docs/standards/git/**` into a target.** A default written into the repo stops
being a default: it converts an offer into a rule the repo now declares, which then wins forever
without anyone having agreed to it. A target that wants its conventions written down routes
through `/docs:add`, on its human's word. The same restraint bars inferring house style from
`git log` — a guess that looks deliberate is worse than the stated default.
