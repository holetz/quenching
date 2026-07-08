---
type: decision          # OKF concept type — non-empty
title: <the decision in one sentence>
description: <one sentence — what is being decided and why it is open>
resource: <the scope/component the decision affects — path / glob / FQN>
timestamp: <ISO 8601 — e.g. 2026-07-06>
status: proposed        # proposed | in-debate | accepted | implemented (→ distill to standards/ and remove)
audience: both
authority: background    # background while open; on implementation the content distills to standards/ (current) and this ADR leaves the tree
vision_refs: [<vision area this decision serves>]
source: <author/team>
maintainer: <owner>
---

# ADR NNNN — <title>

## Context
<the problem; the forces at play. NOT the implementation "how".>

## Considered alternatives
1. <option A> — pros / cons
2. <option B> — pros / cons

## Decision
<the chosen option and why.>

## Consequences
<what changes; what remains open.>

<!-- MOLD (claude-quenching · ADR) → becomes `decisions/NNNN-slug.md` (one ADR per file, so
     `decisions/index.md` stays a pure listing). On IMPLEMENTATION: distill the content into
     the standards layer (type: standard, authority: current), REMOVE this file, and record
     the trail in the "Distilled ledger" of decisions/index.md. History lives in git. -->
