---
type: decision
title: Spec store writes accumulate locally and the store branch keeps a single commit
description: "Why every git-store write stopped being its own push: writes accumulate in one local pending commit, reach the remote only at sync points, and each sync replaces the store branch with one parentless commit under a lease"
resource: plugins/quenching/assets/bin/quenching/specs/backends/git.py, plugins/quenching/assets/bin/quenching/specs/commands/push.py, docs/standards/architecture/spec-backend.md
tags: [decision, architecture, specs, git]
timestamp: 2026-10-29
audience: both
authority: current
source: spec 2123
maintainer: quenching
---

# 0016 — Spec store writes accumulate locally and the store branch keeps a single commit

The rules live in [spec-backend](../standards/architecture/spec-backend.md) §The git store; this
records why they changed. It amends [ADR 0006](0006-specs-move-to-a-git-store-with-thin-cards.md),
which made every write a push.

## Context

Every write to the git store built one commit and pushed it at once, and every
`cq specs record/section/task/discover/promote` is its own process, so a spec's lifecycle became a
stream of pushes. A downstream repository measured a median of 19 store pushes per spec (p90 49,
max 163), bursts of five pushes in six seconds during a conclude, and 3,295 commits on its store
branch; this repository's own store held 8,253.

Nothing shipped reads that history: no `git log`, `blame` or `rev-list` runs on the store branch, a
spec's date comes from its frontmatter, and a card links to the branch tip. Only the tests pinned
commit counts and subjects.

## Decision

- Writes accumulate in ONE local pending commit, `refs/quenching/pending/<branch>` in the common
  `.git`, moved by `git update-ref <new> <old>`. Reads see it, and replay it onto a newly fetched
  tip in memory without moving it.
- The remote is reached only at sync points: `create`, `archive`/`restore`, `import`, `configure`,
  `cq specs push`, and the end of `cq git push`, `cq git pr create` and `cq git pr merge`.
- Every sync replaces the store branch with one parentless commit through
  `--force-with-lease=refs/heads/<branch>:<tip>`, so the branch always holds a single commit and
  the lease stays the compare-and-swap. A remote that refuses the rewrite receives the same tree as
  a fast-forward child; the next writer allowed to rewrite collapses it again.
- Card transitions move to the sync: one request per spec whose lifecycle facts changed between the
  remote tip and the pushed commit. A card that fails after the push landed is a warning beside the
  result, never a failed sync.

A lifecycle drops from about 19 pushes to about 4 (create, PR, archive, merge).

## Alternatives weighed

- **One squashed commit per sync on top of the history, plus an on-demand compaction.** Every sync
  stays a plain fast-forward, but the branch keeps growing. Not chosen.
- **Sync points plus a Stop hook at the end of every agent turn.** The remote never lags more than a
  turn, at about 5–8 pushes per spec. Not chosen.
- **Only an explicit `cq specs push`.** The fewest pushes, but the remote and the board lag until
  someone remembers. Not chosen.
- **A lock file serialising local writes.** Needs a per-platform lock and breaks with the
  compare-and-swap design; `update-ref <new> <old>` keeps the existing retry loop.

## Consequences

- **Lag.** Other clones and the board see a spec's new state only at the next sync point.
  `cq specs status` lists the specs with unsent local writes and since when.
- **Late conflict.** Two clones editing the same spec collide at the sync, not at the write. The
  refusal (`sp-git-stale-write`) names each spec with its local and remote blob and keeps the
  pending ref; `cq specs push --drop <id>` discards the local side once its text is recovered.
- **Loss.** A clone deleted with pending writes loses them; the archive and merge sync points make
  a leftover rare.
- **History is gone.** The first collapse drops the existing remote history; keep a local backup
  ref of the store tip before it if the history matters.
- **Mixed runtimes and downgrades.** An older `cq` reads only the remote and pushes directly: it
  misses writes pending elsewhere in the clone, and a spec changed on both sides refuses at the next
  sync with both blobs. **Run `cq specs push` before rolling out, and before a downgrade**, and merge
  the base into in-flight worktrees.
- **Rewrite permission.** A writer without force-push rights appends instead of collapsing, and the
  sync result says `history: appended`.
