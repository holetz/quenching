---
name: quenching-backlog-triage
description: >-
  Sweeps the repo's OKF backlog/ task inbox and proposes ONE consolidated triage plan — a
  priority (critical|high|medium|low) and tags for each untriaged task, grounded in
  vision/ when present — applied on a single confirmation. Use when the user asks to
  "prioritize the backlog", "triage the backlog", "groom the backlog", or "re-rank the
  tasks". Reads every task's frontmatter directly (no sub-agents — the backlog is small
  by nature), builds one table of proposals with one-line rationales, flags stale tasks
  and duplicates, re-ranks an already-triaged task only with an explicit reason, then
  applies the edits (MERGE — never silently clobber a human-set priority), regenerates
  the derived zone in backlog/index.md, and logs one consolidated update.
  Completion/removal enters the plan only when the human states a task is done — never
  inferred. Not for: capturing ONE task → quenching-backlog; developing a task into a
  change → openspec-propose.
when_to_use: >-
  prioritizing the WHOLE backlog/ inbox in one plan → one OK sweep. Capturing a single
  task is quenching-backlog; developing one into a change is openspec-propose.
allowed-tools: Read, Grep, Glob, Write, Edit
---

# quenching-backlog-triage — prioritize the task inbox

Sweeps the canonical OKF bundle's **entire** task inbox,
[`backlog/`](../../assets/docs/backlog/index.md), and proposes priorities and themes for
what is parked there — the sweep counterpart of the per-item `quenching-backlog` capture.
Unlike `quenching-knowledge-scan`, this sweep fans **no** sub-agents out: a backlog is
small by nature and each task is a few frontmatter lines, so the orchestrator reads
everything directly. The derived-zone format and the shared index/log procedure live with
`quenching-insert`
([../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)); the
`type` vocabulary and conformance rules with `quenching-align`
([../quenching-align/references/taxonomy.md](../quenching-align/references/taxonomy.md),
[.../conformance.md](../quenching-align/references/conformance.md)). Triage is an
**on-demand tool** like `quenching-enrich`/`quenching-visualize` — it is not a
`quenching-cycle` loop stage and carries no cycle-authorization exception: the plan gate
below always applies.

## Doctrine

- **Propose, don't invent.** Every proposed priority and tag traces to the task's own
  title/gist and, when present, the direction in `vision/` — each with a one-line
  rationale in the plan. Priorities only ever take `critical|high|medium|low`.
- **One plan, one OK.** Every proposal merges into ONE consolidated table before any
  write. A single confirmation approves the whole plan; partial adjustments → re-plan; a
  rejected plan applies **nothing**.
- **MERGE, never clobber.** A human-set priority is never silently overwritten — a
  re-rank of an already-triaged task enters the plan only with an explicit reason, and
  only the approved edits are applied.
- **Untriaged is a valid state.** A task the plan cannot honestly rank stays untriaged —
  no forced ranking. An invalid priority value found in a target (e.g.
  `priority: urgent`) renders under Untriaged and the plan proposes the fix.
- **Completion is stated, never inferred.** A removal + Completed-ledger row enters the
  plan only when the human says the task is done or its OpenSpec change is apply-ready.
  Triage alone never removes a task; an abandoned development leaves the task in place.
- **The zone is derived; the ledger is curated.** Rebuild only between the GENERATED
  markers per the `backlog/index.md` bullet in
  [../quenching-insert/references/homes.md](../quenching-insert/references/homes.md)
  §**Updating `index.md`**; the Completed ledger lives outside the zone and gains rows
  only for approved completions.

## Workflow

### 1. Read the backlog directly
Find `docs/backlog/` (the bundle root may be a variant — resolve it as the other skills
do); if the home is missing, stop and offer `quenching-align`, then resume. `Glob`
`backlog/*.md` and read each task's frontmatter **directly — no sub-agents**. Read
`vision/` when present to ground the proposals. Note stale tasks (old `timestamp`),
near-duplicate pairs, and any invalid `priority` value.

### 2. Build ONE triage plan
One table: `Task | Current | Proposed priority | Proposed tags | Rationale (one line)`.
Include: a proposal for every untriaged task (or an honest "stays untriaged"); re-ranks
of triaged tasks **only with an explicit reason**; staleness flags (old `Since`);
duplicate MERGE suggestions; fixes for invalid priority values; completions **only when
the human stated the task is done**. Tags normalized against the ones already in the
backlog.

### 3. One OK
Present the plan and **wait for a single confirmation**. Partial adjustments → adjust and
re-present; rejection → apply nothing and stop.

### 4. Apply exactly what was approved
Edit each task's frontmatter as listed (MERGE — fill/replace only the approved keys,
never a silent clobber). An approved duplicate MERGE moves content into the surviving
task and removes the other; an approved completion removes the file and adds a
`Task | Outcome | Date` row to the Completed ledger (outside the zone), with Outcome a
link to the resulting OpenSpec change/PR/standard or a one-line "done — …".

### 5. Regenerate, log, self-check
Rebuild the GENERATED zone from the tasks' frontmatter (per the `homes.md` bullet;
install the markers first if the target's index predates them, without touching the
fixed prose). Append ONE consolidated entry per **Appending to `log.md`** in
[../quenching-insert/references/homes.md](../quenching-insert/references/homes.md):
`**Update**: [backlog/](/docs/backlog/index.md) — triaged N tasks (X ranked, Y re-ranked,
Z completed)`. Self-check every touched file against
[../quenching-align/references/conformance.md](../quenching-align/references/conformance.md),
plus this skill's own gate: the zone matches disk and its links resolve.

## Invariants to never violate

- Never write anything before the single consolidated confirmation; a rejected plan
  applies nothing.
- Never silently clobber a human-set priority — a re-rank always carries an explicit
  reason and an explicit approval.
- Never infer completion — removal and its Completed-ledger row happen only for tasks the
  human stated are done; an abandoned development leaves the task in place.
- Never use a priority value outside `critical|high|medium|low`, and never force a rank
  on a task the plan cannot honestly ground.
- Never hand-edit inside the GENERATED markers (regenerate the whole zone), never add
  frontmatter to `backlog/index.md`, and never fan out sub-agents — the orchestrator
  reads and writes everything itself.
