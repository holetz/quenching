---
name: quenching-specs-status
description: "Read the whole `specs` front and report where it stands — writes nothing, ever. Triggers on \"specs status\", \"how is the specs front\", \"what is in plans\", \"show me the specs workspace\", \"is specs conformant\", \"what would align fix\", \"dry run the specs sweep\". Reports every finding in the sweep's own sp- vocabulary, split into what quenching-specs-align would fix on one OK, what a cycle command closes, and what neither closes because it needs a human. Shows each spec's frontmatter records as the history they narrate — ranked, interrogated, approved, isolated, reviewed, merged, closed. Near-free by construction, no sub-agents and no per-spec fan-out, so it doubles as an honest dry run before a sweep is authorized. Not for: fixing anything → quenching-specs-align; running one spec's whole cycle → quenching-specs-cycle; ranking the front → quenching-specs-triage; sharpening a spec → quenching-specs-develop."
---

<!-- GENERATED FROM plugins/quenching/commands/specs/status.md -->


# quenching-specs-status — read the front, change nothing

**Input**: `$ARGUMENTS` (optionally a spec slug to detail; omit to read the whole front).

The **read-only** view of the `specs` front. Every other command here either fixes something
(`quenching-specs-align`) or advances one spec a human named — up to
`quenching-specs-cycle`, which conducts a whole lifecycle. This one only looks — and because
it looks at exactly what the sweep looks at, it is also the sweep's honest preview: the plan you
would be authorizing, before you authorize it.

**Near-free by construction.** Three tool calls, whatever the size of the front — and each one
returns a **rendering**, never a payload to re-aggregate. That second half is what makes the first
half true: measured on a 147-spec front, the three calls this command used to make returned 338,875
bytes, and no reader fits that. It still reads the same two payloads `quenching-specs-align`'s
probe reads (`doctor`, `validate` — `--by-code` is the same sweep, grouped), which is what lets the
two agree: a status view that disagreed with the sweep would be worse than none.

The workspace facts (layout, the fourteen sections, the derived stages, the `cq specs` surface)
live in
[specs-develop/spec-driven.md](../../references/specs-develop/spec-driven.md)
§The `specs/` layout §The fourteen sections §Derived stages §The `cq specs` tool surface §The
report mold, which owns the shape step 4 prints in;
every `sp-*` code and what the sweep would do about it, plus where the front is configured and what
the declared backend decides, in
[specs-align/conformance.md](../../references/specs-align/conformance.md)
§Findings the sweep FIXES (inside the one plan → one OK) §Findings the sweep REPORTS (never
auto-closes) §Where the front is configured, and what the backend decides.
Both are **cited, never restated** — this command owns no contract of its own, which is the
point.

## Doctrine

- **Zero writes, no exceptions.** No stamp, no zone regeneration, not even a marker file. A
  status read that changed the thing it read would break its own contract and make the preview a
  lie.
- **Report in the sweep's vocabulary.** Every finding carries the `sp-*` code
  [conformance.md](../../references/specs-align/conformance.md)
  §Findings the sweep FIXES (inside the one plan → one OK) §Findings the sweep REPORTS (never
  auto-closes) defines, and the command that closes it. Never invent a code, never soften one, and
  never report a finding the sweep would not raise — the whole value is that the two agree.
- **Distinguish "would fix" from "would only report".** Split the output the way the sweep splits
  it: what `quenching-specs-align` would fix on one OK, what a cycle command closes, and what neither closes
  because it needs a human. A reader must be able to tell what a sweep would actually do to their
  repo.
- **Show the records as the history they are.** `priority`, `refined`, `approved`, `branch`,
  `reviewed`, `merge`, `outcome`, read in that order, narrate a spec's life: ranked, interrogated,
  approved, isolated, reviewed, merged, closed — `branch` narrates isolation, not that the work
  finished; that is the derived stage `executing`. An absent record is a **not-yet**, never a
  defect — most specs carry two or three, and that is normal.
- **Cheap by construction, and never through a path.** One `doctor`, one `validate --by-code`, one
  `next --front --table` — three **renderings**, so no spec file is opened and nothing is
  re-aggregated here. The table already carries each spec's records, tasks, age and state, and the
  grouping already carries the finding counts; recomposing either in prose is the defect this
  command was measured failing at. Reach for `cq specs status --spec <slug> --json` **only** for a
  spec the user named. A dozen active specs must not cost a dozen payloads. Never fan out
  sub-agents: there is nothing here a sub-agent could parallelize that the tool does not already
  answer in one call.
- **Never infer completion, never rank, never judge.** A spec whose tasks are all checked is *ready
  to conclude*, not *done*. A spec with no `priority` is *unranked*, a valid state, not a defect.
  Staleness is reported with its age, never as a verdict.

## Workflow (one read, one report)

### 1. Resolve the tool + workspace
Resolve `cq specs` per
[align/tool-resolution.md](../../references/align/tool-resolution.md)
§Resolving the tool, invoked via `python3`/`py`. Resolve the `/.specs/` root at the repo root.

**No root at all** is a complete, valid answer: report `sp-no-workspace` and that `quenching-specs-align`
would scaffold it. A legacy `openspec/` present instead is `sp-legacy-workspace` — report it and
that `quenching-specs-align` would migrate it.
**Done when:** the root is resolved or its absence recorded.

### 2. Collect (read-only)
```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs doctor --json
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs validate --by-code
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" specs next --front --table --columns "spec,summary,stage,tasks,records,age,state"
```
**Two of the three are already the report.** `--by-code` is the same sweep `validate --json` runs,
one line per `(code, severity)` with the count and the specs — quote it, never re-tally it.
`next --front --table` is §The spec table itself, printed by the tool: `--columns` is how this
command omits the ones it does not carry, and the order is the tool's, never re-sorted here. Both
carry each spec's records, tasks, age and state, so **there is no per-spec file to open** — asking
the tool is also the only form that survives a backend where the specs are issues and
`/.specs/plans/*.md` does not exist.

**`--front` is `plans/` by construction**, so this pass never enumerates `archive/`: an archived
spec reaches the report only through a finding `validate` raised on it (`sp-no-outcome`, a
non-canonical filename). Say that rather than implying a count nobody read;
`cq specs list --phase archive` is what enumerates them, and it is not run here.

Then read `/.knowledge/index.md` for `okf_version`, and — only
under a suspected legacy migration — `Glob` the `openspec/` tree and the shadow copies
(`.agents/skills/openspec-*/SKILL.md`, `.agents/skills/opsx/*.md`).

Add `cq specs status --spec <slug> --json` **only** when the user named a spec. Every one of these
writes nothing.
**Done when:** every source is read and nothing has been written.

### 3. Classify against the sweep's own codes
Map each observation onto a code from
[conformance.md](../../references/specs-align/conformance.md)
§Findings the sweep FIXES (inside the one plan → one OK) §Findings the sweep REPORTS (never
auto-closes), keeping its two tables intact — what the sweep **fixes** versus what it only
**reports**. Every code is the
sweep's; this command contributes none of its own. Without an OKF bundle, note once that a legacy
`openspec/` fold could not complete (main specs have nowhere to land) and mention `quenching-knowledge-align`.
**Done when:** every observation carries a code and lands in exactly one table.

### 4. Report

```bash
python3 "$(find "${CODEX_HOME:-$HOME/.codex}" "$HOME/.codex" -type f -path '*/quenching-codex*/scripts/cq' -print -quit 2>/dev/null)" components read ../../references/specs-develop/spec-driven.md \
  --sections "§The report mold" --rules-only
```

Emit §The report mold. Five body blocks, **all fixed** — an empty one prints its title and `—`, never
disappears — in this order:

1. **Header** — the front-wide header line, then the resolved root, whether an OKF bundle is
   present, and the verifier states quoted per §Quoting a tool's own output: `doctor`, `validate`,
   the listing check. If the probe would have stopped
   (`quenching-specs-align` step 1), say so in one line: that is the single most useful fact here.
2. **Specs** — §The spec table with `Spec` `Summary` `Stage` `Tasks` `Records` `Age` `State`,
   **quoted from step 2's `--table` output, never retyped**: the tool ordered it, sourced every
   cell and elided what needed eliding, and a hand-composed copy is a second renderer that can
   only drift from it. `Summary` is the spec's `summary:` where one is written and its `title:`
   where none is — the table says how many rows fell back, and that line is carried too, because
   an unwritten `summary:` nobody reports is one nobody writes. Archived specs are **not**
   enumerated (step 2): they appear only where `validate` raised a finding on one.
3. **Would be fixed by `quenching-specs-align`** — §The findings table, marking which rows are
   **code-coupled** (a rename whose blast radius reaches product code) and so would confirm on their
   own. State plainly that this list is what a single OK would authorize.
4. **Closed by a cycle command** — §The findings table, each row's `Closed by` carrying the owning
   command **with its slug**: a spec at 100% →
   `quenching-specs-conclude`; an unmet gate → `quenching-specs-develop`; open tasks → `quenching-specs-execute`; unresolved
   `## Discoveries` → `quenching-specs-develop`'s discoveries bank; nothing ranked and nothing in flight →
   `quenching-specs-triage`.
5. **Closed by neither** — §The findings table, `Closed by` reading *a human*:
   `sp-empty-section` and `sp-stray-heading` (authoring nobody can supply), `sp-no-outcome` (`done`
   and `abandoned` are opposite facts), `sp-impact-uncovered` (add the task or drop the
   declaration — a judgment), `sp-unrefined` (nobody has argued with this spec), a diverged shadow
   copy, and any stale spec. State plainly that **none of these gates anything**, so a reader never
   mistakes a warning for a blocker.

Then §The next-step block — usually the single line `quenching-specs-cycle <slug>` for the
spec this report puts first. Here it is a suggestion and never an offer, which is the mold's rule
for this command.
**Done when:** all five blocks are reported and no file has changed.

## Invariants to never violate

- Never write, anywhere, for any reason — not a stamp, not a zone, not a log line, not a marker. If
  something looks wrong enough to fix, name the command that fixes it and stop.
- Never run `cq specs status --spec <slug>` per active spec by default — only for one the user
  named.
- Never open a spec file to read its records. `next --front --table` carries them, and a path read
  answers only while the backend happens to be `files`.
- **Never re-render what step 2 already rendered.** The table and the grouped findings are quoted
  verbatim; re-sorting, re-tallying or recomposing either in prose makes this command a second
  renderer of a fact the tool owns, which is the defect it was measured failing at.
- Never report a finding with a code the sweep does not define, and never state a finding the sweep
  would not raise.
- Never call a spec *done*, a task *finished*, or a stale spec *abandoned* — completion and
  abandonment are stated by a human, never inferred from a checkbox or a date.
- Never rank, and never propose a `priority` — report what is unranked and name `quenching-specs-triage`.
- Never treat an absent record as a defect. `approved`, `branch`, `reviewed` and `merge` are absent
  on every spec nobody has built yet, which is most of them.
- Never fan out sub-agents, and never hand this command file `context: fork` when it is invoked as
  a sweep's preview — the report has to land in the conversation where the OK will be given.
