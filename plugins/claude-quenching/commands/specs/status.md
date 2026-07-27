---
description: Read the whole specs/ front and report where it stands — writes nothing
argument-hint: [optional-slug]
allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*)
effort: low
---

# /specs:status — read the front, change nothing

**Input**: `$ARGUMENTS` (optionally a spec slug to detail; omit to read the whole front).

The **read-only** view of the `specs/` front. Every other skill here either fixes something
(`/specs:align`), drives something (`/specs:align-and-update`), or acts on one
item a human named. This one only looks — and because it looks at exactly what those sweeps look
at, it is also their honest preview: the plan you would be authorizing, before you authorize it.

Quenching-native, like the whole `specs/` front — `specs.py list` and `specs.py status --plan`
each answer one question at a time; the cross-cutting view, the backlog, the OKF bridge, and the
`sp-*` vocabulary are what this skill assembles from them.

The workspace facts (layout, plan artifact graph, `specs.py` surface) live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md);
every `sp-*` code and what a sweep would do about it in
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md);
the backlog check in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md).
All three are **cited, never restated** — this skill owns no contract of its own, which is the
point: a status view that disagreed with the sweep would be worse than none.

## Doctrine

- **Zero writes, no exceptions.** No stamp, no zone regeneration, no `docs/log.md` entry, not
  even a marker file. A status read that changed the thing it read would break its own contract
  and make the preview a lie. The `allowed-tools` above carry no `Write` or `Edit` — that is the
  enforcement, not a promise.
- **Report in the sweep's vocabulary.** Every finding carries the `sp-*` code
  [conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md) defines and the command
  that closes it. Never invent a code, never soften one, and never report a finding the sweep
  would not raise — the value is that the two agree.
- **Distinguish "would fix" from "would only report".** Split the output the way the sweep splits
  it: what `/specs:align` would fix on one OK, what `/specs:align-and-update` would then drive,
  and what neither closes because it needs a human. A reader must be able to tell what a sweep
  would actually do to their repo.
- **Cheap by construction.** One `doctor`, one `validate`, one `list --json`, one glob. Run
  `status --spec <slug> --json` **only** for plans `list --json` already shows at full task progress
  — the archive candidates. A dozen open plans must not cost a dozen JSON payloads to conclude
  eleven of them are mid-flight. Never fan out sub-agents: there is nothing here a sub-agent could
  parallelize that the tool does not already answer in one call.
- **Never infer completion, never rank, never judge.** A plan whose tasks are all checked is
  *ready to archive*, not *done*. A task with no priority is *untriaged*, a valid state, not a
  defect. Staleness is reported with its age, never as a verdict.

## Workflow (one read, one report)

### 1. Resolve the tool + workspace
Resolve `specs.py` by the fallback in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md)
§Resolving the tool (plugin path → `.claude/hooks/specs.py` → the declared manual check, saying so
in the report), invoked via `python3`/`py`. Resolve the `specs/` root at the repo root. **No root
at all** is a complete, valid answer: report `sp-no-workspace` and that `/specs:align` would
scaffold it. A legacy `openspec/` present instead of `specs/` is `sp-legacy-workspace` — report it
and that `/specs:align` would migrate it.
**Done when:** the root is resolved or its absence recorded.

### 2. Collect (read-only)
`specs.py doctor`; `specs.py validate`; `specs.py list --json` (names, statuses, `lastModified`);
`Glob` `specs/backlog/*.md` and read their frontmatter; read `backlog/index.md`; `Glob` a legacy
`openspec/` tree and the shadow copies (`.claude/skills/openspec-*/SKILL.md`,
`.claude/commands/opsx/*.md`); read `docs/index.md` for `okf_version`; run the backlog check
(`okf-validate.py specs/backlog --listing-root`, per
[backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md)) — it writes nothing.
Then `specs.py status --spec <slug> --json` **only** for the plans `list --json` reports at full task
progress, plus any plan the user named.
**Done when:** every source is read and nothing has been written.

### 3. Classify against the sweep's own codes
Map each observation onto a code from
[conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md), keeping its two tables intact
— what a sweep **fixes** (`sp-no-workspace`, `sp-legacy-workspace`, `sp-doctor`,
`sp-invalid-plan`, `sp-plan-name`, `sp-archive-name`, `sp-task-slug`, the `backlog/` codes, the
shadow-copy codes) versus what it only **reports** (`sp-plan-complete`, `sp-plan-blocked`,
`sp-plan-stale`, `sp-backlog-untriaged`, `sp-ledger-orphan`, `sp-ledger-in-flight`, plus the three
`specs.py validate` warnings — `sp-unrefined`, `sp-design-scaffold`, `sp-impact-uncovered`). Every
code is the sweep's — this skill contributes none of its own. Without an OKF bundle, note that a legacy
`openspec/` fold could not complete (main specs have nowhere to land) and mention `/docs:align`
once.
**Done when:** every observation carries a code and a table.

### 4. Report
One report, in this order:

1. **Header** — the resolved root, whether an OKF bundle is present, and the three verifier states
   verbatim: `doctor`, `validate`, backlog check.
2. **Plans** — a table `Plan | Artifacts | Tasks | Last modified | State`, where State is one of
   *ready to archive* (`sp-plan-complete`), *in progress*, *blocked* (`sp-plan-blocked`), or
   *stale* (`sp-plan-stale`, with the age). Archived plans are a count, not a list, unless one
   carries a non-canonical name.
3. **Backlog** — the counts by priority, the untriaged count, the oldest task's age, and any
   duplicate or invalid-priority observation. Never propose a ranking; that is triage's.
4. **Would be fixed by `/specs:align`** — the fixable codes, with counts, and which of them would
   be **code-coupled** (a rename whose blast radius reaches product code) and so would confirm on
   its own. State plainly that this list is what a single OK would authorize.
5. **Would then be driven by `/specs:align-and-update`** — the cycle actions the conductor closes:
   archives (**by name**, each its own confirmation) and triage.
6. **Closed by neither** — everything needing a human, each with its command: blocked plans →
   `/specs:develop`, abandoned candidates → `/specs:archive`, ledger orphans, diverged
   shadow copies, tasks nobody has said are done, and the three **thinking** warnings
   `specs.py validate` reports — `sp-unrefined` (a plan that reached a checklist with nobody
   interrogating it → `/specs:refine`), `sp-design-scaffold` (a `## Design` still on the
   shipped scaffold → `/specs:refine`, or `/specs:develop` when the content already
   exists), and `sp-impact-uncovered` (a declared standard no task writes →
   `/specs:develop`). Report each with its plan name; state plainly that none of them gates
   apply, so a reader never mistakes a warning for a blocker.

Close with the single most useful next command for this repo's actual state, and nothing else —
no plan, no offer to fix, no "shall I". A status read ends by handing control back.
**Done when:** all six sections are reported and no file has changed.

## Invariants to never violate

- Never write, anywhere, for any reason — not a stamp, not a zone, not a log line, not a marker.
  If something looks wrong enough to fix, name the command that fixes it and stop.
- Never run `status --spec <slug> --json` per active plan by default — only for full-progress plans
  and ones the user named.
- Never report a finding with a code the sweep does not define, and never state a finding the
  sweep would not raise.
- Never call a plan *done*, a task *finished*, or a stale plan *abandoned* — completion and
  abandonment are stated by a human, never inferred from a checkbox or a date.
- Never rank a backlog task, never propose a priority — the report shows what is untriaged and
  names `/specs:triage`.
- Never fan out sub-agents, and never hand this command file `context: fork` when it is invoked as a
  sweep's preview — the report has to land in the conversation where the OK will be given.
