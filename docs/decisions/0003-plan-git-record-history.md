---
type: decision
title: Plan git record history
description: Measurements behind the git record contract: the host-link default-branch rule, the in-place liveness exception and the unproven azure-boards assumption
resource: plugins/quenching/commands/git/**, plugins/quenching/assets/bin/quenching/git/**
tags: [decision, history, workflows]
timestamp: 2026-10-07
audience: both
authority: current
source: vincular-spec-a-branch-commits-e-pr; pilar-git-e-especs-agnosticas-ao-git; plan-git-record standard (history moved 2026-10-07)
maintainer: quenching
---

# Plan git record history

History moved out of [plan-git-record](../standards/workflows/plan-git-record.md). Sections are the original text.

## The in-place liveness exception, measured

MEASURED, and the reason this is written rather than assumed: when in-place work began stamping
the pair, `cq specs next` still ranked on liveness alone, and every spec built in place rose to the
top of that ranking with the reason *"you are on this branch"* whenever the session
stood on the base. The guard the code already carried — *a record whose ref is gone stops
counting* — could not fire, because nothing was ever going to remove `develop`. The shape
generalizes past this record: **an expiry condition that the sentinel value can never satisfy is
not a guard, and it fails silently in the direction of always-true.**

## closingIssuesReferences on a non-default base, measured (task 1.1)

**Measured for GitHub (task 1.1):** `Closes #<n>` only
populates `closingIssuesReferences` — the fact a caller can read back — when the PR's base *is*
that default; on any other base (this repo's own `develop`) the same keyword still cross-references
the issue but never closes it, so nothing readable exists to fall back on. The rule this forces:

## azure-boards assumption, unproven

**The same rule is assumed, not yet measured, for `azure-boards`** — its
`--work-items` link is a structurally different mechanism (an explicit API link, not keyword
parsing), so the branch restriction may not apply there at all; task 1.2 remains blocked (no
authority to create artifacts in a real corporate org from an autonomous run) and is what would
prove or break the assumption.

