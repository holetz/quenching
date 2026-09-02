---
description: Rank the provider-owned plans front — ONE ordered list the human confirms and writes as priority records. Triggers on "triage the specs", "prioritize the front", "rank the plans", "what matters most", "re-rank these", "order the plans", "which of these first". Reads the provider front and writes only priority fields. Not for: closing → /quenching:specs:conclude; resolving discoveries → /quenching:specs:develop; building → /quenching:specs:execute; conformance → /quenching:specs:status.
argument-hint: [optional-id]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion
model: opus
---

# /quenching:specs:triage — rank the front, once, on one confirmation

**Input**: `$ARGUMENTS` — optionally one ID to limit the sweep; omit to rank everything in
the provider-owned `plans` phase.

The prioritization sweep. It reads every spec in
the provider-owned plans front, proposes ONE ordered list, and — on a single
confirmation — writes each spec's `priority` record.

**This is the only command that ranks.** `cq specs next --front` consumes what this writes: with no
`priority` anywhere and nothing in flight, its ordering falls back to age alone, which is an
ordering and not a judgment. Triage is what turns it into one.

**It ranks and nothing else.** It does not close specs out, resolve `## Discoveries`, or decide
that anything is finished — those are `/quenching:specs:conclude` and `/quenching:specs:develop`'s discoveries stage.
A sweep that could also delete is a sweep nobody can safely re-run.

The layout, the derived stages and the front's on-write check live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The provider-owned document §Derived stages. The `cq specs` surface lives in
[specs-surface.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/specs-surface.md)
§The `cq specs` tool surface; the report mold, which owns the shape of both the step 2 table and
the step 6 report, lives in
[report-mold.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/report-mold.md)
§The report mold. How the tool is resolved and its path written lives in
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
| `complexity` | one of `low` · `medium` · `high` · `xhigh`, never a numeric size — see below | proposed on **every** ranked row. `low` needs concrete grounds; without them the floor is `medium` |
| `date` | when the ranking was made | stamped on every write, because a ranking ages |

The record is `writeOnce: false`: a later sweep re-ranks, and each write restamps `date`. Only this
command writes it.

**`complexity` answers a different question than `level`.** Propose it against the criterion
[spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §The scale
states: how much a human needs to be part of the process, from `low` (the LLM can carry it with
close to no supervision) to `xhigh` (a judgment stage joins the plan).

**Every ranked row gets one, and `medium` is the floor for a guess.** A spec too thin to judge — a
`captured` one with a `## Problem` and no `## Proposal` — still leaves this sweep carrying
`medium`, never blank and never `low`.

## Workflow

### 1. Read the front directly
Resolve the provider-owned plans front through `cq specs`; there is no local `/.specs/plans/` source
to enumerate. A provider refusal → report it and stop; do not offer a local seed. Then:
```bash
cq specs list --phase plans --json      # every spec in plans/: folder, derived stage, and its records
cq specs section <id> Problem         # per spec being ranked, for the reason column
```
`list --phase plans --json` carries the seven `records` for exactly the front this sweep ranks —
never the `archive/` history alongside it — so the current `priority` of every spec in scope arrives
in that one call — **never open a spec file to read it.** Read `/docs/vision/` when present, to ground the
ordering in where the repo is going rather than in what is loudest. No sub-agents.

Note what the table will have to explain: specs already ranked, specs whose ranking predates their
current stage, near-duplicates, and any `priority` whose shape does not match §The record this
command owns.
**Done when:** every spec in scope has been read and the anomalies are listed.

### 2. Build ONE ranking table
§The spec table, in its proposal form — the shared columns carrying each spec's **current** state,
then the four this command adds:

| Spec | Summary | Stage | Tasks | Priority | Complexity | Proposed `level` | Proposed `criticality` | Proposed `complexity` | Reason |

Rules for the table:
- **Every spec in scope gets a row** — including "stays unranked, because …".
- `level` values are **contiguous from 1** across the ranked rows. A gap or a duplicate is a bug in
  the proposal, not a nuance.
- A spec already carrying a `priority` appears with its current value and a **stated reason** for
  any change; no reason means no change. `Complexity` and `Proposed complexity` are two columns for
  that reason: the value on disk and the value being proposed sit side by side, so a re-judgement is
  visible as one and an unchanged row repeats itself.
- **Every ranked row proposes a `complexity`** — `medium` when the spec is too thin to judge, and
  the reason column says which of the two it is ("floored at `medium`, no `## Proposal` yet" reads
  differently from "`medium` — the pattern is proven in the tree"). `low` appears only where the
  reason names the grounds that earned it.
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
  'cq specs record <id1> priority --set level=<n1> --set criticality=<word1> --set complexity=<word1> --set date=<today>' \
  'cq specs record <id2> priority --set level=<n2> --set criticality=<word2> --set complexity=<word2> --set date=<today>' \
  ... \
| xargs -0 -P 8 -I{} sh -c '{}'
```
One fully-formed `cq specs record` line per approved row — all four `--set` on every line, because
§The record this command owns floors `complexity` at `medium` rather than omitting it — piped
NUL-delimited so no argument inside a line is ever split. `sh -c '{}'` runs each line as its own command, up to 8 at
once. The tool merges: a field not named survives, and `id`, `title`, `date`, `verification` and the
other six records are never in reach of this write. Stamp the record's own `date` on every write —
it is a different key from the spec's capture `date:`. Editing the frontmatter by hand would do the
same thing only while the backend is `files` — against a backend whose specs are issues there is no
file to edit.
**Done when:** each approved row is recorded through the provider and no unapproved row was touched.

### 5. Check
```bash
cq specs validate --phase plans --json
```
That is the whole check, and it must exit 0. Nothing else was written: the ranking lives in each
spec's own `priority` record, there is no listing to regenerate, and nothing goes into the `/docs/`
bundle — the log this used to append to is retired.
**Done when:** the validator is clean, or its residue is reported verbatim.

### 6. Report

```bash
cq components read ${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/report-mold.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. Two body blocks:

1. **The ranking as it now stands** — fixed. Never redigit the 42-row table the model already
   composed at step 2 — the ranking now on disk is a tool call away, so run one and quote its
   output verbatim (§Quoting a tool's own output) rather than recomposing it in prose:
   ```bash
   cq specs next --front --table --order priority \
     --columns "spec,summary,stage,tasks,priority,complexity"
   ```
   §The spec table, the four proposal columns dropped, `Priority` and `Complexity` showing the
   values now on disk — this is the same shape, printed by the tool instead of retyped by the model.
   Specs that stayed unranked keep their row, `Priority` and `Complexity` both reading `—` — the two
   empty together, because a row this sweep could not place is the only row that carries neither.

   **`--order priority` is the point of the call, not a flourish.** The default ordering is the
   four-factor one `next` owns — executing first, then closest to done — and a block titled *the
   ranking as it now stands* that leads with what is in flight has shown the reader everything
   except the ranking. Under `priority` the unranked sort last, together, where they read as the
   tail the sweep could not place.

   **The rendering is the tool's, and this command holds no copy of it.** This block used to carry
   a `python3 -c` heredoc that re-sorted `list --json` and printed the table itself — one of three
   divergent hand-written renderers of one ranking, which is exactly the fan-out
   `docs/standards/architecture/report-mold.md` forbids. Quote the output; never re-sort it,
   re-tally it, or reach for the payload behind it.
2. **Observations** — optional, omitted whole when there are none. §The observations table, each
   row's `Recommended action` **runnable as printed**: the command with its real argument
   substituted, never a bare command name the reader has to complete.

Then §The next-step block, whose recommended line is `/quenching:specs:execute <id>` for the
spec the approved ranking put first — the first thing the `priority` this just wrote decides.
**Done when:** both blocks and the next-step block are shown.

## Invariants to never violate

- Never write anything before the single consolidated confirmation; a rejected plan applies nothing.
- Never silently clobber a human-set `priority` — a re-rank carries an explicit reason and an
  explicit approval.
- Never propose duplicate or non-contiguous `level` values, and never force a rank onto a spec the
  sweep cannot honestly place.
- Never write a ranked row without a `complexity`, and never guess one below `medium`. `low` is a
  claim that the work can run almost unattended, so it is written only where the reason names what
  earned it.
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
  command name, or a literal `<id>` reaching the output, is a defect. The row exists so the next
  step can be copied; one the reader has to complete is the gap §The observations table was given
  its own mold to close.
