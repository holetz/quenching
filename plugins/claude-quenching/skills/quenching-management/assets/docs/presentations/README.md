---
title: presentations/ — human deliverables (binary)
audience: human
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `presentations/` — human deliverables

Our **visual deliverables**: slides, source diagrams, and reports. Binaries that
belong in `docs/` but **not** in the normative layer.

**The LLM never opens the binary** — it reads the **sidecar `.md`** alongside it
(summary + key points + `binary:` pointing to the source). The `quenching-docs` skill
applies the sidecar mold. The binary is `audience: human`; the sidecar is
`audience: agent` / `authority: background`.

Boundary: `presentations/` = "our **visual** deliverables" — distinct from
`reference/` (external factual reference). Content that became current/active
**distills into `standards/`**.

## Subfolders

| Subfolder | What lives there |
| --- | --- |
| [slides/](slides/README.md) | decks (.pptx), onboarding exports |
| [diagrams/](diagrams/README.md) | diagrams — prefer diagrams-as-code |
| [reports/](reports/README.md) | stakeholder reports/PDFs |

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
