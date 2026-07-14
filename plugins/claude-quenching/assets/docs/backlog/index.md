# `backlog/` — the raw idea inbox

The fast, low-ceremony landing spot for an **idea** before its scope or direction is
decided — the place a thought is parked between "I thought of this" and "I'm ready to
work on it". It exists to **seed the OpenSpec cycle**: when an idea is ready,
`openspec-propose` develops it into a change with apply-ready artifacts
(`openspec/changes/<name>/` — proposal, design, delta specs, tasks).

**Boundary:** a *raw, undeveloped* idea — distinct from `vision/` (settled direction with
no deadline) and `decisions/` (a settled decision with considered alternatives). Each idea
carries `type: idea` and nothing more than a title, one-sentence gist, and timestamp — no
pillar, no `vision_refs`, no done-criteria (that thinking belongs in the OpenSpec cycle).

## Organization

```
backlog/
  <idea-slug>.md     # one idea per file (type: idea) — flat, no pillar subfolders
```

## Lifecycle

1. **Capture** — an idea lands here in seconds (`quenching-insert`, minimal `idea` mold).
2. **Develop** — `openspec-explore` thinks it through and/or `openspec-propose` uses the
   idea as the seed of a change, generating its artifacts.
3. **Distill** — once the change's artifacts are **apply-ready**, the idea file **leaves
   the tree** (mirroring how an implemented ADR distills into `standards/` and leaves
   `decisions/`) and the transition is recorded in the Developed ledger below. An abandoned
   exploration leaves the idea in place.

## What does NOT go here

- An idea already developed into an OpenSpec change (remove it; log it in the Developed
  ledger).
- Settled direction with no deadline (→ `vision/`).
- A settled decision with considered alternatives (→ `decisions/`).

## Developed ledger

Record each idea here when a change's artifacts are apply-ready and you remove the file:

| Idea | Developed into | Date |
| --- | --- | --- |
| _(none yet)_ | | |

Mold: `backlog/idea.md` (applied by `quenching-insert`).
