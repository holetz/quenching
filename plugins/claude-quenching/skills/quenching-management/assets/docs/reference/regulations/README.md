---
title: regulations/ — regulatory standards
audience: agent
authority: background
source: <regulatory body>
maintainer: <owning team>
updated: 2026-06-29
---

# `reference/regulations/`

External regulatory standards (PDFs of resolutions, circulars, norms). These are
binaries of **low signal per token** if ingested directly — so the LLM consumes
them via a **sidecar `.md`** alongside each file (summary + key points +
`binary:` pointing to the source), **never opening the binary**. See the method's
sidecar mold (skill `quenching-docs`).

Boundary: the regulation itself lives here (what the regulator requires). **Our
interface** to it — how we implement the rule — lives in `standards/mlops/`.

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
