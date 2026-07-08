# `backlog/` — the raw idea inbox

The fast, low-ceremony landing spot for an **idea** before its scope or direction is
decided — the place a thought is parked between "I thought of this" and "I'm ready to
work on it". It exists to **feed `superpowers:brainstorming`**: when an idea is ready,
brainstorming develops it into an approved design spec (`docs/superpowers/specs/…`).

**Boundary:** a *raw, undeveloped* idea — distinct from `vision/` (settled direction with
no deadline) and `decisions/` (a settled decision with considered alternatives). Each idea
carries `type: idea` and nothing more than a title, one-sentence gist, and timestamp — no
pillar, no `vision_refs`, no done-criteria (that thinking belongs in brainstorming).

## Organization

```
backlog/
  <idea-slug>.md     # one idea per file (type: idea) — flat, no pillar subfolders
```

## Lifecycle

1. **Capture** — an idea lands here in seconds (`quenching-insert`, minimal `idea` mold).
2. **Develop** — invoke `superpowers:brainstorming` on the idea; its "explore project
   context" step finds this inbox.
3. **Distill** — once brainstorming's design spec is **approved**, the idea file **leaves
   the tree** (mirroring how an implemented ADR distills into `standards/` and leaves
   `decisions/`) and the transition is recorded in the Developed ledger below. An abandoned
   brainstorming session leaves the idea in place.

## What does NOT go here

- An idea already brainstormed and distilled (remove it; log it in the Developed ledger).
- Settled direction with no deadline (→ `vision/`).
- A settled decision with considered alternatives (→ `decisions/`).

## Developed ledger

Record each idea here when brainstorming distills it and you remove the file:

| Idea | Developed into | Date |
| --- | --- | --- |
| _(none yet)_ | | |

Mold: `backlog/idea.md` (applied by `quenching-insert`).
