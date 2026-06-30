---
title: diagrams/ — diagrams
audience: human
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `presentations/diagrams/`

Diagrams. **Prefer diagrams-as-code** (`.drawio`, `.puml`, `.mermaid`): the text
source is versionable and readable by the agent. For binary/image sources, keep a
**sidecar `.md`** alongside (mold applied by the `quenching-docs` skill) describing
the flow; the LLM reads the sidecar, not the image.

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
