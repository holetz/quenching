---
description: Create ONE spec in plans/ — effort proportional to what you gave it, never an interrogation. Triggers on "capture this", "park a spec", "add it to the backlog", "note this for later", "file a spec", "turn my plan into a spec", "convert this Claude Code plan", "make a spec from my plans folder". A sentence becomes the Problem section and nothing else, in seconds; a Claude Code plan file becomes every section it actually supports, mapped and never invented. Not for: filling a spec's remaining sections, or interrogating one → /specs:develop; building one → /specs:execute; closing one out → /specs:conclude; taking a branch or worktree → /specs:isolate; ranking the whole front → /specs:triage.
argument-hint: [what to capture, or a path to a plan file]
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(python3:*), Bash(py:*), AskUserQuestion
---

# /specs:create — put one spec in `plans/`

**Input**: `$ARGUMENTS` — a short description of the problem, **or** a path to a Claude Code plan
file. With neither, glob `~/.claude/plans/*.md`; if that is empty too, ask what to capture.

Creates ONE spec in [`specs/plans/`](../../assets/specs/plans/index.md). That folder is a spec's
whole active life, so what is created here is what gets built: this command creates the file,
`/specs:develop` fills its sections, `/specs:execute` builds it, and `/specs:conclude` closes it
out under the same basename. Nothing here to retire, hand off, or reconcile — and no ledger.

The date prefix is stamped **once, here**, and never rewritten: `promote` moves the file without
renaming it, so this basename is the spec's identity for its whole lifecycle.

The layout, the thirteen canonical sections, the gates and the `specs.py` surface live in
[specs-develop/spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md);
the listing-zone format and the tool fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md);
the shared log procedure in
[docs-add/homes.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-add/homes.md).

## The one rule: effort proportional to input

This command has two inputs of wildly different richness, and exactly one behaviour: **write down
what you were given, and nothing more.**

| Input | What gets written | Cost |
| --- | --- | --- |
| a sentence | `## Problem`, alone | seconds |
| a Claude Code plan file | every section the plan actually supports | one read, one confirmation |

Both obey the same prohibition — **zero interrogation**. Never ask for scope, tasks, design, or a
verification policy. What was not said is left out, and an absent heading is a *not-yet*, not an
omission. The gates get walked by `/specs:develop`; the hard questions get asked by
`/specs:develop` too. Neither belongs here.

The difference between the two rows is **not** effort spent thinking — it is only how much the
input already contained. A rich plan file gets more sections because it *has* more sections, never
because this command worked harder at it.

## Doctrine

- **A sentence becomes `## Problem` and stops.** `specs.py new` stamps the frontmatter (`slug`,
  `title`, `verification`) and that one heading. Every other canonical heading is left ABSENT,
  which the stage-scoped explicit-none rule
  ([spec-driven.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-develop/spec-driven.md) §The gates)
  makes legal. Writing thirteen `- none` headings here would make a fresh capture derive as
  `designed` and clear the whole ready gate without anyone having thought anything.
- **Never invent what the input lacks.** On the plan-file path, `- none — the plan recorded no
  alternatives` is honest; a fabricated risk is not. Where the source said nothing, either leave
  the heading absent or write an explicit none that *says* the source was silent.
- **The date is stamped once, and never again.** Never rename a spec to "fix" its date.
- **English kebab slug, flat home.** One spec per file, no subfolders. The slug is the identity
  every command names, so it is worth a moment's thought — two specs resolving to one slug makes
  every later command refuse (exit 2).
- **MERGE, never clobber.** `specs.py new` refuses (exit 2) on an existing slug. Take that as the
  answer: sharpen the existing spec instead, or pick a different slug.
- **The zone is derived, never hand-edited.** `plans/index.md`'s listing is rebuilt exclusively by
  `specs.py plans reindex`, only between the GENERATED markers.
- **A Claude Code plan file is read-only.** Never move, edit, or delete `~/.claude/plans/*.md` —
  it stays where Claude Code put it.

## Resolving the tool

Resolve `specs.py` by the fallback in
[specs-create/plans-zone.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-create/plans-zone.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal), never on prose.

## Workflow

### 1. Resolve the workspace and classify the input
Find `specs/` at the target repo root. If `plans/` and `archive/` are **absent**, install the seed
from `${CLAUDE_PLUGIN_ROOT}/assets/specs/` and continue. If a legacy `backlog/` or `ready/` still
holds specs, say so once and name `specs.py migrate` — never create a spec into a legacy folder.

Then classify what you were given: **prose** → the sentence path; **a path to an existing `.md`**,
or an explicit ask to convert a plan → the plan-file path.
**Done when:** the workspace resolves and the path is chosen.

### 2. Derive the slug
Take a title and a one-sentence problem from the input, and derive an English kebab slug. On the
plan-file path, derive it from the plan's title or goal ("Add rate limiting to the API" →
`add-api-rate-limiting`). Run `specs.py list --json` to check for a collision.
**Done when:** a free canonical slug is in hand.

### 3. Plan-file path only — read it, and read the bundle
Read the whole plan file and classify its parts against §The mapping below. Then, if the repo
carries an OKF bundle (`docs/index.md` with `okf_version`), read what constrains the work:
`docs/standards/` for the subjects it touches, and `docs/knowledge/glossary.md` so the spec uses
the repo's canonical terms. No bundle → skip silently.

**On the sentence path, skip this step entirely** — reading a bundle to write two sentences is
exactly the cost this command exists to avoid.
**Done when:** the plan's parts are classified, or the sentence path skipped this.

### 4. Plan-file path only — ONE plan → one confirmation
Show, in one plan: the slug and destination `plans/YYYY-MM-DD-<slug>.md`; which sections will be
filled and a one-line preview of each; the number of tasks derived; and which sections will carry
an explicit none because the source was silent. Wait. Declined → nothing is written.

**The sentence path never confirms.** It writes one file from one sentence; a confirmation would
cost more than the thing being confirmed.
**Done when:** the user has answered, or the sentence path skipped this.

### 5. Create the file
```bash
specs.py new <slug> --title "<title>" [--verification per-task|per-section|end-of-plan]
```
Exit 2 means the slug already exists — say so and stop, never invent a variant to get past it.
`--verification` is passed **only** if the source stated a policy; otherwise the default stands and
`/specs:develop` can set it later.
**Done when:** `plans/YYYY-MM-DD-<slug>.md` exists and the tool exited 0.

### 6. Write the sections
Always write `## Problem` — the problem or opportunity in the source's own framing. Two sentences
is a complete answer.
```bash
specs.py section <slug> Problem --write   # body on stdin
```

**Sentence path: stop here.** Write nothing into any other heading.

**Plan-file path:** additionally write each section the plan actually supports, via
`specs.py section <slug> "<Heading>" --write`. Where the plan was silent on a section you are
writing others around, write `- none — <what the source did not record>`. Never fabricate.
**Done when:** `## Problem` is filled, and no section beyond what the input supported exists.

### 7. Regenerate the derived zone
Call `specs.py plans reindex`. The tool owns the zone format and rebuilds it deterministically from
the specs on disk, grouped by derived stage, only between the GENERATED markers.
**Done when:** the zone lists the new spec.

**Nothing is written into `docs/`.** Creating a spec used to append a line to the bundle's
`docs/log.md`; that artifact is retired, and the spec's own frontmatter already records when it
was captured. `specs/` stands on its own.

**No glossary tail here.** Every other capture command runs **Enriching the glossary** as its tail;
this one deliberately does not. A new spec names work, not a concept — the step was a no-op in the
overwhelming majority of runs, and paying to read `knowledge/glossary.md` on a path whose contract
is "seconds" is the wrong trade. A term a spec genuinely coins is caught by
`/docs:glossary-backfill`, or by `/docs:define` when the human says the word matters.

### 8. Check
Run `specs.py validate --spec <slug>` (the spec's own conformance) and
`okf-validate.py specs/plans --listing-root` (the **listing** only — a spec carries no OKF `type:`
and the bundle validator is not pointed at it, per
[specs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-align/conformance.md)).
Then confirm the one thing neither sees: the zone matches disk.
**Done when:** both checks are clean, or the residue is reported verbatim.

### 9. Report
Name the spec (`plans/YYYY-MM-DD-<slug>.md`) and its slug. On the plan-file path, add which
sections were filled from which part of the source, the task count derived, which sections carry an
explicit none — and say plainly that the source file was **read, never moved or deleted**. Name the
next step: `/specs:develop <slug>` to take it further, or `/specs:continue` to be told what to do
next across the whole front.

**Isolation is forwarded, never offered.** If the human asks for a branch or a worktree — now, or
because they want the spec to live on the branch that will carry its work — name
`/specs:isolate <slug>` as the next command. It owns the branch name, the worktree placement and the
`branch: {base, work}` record. Do **not** raise it unprompted: a new prompt in one of the two
most-run commands costs friction for everyone to serve the minority who isolate this early.
**Done when:** the summary is shown.

## The mapping — a Claude Code plan → canonical sections

A Claude Code plan is prose with loose headings, and they may be in any language
(`## Context` / `## Contexto`, `## Decisions` / `## Decisões`) — **match on meaning, never on the
literal string.**

| Native plan part | Canonical section |
| --- | --- |
| context, background, the problem, why now | `## Problem` |
| the goal, what it changes | `## Proposal` |
| non-goals, "fora de escopo", what it will not do | `## Out of Scope` |
| declared scope, files and docs it will touch | `## Impact` |
| acceptance criteria, how to confirm it worked | `## Validation` |
| decisions, chosen approach, architecture, "Decisões" | `## Design` |
| approaches weighed and dropped | `## Alternatives Considered` |
| open questions, "a decidir", unresolved choices | `## Open Decisions` |
| risks, trade-offs, "Riscos" | `## Risks` |
| phases, steps, numbered work, "Etapas" | `## Tasks` (`- [ ]` under `### N. <Section>`) |
| a verification / testing section | `## Tasks` (trailing verification items) |

A plan that carries none of the middle rows produces a spec with `## Problem` and `## Proposal`
and stops — which is the correct outcome, not a failure. **There is no rule that a converted plan
must reach the ready gate**; `/specs:develop` takes it the rest of the way.

## Invariants to never violate

- Never interrogate — no scope, task, design, or policy questions on either path.
- Never write a heading the input did not support, and never stamp `- none — <reason>` into a
  section nobody is otherwise writing around: an explicit none is an *answer*, and at capture
  nobody has given one.
- Never invent content a source plan lacks. Absent, or an honest none that names the silence.
- Never work around `specs.py new`'s exit 2 by inventing a slug variant — a near-duplicate slug is
  worse than a refusal, because identity *is* the slug.
- Never rename a spec to change its date. The prefix records when it was born.
- Never move, edit, or delete a `~/.claude/plans/*.md` file.
- Never hand-edit inside the GENERATED markers (call `specs.py plans reindex`), and never add
  frontmatter to `plans/index.md`.
- Never stamp an OKF `type:` on a spec to quiet the bundle validator.
- Never create a spec into a legacy `backlog/` or `ready/` folder — report and name
  `specs.py migrate`.
- Never add a step to the sentence path. The glossary tail was removed on purpose; anything else
  that reads a bundle file to produce an expected no-op belongs to a sweep, not to creation.
