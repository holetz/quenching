---
title: decisions/ — open decisions (ADR)
audience: both
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `decisions/` — ADRs, open decisions

An ADR records a decision **not yet implemented**, under debate, with considered
alternatives. When **implementing**, the content **distills into `standards/`** and
the ADR **leaves the tree** — git preserves the history and the "Distilled" ledger
below records the trail. A decision already current/active does not sit here.

## Organization

```
decisions/
  NNNN-slug/
    README.md      # frontmatter: title, status, vision_refs, updated
```

## Lifecycle

`proposed → in-debate → accepted → implemented(→distill to standards/ and remove)`

An ADR that is accepted **and implemented** but remains in the tree is Drifted:
distill and remove.

## Distilled Ledger

<!-- When removing an implemented ADR, record it here: -->
| ADR | Decision | Distilled to | Date |
| --- | --- | --- | --- |
| <NNNN> | <title> | <standards/ doc> | <YYYY-MM-DD> |

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
