---
description: Rank the whole plans/ front — ONE ordered list the human confirms, written back as a priority record on each spec. Triggers on "triage the specs", "prioritize the front", "rank the plans", "what matters most", "re-rank these", "order the plans", "which of these first". Reads every spec's frontmatter and derived stage directly, no sub-agents; proposes one table with a one-line reason per row; applies only what was approved, merging and never clobbering a human's ranking. Writes the priority record — level, criticality, complexity, date — and nothing else. Never removes a spec, never infers completion, never treats staleness as abandonment. Not for: closing a spec out or abandoning it → /quenching:specs:conclude; resolving a spec's discoveries → /quenching:specs:develop; building the top-ranked spec → /quenching:specs:cycle; the conformance view of the workspace → /quenching:specs:status.
argument-hint: [optional-slug]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion
model: opus
---

# /quenching:specs:triage — rank the front, once, on one confirmation

**Input**: `$ARGUMENTS` — optionally one slug to limit the sweep; omit to rank everything in
`plans/`.

The prioritization sweep. It reads every spec in
`/.specs/plans/`, proposes ONE ordered list, and — on a single
confirmation — writes each spec's `priority` record.

**This is the only command that ranks.** `cq specs next --front` consumes what this writes: with no
`priority` anywhere and nothing in flight, its ordering falls back to age alone, which is an
ordering and not a judgment. Triage is what turns it into one.

**It ranks and nothing else.** It does not close specs out, resolve `## Discoveries`, or decide
that anything is finished — those are `/quenching:specs:conclude` and `/quenching:specs:develop`'s discoveries bank.
A sweep that could also delete is a sweep nobody can safely re-run.

The layout, the derived stages, the front's on-write check and the `cq specs` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The `specs/` layout §Derived stages §The `cq specs` tool surface §The report mold, which owns the
shape of both the step 2 table and the step 6 report; how the tool is resolved and its path
written in
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation. Both cited, never
restated.

## Resolving the tool

Resolve `cq` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool. Branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

## The record this command owns

```yaml
priority:
  level: 3
  criticality: high
  complexity: medium
  date: 2026-07-27
```

| Field | What it is | Rule |
| --- | --- | --- |
| `level` | this spec's **position in one ordered list** — 1 is next | an integer, unique across the front. This is what ranks. |
| `criticality` | a coarse word: `critical` · `high` · `medium` · `low` | the fallback that still ranks a half-filled record. Never the primary answer. |
| `complexity` | one of `low` · `medium` · `high` · `xhigh`, never a numeric size — see below | proposed **only** when the spec is concrete enough to judge; otherwise left out |
| `date` | when the ranking was made | stamped on every write, because a ranking ages |

**`level` is a position, not a label.** Five specs marked "high" is not a ranking — it is the
absence of one, written down. The whole value of this sweep is that somebody had to decide what
comes *after* what, and an ordinal is the only form that cannot dodge it. `criticality` exists
because a partially-ranked front should still sort, not because it is an easier way to answer.

The record is `writeOnce: false`: a later sweep re-ranks, and each write restamps `date`. Only this
command writes it.

**`complexity` answers a different question than `level`.** It is never about how big or how
important the change is — that is what `level` and `criticality` already answer. Propose it
against the criterion
[gears.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-cycle/gears.md) §Deriving the gears plan
states: how much a human needs to be part of the process, from `low` (the LLM can carry it with
close to no supervision) to `xhigh` (a judgment stage joins the plan).

## Doctrine

- **Propose, don't invent.** Every proposed position traces to something readable — the spec's own
  `## Problem`, its derived stage, its task progress, its age, and `/.knowledge/vision/` when the repo has
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
  A spec that will not be built is `/quenching:specs:conclude --outcome abandoned`, on the human's word, and
  staleness is never evidence of it — a spec untouched for a year may be waiting on a vendor.
- **Nothing but the record is written.** Ranking touches each spec's `priority` frontmatter and no
  other file — there is no listing to refresh, because `cq specs list` derives one on demand.
- **No sub-agents.** A front is small by nature and a spec's frontmatter is a few lines; the
  orchestrator reads and writes everything itself.

## Workflow

### 1. Read the front directly
Find `/.specs/plans/` at the target repo root. Missing → stop and offer `/quenching:specs:create`, which
installs the seed. Then:
```bash
cq specs list --phase plans --json      # every spec in plans/: folder, derived stage, and its records
cq specs section <slug> Problem         # per spec being ranked, for the reason column
```
`list --phase plans --json` carries the seven `records` for exactly the front this sweep ranks —
never the `archive/` history alongside it — so the current `priority` of every spec in scope arrives
in that one call — **never open a spec file to read it.** Read `/.knowledge/vision/` when present, to ground the
ordering in where the repo is going rather than in what is loudest. No sub-agents.

Note what the table will have to explain: specs already ranked, specs whose ranking predates their
current stage, near-duplicates, and any `priority` whose shape does not match §The record this
command owns.
**Done when:** every spec in scope has been read and the anomalies are listed.

### 2. Build ONE ranking table
§The spec table, in its proposal form — the shared columns carrying each spec's **current** state,
then the four this command adds:

| Spec | Title | Stage | Tasks | Priority | Proposed `level` | `criticality` | `complexity` | Reason |

Rules for the table:
- **Every spec in scope gets a row** — including "stays unranked, because …".
- `level` values are **contiguous from 1** across the ranked rows. A gap or a duplicate is a bug in
  the proposal, not a nuance.
- A spec already carrying a `priority` appears with its current value and a **stated reason** for
  any change; no reason means no change.
- `complexity` is left blank rather than guessed.
- Anything the sweep noticed but does not rank — a near-duplicate pair, a stub going nowhere, a
  ranking whose grounds have expired — is listed **below** the table as an observation naming the
  command **and the exact argument** that would act on it, runnable as printed. Never as a row.
**Done when:** one table covers every spec in scope, with contiguous levels and a reason per change.

### 3. One OK
Present the table and **wait for a single confirmation**. Adjustments → adjust and re-present;
rejection → write nothing and stop. Use **AskUserQuestion** when the choice is between two orderings
rather than open-ended.
**Done when:** the human has approved, adjusted, or rejected the whole table.

### 4. Apply exactly what was approved
One call per approved spec, run in parallel, and **never an edit to the file.** Against the
`github` backend each write is one network round-trip, and a front's worth of them in series is
what blew past a 120s timeout in the measured session — `xargs -P 8`, the same pattern that
session already improvised on the read side, generalized here to the write:
```bash
printf '%s\0' \
  'cq specs record <slug1> priority --set level=<n1> --set criticality=<word1> [--set complexity=<level1>] --set date=<today>' \
  'cq specs record <slug2> priority --set level=<n2> --set criticality=<word2> [--set complexity=<level2>] --set date=<today>' \
  ... \
| xargs -0 -P 8 -I{} sh -c '{}'
```
One fully-formed `cq specs record` line per approved row — `--set complexity` present or omitted
per row, exactly as §The record this command owns already says — piped NUL-delimited so no
argument inside a line is ever split. `sh -c '{}'` runs each line as its own command, up to 8 at
once. The tool merges: a field not named survives, and `slug`, `title`, `date`, `verification` and the
other six records are never in reach of this write. Stamp the record's own `date` on every write —
it is a different key from the spec's capture `date:`. Leave `--set complexity` off
rather than guessing it. Editing the frontmatter by hand would do the same thing only while the
backend is `files` — against a backend whose specs are issues there is no file to edit.
**Done when:** each approved row is on disk and no unapproved row was touched.

### 5. Check
```bash
cq specs validate --phase plans --json
```
That is the whole check, and it must exit 0. Nothing else was written: the ranking lives in each
spec's own `priority` record, there is no listing to regenerate, and nothing goes into the `/.knowledge/`
bundle — the log this used to append to is retired.
**Done when:** the validator is clean, or its residue is reported verbatim.

### 6. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. Two body blocks:

1. **The ranking as it now stands** — fixed. Never redigit the 42-row table the model already
   composed at step 2 — the ranking now on disk is a tool call away, so run one and quote its
   output verbatim (§Quoting a tool's own output) rather than recomposing it in prose:
   ```bash
   cq specs list --phase plans --json | python3 -c '
   import json, sys
   rows = json.load(sys.stdin)["specs"]
   print("| Spec | Title | Stage | Tasks | Priority |")
   print("| --- | --- | --- | --- | --- |")
   for s in rows:
       slug, title, stage = s["slug"], s["title"], s["stage"]
       t = s["tasks"]
       checked, total, blocked = t["checked"], t["total"], t["blocked"]
       tasks = "—" if not total else f"{checked}/{total}" + (f" · {blocked} blocked" if blocked else "")
       p = s["records"].get("priority") or {}
       level, crit = p.get("level", "—"), p.get("criticality", "—")
       priority = "—" if not p else f"{level} · {crit}"
       print(f"| {slug} | {title} | {stage} | {tasks} | {priority} |")
   '
   ```
   §The spec table, the four proposal columns dropped and `Priority` showing the value now on
   disk — this is the same shape, printed by the tool instead of retyped by the model. Specs that
   stayed unranked keep their row, `Priority` reading `—`.
2. **Observations** — optional, omitted whole when there are none. §The observations table, each
   row's `Recommended action` **runnable as printed**: the command with its real argument
   substituted, never a bare command name the reader has to complete.

Then §The next-step block, whose recommended line is `/quenching:specs:cycle <slug>` for the
spec the approved ranking put first — the first thing the `priority` this just wrote decides.
**Done when:** both blocks and the next-step block are shown.

## Invariants to never violate

- Never write anything before the single consolidated confirmation; a rejected plan applies nothing.
- Never silently clobber a human-set `priority` — a re-rank carries an explicit reason and an
  explicit approval.
- Never propose duplicate or non-contiguous `level` values, and never force a rank onto a spec the
  sweep cannot honestly place.
- Never write a field outside the `priority` record. This command ranks; it does not develop,
  execute, or conclude.
- Never edit a spec's frontmatter directly. `cq specs record` is the writer, and it is what keeps
  the merge honest and the write backend-agnostic.
- Never remove a spec, move a spec, tick a checkbox, or resolve a `## Discoveries` line.
- Never infer completion or abandonment, and never treat staleness as evidence of either.
- Never create or refresh a `plans/index.md`. The artifact is retired; `cq specs list` derives the
  same listing from disk on demand.
- Never fan out sub-agents, and never re-implement a check in prose — run `cq specs validate` and
  report what it says.
- **Never print an observation whose `Recommended action` is not runnable as printed** — a bare
  command name, or a literal `<slug>` reaching the output, is a defect. The row exists so the next
  step can be copied; one the reader has to complete is the gap §The observations table was given
  its own mold to close.
