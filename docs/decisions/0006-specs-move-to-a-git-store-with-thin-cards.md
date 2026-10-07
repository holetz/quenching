---
type: decision
title: Specs move from tracker bodies to a git store with thin cards
description: Why the canonical spec document moved from the issue or work-item body to the quenching branch, the measurements behind it, and the migration result
resource: plugins/quenching/assets/bin/quenching/specs/**
tags: [decision, history, architecture, specs]
timestamp: 2026-10-07
audience: both
authority: current
source: mapeamento-critico 01/02 and S11-S16
maintainer: quenching
---

# Specs move from tracker bodies to a git store with thin cards

The rules live in [spec-backend](../standards/architecture/spec-backend.md); this records why they
changed.

## Decision

The canonical spec document lives in `specs/<id>.md` on the `quenching` branch of the code
repository's remote. The tracker item becomes a **card**: title, summary, progress, link to the
file and `spec:*` labels, written only at lifecycle transitions. The `github` and `azure-boards`
backends stay supported and are deprecated. The 243 closed issues stay untouched as history.

## Why

The tracker body held the plan in the place a human card belongs, so every read paid a network
cost that grew with the history, a lifecycle cost about 110–125 requests, and a write had no
compare-and-swap. Git gives all three at the host that already holds the code.

## Measured

- `cq specs list` over the full front: 4.7 s against the tracker, 0.39 s on the git store.
- `cq specs next --front`: 3–15 s against the tracker, 0.08 s on the git store.
- 246 specs migrated with `cq specs migrate --to git`; the equality proof reported 0 differences
  modulo locator.
- Reading the branch tree with one `git cat-file --batch` took 0.04 s for the same front.

## Consequences

- The tracker serialisation rules (body reassembly, 65,536-character continuation comments, label
  and placement reaffirmation) apply only to the deprecated backends and are condensed in the
  standard under *Legacy tracker backends*. Their full prose is in this file's repository history
  and in [ADR 0001](0001-spec-backend-measurements.md).
- Concurrent writes to different specs both land; the same spec lands once and refuses once
  (`sp-git-stale-write`).
- A card failure never rolls back the spec (`sp-card-failed`).
- The specs-reader plugin reads the branch through a bare mirror and cannot write.
