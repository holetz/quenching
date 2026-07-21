# The `openspec/backlog/index.md` DERIVED zone + the on-write self-check

The backlog lives at **`openspec/backlog/`** — a quenching-managed subfolder of the
`openspec/` tree, **outside** the OKF `docs/` bundle. Because it is outside the bundle, the
OKF validator (`okf-validate.py`, docs-scoped) never scans it and the OKF insert procedure in
[`../../quenching-add/references/homes.md`](../../quenching-add/references/homes.md) does
**not** own its index zone. This file is the single owner of the backlog index-zone format and
the backlog skills' own on-write self-check; both `openspec-backlog` and
`openspec-backlog-triage` cite it. The log entry a capture/triage appends still lands in the
bundle's `docs/log.md` (the bundle log records the cross-boundary event).

## The DERIVED zone in `backlog/index.md`

`backlog/index.md` carries a **DERIVED zone**: rebuild only what is between
`<!-- BEGIN GENERATED -->` / `<!-- END GENERATED -->`, exclusively from `backlog/*.md`
frontmatter (`title`/`description`/`tags`/`priority`/`complexity`/`timestamp`):

- a summary line — `**N tasks** · X critical · Y high · Z medium · W low · K untriaged`;
- one `Task | Description | Tags | Complexity | Since` table per priority level
  (Critical → High → Medium → Low → Untriaged; empty groups omitted; rows **oldest-first**
  within each group so stale tasks surface; Complexity = the task's `complexity` in dev hours
  rendered `Nh`, or `—` when absent; Since = the task's `timestamp`);
- then alphabetical "By theme" bullets — `**<tag>** (n): [task-a](task-a.md), …` — a task
  lists under each of its tags.

A task with an unknown `priority` value renders under Untriaged. Never hand-edit inside the
markers; the **Completed ledger** stays OUTSIDE the zone (curated by hand, rows only on
completion). If a target's `backlog/index.md` predates the markers, install them without
touching the fixed prose around them.

## The on-write self-check (replaces hook coverage)

Since the OKF hook does not cover `openspec/backlog/`, each backlog skill self-checks every
task it writes as a skill-internal gate:

- the task's frontmatter is **parseable YAML** with a **non-empty `type`** (`type: task`);
- the DERIVED zone matches the tasks on disk and every zone link resolves;
- `index.md` stays a frontmatter-free listing and the Completed ledger was not touched inside
  the zone.

## Appending to the bundle log

Newest first, in the bundle's `docs/log.md` (per §Appending to `log.md` in
[`../../quenching-add/references/homes.md`](../../quenching-add/references/homes.md)):
`**Creation**: [<title>](/openspec/backlog/<task-slug>.md) — <one line>` for a capture, a
single consolidated `**Update**: backlog — triaged N tasks (…)` for a triage sweep.
