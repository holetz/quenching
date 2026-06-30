---
title: reference/ — external reference (what we consume)
audience: agent
authority: background
source: <external origin>
maintainer: <owning team>
updated: 2026-06-29
---

# `reference/` — EXTERNAL reference material

**Factual material about what WE CONSUME** — tool docs, libraries, and regulatory
standards. External to what we produce; it is background/reference, **never**
our contract (`authority: background`).

Boundary (the subtlest one): `reference/` = "facts about what **WE CONSUME**
(external)" — distinct from `standards/` ("how **WE** do it", current/active) and
from `catalog/` ("our **data**"). Example: the Res. 4.966 regulation (the PDF of the
standard) lives in [regulations/](regulations/README.md); **our interface** to it
(how we implement it) lives in `standards/mlops/`.

## Subfolders

| Subfolder | What lives there |
| --- | --- |
| [tools/](tools/README.md) | docs for tools we use |
| [libraries/](libraries/README.md) | docs for libraries/dependencies |
| [regulations/](regulations/README.md) | regulatory standards (PDFs via sidecar) |

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
