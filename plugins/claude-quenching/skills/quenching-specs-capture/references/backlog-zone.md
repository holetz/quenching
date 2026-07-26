# The `specs/backlog/index.md` DERIVED zone + the on-write check

The backlog lives at **`specs/backlog/`** — a quenching-managed sibling of the plan folders and
`archive/`, **outside** the OKF `docs/` bundle. Because it is outside the bundle, the OKF hook
(configured with `docsDir: docs`) never fires on it and the OKF insert procedure in
[`../../quenching-docs-add/references/homes.md`](../../quenching-docs-add/references/homes.md) does
**not** own its index zone. This file is the single owner of the backlog index-zone contract and
the backlog skills' own on-write check; both `quenching-specs-capture` and
`quenching-specs-triage` cite it. The log entry a capture/triage appends still lands in the
bundle's `docs/log.md` (the bundle log records the cross-boundary event).

## The DERIVED zone — owned by `specs.py backlog reindex`

`backlog/index.md` carries a **DERIVED zone** between `<!-- BEGIN GENERATED -->` /
`<!-- END GENERATED -->`. The backlog skills **do not regenerate it by hand** — they call the
tool, which owns the format:

```bash
specs.py backlog reindex          # resolve the script per §Resolving the tool below
```

`reindex` rebuilds the zone **deterministically from `backlog/*.md` frontmatter**
(`title`/`description`/`tags`/`priority`/`complexity`/`timestamp`), anchoring on the existing
markers (or on the `## Current tasks` heading when the markers are absent — that is how
`sp-zone-missing` is repaired), and **never touches the fixed prose or the Completed ledger**
outside the markers. What the tool produces, in order:

- a summary line — `**N tasks** · X critical · Y high · Z medium · W low · K untriaged`;
- one `#### <Priority>` section with a `Task | Description | Tags | Complexity | Since` table per
  priority level (Critical → High → Medium → Low → Untriaged; empty groups omitted; rows
  **oldest-first** by `timestamp` within each group so stale tasks surface; Complexity = the task's
  `complexity` rendered `Nh`, or `—`; Since = the task's `timestamp`);
- a `#### By theme` section — alphabetical bullets `**<tag>** (n): [task-a](task-a.md), …`, a task
  listed under each of its tags.

A task with an unknown `priority` renders under Untriaged. When there are no tasks, the zone is the
single line `_(no tasks parked — …)_`. Because the render is deterministic, `reindex` reports
`changed: false` when the zone already matches disk — the skill reads that JSON to know whether it
wrote anything. Never hand-edit inside the markers; the **Completed ledger** stays OUTSIDE the zone
(curated by hand, rows only on completion).

## The on-write check — run the validator, do not re-implement it

The backlog sits outside the `docs/` bundle, so the OKF `PostToolUse`/`Stop` hook (docs-scoped by
config) never fires on it. `okf-validate.py` takes its root as an argument, and every rule the
backlog needs is already in its conformance core, so each backlog skill closes with the real check:

```bash
okf-validate.py specs/backlog --listing-root
```

`--listing-root` says "this tree is a quenching-managed listing, not an OKF bundle root": the
`index.md` is held to the plain-listing rule (frontmatter-free — ERROR if it carries any) instead
of the bundle-root rule that expects `okf_version`, and the `bundle-no-index` SHOULD is dropped.
Everything else applies unchanged — a task's frontmatter parseable with a non-empty `type` (ERROR),
no index carrying a `type` (ERROR), every index link resolving (`index-broken-link`), no task the
zone forgot to list (`index-orphan`). `resource` is not warned for `type: task`, since the mold
omits it on purpose.

**Exit 0 with no `index-broken-link` / `index-orphan` finding is the pass condition** — exit 0
alone does not prove the WARN-level structural checks clear, so read the findings.

One thing the validator does not know, which stays the skill's responsibility:

- the **Completed ledger** outside the markers was not touched (the zone-matches-disk property is
  now `specs.py backlog reindex`'s guarantee, not a hand comparison).

## Resolving the tool

Both `specs.py` and `okf-validate.py` resolve by the same fallback: the plugin path
(`${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py`, `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`)
first, then a copy installed into the target's `.claude/hooks/`, and if neither resolves, the
declared **manual** fallback — check those same rules by hand and **say in the report that the
check was manual**, never silently skip it. `quenching-specs-align` installs `specs.py` into a
target's `.claude/hooks/`; `quenching-docs-align` installs `okf-validate.py` and the hook config.

## Appending to the bundle log

Newest first, in the bundle's `docs/log.md` (per §Appending to `log.md` in
[`../../quenching-docs-add/references/homes.md`](../../quenching-docs-add/references/homes.md)):
`**Creation**: [<title>](/specs/backlog/<task-slug>.md) — <one line>` for a capture, a single
consolidated `**Update**: backlog — triaged N tasks (…)` for a triage sweep.
