---
title: backlog/ — what is missing, by pillar
audience: both
authority: background
source: <owning team>
maintainer: <owning team>
updated: 2026-06-29
---

# `backlog/` — what is missing

Lists **only what is missing**, by pillar/area. A completed item **leaves the tree**
(history stays in git; the change distills to `standards/`) — mirrors how an
implemented ADR is removed. **No deadline, milestone, or order.**

## Organization

```
backlog/
  <pillar>/
    <item-slug>.md     # frontmatter: title, pilar, vision_refs
```

Each item references the `vision/` area it unlocks (`vision_refs`).

## What does NOT go here

- An already-done item (remove it).
- Direction/aspiration (goes in `vision/`).
- Open decision with alternatives (goes in `decisions/`).

> _Skeleton installed by `quenching-management` — spec in
> `references/docs-taxonomy.md`._
