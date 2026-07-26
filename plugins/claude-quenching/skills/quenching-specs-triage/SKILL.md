---
name: quenching-specs-triage
description: >-
  Sweeps the whole specs/ front and proposes ONE consolidated plan: every backlog spec by its
  DERIVED stage (captured/proposed/designed/refined), plus every active spec's ## Discoveries
  resolved in place. Use when the user asks to "triage the backlog", "groom the specs", "sweep
  the discoveries", "what should I pick up next", or "re-rank what is parked". Reads each spec's
  headings and frontmatter directly (no sub-agents), flags stale and duplicate specs, and turns
  each ## Discoveries line into either a new captured spec (-> promoted: <slug>) or a dismissal
  (-> dismissed: <reason>), applied on a single confirmation, then regenerates the listing zone
  and logs one update. Provenance is never lost and the human pays the decision cost in batch.
  Not for: capturing ONE spec -> quenching-specs-capture; advancing a spec's sections ->
  quenching-specs-develop; workspace structure -> quenching-specs-align.
when_to_use: >-
  sweeping the whole front in one plan -> one OK: backlog stages plus every spec's discoveries.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(python3:*), Bash(py:*)
user-invocable: false
---

# quenching-specs-triage — prioritize the task inbox

Sweeps the **entire** task inbox at
[`specs/backlog/`](../../assets/specs/backlog/index.md), and proposes priorities and
themes for what is parked there — the sweep counterpart of the per-item `quenching-specs-capture`
capture. The backlog is a **quenching-managed** sibling of the plan folders and `specs/archive/`,
**outside** the OKF `docs/` bundle, so the hook never fires on it — this skill runs the validator
over it explicitly instead (`--listing-root`).
Unlike `quenching-docs-glossary-backfill`, this sweep fans **no** sub-agents out: a backlog is small
by nature and each task is a few frontmatter lines, so the orchestrator reads everything
directly. The backlog index-zone format, the `specs.py backlog reindex` contract, and the
on-write check live in
[../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md);
the shared log procedure lives with `quenching-docs-add`
([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)). Triage is
**Stage 3 of the `specs/` front's pipeline** — it is not a `docs/`-front stage, and it is not
a per-item tool. **Exception — cycle-authorized runs:** invoked by `quenching-specs-align-and-update`
(or `quenching-align-and-update-all`) under the cycle-authorization contract
([../quenching-align-and-update-all/references/convergence.md](../quenching-align-and-update-all/references/convergence.md)
§cycle-authorization), the plan below is presented as narration, not a gate. Run standalone, the
gate always applies — and either way, a **completion** (removing a task) still needs the human's
explicit word, which no authorization ever covers.

## Doctrine

- **Propose, don't invent.** Every proposed priority, tag, and complexity traces to the
  task's own title/gist and, when present, the direction in `docs/vision/` — each with a
  one-line rationale in the plan. Priorities only ever take `critical|high|medium|low`;
  `complexity` is a rough size in development hours, proposed only when the task is concrete
  enough to size (otherwise left absent — no forced estimate).
- **One plan, one OK.** Every proposal merges into ONE consolidated table before any
  write. A single confirmation approves the whole plan; partial adjustments → re-plan; a
  rejected plan applies **nothing**.
- **MERGE, never clobber.** A human-set priority or complexity is never silently
  overwritten — a re-rank (or re-size) of an already-triaged task enters the plan only with
  an explicit reason, and only the approved edits are applied.
- **Untriaged is a valid state.** A task the plan cannot honestly rank stays untriaged —
  no forced ranking. An invalid priority value found in a target (e.g.
  `priority: urgent`) renders under Untriaged and the plan proposes the fix.
- **Completion is stated, never inferred.** A removal + Completed-ledger row enters the
  plan only when the human says the task is done or its plan is ready-to-promote.
  Triage alone never removes a task; an abandoned plan leaves the task in place.
- **The zone is derived; the ledger is curated.** `specs.py backlog reindex` rebuilds the
  zone from the tasks' frontmatter, only between the GENERATED markers, per
  [../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md);
A finished spec is in `archive/` with `outcome: done` — there is no ledger to curate.

## Workflow

### 1. Read the backlog directly
Find `specs/backlog/` (the `specs/` tree lives at the target repo root); if it is missing,
stop and offer `quenching-specs-capture` (which installs the seed) or note there is nothing
to triage. `Glob` `backlog/*.md` and read each task's frontmatter **directly — no sub-agents**.
Read `docs/vision/` when present to ground the proposals. Note stale tasks (old `timestamp`),
near-duplicate pairs, and any invalid `priority` value. Resolve `specs.py` and
`okf-validate.py` per
[../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md)
§Resolving the tool.

### 2. Build ONE triage plan
One table: `Task | Current | Proposed priority | Proposed tags | Proposed complexity | Rationale (one line)`.
Include: a proposal for every untriaged task (or an honest "stays untriaged"); re-ranks
of triaged tasks **only with an explicit reason**; a rough `complexity` (dev hours) only when
the task is concrete enough to size (else leave the cell empty); staleness flags (old `Since`);
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
spec to `archive/` with `outcome: done` — a completed spec IS its own record, and there is no ledger row to write or keep in step.

### 5. Regenerate, log, check
Call `specs.py backlog reindex` to rebuild the GENERATED zone from the tasks' frontmatter (per
[../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md);
the tool installs the markers first if the target's index predates them, without touching the
fixed prose; read its `changed` field to know whether it wrote). Append ONE consolidated entry
to the bundle's `docs/log.md` per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md):
`**Update**: [backlog/](/specs/backlog/index.md) — triaged N tasks (X ranked, Y re-ranked,
Z completed)` (skip the log entry if the repo has no `docs/` bundle). Then run the check in
[../quenching-specs-capture/references/backlog-zone.md](../quenching-specs-capture/references/backlog-zone.md)
§The on-write check — `okf-validate.py specs/backlog --listing-root`, exit 0 with no
`index-broken-link` / `index-orphan` — and confirm what it cannot see: the zone matches disk and
A finished spec is in `archive/` with `outcome: done` — there is no ledger to curate. The hook is docs-scoped by config, so it does not
fire here; this run is the coverage.

## Invariants to never violate

- Never write anything before the single consolidated confirmation; a rejected plan
  applies nothing.
- Never silently clobber a human-set priority — a re-rank always carries an explicit
  reason and an explicit approval.
- Never infer completion — removal and its Completed-ledger row happen only for tasks the
  human stated are done; an abandoned plan leaves the task in place.
- Never use a priority value outside `critical|high|medium|low`, and never force a rank
  on a task the plan cannot honestly ground.
- Never hand-edit inside the GENERATED markers (call `specs.py backlog reindex`), never add
  frontmatter to `backlog/index.md`, and never fan out sub-agents — the orchestrator
  reads and writes everything itself.
- Never re-implement the conformance checks in prose — run `okf-validate.py` with
  `--listing-root` and report what it says; only the zone-matches-disk and ledger checks are
  the skill's own.
