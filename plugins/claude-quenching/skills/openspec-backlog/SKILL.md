---
name: openspec-backlog
description: >-
  Captures ONE task into the repo's OKF backlog/ — the task inbox — in seconds: a minimal
  type: task stamp, with optional priority/tags/complexity only when the human states them
  inline. Use when the user asks to "add to the backlog", "park a task", "capture a task",
  "note this for later", or "backlog this". Extracts title + gist from the phrasing ("park X,
  high priority, theme auth, ~8h" → priority: high, tags: [auth], complexity: 8; tags
  normalized against ones already in the backlog), dedupes by slug/title (MERGE, never clobber), writes
  backlog/<task-slug>.md from the task mold, regenerates the derived GENERATED zone in
  backlog/index.md, logs the creation, and self-checks. Zero interrogation: what was not
  said is left out — no priority means untriaged, a valid state. Not for: prioritizing
  the whole backlog → openspec-backlog-triage; any other kind of doc → quenching-add.
when_to_use: >-
  parking ONE task in the backlog/ inbox, fast and minimal. The prioritization sweep is
  openspec-backlog-triage; routing any other kind of doc is quenching-add.
allowed-tools: Read, Grep, Glob, Write, Edit
user-invocable: false
effort: low
---

# openspec-backlog — park one task in the inbox

Files ONE task into the task inbox,
[`openspec/backlog/`](../../assets/openspec/backlog/index.md) — the fast, low-ceremony
landing spot for a unit of work, raw (it seeds the OpenSpec cycle, `openspec-explore` /
`openspec-propose`, before it becomes work) or already clear in scope, parked between "I
thought of this" and "I'm working on this". The backlog is a **quenching-managed** subfolder
of the `openspec/` tree, **outside** the OKF `docs/` bundle, so the OKF validator never scans
it and this skill self-checks each task on write. The mold is
`${CLAUDE_PLUGIN_ROOT}/assets/templates/backlog/task.md`; the backlog index-zone format and
the on-write self-check live in [references/backlog-zone.md](references/backlog-zone.md); the
shared log/glossary procedure lives with `quenching-add`
([../quenching-add/references/homes.md](../quenching-add/references/homes.md)); the
`type: task` stamp and the conformance core with `quenching-align`
([../quenching-align/references/conformance.md](../quenching-align/references/conformance.md)).
For prioritizing the whole inbox instead of capturing one task, see
`openspec-backlog-triage`.

## Doctrine

- **Capture in seconds — the stamp stays minimal.** `type: task`, title, one-sentence
  gist, timestamp. `priority` (`critical|high|medium|low`), `tags` (themes), and
  `complexity` (a rough size in development hours) are stamped ONLY when the human states
  them inline. No `done-criteria`, no `vision_refs`, no detailed planning — that thinking
  belongs to the OpenSpec cycle or execution, never to capture; `complexity` is the one
  rough estimate that may be stamped here. `resource` is deliberately omitted — nothing is
  built yet to point at.
- **Zero interrogation.** Never ask for a priority, a theme, or scope. What was not said
  is left out; a task without `priority` is **untriaged** — a valid state
  `openspec-backlog-triage` exists to fill, not a gap to chase at capture time.
- **Tags are normalized, never minted casually.** Reuse a theme already present in the
  backlog's tasks (`auth`, not a fresh `authentication`); a genuinely new theme is fine.
- **Flat home, English kebab slug.** One task per file, `backlog/<task-slug>.md`, no
  subfolders. Frontmatter is canonical English; the 1–3-sentence body may follow the
  repo's language.
- **MERGE, never clobber.** A slug/title collision merges into the existing task (fill
  missing keys, sharpen the gist) or aborts if it is the same task — never overwrite.
- **The zone is derived, never hand-edited.** `backlog/index.md`'s task listing is
  rebuilt exclusively from the tasks' frontmatter, only between the GENERATED markers,
  per [references/backlog-zone.md](references/backlog-zone.md). The Completed ledger stays
  outside the zone, untouched.

## Workflow

### 1. Resolve the backlog
Find `openspec/backlog/` (the `openspec/` root may sit at the repo root or a store — resolve
it as the openspec skills do). If `openspec/backlog/` is **absent**, install the seed
`index.md` from `${CLAUDE_PLUGIN_ROOT}/assets/openspec/backlog/index.md` (create the folder;
if `openspec/` itself is missing, offer `openspec init` first, then seed the folder), then
continue.

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
Rebuild `backlog/index.md`'s GENERATED zone from the tasks' frontmatter, per
[references/backlog-zone.md](references/backlog-zone.md). If a target's `backlog/index.md`
predates the markers, install them without touching the fixed prose around them.

### 6. Log and enrich the glossary
Append `**Creation**: [<title>](/openspec/backlog/<task-slug>.md) — <one line>` to the
bundle's `docs/log.md` per **Appending to `log.md`**, then run the shared glossary tail step
per **Enriching the glossary** (both in
[../quenching-add/references/homes.md](../quenching-add/references/homes.md)) —
normally a no-op for a task. (If the repo has no `docs/` OKF bundle, skip these two — the
backlog stands on its own under `openspec/`.)

### 7. Self-check
Run the skill-internal self-check in [references/backlog-zone.md](references/backlog-zone.md):
the task's frontmatter is parseable YAML with a non-empty `type: task`, the GENERATED zone
matches the tasks on disk, every zone link resolves, and the Completed ledger was untouched.
Since `openspec/backlog/` is outside the OKF bundle, the `okf-validate.py` hook does **not**
cover it — this self-check is what replaces the hook for task frontmatter.

## Invariants to never violate

- Never interrogate the human at capture — no priority, theme, or scope questions; absent
  keys stay absent (untriaged is a valid state).
- Never invent a `priority` or a tag the human did not state, and never use a priority
  value outside `critical|high|medium|low`.
- Never clobber an existing task on collision — MERGE or abort.
- Never hand-edit inside the GENERATED markers, never touch the Completed ledger at
  capture, and never add frontmatter to `backlog/index.md`.
- Never expand the stamp beyond the mold — no `done-criteria`, `vision_refs`, assignees, or a
  status field (`complexity` in dev hours is the one allowed estimate); status is positional
  (in the tree = open).
