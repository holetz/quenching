---
title: standards/ — current/active reference (our contracts)
summary: the current/active contracts and conventions of this repo — one standard per file, subject subfolders, indexed by INDEX.md
audience: both
authority: current
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `standards/` — current/active reference, OUR contracts

Here lives the current/active **standard/contract** — "how it should be and why",
versioned, the shared source of truth. One standard per file; subfolder names by
**subject**. Distinct from `reference/` (facts about what we consume, external) and
from `catalog/` (our data). Vision does not live here (→ `vision/`); open
decisions do not live here (→ `decisions/`).

We keep only the subtopics that apply to the repo, and within each subtopic break the
standards **one concept per file** by considering the candidate sub-standards catalog
(spec in `references/docs-taxonomy.md`) — a **consideration** checklist, evidence-gated
generation, recorded deferral, **not** a blind generate list (completeness of what
fits). Every current doc goes into [INDEX.md](INDEX.md) — the layer index must list
exactly what exists (an index that lies = Drifted).

## Subtopics

| Subfolder | What it governs |
| --- | --- |
| [architecture/](architecture/README.md) | system structure + architectural patterns (patterns live here) |
| [code/](code/README.md) | code conventions, imports, lint, pins, SYMBOL naming |
| [naming/](naming/README.md) | DATA naming (tables/columns/descriptions) |
| [data-modeling/](data-modeling/README.md) | grain, key, joins, catalog/schema choice |
| [ci-cd/](ci-cd/README.md) | build/deploy, "code defines YAML", manifest generation |
| [workflows/](workflows/README.md) | job/task/schema framework, job parameters |
| [mlops/](mlops/README.md) | model lifecycle, lineage, regulatory interface |
| [quality/](quality/README.md) | data quality, drift/stability, model monitoring |
| [platform/](platform/README.md) | deploy targets, permissions/governance, external services |

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
