# `backlog/` — the task inbox

The fast, low-ceremony landing spot for a **task** — a unit of work captured in seconds,
raw (it needs the plan cycle before it becomes work) or already clear in scope —
parked between "I thought of this" and "I'm working on this". It is a **quenching-managed**
sibling of the plan folders and `archive/` in the `specs/` tree, **outside** the
`docs/` OKF bundle: a raw task seeds a **plan** — `quenching-specs-explore` thinks it
through and `quenching-specs-plan-propose` develops it into a plan with apply-ready artifacts
(`specs/<name>/` — proposal, optional design, tasks); a task already clear in
scope goes straight to execution.

**Boundary:** a *parked* unit of work — distinct from `docs/vision/` (settled direction with
no deadline). Each task carries `type: task`, a title, a one-sentence gist, and a timestamp;
`tags` (themes), `priority` (`critical|high|medium|low`), and `complexity` (a rough size in
development hours) are **optional** — a task without `priority` is **untriaged**, a valid state
`quenching-specs-backlog-triage` exists to fill. No done-criteria, no `vision_refs`, no detailed
planning (that thinking belongs to the plan cycle or execution) — `complexity` is the one
rough estimate that may be stamped at capture.

## Organization

```
backlog/
  <task-slug>.md     # one task per file (type: task) — flat, no subfolders
```

## Lifecycle

1. **Capture** — a task lands here in seconds (`quenching-specs-backlog-add`; minimal `task` mold —
   priority/tags only when stated).
2. **Triage (optional)** — `quenching-specs-backlog-triage` proposes priority/tags in one
   plan → one OK sweep; a task may also be born triaged (stated inline at capture).
3. **Develop / execute** — the plan cycle (`quenching-specs-explore` / `quenching-specs-plan-propose`)
   for raw tasks; direct execution for tasks already clear in scope.
4. **Leave the tree** — once developed into a plan with apply-ready artifacts or done,
   the file is **removed** and the transition recorded in the Completed ledger below.
   Removal happens on completion/approval, never on triage; an abandoned development
   leaves the task in place.

## What does NOT go here

- A task already developed or done (remove it; log it in the Completed ledger).
- Settled direction with no deadline (→ `docs/vision/`).

## Current tasks

<!-- BEGIN GENERATED: rebuilt from the tasks' frontmatter by `specs.py backlog reindex`
     (called by `quenching-specs-backlog-add`/`quenching-specs-backlog-triage`) — DO NOT edit
     by hand. Content, in order:
       **N tasks** · X critical · Y high · Z medium · W low · K untriaged
       one table per priority level (Critical → High → Medium → Low → Untriaged; empty
       groups omitted), columns `Task | Description | Tags | Complexity | Since` (Complexity =
       the task's `complexity` in dev hours rendered `Nh`, or `—` when absent; Since = the
       task's `timestamp`), rows OLDEST-FIRST within each group so stale tasks surface;
       then "By theme": alphabetical bullets `**<tag>** (n): [task-a](task-a.md), …`
       (a task with two tags appears under both).
-->
_(no tasks parked — this listing is regenerated deterministically from `backlog/*.md` frontmatter)_
<!-- END GENERATED -->

## Completed ledger

Record each task here when it is completed — or its plan supersedes it — and
you remove the file (curated history, kept **outside** the generated zone):

| Task | Outcome | Date |
| --- | --- | --- |
| _(none yet)_ | | |

Mold: `backlog/task.md` (applied by `quenching-specs-backlog-add`).
