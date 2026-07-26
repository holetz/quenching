---
name: quenching-specs-backlog-add
description: >-
  Captures ONE task into specs/backlog/ — the task inbox, a quenching-managed sibling of the
  plan folders and specs/archive/, OUTSIDE the OKF docs/ bundle — in seconds: a minimal
  type: task stamp, with optional priority/tags/complexity only when the human states them
  inline. Use when the user asks to "add to the backlog", "park a task", "capture a task",
  "note this for later", or "backlog this". Extracts title + gist from the phrasing ("park X,
  high priority, theme auth, ~8h" → priority: high, tags: [auth], complexity: 8; tags
  normalized against the backlog's), dedupes by slug/title (MERGE, never clobber),
  writes backlog/<task-slug>.md from the task mold, calls `specs.py backlog reindex`,
  logs, and validates. Zero interrogation: what was
  not said is left out — no priority means untriaged, a valid state. Not for: prioritizing the
  whole backlog → quenching-specs-backlog-triage; developing a task into a plan →
  quenching-specs-plan-propose; any other kind of doc → quenching-docs-add.
when_to_use: >-
  parking ONE task in the backlog/ inbox, fast and minimal.
allowed-tools: Read, Grep, Glob, Write, Edit, Bash(python3:*), Bash(py:*)
user-invocable: false
effort: low
---

# quenching-specs-backlog-add — park one task in the inbox

Files ONE task into the task inbox,
[`specs/backlog/`](../../assets/specs/backlog/index.md) — the fast, low-ceremony landing spot
for a unit of work, raw (a task seeds a **plan** — thought through by `quenching-specs-explore`,
developed by `quenching-specs-plan-propose` — before it becomes work) or already clear in scope,
parked between "I thought of this" and "I'm working on this". The backlog is a
**quenching-managed** sibling of the plan folders and `specs/archive/`, **outside** the OKF
`docs/` bundle, so the OKF hook never fires on it — this skill runs the validator over it
explicitly instead (`--listing-root`). The mold is
`${CLAUDE_PLUGIN_ROOT}/assets/templates/backlog/task.md`; the backlog index-zone format, the
`specs.py backlog reindex` contract, and the on-write check live in
[references/backlog-zone.md](references/backlog-zone.md); the shared log procedure lives with
`quenching-docs-add`
([../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md)); the
`type: task` stamp and the conformance core with `quenching-docs-align`
([../quenching-docs-align/references/conformance.md](../quenching-docs-align/references/conformance.md)).
For prioritizing the whole inbox instead of capturing one task, see
`quenching-specs-backlog-triage`.

**The hot path is three files.** A capture reads the backlog's task frontmatter (dedupe), writes
one task file, calls `specs.py backlog reindex` to rebuild the derived zone, and appends one log
line. It does **not** run the glossary tail every other capture skill runs — see Step 6 for why.

## Doctrine

- **Capture in seconds — the stamp stays minimal.** `type: task`, title, one-sentence
  gist, timestamp. `priority` (`critical|high|medium|low`), `tags` (themes), and
  `complexity` (a rough size in development hours) are stamped ONLY when the human states
  them inline. No `done-criteria`, no `vision_refs`, no detailed planning — that thinking
  belongs to the plan (`quenching-specs-explore` / `quenching-specs-plan-propose`) or to
  execution, never to capture; `complexity` is the one rough estimate that may be stamped
  here. `resource` is deliberately omitted — nothing is built yet to point at.
- **Zero interrogation.** Never ask for a priority, a theme, or scope. What was not said
  is left out; a task without `priority` is **untriaged** — a valid state
  `quenching-specs-backlog-triage` exists to fill, not a gap to chase at capture time.
- **Tags are normalized, never minted casually.** Reuse a theme already present in the
  backlog's tasks (`auth`, not a fresh `authentication`); a genuinely new theme is fine.
- **Flat home, English kebab slug.** One task per file, `backlog/<task-slug>.md`, no
  subfolders. Frontmatter is canonical English; the 1–3-sentence body may follow the
  repo's language.
- **MERGE, never clobber.** A slug/title collision merges into the existing task (fill
  missing keys, sharpen the gist) or aborts if it is the same task — never overwrite.
- **The zone is derived, never hand-edited.** `backlog/index.md`'s task listing is
  rebuilt exclusively by `specs.py backlog reindex` from the tasks' frontmatter, only
  between the GENERATED markers, per [references/backlog-zone.md](references/backlog-zone.md).
  The Completed ledger stays outside the zone, untouched.

## Workflow

### 1. Resolve the backlog
Find `specs/backlog/` (the `specs/` tree lives at the target repo root). If `specs/backlog/`
is **absent**, install the seed `index.md` from
`${CLAUDE_PLUGIN_ROOT}/assets/specs/backlog/index.md` (create the folder), then continue.
Resolve `specs.py` and `okf-validate.py` per
[references/backlog-zone.md](references/backlog-zone.md) §Resolving the tool.

### 2. Extract from the user's phrasing
Take the title and one-sentence gist from what the human said. Parse `priority`/`tags`
ONLY when stated inline ("park X, high priority, theme auth" → `priority: high`,
`tags: [auth]`). Normalize tags against the ones already present in `backlog/*.md`
frontmatter. **Zero interrogation** — what was not said is left out.

### 3. Dedupe
`Grep`/`Glob` `backlog/` for a similar slug or title. On a collision, MERGE into the
existing task (never clobber a filled key) — or abort and say so if it is the same task.

### 4. Stamp and write
Fill the `task.md` mold and write `backlog/<task-slug>.md` (English kebab slug). Drop the
optional keys (`priority`/`tags`/`complexity`) that were not stated; `priority` only ever
takes `critical|high|medium|low`, and `complexity` is development hours (a number or a range
like `4-8`).

### 5. Regenerate the derived zone
Call `specs.py backlog reindex` (resolved per §Resolving the tool). The tool owns the zone
format and rebuilds it deterministically from the tasks' frontmatter, only between the
GENERATED markers — never hand-edit inside them, and never touch the Completed ledger. Read
its `changed` field from the JSON to know whether the zone was rewritten (`changed: false`
means it already matched disk). If a target's `backlog/index.md` predates the markers, the
tool anchors on the `## Current tasks` heading to install them without touching the fixed
prose around them.

### 6. Log — one append, nothing else
Append `**Creation**: [<title>](/specs/backlog/<task-slug>.md) — <one line>` to the bundle's
`docs/log.md` per **Appending to `log.md`** in
[../quenching-docs-add/references/homes.md](../quenching-docs-add/references/homes.md). Read only the head
of the file — enough to find or place today's `## YYYY-MM-DD` heading — never the whole history.
(No `docs/` bundle → skip; the backlog stands on its own under `specs/`.)

**No glossary tail here.** Every other capture skill runs **Enriching the glossary** as its tail
step; this one deliberately does not. A parked task names work, not a concept — the step was a
no-op in the overwhelming majority of captures, and paying to read `knowledge/glossary.md` on a
path whose whole contract is "seconds, zero interrogation" is the wrong trade. A term a task
genuinely coins is caught by `quenching-docs-glossary-backfill`, which sweeps for exactly this, or by
`quenching-docs-define` when the human says the word matters.

### 7. Check
Run the validator over the backlog per
[references/backlog-zone.md](references/backlog-zone.md) §The on-write check —
`okf-validate.py specs/backlog --listing-root`, exit 0 with no `index-broken-link` /
`index-orphan` finding — then confirm the two things it cannot see: the GENERATED zone matches
the tasks on disk (guaranteed when `reindex` reported `changed: false`, or after it rewrote the
zone), and the Completed ledger was untouched. The hook is docs-scoped by config, so it does not
fire here; this run is the coverage.

## Invariants to never violate

- Never interrogate the human at capture — no priority, theme, or scope questions; absent
  keys stay absent (untriaged is a valid state).
- Never invent a `priority` or a tag the human did not state, and never use a priority
  value outside `critical|high|medium|low`.
- Never clobber an existing task on collision — MERGE or abort.
- Never hand-edit inside the GENERATED markers (call `specs.py backlog reindex`), never touch
  the Completed ledger at capture, and never add frontmatter to `backlog/index.md`.
- Never expand the stamp beyond the mold — no `done-criteria`, `vision_refs`, assignees, or a
  status field (`complexity` in dev hours is the one allowed estimate); status is positional
  (in the tree = open).
- Never add a step to the capture path. The glossary tail was removed on purpose; anything else
  that reads a bundle file to produce an expected no-op belongs to a sweep, not to capture.
