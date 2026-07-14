# `vision/` — direction, segmented by area

Where the platform is heading (target state, "the what and why"), **without a schedule**.
The vision is **segmented by area**: one file per pillar/area (`<area>.md`, `type: vision`),
not a single `VISION.md`.

**Boundary:** direction **carries no deadline, milestone, or order**. A **raw task** toward
it lands in [backlog/](/docs/backlog/index.md) (the task inbox); what **has already become
reality** distills into [standards/](/docs/standards/index.md); an open decision about *how*
lives in [decisions/](/docs/decisions/index.md).

## Organization

```
vision/
  <area>.md        # one shell per area (type: vision) — e.g. platform.md, data.md
```

Mold: `vision/area.md` (applied by `quenching-insert`). This home starts empty — the repo
declares its areas.
