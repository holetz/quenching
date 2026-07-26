# Specs front v2 — single-file lifecycle specs

## Why

The three-artifact plan model fragments one unit of thought across `proposal.md`, `design.md`,
`tasks.md`, and `.specs.json` — and the seams show in this very workspace. The active plan
carries 46 tasks and ~600 lines across four files, one of which (`baseline.md`) had to be
invented outside the schema because the contract had no home for a handoff record. A whole
skill (`quenching-specs-plan-update`) exists mostly to keep the three files coherent. A backlog
task and the plan it seeds are two objects glued by a ledger row whose meaning ("developed",
not "done") needs a paragraph of doctrine and an `sp-ledger-orphan` code to police. A human
cannot follow a plan at this complexity, and the structure resists lean plans instead of
encouraging them.

v2 collapses the unit of work to ONE markdown file that lives through its whole lifecycle,
moving through phase folders so a plain file listing IS the status view. Fixed sections with
per-phase gates keep the deterministic rails; sub-stages are derived from section completeness,
never declared; the human OK becomes a gated folder move recorded in git history.

## What Changes

- A spec is one markdown file for its entire lifecycle; phases enrich it, never split it. The
  backlog task and the plan become the same object — the ledger's two meanings die.
- `specs/` becomes three phase folders: `backlog/` (definition — raw problem through refined
  plan), `ready/` (execution — ready to build or building), `archive/` (done or abandoned,
  distinguished by `outcome:` frontmatter).
- Every spec file is named `YYYY-MM-DD-<slug>.md` in EVERY folder. The date is stamped once, at
  capture, and never rewritten — not on promote, not at archive — so a plain listing of any
  folder is chronological (how long has this sat in `backlog/`? how long has this build been
  open in `ready/`?) and a promote stays a pure `git mv`.
- A fixed set of THIRTEEN sections with per-phase requirements: `## Problem`, `## Proposal`,
  `## Out of Scope`, `## Impact`, `## Validation`, `## Design`, `## Alternatives Considered`,
  `## Open Decisions`, `## Risks`, `## Handoff`, `## Tasks`, `## Discoveries`, `## Outcome`. The
  six sections v1 spread across `proposal.md` and `design.md` survive **by name** — dropping them
  would break two mechanisms outright: a task with no `verify:` falls back to the proposal's
  `## Validation`, and `## Impact` is machine-parsed by `parse_impact_standards()`, so removing it
  silently disables `sp-impact-uncovered`. Headings are canonical English (a parsed contract, like
  frontmatter keys); body prose follows the repo's language. The explicit-none rule
  (`- none — <reason>`) survives, but becomes **phase-scoped**: a heading is required — and
  required to carry an explicit none — only once its own phase gate is reached, so `new` stamps
  `## Problem` alone and a captured spec is four lines of body, not a thirteen-heading skeleton.
- Sub-stages are DERIVED from section completeness by `specs.py` (captured → proposed →
  designed → refined → executing), shown in the generated index — never declared, so they
  cannot lie or go stale.
- `specs.py` v2: `promote <slug>` (gated transition, exit 2 listing missing gates, then the
  move), `section <slug> <heading> [--write]` (deterministic partial read/write — the tool that
  makes lean agent context real), `discover <slug> <text>` (append to `## Discoveries`),
  slug-based resolution across folders; `task`/`next`/`status`/`list`/`parallel`/`validate`/
  `doctor` reworked to the single-file model; `archive` folds into `promote`; `.specs.json`
  dies.
- The five-attempt budget is dropped. A blocked task is a visible
  `- [!] <id> <title> — blocked: <reason>` marker in `## Tasks`: human-legible, no hidden
  state, `next` skips it.
- The executor contract: the orchestrator is the spec's ONLY writer (via `specs.py`);
  executors receive a task line + `## Handoff` + the subject's standards, and return
  structured results including discoveries; the orchestrator runs `verify:` and commits —
  whoever commits, verifies.
- One-way migration in `quenching-specs-align` v2: an active 3-file plan folds into a single
  file, a backlog task file becomes a captured-stage spec, and the existing `specs/archive/`
  stays untouched (historical, read-only).
- The thirteen `quenching-specs-*` skills and their command wrappers are rewritten to v2. The
  surface should shrink — propose/refine/update converge on stage-advancing edits of
  one file; abandon becomes promote-to-archive with `outcome: abandoned`; backlog-add becomes
  the capture skill; triage sweeps derived stages plus every active spec's `## Discoveries` — and
  that shrink is **measured, not expected**: a baseline is recorded before the rewrite and asserted
  after it (`skills.py budget` + `lint`), because the always-on surface sits at 88% of its ceiling
  and an overrun is paid silently by every session in every installed repo.
- Templates, `assets/specs/`, and the three `QUENCHING.md` manuals updated to the new surface.
- The four `authority: current` standards in the blast radius are taken on, not left to rot:
  `docs/standards/workflows/plan-artifacts.md` is rewritten **in place** (same path, new title,
  plus a short section on reading a v1 plan in `specs/archive/`), `workflows/task-execution.md` is
  edited surgically (the five-attempt failure budget dies; the rest of the execution contract
  survives), and the two enumerations (`naming/command-surface.md`, `automation/skills.md`) plus
  `knowledge/glossary.md` are re-pointed.

## Out of Scope

- The `docs/` (OKF) front and the `.claude/` front — untouched. The `specs/`↔`docs/` boundary
  survives as-is: a plan still writes its durable rule straight into `docs/standards/` during
  apply, and archive-time distillation still exists.
- Migrating `specs/archive/**` to the new format — it is historical and read-only; churn
  without gain.
- The three open backlog decisions (`decide-plan-quick-skill`, `decide-sp-unrefined-severity`,
  `split-specs-py-backlog-renderer`) — v2 likely obsoletes the latter two, but triage decides
  that, not this plan.
- Renaming the command surface beyond what the skill rewrite itself forces.
- **Upgrading an installed target repo that holds a v1 `specs/` workspace.** The plugin ships to
  other repositories, and the `VERSION`/`plugin.json` bump in task 6.2 is what Claude Code uses to
  apply an upgrade — so a target can wake up with v2 skills over v1 data, having run no migration.
  No format coexistence is built for that case: the target re-aligns manually with `/specs:align`,
  which drives `migrate`, and the three `QUENCHING.md` manuals say so (task 5.1). The exposure this
  leaves — a v1 workspace reading as *empty* rather than as *wrong format* — is recorded and
  accepted in design.md §Risks.

## Validation

- Throwaway-workspace exercise of the full lifecycle: `specs.py new` → `section --write` →
  `promote` (first a refusal listing the missing sections **of the destination phase**, exit 2;
  then success) → `next` / `task --check` → a `[!]` block → `promote` to archive. Exit codes
  0/1/2 exactly as declared, and the file's basename byte-identical in all three folders at the end.
- The phase-scoped explicit-none rule holds in both directions: a freshly captured spec derives as
  `captured` — never `designed`, which is the regression an absolute explicit-none over thirteen
  sections would cause — and a heading that exists but is empty is a refusal, not a filled section.
- `okf-validate.py assets/docs` → 0 errors; the backlog/listing check re-pointed at whatever
  seed shape v2 ships (`--listing-root`).
- Dogfood, in two hops. First against a **throwaway copy** of this repo's `specs/` (task 3.3): all
  three active plans fold correctly, `specs.py validate` clean, `specs/archive/**` untouched.
  Then, once the tool is built and the skills are rewritten, the **real** workspace (task 6.3) —
  last, because this plan lives inside the workspace it migrates.
- The surface budget holds: `skills.py budget` under its ceiling and `skills.py lint` carrying no
  code class absent from the pre-rewrite baseline recorded in task 4.1.
- Version lockstep: `VERSION`, `plugin.json`, `marketplace.json`, and `specs.py --version`
  agree.

## Impact

### Standards this plan will write into docs/standards/

- `docs/standards/workflows/plan-artifacts.md` — rewritten in place: the thirteen-section
  single-file contract, phase-scoped explicit-none, promote-as-the-human-OK, the one template, and
  a short section on reading a v1 plan in `specs/archive/`
- `docs/standards/workflows/task-execution.md` — edited surgically: the five-attempt failure budget
  gives way to the `[!]` blocked marker, and the `verify:` fallback is re-pointed at the single
  file's `## Validation`
- `docs/standards/naming/command-surface.md` — the `quenching-specs-*` ↔ `/specs:*` enumeration
  re-derived from the v2 surface
- `docs/standards/automation/skills.md` — the one example naming a v1 skill
  (`quenching-specs-plan-refine --mode`) re-pointed at its v2 successor

### Standards at `authority: background` this plan may resolve

- none — the bundle carries no `authority: background` doc at all (verified 2026-07-25: zero
  frontmatter matches under `docs/`). Every standard in this plan's blast radius is `current`, and
  each one is declared above.

### Product code this plan expects to touch

- `plugins/claude-quenching/assets/bin/specs.py` — full v2 rewrite
- `plugins/claude-quenching/assets/specs/**` — schema, single-file template, folder seeds
- `plugins/claude-quenching/skills/quenching-specs-*/**` — the thirteen skills, rewritten or merged
- `plugins/claude-quenching/commands/specs/**` — wrappers follow the new surface
- `plugins/claude-quenching/assets/{docs,specs,claude}/QUENCHING.md` — command-surface enumeration
- `docs/knowledge/glossary.md` — the two entries the v2 contract retires or rewrites ("Failure
  budget", "Refinement record"), plus the derived listings under `docs/standards/`
- `README.md`, `CLAUDE.md` — the front's description and the 2×4 matrix wording
