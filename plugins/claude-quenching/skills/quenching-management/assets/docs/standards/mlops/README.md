---
title: mlops/ — model lifecycle
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

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
