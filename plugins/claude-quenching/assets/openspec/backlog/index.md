# `backlog/` — the task inbox

The fast, low-ceremony landing spot for a **task** — a unit of work captured in seconds,
raw (it needs the OpenSpec cycle before it becomes work) or already clear in scope —
parked between "I thought of this" and "I'm working on this". It is a **quenching-managed**
subfolder of the `openspec/` tree (sibling of `specs/` and `changes/`), **outside** the
`docs/` OKF bundle: a raw task seeds the OpenSpec cycle — `openspec-explore` thinks it
through and `openspec-propose` develops it into a change with apply-ready artifacts
(`openspec/changes/<name>/` — proposal, design, delta specs, tasks); a task already clear in
scope goes straight to execution.

**Boundary:** a *parked* unit of work — distinct from `docs/vision/` (settled direction with
no deadline). Each task carries `type: task`, a title, a one-sentence gist, and a timestamp;
`tags` (themes), `priority` (`critical|high|medium|low`), and `complexity` (a rough size in
development hours) are **optional** — a task without `priority` is **untriaged**, a valid state
`openspec-backlog-triage` exists to fill. No done-criteria, no `vision_refs`, no detailed
planning (that thinking belongs to the OpenSpec cycle or execution) — `complexity` is the one
rough estimate that may be stamped at capture.

## Organization

```
backlog/
  <task-slug>.md     # one task per file (type: task) — flat, no subfolders
```

## Lifecycle

1. **Capture** — a task lands here in seconds (`openspec-backlog`; minimal `task` mold —
   priority/tags only when stated).
2. **Triage (optional)** — `openspec-backlog-triage` proposes priority/tags in one
   plan → one OK sweep; a task may also be born triaged (stated inline at capture).
3. **Develop / execute** — the OpenSpec cycle (`openspec-explore` / `openspec-propose`)
   for raw tasks; direct execution for tasks already clear in scope.
4. **Leave the tree** — once developed into a change with apply-ready artifacts or done,
   the file is **removed** and the transition recorded in the Completed ledger below.
   Removal happens on completion/approval, never on triage; an abandoned development
   leaves the task in place.

## What does NOT go here

- A task already developed or done (remove it; log it in the Completed ledger).
- Settled direction with no deadline (→ `docs/vision/`).

## Current tasks

<!-- BEGIN GENERATED: rebuilt from the tasks' frontmatter by `openspec-backlog`/
     `openspec-backlog-triage` — DO NOT edit by hand. Content, in order:
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

Record each task here when it is completed — or its OpenSpec change supersedes it — and
you remove the file (curated history, kept **outside** the generated zone):

| Task | Outcome | Date |
| --- | --- | --- |
| _(none yet)_ | | |

Mold: `backlog/task.md` (applied by `openspec-backlog`).
