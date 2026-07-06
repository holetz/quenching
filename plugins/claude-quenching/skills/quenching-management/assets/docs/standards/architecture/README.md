---
title: architecture/ — system structure + architectural patterns
summary: system structure — layers, modules, boundaries — and the current architectural patterns
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/architecture/`

The system structure (layers, modules, boundaries) and the current/active
**architectural patterns**. **`patterns` lives here** — there is no `docs/patterns/`;
a design/architecture pattern is a doc in this home. One standard per file; add to
[../INDEX.md](../INDEX.md) when creating.

Boundary: this is the shape of the system (the structural why). Code conventions
(imports, lint, symbols) live in [../code/](../code/README.md); decisions still
open live in `decisions/`.

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `layers` · `module-boundaries` · `patterns` · `dependency-direction` · `integration-points`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
