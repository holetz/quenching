---
type: standard
title: Branch flow — PR onto the primary, deliberate release
description: One long-lived branch — the primary (main) — where every PR merges and review lives, the release as a deliberate local act that bumps, tags and publishes what the primary accumulated, the trigger on demand and with no cadence, the question that pushes toward grouping when the primary carries a single PR since the last tag, and the transition for anyone coming from the two-branch flow
resource: .claude/commands/release.md, plugins/quenching/assets/bin/quenching/git/**, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/cycle.md, plugins/quenching/assets/references/align/convergence.md
tags: [git, branching, release, workflow, main]
timestamp: 2026-08-17
audience: both
authority: current
source: rewritten by spec eliminar-branch-de-integracao (2026-08-17) — the two-branch flow (develop integrates, main publishes) ceased to exist: the primary receives every PR and the release is the deliberate local act that publishes it; the transition for anyone coming from the old flow added in the same rewrite
maintainer: quenching
---

# Branch flow — PR onto the primary, deliberate release

This repository publishes from **one** long-lived branch. There is no separate integration branch:
all work enters through a pull request and the release is the only act that publishes.

## The single branch

| Branch | Role |
| --- | --- |
| `main` | **Publishes.** It is the repository's default branch and where every PR merges. The release is the only act that moves the version lockstep ([versioning-release.md](../ci-cd/versioning-release.md)) and creates the tag. |

The primary branch is not configured — it resolves through the chain `origin/HEAD →
init.defaultBranch → main` ([plan-git-record.md](../workflows/plan-git-record.md)).

## The PR is the entry route

All work enters `main` through a pull request: the spec execution route followed by
`/quenching:git:pr:create` opens the PR against the primary branch and human review lives in the PR.
There is no local merge of specs — each change is reviewed before it enters, not after.

## The trigger is demand, not cadence

The release is a deliberate act of the maintainer. There is no cadence, no merge counter, no time
window — the trigger is "I decided to publish", never "time has passed" or "something merged".

**The mitigation against habit.** Nothing in the flow forces several specs to be grouped into one
release: the maintainer is a single person, so the scenario where every spec becomes a release out
of habit costs one release per spec and gains nothing. So when the primary carries **a single PR**
since the last tag, the release command asks whether that is a release or a habit — no counter, no
block, one question only, at the single moment where it fits.

## Where the flow is declared

| What | Where | Consumers |
| --- | --- | --- |
| The policy in prose | this document | `/quenching:specs:execute` and `/quenching:specs:conclude`, as read-if-present |
| The version bump | [versioning-release.md](../ci-cd/versioning-release.md) | the release verb |
| The `base` inference chain | [plan-git-record.md](../workflows/plan-git-record.md) | the unstamped spec |

The `base` inference chain — used when a spec starts on a branch nobody stamped — resolves
`origin/HEAD → init.defaultBranch → main`, the primary branch, which is where the work belongs.

## Adopting the flow in a repository that had develop

A repository coming from the two-branch flow (develop integrates, main publishes) has work
accumulated on `develop` that `main` has not received yet. The transition is **an act of the
maintainer**: one last `develop → main` PR publishes the accumulation in one go, and from it on
develop becomes orphaned and the single-branch flow governs. The new release (with no
`develop → main` merge) does not publish that accumulation — the transition uses the very route the
new flow adopts, the PR.

A spec's `branch.base` is stamped once, at the start of the work, and never re-inferred afterwards
— see [plan-git-record.md](../workflows/plan-git-record.md). A spec in flight with `base: develop`
follows the write-once record through to conclusion; only the specs cut after the transition are
born with the primary as their base.

## Publication, in two halves

- **What the release is** — patch, minor or major; whether it is worth publishing now; what changes
  for whoever installs it — is **human judgment**, conducted by a dedicated command. That judgment
  is not automatable: see [versioning-release.md](../ci-cd/versioning-release.md) on why a
  versioning policy stays out of scope.
- **How the release is executed** — the artifacts' lockstep and the tag, mechanically — is the
  `cq specs release` verb. No string surgery, covered by the test suite.

## Publication is always local

The bump, the commit and the tag happen on the primary branch, with no release PR. A local act lets
the maintainer decide "I publish now" without depending on any external review: each spec's review
already happened in its entry PR, and the release only chooses when the accumulation becomes a
version.

## The consumer changes nothing

A marketplace accepts a `ref` — branch, tag or commit — and, in its absence, resolves through the
repository's default branch. `main` is that default and receives everything the repo publishes;
whoever already installed (with `ref` or without) keeps receiving what `main` carries, without
touching anything.
