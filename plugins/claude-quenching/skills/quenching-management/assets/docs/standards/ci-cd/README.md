---
title: ci-cd/ — build, deploy and generation
summary: build/deploy process — CI, "code defines YAML", manifest generation
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

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `build` · `deploy` · `manifest-generation` · `pipeline-stages` · `versioning-release`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
