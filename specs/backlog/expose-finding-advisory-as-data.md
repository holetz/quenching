---
type: task
title: Expose a finding's advisory/blocking status as data in okf-validate --json
description: Found by the docs-verification-layer end-of-plan review — "stale-doc is advisory" is restated in five files and twelve places, while the JSON carries no field a skill can branch on
timestamp: 2026-07-25
tags: [docs, validator, conformance]
---

# Expose a finding's advisory/blocking status as data in `okf-validate --json`

`okf-validate.py --json` emits `severity`, `path`, `code`, `message`. Whether a WARN is
**must-fix** (`resource-self`, `index-broken-link`, …) or **advisory** (`stale-doc`) is not in the
payload — it is carried in prose, restated in **five files, twelve places**: `conformance.md` (×3),
`quenching-docs-status/SKILL.md` (×5), `cycle.md`, `bundle-verification.md`, and the validator's
own module docstring (×2).

This is exactly the pattern the plan that found it wrote a standard against.
`docs/standards/quality/bundle-verification.md` says an invariant restated in more than two skills
is owed a **deterministic check** rather than a third restatement — and the same plan then produced
twelve restatements of one rule. It is also at odds with the front's stated principle that skills
branch on **data, never prose**.

The shape to consider is one field per finding — `"advisory": true`, or a `blocking` boolean
derived from the code — so a skill's verify gate filters mechanically instead of every skill
remembering which codes to exclude. The prose it replaces should then be **cut**, not kept
alongside, per that standard's own corollary.

Worth weighing at pickup: it changes the `--json` contract, so any consumer reading the payload
positionally would need checking, and the severity vocabulary (`ERROR`/`WARN`) may be the better
place to express it than a parallel field.
