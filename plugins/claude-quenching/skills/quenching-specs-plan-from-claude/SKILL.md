---
name: quenching-specs-plan-from-claude
description: >-
  Converts a Claude Code native plan file (~/.claude/plans/*.md, or an explicit path) into a
  front plan under specs/, so the work gains the archive-time distillation into docs/ instead of
  dying in the plan file. Use when the user says "turn this plan into a spec", "import my Claude
  Code plan", "convert ~/.claude/plans", "make this plan archivable", or "promote my plan into
  the specs workspace". Reads the native plan, maps its ## Context into the proposal's Why, its
  decisions/approach/risks into design.md, and its phases/steps/verification into tasks.md
  checkboxes; derives a kebab slug, runs specs.py new <slug>, writes the three artifacts from
  that mapping, and applies on ONE confirmation. Then offers to link and retire the
  specs/backlog/ task that seeded it, if one exists (--backlog-task). Not for: generating a plan
  from scratch with no source file → quenching-specs-plan-propose; implementing an existing
  plan's tasks → quenching-specs-plan-apply; revising a plan already in specs/ →
  quenching-specs-plan-update.
when_to_use: >-
  promoting a Claude Code native plan file (~/.claude/plans/*.md, or a given path) into a
  specs/ plan so it can be built and archived. Generating a plan from scratch is
  quenching-specs-plan-propose; implementing one is quenching-specs-plan-apply.
allowed-tools: Read, Write, Edit, Bash(python3:*), Bash(py:*), Glob, Grep, AskUserQuestion, Skill
user-invocable: false
---

# quenching-specs-plan-from-claude — promote a Claude Code plan into the front

A Claude Code native plan (the markdown a planning turn writes to `~/.claude/plans/`) is a
one-shot artifact: it drives the turn that made it, then it is inert. This skill lifts one into
the `specs/` front as a real plan — `proposal.md`, `design.md`, `tasks.md` — so the work
gains everything the front gives: a task checklist `specs.py` can track, isolation while it is
built, and the archive-time distillation of its by-products into the OKF `docs/` bundle. The
native plan file is **read, never moved or deleted** — it stays where Claude Code put it.

Spec-driven facts (the `specs/` layout, the plan artifact graph, the artifact formats, the
`specs.py` tool surface) live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md).
Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool (plugin path → `.claude/hooks/specs.py` → declared manual); invoke with
`python3` or `py`.

**Input**: Optionally an explicit path to a plan file. If omitted, glob `~/.claude/plans/*.md`
and, when more than one exists, let the user pick (never guess — most-recent is a hint, not a
choice).

## The mapping — native plan → front artifacts

A Claude Code plan is prose with loose section headings. Map its parts onto the three artifacts;
sections may be named in any language (`## Context` / `## Contexto`, `## Decisions` / `## Decisões`)
— match on meaning, not the literal string.

| Native plan part | Front artifact | Where |
| --- | --- | --- |
| `## Context` / background / the problem | `proposal.md` | the **Why** (`## Why`) |
| the goal / what it changes | `proposal.md` | `## What Changes`; declared scope → `## Impact` |
| decisions, chosen approach, "Decisões", architecture | `design.md` | `## Decisions` |
| the situation the decisions answer | `design.md` | `## Context` |
| risks, trade-offs, "Riscos" | `design.md` | `## Risks` |
| approaches weighed and dropped | `design.md` | `## Alternatives Considered` |
| open questions, "a decidir", unresolved choices | `design.md` | `## Open Decisions` |
| non-goals, "fora de escopo", what it won't do | `proposal.md` | `## Out of Scope` |
| acceptance criteria, how to confirm it worked | `proposal.md` | `## Validation` |
| phases, steps, numbered work, "Etapas" | `tasks.md` | `- [ ]` checkboxes under `## N. <Section>` |
| a verification / testing / acceptance section | `tasks.md` | trailing `- [ ]` verification tasks |

`design.md` is **required-with-explicit-fallback**, never omitted: if the native plan carries no
real decisions, trade-offs, or risks (a purely mechanical plan), write `- none — <reason>` in each
empty section rather than deleting the file. Never invent content the native plan does not
contain — `- none — the native plan recorded no alternatives` is honest; a fabricated risk is not.
The proposal's `## Out of Scope` and `## Validation` follow the same rule: map them from the
native plan's non-goals and its verification/acceptance section, and answer `- none` where it
said nothing.

## Workflow

### 1. Locate and read the native plan
If a path was given, read it. Otherwise `Glob` `~/.claude/plans/*.md`; with several, present them
(newest first) and let the user choose. Read the whole file and identify its sections against the
mapping table above.
**Done when:** the plan file is read and its parts are classified.

### 2. Derive the slug and check for collision
Derive a kebab-case, canonical-English slug from the plan's title or goal (e.g. "Add rate
limiting to the API" → `add-api-rate-limiting`). Run `specs.py list --json` and, if a plan of
that name already exists, ask whether to pick a new slug or stop — never overwrite an active plan.
**Done when:** a free canonical slug is in hand.

### 3. Read the OKF bundle as context (the OKF bridge)
If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), read what constrains this
work before writing: `docs/standards/` for the subjects the plan touches (the design must not
contradict a binding contract), and `docs/knowledge/glossary.md` (use the repo's canonical terms
in every artifact). No bundle → skip silently.
**Done when:** the relevant standards and glossary are read, or there is no bundle.

### 4. Present ONE plan → one confirmation
Show, in one plan: the slug and destination `specs/<slug>/`; which artifacts will be written
(`proposal.md`, `design.md`, `tasks.md`) and a one-line preview of each from the
mapping; the number of tasks derived; and — if Step 6 found a seed — the backlog task that would be
linked and retired. Wait for the confirmation. Declined → nothing is scaffolded.
**Done when:** the user has answered.

### 5. Scaffold and write the artifacts
Run `specs.py new <slug>` (add `--title "<title>"`, and `--backlog-task <slug>` when Step 6 found a
seed) — it creates `specs/<slug>/` with `.specs.json` and the filled `proposal`/`design`/`tasks`
templates. Then rewrite each template's sections from the mapping, using the resolved paths from
`specs.py status --plan <slug> --json` (never assume paths):
- fill `proposal.md`'s `## Why` / `## What Changes` / `## Out of Scope` / `## Validation` /
  `## Impact`;
- fill `design.md`'s `## Context` / `## Decisions` / `## Alternatives Considered` /
  `## Open Decisions` / `## Risks`, answering `- none — <reason>` where the native plan had
  nothing — never delete the file;
- turn every phase/step/verification item into a `- [ ]` checkbox in `tasks.md` under its
  `## N. <Section>` heading.

Then run `specs.py validate --plan <slug>` and branch on the exit code (**0** ok · **1** findings ·
**2** refusal), never on prose — fix any finding before reporting done.
**Done when:** all three artifacts exist and `specs.py validate` reports no error.

### 6. Offer to retire the seed backlog task (only if one exists)
If the native plan clearly came from a `specs/backlog/<task-slug>.md` task — the user names it, or
its title/gist matches one — offer to link it (`--backlog-task <slug>` in Step 5) and retire it,
exactly as `quenching-specs-plan-propose` §7 does: with ONE confirmation, add a row to the
Completed ledger in `specs/backlog/index.md` (`| <task title> | plan <slug> | YYYY-MM-DD |`),
delete `specs/backlog/<task-slug>.md`, and regenerate the DERIVED zone with `specs.py backlog
reindex` per
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
— never hand-edit inside the markers. The row means *developed*, not *done*; if this plan is later
dropped, `quenching-specs-plan-abandon` strikes the row and restores the task. No matching task →
skip silently; the promotion never invents a seed.
**Done when:** a seed task is retired, or there was none.

### 7. Report
Summarize: the slug and `specs/<slug>/`; the artifacts written (and whether `design.md` was
omitted); the task count; which OKF inputs shaped them (one line); whether a backlog seed was
retired; and the next step — "Run `/specs:plan:apply` to start implementing."
**Done when:** the summary is shown.

## Guardrails
- The native plan file is **read-only** — never move, edit, or delete `~/.claude/plans/*.md`.
- Never invent artifact content the native plan lacks; omit `design.md` rather than pad it.
- Always confirm once before scaffolding (Step 4); a declined confirmation writes nothing.
- Use `specs.py new`/`status`/`validate` for scaffolding and paths — branch on exit codes, never
  on prose; never assume artifact paths.
- Retire a seed backlog task only with Step 6's own confirmation, and never fabricate a seed to
  have one to retire.
