---
description: Convert a Claude Code plan file into a spec, so it can be gated and archived
argument-hint: [path-to-plan-file]
allowed-tools: Read, Write, Edit, Bash(python3:*), Bash(py:*), Glob, Grep, AskUserQuestion, Skill
---

# /specs:from-claude — promote a Claude Code plan into the front

A Claude Code native plan (the markdown a planning turn writes to `~/.claude/plans/`) is a
one-shot artifact: it drives the turn that made it, then it is inert. This skill lifts one into
the `specs/` front as a real plan — the spec's canonical sections — so the work
gains everything the front gives: a task checklist `specs.py` can track, isolation while it is
built, and the archive-time distillation of its by-products into the OKF `docs/` bundle. The
native plan file is **read, never moved or deleted** — it stays where Claude Code put it.

Spec-driven facts (the `specs/` layout, the thirteen canonical sections, the artifact formats, the
`specs.py` tool surface) live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md).
Resolve `specs.py` by the fallback in
[specs-capture/backlog-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-capture/backlog-zone.md)
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
| `## Context` / background / the problem | `## Problem`/`## Proposal` | the **Why** (`## Why`) |
| the goal / what it changes | `## Problem`/`## Proposal` | `## What Changes`; declared scope → `## Impact` |
| decisions, chosen approach, "Decisões", architecture | `## Design` | `## Decisions` |
| the situation the decisions answer | `## Design` | `## Context` |
| risks, trade-offs, "Riscos" | `## Design` | `## Risks` |
| approaches weighed and dropped | `## Design` | `## Alternatives Considered` |
| open questions, "a decidir", unresolved choices | `## Design` | `## Open Decisions` |
| non-goals, "fora de escopo", what it won't do | `## Problem`/`## Proposal` | `## Out of Scope` |
| acceptance criteria, how to confirm it worked | `## Problem`/`## Proposal` | `## Validation` |
| phases, steps, numbered work, "Etapas" | `## Tasks` | `- [ ]` checkboxes under `## N. <Section>` |
| a verification / testing / acceptance section | `## Tasks` | trailing `- [ ]` verification tasks |

`## Design` is **required-with-explicit-fallback**, never omitted: if the native plan carries no
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
(the spec's canonical sections) and a one-line preview of each from the
mapping; the number of tasks derived; and — the section mapping and
linked and retired. Wait for the confirmation. Declined → nothing is scaffolded.
**Done when:** the user has answered.

### 5. Scaffold and write the artifacts
Run `specs.py new <slug>` (add `--title "<title>"`, and `
seed) — it creates `specs/<slug>/` with the spec's frontmatter and the filled `proposal`/`design`/`tasks`
templates. Then rewrite each template's sections from the mapping, using the resolved paths from
`specs.py status --spec <slug> --json` (never assume paths):
- fill `## Problem`/`## Proposal`'s `## Why` / `## What Changes` / `## Out of Scope` / `## Validation` /
  `## Impact`;
- fill `## Design`'s `## Context` / `## Decisions` / `## Alternatives Considered` /
  `## Open Decisions` / `## Risks`, answering `- none — <reason>` where the native plan had
  nothing — never delete the file;
- turn every phase/step/verification item into a `- [ ]` checkbox in `## Tasks` under its
  `## N. <Section>` heading.

Then run `specs.py validate --spec <slug>` and branch on the exit code (**0** ok · **1** findings ·
**2** refusal), never on prose — fix any finding before reporting done.
**Done when:** all three artifacts exist and `specs.py validate` reports no error.

### 6. Report what landed
Name the new spec (`backlog/YYYY-MM-DD-<slug>.md`), which sections were filled from which part of
the native plan, and the task count derived. Say plainly that the native file was **read, never
moved or deleted** — it stays where it was.

**There is no seed task to retire.** v1 converted a native plan into a plan folder and then had to
close out the `backlog/` task that seeded it, via a ledger row. In v2 the parked thing and the
built thing are the same file, so the conversion produces the spec itself and nothing survives
alongside it to reconcile.
**Done when:** the spec's path, section mapping, and task count are reported.

### 7. Report
Summarize: the slug and `specs/<slug>/`; the artifacts written (and whether `## Design` was
omitted); the task count; which OKF inputs shaped them (one line); whether a backlog seed was
retired; and the next step — "Run `/specs:apply` to start implementing."
**Done when:** the summary is shown.

## Guardrails
- The native plan file is **read-only** — never move, edit, or delete `~/.claude/plans/*.md`.
- Never invent artifact content the native plan lacks; omit `## Design` rather than pad it.
- Always confirm once before scaffolding (Step 4); a declined confirmation writes nothing.
- Use `specs.py new`/`status`/`validate` for scaffolding and paths — branch on exit codes, never
  on prose; never assume artifact paths.
- Never invent a seed spec or a link the native plan does not support.
