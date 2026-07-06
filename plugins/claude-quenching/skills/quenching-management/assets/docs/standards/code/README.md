---
title: code/ — code conventions
summary: code conventions — imports, lint/format, dependency pins, symbol naming and related — one concept per file
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/code/`

Current/active code conventions: imports, lint/format, dependency pins, validation,
and **SYMBOL naming** (classes, functions, variables). One standard per file; add to
[../INDEX.md](../INDEX.md) when creating.

Boundary: `code/` governs **symbols** (code). **Data** naming (tables,
columns, descriptions) lives in [../naming/](../naming/README.md) — do not confuse.

## Candidate sub-standards

Break this subject into **one concept per file** (files, not sub-folders). The method
**evaluates** each candidate against the repo and generates the applicable ones
(`file:line`-anchored, full mandatory OKF frontmatter); the full non-closed catalog is
the single source in `references/docs-taxonomy.md` (§ Candidate sub-standards per
subject). For this subject: `imports` · `format-lint` · `typing` · `symbol-naming` · `dependencies-pins` · `error-handling` · `logging` · `docstrings` · `testing-conventions`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads (a **consideration** checklist, evidence-gated
generation, recorded deferral — not a blind generate list). Record each considered
candidate **not** generated here as a deferral with a one-line why; a subject is "done"
only when every candidate is **present or listed here**.

- _(none yet — fill on population)_

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
