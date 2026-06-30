---
title: guides/ — how-to and tutorials
audience: both
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `guides/` — how-to + tutorials

Step-by-step procedures (how-to: "how do I do X") and learning material
(tutorial) for team members. Procedure, not contract.

Boundary: how-to ("how do I do X") ≠ reference ("what it is / how it is today", →
`standards/`) ≠ explanation ("why", → `decisions/` / `vision/`). If a guide
describes the current rule instead of teaching how to execute it, its place is
`standards/`.

## How to organize guides

This home keeps the team's guides. **Which** guides exist and **how** they are
organized is this repo's decision — the skeleton does not ship any ready-made guide.

- **Prefer folder/subfolder structure by subject/area** (subject-first), in
  whatever way makes sense here — for example `deploy/`, `pipelines/`,
  `local-env/`. Standalone guides can live as `.md` files directly in this folder.
- Subfolders by **subject** are welcome. What is **not** reserved is a
  subfolder by **audience** (an `onboarding/` silo): "onboarding" is an audience
  cut, not a subject, and almost every how-to already serves as an entry point
  for newcomers. An onboarding guide, if the repo wants one, is just another guide.

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
