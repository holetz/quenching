---
type: task              # OKF concept type — non-empty
title: <one-line name of the task>
description: <one sentence — the gist>
timestamp: <ISO 8601 — e.g. 2026-07-14>
tags: [<theme>, ...]                   # OPTIONAL — the task's theme(s), normalized against tags already in the backlog
priority: <critical|high|medium|low>   # OPTIONAL — absent = untriaged (a valid state; triage fills it)
---

# <task title>

<1–3 sentences: what the task is, why it might matter, any seed context.
No done-criteria, no vision_refs, no estimates — that thinking happens in the
OpenSpec cycle (`openspec-explore` / `openspec-propose`) or at execution, not here.>

<!-- MOLD (claude-quenching · backlog task) → becomes `backlog/<task-slug>.md`.
     `backlog/` is the TASK INBOX: the fast, low-ceremony landing spot for a unit of work —
     raw (it needs the OpenSpec cycle to be developed) or already clear in scope — parked
     between "I thought of this" and "I'm working on this". `tags`/`priority` are OPTIONAL:
     stamp them only when the human states them inline, and DROP the lines otherwise — a task
     without `priority` is untriaged, a valid state `quenching-backlog-triage` exists to fill.
     `resource` is intentionally omitted — nothing is built yet to point at (the resulting
     `missing-resource` WARN is expected, not a defect). Once the task is developed into an
     OpenSpec change with apply-ready artifacts (`openspec/changes/<name>/`) or done, the file
     LEAVES the tree and the transition is recorded in `backlog/index.md`'s Completed ledger
     (mirroring how an implemented ADR distills into `standards/` and leaves `decisions/`). -->
