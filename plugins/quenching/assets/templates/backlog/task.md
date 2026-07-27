---
type: task              # OKF concept type — non-empty
title: <one-line name of the task>
description: <one sentence — the gist>
timestamp: <ISO 8601 — e.g. 2026-07-14>
tags: [<theme>, ...]                   # OPTIONAL — the task's theme(s), normalized against tags already in the backlog
priority: <critical|high|medium|low>   # OPTIONAL — absent = untriaged (a valid state; triage fills it)
complexity: <dev hours — e.g. 8 or 4-8>   # OPTIONAL — a rough size in development hours; absent = not yet estimated
---

# <task title>

<1–3 sentences: what the task is, why it might matter, any seed context.
No done-criteria, no vision_refs, no detailed planning — that thinking happens in the
plan cycle (`/specs:develop`) or at execution. The one estimate
that may be stamped here is `complexity` — a rough size in development hours, when stated.>

<!-- MOLD (quenching · backlog task) → becomes `backlog/<task-slug>.md`.
     `backlog/` is the TASK INBOX: the fast, low-ceremony landing spot for a unit of work —
     raw (it needs the plan cycle to be developed) or already clear in scope — parked
     between "I thought of this" and "I'm working on this". `tags`/`priority`/`complexity` are
     OPTIONAL: stamp them only when the human states them inline, and DROP the lines otherwise — a
     task without `priority` is untriaged, a valid state `quenching-specs-triage` exists to fill.
     `resource` is intentionally omitted — nothing is built yet to point at. The backlog lives
     under `specs/backlog/`, OUTSIDE the OKF `docs/` bundle, so the OKF validator never scans
     it; the backlog skills self-check each task's frontmatter on write. Once the task is
     developed into a plan in `specs/` with apply-ready artifacts or
     done, the file LEAVES the tree and the transition is recorded in `backlog/index.md`'s
     Completed ledger. -->
