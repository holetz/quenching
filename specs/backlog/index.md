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
**6 tasks** · 0 critical · 0 high · 0 medium · 0 low · 6 untriaged

#### Untriaged

| Task | Description | Tags | Complexity | Since |
| --- | --- | --- | --- | --- |
| [Add provenance and idempotent re-ingestion to quenching-docs-import](add-import-provenance.md) | Deferred from the docs-verification-layer plan — source_uri plus a content hash so a changed source is detectable and a re-import enriches instead of duplicating | docs, import, provenance | — | 2026-07-25 |
| [Decide whether AGENTS.md becomes the default harness target](decide-agents-md-harness-default.md) | Deferred from the docs-verification-layer plan — AGENTS.md is now a Linux Foundation open spec with wide adoption, while the harness molds ship only claude-root.md and claude-subfolder.md | docs, harness, templates | — | 2026-07-25 |
| [Decide whether quenching-specs-plan-quick is still needed](decide-plan-quick-skill.md) | Open decision from the refine-and-execute-specs-flow plan — re-evaluate the express lane after two weeks of using the chained path | specs, skills, taxonomy | — | 2026-07-25 |
| [Decide whether sp-unrefined should escalate to error](decide-sp-unrefined-severity.md) | Open decision from the refine-and-execute-specs-flow plan — revisit the warning's severity once there is evidence about unrefined plans | specs, validation | — | 2026-07-25 |
| [Expose a finding's advisory/blocking status as data in okf-validate --json](expose-finding-advisory-as-data.md) | Found by the docs-verification-layer end-of-plan review — "stale-doc is advisory" is restated in five files and twelve places, while the JSON carries no field a skill can branch on | docs, validator, conformance | — | 2026-07-25 |
| [Split the backlog-zone renderer out of specs.py](split-specs-py-backlog-renderer.md) | specs.py has passed the ~1,200-line threshold its own design set for splitting, and is now 1,388 lines | specs, tooling, maintainability | — | 2026-07-25 |

#### By theme

- **conformance** (1): [expose-finding-advisory-as-data](expose-finding-advisory-as-data.md)
- **docs** (3): [add-import-provenance](add-import-provenance.md), [decide-agents-md-harness-default](decide-agents-md-harness-default.md), [expose-finding-advisory-as-data](expose-finding-advisory-as-data.md)
- **harness** (1): [decide-agents-md-harness-default](decide-agents-md-harness-default.md)
- **import** (1): [add-import-provenance](add-import-provenance.md)
- **maintainability** (1): [split-specs-py-backlog-renderer](split-specs-py-backlog-renderer.md)
- **provenance** (1): [add-import-provenance](add-import-provenance.md)
- **skills** (1): [decide-plan-quick-skill](decide-plan-quick-skill.md)
- **specs** (3): [decide-plan-quick-skill](decide-plan-quick-skill.md), [decide-sp-unrefined-severity](decide-sp-unrefined-severity.md), [split-specs-py-backlog-renderer](split-specs-py-backlog-renderer.md)
- **taxonomy** (1): [decide-plan-quick-skill](decide-plan-quick-skill.md)
- **templates** (1): [decide-agents-md-harness-default](decide-agents-md-harness-default.md)
- **tooling** (1): [split-specs-py-backlog-renderer](split-specs-py-backlog-renderer.md)
- **validation** (1): [decide-sp-unrefined-severity](decide-sp-unrefined-severity.md)
- **validator** (1): [expose-finding-advisory-as-data](expose-finding-advisory-as-data.md)
<!-- END GENERATED -->

## Completed ledger

Record each task here when it is completed — or its plan supersedes it — and
you remove the file (curated history, kept **outside** the generated zone):

| Task | Outcome | Date |
| --- | --- | --- |
| _(none yet)_ | | |

Mold: `backlog/task.md` (applied by `quenching-specs-backlog-add`).
