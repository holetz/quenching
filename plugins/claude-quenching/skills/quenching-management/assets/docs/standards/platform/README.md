---
title: platform/ — platform and governance
summary: deploy targets, permissions/governance and external services
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/platform/`

The current/active platform standard: deploy targets (environments),
permissions/governance (groups, roles), and external services for the bundle/application.
One standard per file; add to [../INDEX.md](../INDEX.md) when creating.

Boundary: this is **where and under what rules** we run. How we build/deploy
lives in [../ci-cd/](../ci-cd/README.md); how we define the work lives in
[../workflows/](../workflows/README.md).

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `deploy-targets` · `permissions-governance` · `external-services` · `secrets`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
