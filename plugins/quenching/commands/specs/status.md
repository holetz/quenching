---
description: Read the whole specs/ front and report where it stands — writes nothing, ever. Triggers on "specs status", "how is the specs front", "what is in plans", "show me the specs workspace", "is specs conformant", "what would align fix", "dry run the specs sweep". Reports every finding in the sweep's own sp- vocabulary, split into what /specs:align would fix on one OK, what a cycle command closes, and what neither closes because it needs a human. Shows each spec's frontmatter records as the history they narrate — ranked, interrogated, approved, built, reviewed, merged, closed. Near-free by construction, no sub-agents and no per-spec fan-out, so it doubles as an honest dry run before a sweep is authorized. Not for: fixing anything → /specs:align; being handed the single next action → /specs:continue; ranking the front → /specs:triage; sharpening a spec → /specs:develop.
argument-hint: [optional-slug]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*)
---

# /quenching:specs:status — read the front, change nothing

**Input**: `$ARGUMENTS` (optionally a spec slug to detail; omit to read the whole front).

The **read-only** view of the `specs/` front. Every other command here either fixes something
(`/quenching:specs:align`), advances one spec a human named, or hands you the next action
(`/quenching:specs:continue`). This one only looks — and because it looks at exactly what the sweep looks at,
it is also the sweep's honest preview: the plan you would be authorizing, before you authorize it.

**Near-free by construction.** Three tool calls, whatever the size of the front. It
reads the same two payloads `/quenching:specs:align`'s probe reads, which is what lets the two agree: a
status view that disagreed with the sweep would be worse than none.

The workspace facts (layout, the fourteen sections, the derived stages, the `specs.py` surface)
live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md)
§The `specs/` layout §The fourteen sections §Derived stages §The `specs.py` tool surface §The
report mold, which owns the shape step 4 prints in;
every `sp-*` code and what the sweep would do about it, plus where the front is configured and what
the declared backend decides, in
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
§Findings the sweep FIXES (inside the one plan → one OK) §Findings the sweep REPORTS (never
auto-closes) §Where the front is configured, and what the backend decides.
Both are **cited, never restated** — this command owns no contract of its own, which is the
point.

## Doctrine

- **Zero writes, no exceptions.** No stamp, no zone regeneration, not even a marker file. A
  status read that changed the thing it read would break its own contract and make the preview a
  lie.
- **Report in the sweep's vocabulary.** Every finding carries the `sp-*` code
  [conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
  §Findings the sweep FIXES (inside the one plan → one OK) §Findings the sweep REPORTS (never
  auto-closes) defines, and the command that closes it. Never invent a code, never soften one, and
  never report a finding the sweep would not raise — the whole value is that the two agree.
- **Distinguish "would fix" from "would only report".** Split the output the way the sweep splits
  it: what `/quenching:specs:align` would fix on one OK, what a cycle command closes, and what neither closes
  because it needs a human. A reader must be able to tell what a sweep would actually do to their
  repo.
- **Show the records as the history they are.** `priority`, `refined`, `approved`, `branch`,
  `reviewed`, `merge`, `outcome`, read in that order, narrate a spec's life: ranked, interrogated,
  approved, built, reviewed, merged, closed. An absent record is a **not-yet**, never a defect —
  most specs carry two or three, and that is normal.
- **Cheap by construction, and never through a path.** One `doctor`, one `validate`, one
  `list --json` — which carries the records, so no spec file is opened at all. Reach for
  `specs.py status --spec <slug> --json` **only** for a spec the user named. A dozen active specs
  must not cost a dozen payloads. Never fan out sub-agents: there is nothing here a sub-agent could
  parallelize that the tool does not already answer in one call.
- **Never infer completion, never rank, never judge.** A spec whose tasks are all checked is *ready
  to conclude*, not *done*. A spec with no `priority` is *unranked*, a valid state, not a defect.
  Staleness is reported with its age, never as a verdict.

## Workflow (one read, one report)

### 1. Resolve the tool + workspace
Resolve `specs.py` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool, invoked via `python3`/`py`. Resolve the `specs/` root at the repo root.

**No root at all** is a complete, valid answer: report `sp-no-workspace` and that `/quenching:specs:align`
would scaffold it. A legacy `openspec/` present instead is `sp-legacy-workspace` — report it and
that `/quenching:specs:align` would migrate it.
**Done when:** the root is resolved or its absence recorded.

### 2. Collect (read-only)
```bash
specs.py doctor --json
specs.py validate --json
specs.py list --json
```
`list --json` carries each spec's seven `records` already, so **there is no per-spec file to
open** — asking the tool is also the only form that survives a backend where the specs are issues
and `specs/plans/*.md` does not exist. Then read `docs/index.md` for `okf_version`, and — only
under a suspected legacy migration — `Glob` the `openspec/` tree and the shadow copies
(`.claude/skills/openspec-*/SKILL.md`, `.claude/commands/opsx/*.md`).

Add `specs.py status --spec <slug> --json` **only** when the user named a spec. Every one of these
writes nothing.
**Done when:** every source is read and nothing has been written.

### 3. Classify against the sweep's own codes
Map each observation onto a code from
[conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)
§Findings the sweep FIXES (inside the one plan → one OK) §Findings the sweep REPORTS (never
auto-closes), keeping its two tables intact — what the sweep **fixes** versus what it only
**reports**. Every code is the
sweep's; this command contributes none of its own. Without an OKF bundle, note once that a legacy
`openspec/` fold could not complete (main specs have nowhere to land) and mention `/quenching:docs:align`.
**Done when:** every observation carries a code and lands in exactly one table.

### 4. Report
Emit §The report mold. Five body blocks, **all fixed** — an empty one prints its title and `—`, never
disappears — in this order:

1. **Header** — the front-wide header line, then the resolved root, whether an OKF bundle is
   present, and the verifier states quoted per §Quoting a tool's own output: `doctor`, `validate`,
   the listing check. If the probe would have stopped
   (`/quenching:specs:align` step 1), say so in one line: that is the single most useful fact here.
2. **Specs** — §The spec table with `Spec` `Title` `Stage` `Tasks` `Records` `Age` `State`. `Age` is
   days since `list --json`'s `date`; this command never calls `next --front`, and says so rather
   than leaving the figure sourceless. `Records` lists which of the seven are set; `State` is *ready
   to conclude* (`sp-spec-complete`), *executing*, *blocked* (`sp-spec-blocked`), *stale*
   (`sp-spec-stale`, with the age), or the stage's own name. Archived specs are a count, not a list,
   unless one carries a non-canonical name or no `outcome:`.
3. **Would be fixed by `/quenching:specs:align`** — §The findings table, marking which rows are
   **code-coupled** (a rename whose blast radius reaches product code) and so would confirm on their
   own. State plainly that this list is what a single OK would authorize.
4. **Closed by a cycle command** — §The findings table, each row's `Closed by` carrying the owning
   command **with its slug**: a spec at 100% →
   `/quenching:specs:conclude`; an unmet gate → `/quenching:specs:develop`; open tasks → `/quenching:specs:execute`; unresolved
   `## Discoveries` → `/quenching:specs:develop`'s discoveries bank; nothing ranked and nothing in flight →
   `/quenching:specs:triage`.
5. **Closed by neither** — §The findings table, `Closed by` reading *a human*:
   `sp-empty-section` and `sp-stray-heading` (authoring nobody can supply), `sp-no-outcome` (`done`
   and `abandoned` are opposite facts), `sp-impact-uncovered` (add the task or drop the
   declaration — a judgment), `sp-unrefined` (nobody has argued with this spec), a diverged shadow
   copy, and any stale spec. State plainly that **none of these gates anything**, so a reader never
   mistakes a warning for a blocker.

Then §The next-step block — usually the single line `/quenching:specs:continue`. Here it is a
suggestion and never an offer, which is the mold's rule for this command.
**Done when:** all five blocks are reported and no file has changed.

## Invariants to never violate

- Never write, anywhere, for any reason — not a stamp, not a zone, not a log line, not a marker. If
  something looks wrong enough to fix, name the command that fixes it and stop.
- Never run `specs.py status --spec <slug>` per active spec by default — only for one the user
  named.
- Never open a spec file to read its records. `list --json` carries them, and a path read answers
  only while the backend happens to be `files`.
- Never report a finding with a code the sweep does not define, and never state a finding the sweep
  would not raise.
- Never call a spec *done*, a task *finished*, or a stale spec *abandoned* — completion and
  abandonment are stated by a human, never inferred from a checkbox or a date.
- Never rank, and never propose a `priority` — report what is unranked and name `/quenching:specs:triage`.
- Never treat an absent record as a defect. `approved`, `branch`, `reviewed` and `merge` are absent
  on every spec nobody has built yet, which is most of them.
- Never fan out sub-agents, and never hand this command file `context: fork` when it is invoked as
  a sweep's preview — the report has to land in the conversation where the OK will be given.
