# Dimension 3 · Vision

Vision is **where the repo is heading** — the target state and the "what and why" of
it, with no timeline. Its canonical home is `docs/vision/`, a folder segmented by area
(one shell per pillar), not a single `VISION.md`.

> **Canonical home — `docs/vision/` · Fixed (canonical).** A single root `VISION.md` or
> `ROADMAP.md` is a variant to migrate, with your OK. See
> [Fixed vs. adaptive](../architecture.md).

## Why it belongs in the method

Vision is a different *kind* of knowledge from the current standard. In Diátaxis terms
it is **explanation** — the reasoning about where the work is going — and mixing it into
the reference layer ("how it is today") is exactly the boundary error that makes a
knowledge base untrustworthy ([Diátaxis](https://diataxis.fr/)). Keeping direction in its
own home is also what lets **spec-driven development** work: intent and target state are
captured *before* implementation, so the code can be rebuilt from the stated direction
rather than the direction being reverse-engineered from the code
([Spec-driven development — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices)).

The discipline the method enforces is **no deadlines**. Vision with dates becomes a
backlog ([4](04-backlog.md)); vision that already shipped becomes a standard
([2](02-standards.md)). Segmenting by pillar keeps the pillars stable while the
work underneath them churns.

## What "good" looks like

- One shell per area/pillar, each starting with a comment that declares the pillar.
- **No milestones, dates or ordering** — direction has no deadline.
- Explicit non-goals.
- What already became reality has been distilled out to `standards/`.

## How it drifts

- **Dates or milestones** infiltrated — it has started to be a roadmap.
- **Became a backlog** — a task list instead of a target state.
- **Outdated vs. reality** — something already current still listed as a goal.
- **Single `VISION.md`** instead of the segmented folder.

## How the method closes the gap

This is a **human content decision** — the method **proposes** the diff (segment the
single `VISION.md` into pillar shells, move "still missing" to `backlog/`, distill reality
to `standards/`) but never writes the direction itself. The `vision/` skeleton ships as
part of the `docs/` scaffold — see [Bundled artifacts](../../plugin/artifacts.md).

## Sources

- [Diátaxis — A systematic framework for technical documentation](https://diataxis.fr/) — accessed 2026-06-28
- [Spec-driven development: unpacking one of 2025's key new engineering practices — Thoughtworks](https://www.thoughtworks.com/en-us/insights/blog/agile-engineering-practices/spec-driven-development-unpacking-2025-new-engineering-practices) — 2025
- [Understanding Spec-Driven Development — Martin Fowler](https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html) — 2025
