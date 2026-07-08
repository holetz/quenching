# `decisions/` — ADRs, open decisions

An ADR records a decision **not yet implemented**, under debate, with considered
alternatives. When implemented, its content **distills into
[standards/](/docs/standards/index.md)** and the ADR **leaves the tree** — git keeps the
history and the "Distilled" ledger below records the trail. A decision already
current/active does not sit here.

**Boundary:** open decision (the *why we chose*) — distinct from `standards/` (the
current contract) and `vision/` (direction). Each ADR carries `type: decision`.

## Organization

```
decisions/
  NNNN-slug.md     # one ADR per file (type: decision) — e.g. 0007-adopt-uc.md
```

One ADR per file (MADR's single-file default), so `index.md` stays a pure listing (no
`type`). If an ADR needs attachments, use a folder `NNNN-slug/` whose `index.md` lists the
parts and whose body is a concept file (e.g. `NNNN-slug/decision.md`, `type: decision`) —
never put the `type` on the folder's `index.md`. Lifecycle:
`proposed → in-debate → accepted → implemented (→ distill to standards/ and remove)`.

## Distilled ledger

Record each implemented ADR here when you remove it:

| ADR | Decision | Distilled to | Date |
| --- | --- | --- | --- |
| _(none yet)_ | | | |

Mold: `decisions/adr.md` (applied by `quenching-insert`).
