---
title: quality/ — data and model quality
summary: data and model quality — row checks, drift/stability, model monitoring
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/quality/`

The current/active quality standard: data quality (per-row validations), data
drift/stability, and model monitoring. One standard per file; add to
[../INDEX.md](../INDEX.md) when creating.

Boundary: this is **how we measure and ensure** quality. The model lifecycle itself
lives in [../mlops/](../mlops/README.md); data modeling lives in
[../data-modeling/](../data-modeling/README.md).

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `row-checks` · `data-drift` · `model-monitoring` · `stability`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
