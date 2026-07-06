---
title: mlops/ — model lifecycle
summary: model lifecycle, lineage and our interface to the regulatory framework
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/mlops/`

The current/active MLOps standard: model lifecycle (train → register → deploy →
monitor), lineage, and **our interface** to the regulatory framework (how we
implement Res. 4.966 and related). One standard per file; add to
[../INDEX.md](../INDEX.md) when creating.

Boundary: this is **how WE implement** the regulatory requirement. The regulation
itself (the PDF of the standard) is external material and lives in
`reference/regulations/` (consumed via sidecar). Model quality/drift monitoring
lives in [../quality/](../quality/README.md).

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `model-lifecycle` · `lineage` · `experiment-tracking` · `regulatory-interface` · `serving`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
