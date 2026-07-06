---
title: data-modeling/ — data modeling
summary: how we model data — grain, keys, joins, catalog/schema choice
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/data-modeling/`

The current/active data modeling (the "database"): grain of each table, keys, joins,
and the criteria for choosing catalog/schema. One standard per file; add to
[../INDEX.md](../INDEX.md) when creating.

Boundary: this is **how we model** the data. Table/column names live in
[../naming/](../naming/README.md); metadata for each concrete table lives in
`catalog/`.

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `grain` · `keys` · `joins` · `schema-catalog-choice` · `historization`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
