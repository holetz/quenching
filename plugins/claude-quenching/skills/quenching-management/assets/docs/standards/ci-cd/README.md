---
title: ci-cd/ — build, deploy and generation
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/ci-cd/`

The current/active build/deploy process: how CI runs, the **"code defines YAML"**
rule (generated artifacts never edited by hand), and manifest generation. One
standard per file; add to [../INDEX.md](../INDEX.md) when creating.

Boundary: this is the **delivery process**. The framework that defines jobs/tasks
lives in [../workflows/](../workflows/README.md); the target platform (targets,
permissions) lives in [../platform/](../platform/README.md).

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
