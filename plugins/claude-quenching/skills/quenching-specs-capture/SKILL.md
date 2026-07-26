---
name: quenching-specs-capture
description: >-
  Captures ONE spec into specs/backlog/ — the definition phase — in seconds, as a file carrying
  ## Problem and nothing else. Use when the user asks to "capture this", "park a spec", "note
  this for later", "add to the backlog", or "capture an idea". Runs `specs.py new <slug>`, which
  stamps YYYY-MM-DD-<slug>.md ONCE (the date is never rewritten again), writes ## Problem from
  the user's phrasing, regenerates the backlog listing zone, and logs. Zero interrogation: a
  captured spec is four lines of body, not a thirteen-heading skeleton, and every other heading
  is a not-yet rather than an omission. The thing parked here is the SAME FILE that will later
  be built and archived — there is no separate task object and no ledger. Not for: advancing a
  spec's sections toward the ready gate → quenching-specs-develop; sweeping the whole backlog →
  quenching-specs-triage; a doc for the OKF bundle → quenching-docs-add.
when_to_use: >-
  capturing ONE spec into the backlog/ definition phase, fast and minimal.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(python3:*), Bash(py:*)
user-invocable: false
effort: low
---

# quenching-specs-capture — park one spec in the definition phase

Files ONE spec into [`specs/backlog/`](../../assets/specs/backlog/index.md) — the **definition
phase**, the fast landing spot between "I thought of this" and "I'm working on this".

**What is parked here is what gets built.** v1 had a task inbox and a separate plan folder glued
by a ledger row whose meaning ("developed", not "done") needed a paragraph of doctrine to police.
v2 has one file: this skill creates it, `quenching-specs-develop` fills its sections,
`quenching-specs-apply` builds it, and it ends in `archive/` under the same basename. So there is
nothing here to retire, hand off, or reconcile — and no ledger.

The date prefix is stamped **once, here**, and never rewritten: `promote` moves the file without
renaming it, so this basename is the spec's identity for its whole lifecycle.

The layout, the thirteen canonical sections, the phase gates, and the `specs.py` surface live in
[../quenching-specs-develop/references/spec-driven.md](../quenching-specs-develop/references/spec-driven.md);
the backlog listing-zone format and the on-write check in
[references/backlog-zone.md](references/backlog-zone.md); the shared log procedure with
`quenching-docs-add`
([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)).
For sweeping the whole backlog instead of capturing one spec, see
`quenching-specs-triage`.

**The hot path is three files.** A capture resolves the workspace, runs `specs.py new`, writes
`## Problem`, regenerates the listing zone, and appends one log line. It does **not** run the
glossary tail every other capture skill runs — see Step 5 for why.

## Doctrine

- **Capture in seconds — `## Problem` and nothing else.** `specs.py new` stamps the frontmatter
  (`slug`, `title`, `verification`) and the one heading. Every other canonical heading is left
  ABSENT, which is a *not-yet*, not an omission — the phase-scoped explicit-none rule
  ([spec-driven.md](../quenching-specs-develop/references/spec-driven.md) §The phase gates) is what
  makes that legal and what keeps the derived stage honest. Writing thirteen `- none` headings
  here would make a fresh capture derive as `designed` and pass every promote gate without
  anyone having thought anything.
- **Zero interrogation.** Never ask for scope, tasks, design, or a verification policy. What was
  not said is left out. `quenching-specs-develop` is where the gates get walked, and
  `quenching-specs-refine` is where the hard questions get asked — neither belongs here.
- **The date is stamped once, and never again.** `specs.py new` writes `YYYY-MM-DD-<slug>.md`;
  `promote` moves the file without renaming it. Never rename a spec to "fix" its date.
- **English kebab slug, flat home.** One spec per file, no subfolders. The slug is the identity
  every command and cross-reference names, so it is worth a moment's thought — two specs
  resolving to one slug makes every later command refuse (exit 2).
- **MERGE, never clobber.** `specs.py new` refuses (exit 2) on an existing slug. Take that as the
  answer: sharpen the existing spec's `## Problem` instead, or pick a different slug.
- **The zone is derived, never hand-edited.** `backlog/index.md`'s listing is rebuilt exclusively
  by `specs.py backlog reindex`, only between the GENERATED markers, per
  [references/backlog-zone.md](references/backlog-zone.md).

## Workflow

### 1. Resolve the workspace
Find `specs/` at the target repo root. If the three phase folders are **absent**, install the seed
from `${CLAUDE_PLUGIN_ROOT}/assets/specs/` and continue. Resolve `specs.py` and
`okf-validate.py` per [references/backlog-zone.md](references/backlog-zone.md) §Resolving the tool.
**Done when:** the workspace and both tools resolve.

### 2. Derive the slug and create the file
Take a title and a one-sentence problem from what the human said, derive an English kebab slug,
then:
```bash
specs.py new <slug> --title "<title>" [--verification per-task|per-section|end-of-plan]
```
Exit 2 means the slug already exists — say so and stop, never invent a variant to get past it.
`--verification` is passed only if the human stated a policy; otherwise the default stands and
`quenching-specs-develop` can set it later.
**Done when:** `backlog/YYYY-MM-DD-<slug>.md` exists and the tool exited 0.

### 3. Write `## Problem`
```bash
specs.py section <slug> Problem --write   # body on stdin
```
The problem or opportunity, in the human's own framing — two sentences is a complete answer.
Write nothing into any other heading.
**Done when:** `## Problem` is filled and no other section was created.

### 4. Regenerate the derived zone
Call `specs.py backlog reindex`. The tool owns the zone format and rebuilds it deterministically
from the specs on disk, grouped by derived stage, only between the GENERATED markers.
**Done when:** the zone lists the new spec under **Captured**.

### 5. Log — one append, nothing else
Append `**Creation**: [<title>](/specs/backlog/<YYYY-MM-DD-slug>.md) — <one line>` to the bundle's
`docs/log.md` per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md). Read only the
head of the file — enough to find or place today's `## YYYY-MM-DD` heading — never the whole
history. (No `docs/` bundle → skip; `specs/` stands on its own.)
**Done when:** exactly one line was appended, or the bundle is absent.

**No glossary tail here.** Every other capture skill runs **Enriching the glossary** as its tail;
this one deliberately does not. A captured spec names work, not a concept — the step was a no-op
in the overwhelming majority of captures, and paying to read `knowledge/glossary.md` on a path
whose whole contract is "seconds, zero interrogation" is the wrong trade. A term a spec genuinely
coins is caught by `quenching-docs-glossary-backfill`, or by `quenching-docs-define` when the human
says the word matters.

### 6. Check
Run `specs.py validate --spec <slug>` (the spec's own conformance — filename, frontmatter, the
phase-scoped rule) and `okf-validate.py specs/backlog --listing-root` (the **listing** only —
a spec carries no OKF `type:` and the bundle validator is not pointed at it, per
[../quenching-specs-align/references/conformance.md](../quenching-specs-align/references/conformance.md)
§What checks the backlog listing). Then confirm the one thing neither sees: the zone matches disk.
**Done when:** both checks are clean, or the residue is reported verbatim.

## Invariants to never violate

- Never interrogate the human at capture — no scope, task, or design questions; absent headings
  stay absent, because a not-yet is not an omission.
- Never write a heading other than `## Problem`, and never stamp `- none — <reason>` into one: an
  explicit none is an *answer*, and at capture nobody has given one.
- Never work around `specs.py new`'s exit 2 by inventing a slug variant — a near-duplicate slug is
  worse than a refusal, because identity in v2 *is* the slug.
- Never rename a spec to change its date. The prefix records when it was born.
- Never hand-edit inside the GENERATED markers (call `specs.py backlog reindex`), and never add
  frontmatter to `backlog/index.md`.
- Never stamp an OKF `type:` on a spec to quiet the bundle validator.
- Never add a step to the capture path. The glossary tail was removed on purpose; anything else
  that reads a bundle file to produce an expected no-op belongs to a sweep, not to capture.
