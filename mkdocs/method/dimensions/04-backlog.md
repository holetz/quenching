# Dimension 4 · Backlog

The backlog is the tracked list of **what's still missing**, organized by pillar or area.
It is the bridge between direction (where we're going) and decisions (what we're weighing).

> **Canonical home — `docs/backlog/` · Fixed (canonical).** Converge a stray `TODO.md` or
> issue-dump to this home, with your OK. See [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

The backlog exists so that "not done yet" has a home that is **neither** direction
**nor** a decision. In Diátaxis terms it is the **how-to** quadrant of pending work —
goal-oriented, actionable — and keeping it separate is what stops `vision/` from rotting
into a task list and an ADR from doubling as a tracker ([Diátaxis](https://diataxis.fr/)).
It is also the natural counterpart to spec-driven work: the gap between the stated target
state and what the repo actually has is *exactly* the backlog
([Spec-driven development — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)).

The method's hygiene rule is that a **completed item leaves the tree** — git keeps the
history, so a backlog that accumulates done items is just noise the agent has to wade
through. Each item references the direction it serves, so the "why" is always one hop away.

## What "good" looks like

- A tree by pillar; each item references its direction (e.g. a `vision_refs` pointer).
- A **completed item is removed** (history stays in git), not checked off in place.
- No deadlines or hard ordering — priority is judgement, not a fixed sequence.

## How it drifts

- **Completed items accumulating** instead of leaving.
- **Deadlines / ordering** baked in.
- **Duplicates an ADR** — a decision masquerading as a backlog item.
- **No reference to direction** — orphaned work with no "why".

## How the method closes the gap

It removes completed items and creates missing ones with a direction reference. The payload
is the `quenching-docs` skill plus the `docs/backlog/` scaffold and a backlog-item template
— see [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Diátaxis — A systematic framework for technical documentation](https://diataxis.fr/) — accessed 2026-06-28
- [Spec-driven development: unpacking one of 2025's key new engineering practices — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices) — 2025
