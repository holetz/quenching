---
description: Rank the whole plans/ front — ONE ordered list the human confirms, written back as a priority record on each spec. Triggers on "triage the specs", "prioritize the front", "rank the plans", "what matters most", "re-rank these", "order the plans", "which of these first". Reads every spec's frontmatter and derived stage directly, no sub-agents; proposes one table with a one-line reason per row; applies only what was approved, merging and never clobbering a human's ranking. Writes the priority record — level, criticality, complexity, date — and nothing else. Never removes a spec, never infers completion, never treats staleness as abandonment. Not for: closing a spec out or abandoning it → /specs:conclude; resolving a spec's discoveries → /specs:develop; being handed the single next action → /specs:continue; the conformance view of the workspace → /specs:status.
argument-hint: [optional-slug]
allowed-tools: Read, Grep, Glob, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion
---

# /specs:triage — rank the front, once, on one confirmation

**Input**: `$ARGUMENTS` — optionally one slug to limit the sweep; omit to rank everything in
`plans/`.

The prioritization sweep. It reads every spec in
[`specs/plans/`](${CLAUDE_PLUGIN_ROOT}/assets/specs/plans/index.md), proposes ONE ordered list, and — on a single
confirmation — writes each spec's `priority` record.

**This is the only command that ranks.** `/specs:continue` consumes what this writes: with no
`priority` anywhere and nothing in flight, its ordering falls back to age alone, which is an
ordering and not a judgment. Triage is what turns it into one.

**It ranks and nothing else.** It does not close specs out, resolve `## Discoveries`, or decide
that anything is finished — those are `/specs:conclude` and `/specs:develop`'s discoveries bank.
A sweep that could also delete is a sweep nobody can safely re-run.

The layout, the derived stages and the `specs.py` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md);
the listing-zone format and the on-write check in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md);
the shared log procedure in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md). All cited, never
restated.

## Resolving the tool

Resolve `specs.py` and `okf-validate.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## The record this command owns

```yaml
priority:
  level: 3
  criticality: high
  complexity: 8
  date: 2026-07-27
```

| Field | What it is | Rule |
| --- | --- | --- |
| `level` | this spec's **position in one ordered list** — 1 is next | an integer, unique across the front. This is what ranks. |
| `criticality` | a coarse word: `critical` · `high` · `medium` · `low` | the fallback that still ranks a half-filled record. Never the primary answer. |
| `complexity` | a rough size in development hours | proposed **only** when the spec is concrete enough to size; otherwise left out |
| `date` | when the ranking was made | stamped on every write, because a ranking ages |

**`level` is a position, not a label.** Five specs marked "high" is not a ranking — it is the
absence of one, written down. The whole value of this sweep is that somebody had to decide what
comes *after* what, and an ordinal is the only form that cannot dodge it. `criticality` exists
because a partially-ranked front should still sort, not because it is an easier way to answer.

The record is `writeOnce: false`: a later sweep re-ranks, and each write restamps `date`. Only this
command writes it.

## Doctrine

- **Propose, don't invent.** Every proposed position traces to something readable — the spec's own
  `## Problem`, its derived stage, its task progress, its age, and `docs/vision/` when the repo has
  one. Each row carries a one-line reason. A rank with no visible grounds cannot be overruled in one
  word, which is the only way a human reviews twenty of them.
- **One plan, one OK.** Every proposal merges into ONE table before anything is written. A single
  confirmation approves the whole list; partial adjustments → re-present; a rejected plan writes
  **nothing**.
- **MERGE, never clobber.** A `priority` a human set is never silently overwritten. A re-rank of an
  already-ranked spec enters the table only with an explicit reason, and only approved rows apply.
- **Unranked is a valid state.** A spec this sweep cannot honestly place stays unranked — no forced
  ordinal. Say which ones, and why.
- **Never remove, never close, never infer completion.** Triage moves no file and archives nothing.
  A spec that will not be built is `/specs:conclude --outcome abandoned`, on the human's word, and
  staleness is never evidence of it — a spec untouched for a year may be waiting on a vendor.
- **The zone is derived.** `plans/index.md`'s listing is rebuilt exclusively by
  `specs.py plans reindex`, only between the GENERATED markers.
- **No sub-agents.** A front is small by nature and a spec's frontmatter is a few lines; the
  orchestrator reads and writes everything itself.

## Workflow

### 1. Read the front directly
Find `specs/plans/` at the target repo root. Missing → stop and offer `/specs:create`, which
installs the seed. Then:
```bash
specs.py list --json                    # every spec, its folder, its derived stage
```
Read each spec's frontmatter and its `## Problem` first lines directly — no sub-agents. Read
`docs/vision/` when present, to ground the ordering in where the repo is going rather than in what
is loudest.

Note what the table will have to explain: specs already ranked, specs whose ranking predates their
current stage, near-duplicates, and any `priority` whose shape does not match §The record this
command owns.
**Done when:** every spec in scope has been read and the anomalies are listed.

### 2. Build ONE ranking table
| Spec | Stage | Progress | Current | Proposed `level` | `criticality` | `complexity` | Reason |

Rules for the table:
- **Every spec in scope gets a row** — including "stays unranked, because …".
- `level` values are **contiguous from 1** across the ranked rows. A gap or a duplicate is a bug in
  the proposal, not a nuance.
- A spec already carrying a `priority` appears with its current value and a **stated reason** for
  any change; no reason means no change.
- `complexity` is left blank rather than guessed.
- Anything the sweep noticed but does not rank — a near-duplicate pair, a stub going nowhere, a
  ranking whose grounds have expired — is listed **below** the table as an observation naming the
  command that would act on it. Never as a row.
**Done when:** one table covers every spec in scope, with contiguous levels and a reason per change.

### 3. One OK
Present the table and **wait for a single confirmation**. Adjustments → adjust and re-present;
rejection → write nothing and stop. Use **AskUserQuestion** when the choice is between two orderings
rather than open-ended.
**Done when:** the human has approved, adjusted, or rejected the whole table.

### 4. Apply exactly what was approved
Edit each approved spec's frontmatter, **merging** the `priority` record — fill or replace only the
approved fields, never rewrite the frontmatter wholesale (`slug`, `title`, `verification` and every
other record must survive). Stamp `date` on every write.
**Done when:** each approved row is on disk and no unapproved row was touched.

### 5. Regenerate, log, check
```bash
specs.py plans reindex
okf-validate.py specs/plans --listing-root
```
`plans reindex` rebuilds the GENERATED zone from disk (read its `changed` field to know whether it
wrote). Nothing is written into the `docs/` bundle: the ranking lives in each spec's own
`priority` record, and the bundle log this used to append to is retired.

The validator must exit 0 with no `index-broken-link` / `index-orphan`. The hook is docs-scoped by
config and never fires here, so this run is the coverage.
**Done when:** the zone matches disk, and the validator is clean or its residue is reported
verbatim.

### 6. Report
The ordered list as it now stands, what changed and why, which specs stayed unranked, and the
observations from step 2 with the command each routes to. Close by naming `/specs:continue` — the
consumer of what this just wrote.
**Done when:** the summary is shown.

## Invariants to never violate

- Never write anything before the single consolidated confirmation; a rejected plan applies nothing.
- Never silently clobber a human-set `priority` — a re-rank carries an explicit reason and an
  explicit approval.
- Never propose duplicate or non-contiguous `level` values, and never force a rank onto a spec the
  sweep cannot honestly place.
- Never write a field outside the `priority` record. This command ranks; it does not develop,
  execute, or conclude.
- Never remove a spec, move a spec, tick a checkbox, or resolve a `## Discoveries` line.
- Never infer completion or abandonment, and never treat staleness as evidence of either.
- Never hand-edit inside the GENERATED markers (call `specs.py plans reindex`), and never add
  frontmatter to `plans/index.md`.
- Never fan out sub-agents, and never re-implement the listing check in prose — run
  `okf-validate.py --listing-root` and report what it says.
