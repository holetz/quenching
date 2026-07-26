# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin marketplace** with a single plugin, `claude-quenching`
(source: [plugins/claude-quenching/](plugins/claude-quenching/)). The plugin forces a *target*
repository's **three fronts** — the `docs/` **Open Knowledge Format (OKF v0.1)** bundle, the
native `specs/` spec-driven workspace, and the `.claude/` skill + command surface — into one
canonical shape and keeps them conformant, via thirty skills, all under one
`quenching-<front>-<object>-<verb>` taxonomy, plus `/docs`, `/specs`, `/skill` and the root
`/align`, `/align-and-update` commands and two self-contained stdlib Python tools (the OKF
enforcement hook `okf-validate.py` and the plan-cycle CLI `specs.py`).

**The whole surface is one 2×4 matrix.** Every front has exactly two entry points, and two more
span all three:

| Front | **align** — structure, ONE pass | **align-and-update** — + content, LOOPED |
| --- | --- | --- |
| `docs/` | `/docs:align` → `quenching-docs-align` | `/docs:align-and-update` → `quenching-docs-align-and-update` |
| `specs/` | `/specs:align` → `quenching-specs-align` | `/specs:align-and-update` → `quenching-specs-align-and-update` |
| `.claude/` | `/skill:align` → `quenching-skill-align` | `/skill:align-and-update` → `quenching-skill-align-and-update` |
| all three | `/align` → `quenching-align-all` | `/align-and-update` → `quenching-align-and-update-all` |

An **align** shares one interface — read-only inventory → ONE plan → one OK → apply → verify —
and stops. An **align-and-update** runs that align as Stage 1, then pulls in the content sitting
out-of-band for that front, and **loops to a fixpoint**. Everything else in the plugin is a stage
one of these eight invokes, or a per-item capture tool.

There is no application code, no build step, and no test framework here — the repo is
markdown skills (instructions for Claude) plus one dependency-free Python script (the OKF
validator). Treat
skill bodies (`SKILL.md`, `references/*.md`) as the "source code": they are prose
instructions a future Claude session executes literally, so precision in wording matters
as much as correctness in a normal codebase.

## Repository layout

```
.claude-plugin/marketplace.json        # marketplace manifest, lists the one plugin
plugins/claude-quenching/
  .claude-plugin/plugin.json           # plugin manifest (name, version, keywords)
  VERSION                              # plugin version, kept in lockstep with plugin.json
  skills/<skill-name>/
    SKILL.md                           # frontmatter (name/description/when_to_use/allowed-tools) + workflow
    references/*.md                    # doctrine/spec loaded only when the skill runs
  commands/align.md                    # /align — root wrapper over quenching-align-all (three fronts, one pass)
  commands/align-and-update.md         # /align-and-update — root wrapper over quenching-align-and-update-all (three fronts, looped)
  commands/specs/*.md                  # /specs:* — thin wrappers over the thirteen specs-front quenching-specs-* skills (specs/plan/*, specs/backlog/* nested a level deeper)
  commands/docs/*.md                   # /docs:* — thin wrappers over the eleven OKF-bundle quenching-docs-* skills
  commands/docs/documentation/build.md # /docs:documentation:build — the one nested wrapper (acts on ONE home)
  commands/skill/*.md                  # /skill:* — thin wrappers over the four .claude-automation quenching-skill-* skills
  assets/                              # the INSTALLABLE PAYLOAD — copied into target repos, never executed here
    docs/                              # canonical OKF bundle skeleton (index.md listings, log.md seeds, glossary seed)
      QUENCHING.md                     # operator manual for the docs/ front — installed by quenching-docs-align
    specs/                             # native specs/ workspace payload: schema.json (3-artifact graph), templates/{proposal,design,tasks}.md, backlog/ seed (task inbox, type: task), QUENCHING.md
      QUENCHING.md                     # operator manual for the specs/ front — installed by quenching-specs-align
    claude/QUENCHING.md                # operator manual for the .claude/ front — installed by quenching-skill-align
    templates/                         # molds: concept-front, standard-front, catalog/*, backlog/task, harness/*, automation/*, ...
    bin/
      specs.py                         # zero-dependency native plan-cycle CLI (new/list/status/next/task/backlog/validate/archive/doctor)
    hooks/
      okf-validate.py                  # zero-dependency OKF v0.1 conformance checker (CLI + hook)
      hooks-config.json                # checker config (block `okfValidate`)
      settings.snippet.json            # hook wiring to merge into a target's .claude/settings.json
```

`assets/` is inert here (≥2 levels below any `SKILL.md`, so Claude Code does not surface it
as a live skill) — it is the payload the skills stamp into *other* repositories.

Every skill is `user-invocable: false` — hidden from the `/` menu, but still invoked by Claude
via its description or by a thin **command wrapper**. All thirty skills share one
`quenching-<front>-<object>-<verb>` taxonomy, mirrored in the command path. They split by front:
`/docs:*` mirrors the eleven that act on the OKF `docs/` bundle (one nested a level deeper as
`/docs:documentation:build`, because it acts on a single **home**, not the bundle); `/specs:*`
mirrors the thirteen that act on the native `specs/` workspace (the plan skills nested under
`/specs:plan:*`, the inbox under `/specs:backlog:*`); `/skill:*` mirrors the four that act on the
target's `.claude/` automation surface (`quenching-skill-new` → `/skill:new`,
`quenching-skill-align` → `/skill:align`, `quenching-skill-align-and-update` →
`/skill:align-and-update`, `quenching-skill-eval` → `/skill:eval`); and the **root `/align`** + **`/align-and-update`** mirror the two
that span all three fronts — deliberately outside the three namespaces, because they are what
cross them. The wrappers under `commands/` are the explicit user entry points, the skills are
the implementation. Every skill has exactly one wrapper (30 ↔ 30).

## The thirty skills and how they relate

| Skill | Role |
| --- | --- |
| `quenching-docs-align` | Installer + force-aligner + validator. Migrates a target's `docs/` to the canonical tree, stamps frontmatter, regenerates every `index.md`, establishes `log.md`. Invasive: one full plan, one confirmation (a code-coupled rename gets its own). |
| `quenching-docs-add` | Adds ONE new concept doc (standard, catalog table, announcement, …) into the right home with a complete OKF stamp. |
| `quenching-docs-import` | Imports an external source (local files/folders, or URLs) and mints MULTIPLE OKF docs in one plan→OK pass — a batch fan-out of the insert procedure (cites `homes.md`). Bounded web ingestion; additive/merge only, never deletes. |
| `quenching-docs-learn` | Captures ONE piece of generic knowledge a human states into `knowledge/`. |
| `quenching-docs-glossary-backfill` | Sweeps the WHOLE bundle to backfill `knowledge/glossary.md` with terms already documented but never listed; fans sub-agents out per home slice. |
| `quenching-docs-define` | Adds/refines ONE glossary entry on demand — the single-term counterpart of `quenching-docs-glossary-backfill`. |
| `quenching-docs-import-memory` | Drains `~/.claude/projects/<cwd>/memory/` into the bundle, clearing each memory once its doc lands and passes conformance. |
| `quenching-docs-harness` | Refactors a target's `CLAUDE.md`/`AGENTS.md` into thin pointers over its `docs/` bundle, MOVING (never copying) inlined durable knowledge into its home. |
| `quenching-docs-documentation-build` | Owns the **site layer** over the `documentation/` home (`/docs:documentation:build`): the root `mkdocs.yml`/`requirements.txt`, the `.pages` nav files, `site/` gitignore, opt-in Pages CI, and a `mkdocs build --strict` verification. Installs, MERGES a customized config forward (missing keys only, as a diff), regenerates a stale nav; **never touches a page** — page-level drift is reported (`site-*` codes) with the command that fixes it. `quenching-docs-align` step 7 does the first install and hands off here. On-demand tool, not a loop stage. |
| `quenching-docs-status` | The `docs`-front's only **read-only** view (`/docs:status`): every conformance finding in the validator's own codes, plus bundle **density** — concept docs per home (empty homes shown as `0`), glossary size, which `standards/` subjects hold anything — split into what `/docs:align` fixes, what `/docs:align-and-update` drives, and what neither closes. Density figures carry **no finding code**, so a bundle that passes every check while knowing nothing is visible without becoming a defect list. Writes nothing (no `Write`/`Edit` in `allowed-tools`); owns no contract, cites `conformance.md` + `cycle.md`. The `docs` counterpart of `quenching-specs-status`. |
| `quenching-skill-new` | Mints or edits ONE skill in a target's local automation surface (`.claude/skills/` + `.claude/commands/`): single-axis classification (domain-bound × generic), canonical name, mirrored command wrapper, writing doctrine, OKF tail (registry GENERATED zone, glossary offer, log, self-check). One plan → one OK. Owns `references/doctrine.md` + `references/taxonomy.md`. |
| `quenching-skill-eval` | Evaluates ONE skill (`/skill:eval`) by running its cases twice — with the skill loaded and without — in isolated sub-agents, grading every assertion against **quoted evidence**, and reporting the delta over pass rate, tokens and duration. Writes `evals/evals.json` beside the skill plus a per-case `grading.json` and a `benchmark.json`; a skill whose delta is **zero is reported as teaching nothing**, never quietly passed. Description tuning runs on measured should-trigger / should-not-trigger rates, never on taste. Not for: minting or editing a skill → `quenching-skill-new`; the mechanical conformance checks → `skills.py lint`. |
| `quenching-skill-align` | The sweep counterpart: read-only inventory of the existing skill/command surface, ONE migration plan (renames, wrapper mirroring, rule + registry from the molds when missing; keep-and-report unroutables; deletion only on human word), one OK (code-coupled renames individually), post-apply verification. Cites the sibling's references. |
| `quenching-docs-align-and-update` | The `docs`-front conductor: runs `align` → `import-memory` → `harness` → `glossary-backfill` as a dependency pipeline, pass after pass, until a fixpoint (nothing changes and the validator is clean) or a pass cap. (`import` and `quenching-docs-documentation-build` are on-demand tools, not loop stages.) |
| `quenching-skill-align-and-update` | The `.claude`-front conductor: Stage 1 `quenching-skill-align`, Stage 2 a **read-only doctrine audit of every skill body** — the one thing the align is forbidden to touch — reported with the `/skill:new` that fixes it, never rewritten. No out-of-band store to drain, so it converges in 1–2 passes and says so. |
| `quenching-align-all` | The **structural** cross-front conductor (root `/align`): one read-only probe of the three fronts, ONE OK, then `quenching-docs-align` → `quenching-specs-align` → `quenching-skill-align` in dependency order (docs first — the other two write OKF artifacts into it; openspec before skills — it clears the CLI shadow copies the skill sweep would otherwise inventory). One pass, not a fixpoint; conducts, never reimplements. |
| `quenching-align-and-update-all` | The **looping** cross-front conductor (root `/align-and-update`): invokes the three FRONT CONDUCTORS in the same order and loops across fronts, because they feed each other (an archive's distillation is glossary work; the skill front's registry is a `docs/` listing). Authorization **nests one level** — the human confirms once for the whole repo. Owns `references/convergence.md`, the contract every conductor cites. Cross-front pass cap 3. |
| `quenching-specs-align-and-update` | The `specs/`-front conductor: `quenching-specs-align` → `quenching-specs-plan-archive` (each complete plan, **its own confirmation**) → `quenching-specs-backlog-triage`, looped. A **3-stage** pipeline — there is no sync stage, because a plan writes its rule straight into `docs/standards/`. Drives exactly the cycle actions `quenching-specs-align` only reports. Never proposes, never implements, never infers completion. Owns `references/cycle.md`. |
| `quenching-specs-align` | The `specs/`-front align + installer (quenching-native): scaffolds `specs/` by copying `assets/specs/`, installs `specs.py` into `.claude/hooks/`, runs `specs.py doctor`/`validate` and applies their declared remedies, normalizes plan + archive names, seeds/stamps the `backlog/` inbox and regenerates its zone via `specs.py backlog reindex`, **migrates a legacy `openspec/` workspace** to `specs/` (flatten, fold main specs into `docs/standards/`, drop `config.yaml`, `.openspec.yaml`→`.specs.json`, discard deltas, clear shadow copies). Cycle actions are REPORTED, never driven. Owns `references/conformance.md`. |
| `quenching-specs-backlog-add` | Captures ONE task into `specs/backlog/` (the task inbox, outside the OKF bundle) in seconds — minimal `type: task` stamp; inline-stated `priority`/`tags`/`complexity` (rough dev hours) only (zero interrogation; untriaged is a valid state); dedupes, regenerates the index's derived zone via `specs.py backlog reindex`, logs. |
| `quenching-specs-backlog-triage` | The prioritization sweep: reads task frontmatter directly (no sub-agents), proposes ONE triage plan (priority/tags/optional complexity with rationale, staleness, duplicates), applies on one OK, regenerates the zone via `specs.py backlog reindex`. Completion only when human-stated. Stage 3 of the front's pipeline. |
| `quenching-specs-status` | The front's only **read-only** view: active plans with task progress and state, the backlog by priority, the `specs.py doctor`/`validate` + backlog-check results — split into what `/specs:align` would fix, what `/specs:align-and-update` would drive, and what neither closes. Reports in the sweep's own `sp-*` vocabulary, so it doubles as an honest dry run before the OK. Writes nothing (no `Write`/`Edit` in `allowed-tools`); owns no contract, cites all three. |
| `quenching-specs-plan-abandon` | The exit `plan-archive` cannot give: closes out a plan that will **not** be built — archives it with an `ABANDONED.md`, **syncs nothing** (there is no delta), offers to reopen the seed backlog task (untriaged), harvests at most `authority: background`. Closes the task-lifecycle hole `quenching-specs-plan-propose` opens by retiring a task at apply-ready. Never inferred from staleness by any sweep or conductor. |
| `quenching-specs-explore` | Thinking partner before/during a plan; spec-driven + OKF awareness (reads active plans + glossary/knowledge/standards, routes durable insights to the quenching-docs-* skills). Never implements. |
| `quenching-specs-plan-propose` | Creates a plan and generates its artifacts (proposal, design, tasks) until apply-ready — **no deltas**; every section is required-with-explicit-fallback (`- none`), the `docs/standards/` docs it will write appear as `tasks.md` items under `## Impact`'s **parsed** sub-heading, and the plan's `verification` policy is declared here. Reads the OKF bundle as context; retires a seed `specs/backlog/` task into the Completed ledger; offers a refine pass at apply-ready. Owns `references/artifacts.md` + `references/spec-driven.md`. |
| `quenching-specs-plan-refine` | The **generative** counterpart of `plan-update`: interrogates a plan's artifacts in four modes (`interview`, `critic`, `premortem`, `alternatives`), ONE question at a time with an inline recommendation, accumulating answers and applying them in a SINGLE edit at the end, under a declared stop condition. Records `refined: {mode, date}` in `.specs.json`, which clears `sp-unrefined`. Never gates — a plan may always be built unrefined. Owns `references/techniques.md`. |
| `quenching-specs-plan-apply` | Implements a plan's `tasks.md` and **proves** each task — refuses to start on a dirty tree, offers branch/worktree isolation, then per task: writes the code, runs its `verify:` under the plan's declared policy (retrying within a five-attempt budget, re-reading at two), self-reviews the diff on four items, commits it alone as `plan/<name>: <id> <title>`, and only then ticks the box via `specs.py task --check`. Reads the touched subjects' `standards/` as binding contracts; writes durable rules straight into `docs/standards/`, honestly `authority`-graded. May delegate a file-scoped executor sub-agent (never `context: fork`); offers the whole-branch review and chains into archive at 100%. Owns `references/execution.md`. |
| `quenching-specs-plan-update` | Revises a plan's existing planning artifacts and keeps them coherent; never edits code. |
| `quenching-specs-plan-from-claude` | Converts a Claude Code native plan (`~/.claude/plans/*.md`, or a given path) into a front plan, so the work gains the archive-time distillation instead of dying in the plan file: `## Context` → proposal *Why*, decisions/approach → `design.md`, phases/steps → `tasks.md` checkboxes. Runs `specs.py new`, one confirmation; offers to link and retire a seeding backlog task. |
| `quenching-specs-plan-archive` | Checks completion via `specs.py status`, moves the plan to `specs/archive/YYYY-MM-DD-<name>/` via `specs.py archive`, then offers ONE OKF distillation pass — **the single bridge** — carrying by-products the plan did not already write into `docs/` (durable knowledge → `docs/`, per its `references/distill.md`). Nothing is synced; the behavior was written to `standards/` during apply. |

Each `SKILL.md` frontmatter `description` carries its own trigger phrases and its "Not
for: X → other-skill" boundary — read the target skill's frontmatter before assuming
which one owns a task. Shared procedure lives once in its owner and other skills cite it
rather than restating it: the insert procedure in
[`quenching-docs-add/references/homes.md`](plugins/claude-quenching/skills/quenching-docs-add/references/homes.md),
the checks in
[`quenching-docs-align/references/conformance.md`](plugins/claude-quenching/skills/quenching-docs-align/references/conformance.md),
the spec-driven facts (layout, plan artifact graph, `specs.py` surface, the `specs/`↔`docs/`
boundary) in
[`quenching-specs-plan-propose/references/spec-driven.md`](plugins/claude-quenching/skills/quenching-specs-plan-propose/references/spec-driven.md),
the per-artifact authoring doctrine in
[`quenching-specs-plan-propose/references/artifacts.md`](plugins/claude-quenching/skills/quenching-specs-plan-propose/references/artifacts.md),
the `specs/` workspace conformance contract (canonical shape, `sp-*` finding codes, fixes vs.
reports, legacy migration) in
[`quenching-specs-align/references/conformance.md`](plugins/claude-quenching/skills/quenching-specs-align/references/conformance.md),
the cycle-authorization + convergence contract shared by **all five** conductors in
[`quenching-align-and-update-all/references/convergence.md`](plugins/claude-quenching/skills/quenching-align-and-update-all/references/convergence.md)
(each front conductor's own `references/cycle.md` holds **only** that front's pipeline and
routing table — never the contract),
the **sweep contract shared by all three aligns** — convergence over accommodation, one plan →
one OK with code-coupled items gating individually, the two-scan blast-radius procedure,
MERGE-never-clobber, never-delete-on-a-guess, align-conformance-report-the-cycle — in
[`quenching-align-all/references/sweep-doctrine.md`](plugins/claude-quenching/skills/quenching-align-all/references/sweep-doctrine.md)
(each align's `## Doctrine` cites it and states **only** its own front's deltas),
the OKF distillation doctrine in
[`quenching-specs-plan-archive/references/distill.md`](plugins/claude-quenching/skills/quenching-specs-plan-archive/references/distill.md),
and the skill-writing doctrine + automation taxonomy in
[`quenching-skill-new/references/doctrine.md`](plugins/claude-quenching/skills/quenching-skill-new/references/doctrine.md)
and [`quenching-skill-new/references/taxonomy.md`](plugins/claude-quenching/skills/quenching-skill-new/references/taxonomy.md)
(cited by `quenching-skill-align`, never restated).

### The `specs/` front ↔ OKF relation

The `specs/` front is **entirely native** — the plugin absorbed what it used to borrow from the
external OpenSpec CLI (`@fission-ai/openspec`). There is no Node runtime, no `config.yaml`, no
main-spec store, and **no delta format**: a **plan** writes its durable rule **directly** into
`docs/standards/` (honestly `authority`-graded), isolated on a branch while it is built. Two
stdlib Python tools give the LLM deterministic rails — `okf-validate.py` (the OKF hook) and
`specs.py` (`new`/`list`/`status`/`next`/`task`/`parallel`/`backlog`/`validate`/`archive`/`doctor`,
uniform `--json` and strict exit codes 0/1/2). The skills branch on data, never on prose.

The unit of work is a **plan** (`specs/<plan-name>/` — `proposal.md`, `design.md`, `tasks.md`,
`.specs.json`), not an "OpenSpec change", and there is no separate spec store to
bridge to, so the old delta (a branch reimplemented in markdown) is gone: isolation-while-building
is a real git **branch or worktree** (offered by `quenching-specs-plan-apply`), with merge,
history, and reversion. The **OKF bridge** is a single pass at archive time: `docs/` is read as
context going in (standards, glossary; a `specs/backlog/` task as seed), and the by-products the
plan did not already commit to `docs/` are distilled out at archive (never bulk-copied). `specs/`
and `docs/` never duplicate content — the boundary is owned once by
[`spec-driven.md`](plugins/claude-quenching/skills/quenching-specs-plan-propose/references/spec-driven.md) §Boundary.

Of the thirteen `quenching-specs-*` skills, **two** are stages of the front's 3-stage pipeline when
`quenching-specs-align-and-update` conducts it — `quenching-specs-plan-archive` and
`quenching-specs-backlog-triage`; the plan skills (`propose`, `refine`, `apply`, `update`,
`from-claude`) and `explore` never are, because each needs fresh human intent a conducted pass
does not have.
`quenching-specs-align` is the front's own aligner *and* installer (it scaffolds `specs/` and
installs `specs.py`; it also **migrates a legacy `openspec/` workspace** one-way). Every skill on
this front is quenching-native — no `metadata.generatedBy` anywhere.

**The ledger's two meanings.** `quenching-specs-plan-propose` retires a seed task into
`backlog/index.md`'s Completed ledger at **apply-ready** — that row means *developed*, not *done*,
and the Outcome column is what distinguishes it from a row written when a human states a task is
finished. A plan dropped after that point is what `quenching-specs-plan-abandon` exists to handle;
one dropped *without* it leaves an `sp-ledger-orphan`, which `quenching-specs-align` and
`quenching-specs-status` report and neither ever auto-repairs (the ledger is curated by hand, always).

## The OKF bundle contract

Every target repo the plugin aligns converges to the **same tree** under `docs/`:
`standards/` (current contracts, subject subfolders — an agreed-but-unproven rule sits here as
`authority: background`; there is no separate `decisions/` home), `catalog/` (own data),
`vision/`, `documentation/`, `knowledge/` (incl. fixed `glossary.md`),
`reference/` (external facts). The **task inbox** lives **outside** the bundle at
`specs/backlog/` (`type: task`, optional `priority`/`tags`/`complexity`, derived index zone —
a quenching-managed `specs/` sibling, not scanned by the OKF validator). Rules the plugin
enforces everywhere:

- `index.md` is a reserved, frontmatter-free listing (exception: root `docs/index.md`
  carries only `okf_version: "0.1"`).
- Every other concept doc MUST have YAML frontmatter with a non-empty `type` from the
  fixed vocabulary.
- `log.md` uses `## YYYY-MM-DD` headings, newest first.
- Folder names, concept-doc file slugs, frontmatter keys, and `type` values are canonical
  English (cross-repo greppable); body prose may follow the target repo's language;
  identifier-derived slugs (catalog tables, repo names) stay verbatim.
- `CLAUDE.md`, `AGENTS.md`, **and `QUENCHING.md`** are **exempt** basenames — harness pointers
  and the plugin's own operator manual, never OKF concepts. Never stamp a `QUENCHING.md`, never
  convert it to `index.md`, and never overwrite one whose banner a human removed.

The full normative spec is in each skill's `references/` (`okf-spec.md`, `taxonomy.md`,
`migration.md`, `conformance.md`).

## The three operator manuals (`QUENCHING.md`)

Each align installs a static, repo-agnostic **operator manual** beside the front it owns —
`assets/docs/QUENCHING.md` → `docs/` (`quenching-docs-align`), `assets/specs/QUENCHING.md` →
`specs/` (`quenching-specs-align`), `assets/claude/QUENCHING.md` → `.claude/`
(`quenching-skill-align`). They explain to a *target repo's* reader how the skills operate:
commands, the one-plan-one-OK model, generated zones, the hook, recipes, troubleshooting. They
are written in **English** (the canonical-surface rule) and must stay repo-agnostic — no fact
about any particular repository ever goes in them.

The four-branch refresh rule is owned **once**, by `quenching-docs-align/SKILL.md` §4 (absent →
install · older banner → overwrite · same-or-newer → leave · banner removed by a human → keep
and report); the other two aligns **cite** it. The banner's `<VERSION>` placeholder is filled
from the `VERSION` file at copy time, so a release adds no lockstep item — but a command rename
or a new skill **does** mean editing all three manuals, since they enumerate the command surface.

## The enforcement hook (`assets/hooks/okf-validate.py`)

Stdlib-only Python; runs as a CLI (`okf-validate.py <dir> [--json] [--listing-root]`,
exit 0 = conforms)
or as a hook (reads hook JSON on stdin, dispatches on `hook_event_name`):
`PostToolUse` and `Stop` propose fixes via `additionalContext`; an opt-in `PreToolUse`
(`hardBlock: true`) denies the two hard violations (a typed `index.md`, an untyped concept
doc). The `Stop` sweep is dirty-gated by default (`stopScan: "dirty"`) via a marker file so
a turn touching no `docs/**` file costs one stat. **`--listing-root`** points the same checker
at a quenching-managed tree that is not an OKF bundle root — today `specs/backlog/`, which the
hook's `docsDir` never reaches: the scanned `index.md` is held to the plain-listing rule instead
of the bundle-root one, and `bundle-no-index` is dropped. `type: task` is also exempt from the
`resource` recommendation, since the backlog mold omits it deliberately. This is what replaced
the backlog skills' hand-written prose self-check. `--version` is kept in lockstep with
`plugins/claude-quenching/VERSION`; `quenching-docs-align` step 6 offers to install or upgrade it
into a target's `.claude/hooks/`.

## The plan-cycle tool (`assets/bin/specs.py`)

Stdlib-only Python, the same self-contained mold as `okf-validate.py` — the deterministic rails
for the `specs/` front, replacing what the plugin used to borrow from the external OpenSpec CLI.
Uniform contract: `--json` on every subcommand and strict exit codes (**0** ok · **1** findings ·
**2** refusal — e.g. `archive` on a plan with open tasks and no `--force`), so a skill branches on
data, never on prose. Subcommands: `new` (scaffold a plan folder + filled templates + `.specs.json`,
incl. the `--verification` policy), `list`, `status --plan <n>` (the 3-artifact graph —
`proposal`→`design`→`tasks`, `applyRequires: [tasks]` — plus the verification policy, the
refinement record, and blocked tasks), **`next --plan <n>`** (THE single next action, carrying the
task's `verify:`/`files:`/`pattern:`/`[P]`, and **skipping a task that burned its attempt budget**),
**`task --plan <n> --check <id>`** (flip a checkbox mechanically) with `--attempt`/`--reset-attempts`
for the failure budget, **`parallel --plan <n>`** (verify a `[P]` group's `files:` sets are
disjoint — mechanically, never judged in prose), **`backlog reindex`** (regenerate the
`backlog/index.md` GENERATED zone — the tool OWNS that format), `validate` (structure plus the
three non-gating thinking warnings `sp-unrefined`/`sp-design-scaffold`/`sp-impact-uncovered`),
`archive`, `doctor`. Schema and templates load from `assets/specs/` when adjacent, else from
embedded fallbacks, so an installed copy under a target's `.claude/hooks/` still works — which is
why **the templates are duplicated in `specs.py` as constants and must be edited in lockstep**. `quenching-specs-align` installs it; its `--version` is kept in
lockstep with `VERSION`.

## Verifying changes

There is no test suite. To verify the plugin's own shipped skeleton is still conformant
after touching anything under `plugins/claude-quenching/assets/`:

```bash
cd plugins/claude-quenching
# version lockstep — VERSION, specs.py, and okf-validate.py must all agree
cat VERSION; python3 assets/bin/specs.py --version; python3 assets/hooks/okf-validate.py --version
# the skeleton and the backlog seed are conformant by construction
python3 assets/hooks/okf-validate.py assets/docs                          # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/backlog --listing-root  # 0 error(s), 0 warning(s)
```

`specs.py` itself has no fixture in the repo; exercise it in a throwaway workspace
(`specs.py new x` → `status`/`next`/`task` → `archive x --force`) when its logic changes.
On this machine, `python3`/`py` resolve to the Windows Store stub — use the real interpreter at
`C:\Users\<user>\AppData\Local\Programs\Python\Python312\python.exe`.

When editing a `SKILL.md`, keep the `description` under the shared **1,536-character**
per-skill cap (Claude Code truncates beyond it) with trigger phrases in the frontmatter's
second sentence so truncation never eats them; keep skill bodies well under 500 lines and
push shared procedure into the owning `references/*.md` instead of restating it in every
skill that cites it.

## Two rules that must survive any refactor

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`quenching-align-and-update-all/references/convergence.md` §cycle-authorization) must still surface code-coupled
  confirmations mid-flow, which a forked context cannot present.
- **Never downgrade classification or executor sub-agents to `haiku` in
  `quenching-docs-import-memory`.** A misclassification there becomes a wrong memory deletion —
  see the model-policy table in
  [plugins/claude-quenching/README.md](plugins/claude-quenching/README.md#cost-model) for
  which sub-agent calls in the other skills are safe to run on cheaper models/effort.

## Releasing

Bump `version` in `plugins/claude-quenching/.claude-plugin/plugin.json` **and**
`plugins/claude-quenching/VERSION` together — that pair is what Claude Code uses to detect
and apply an upgrade. Keep the `VERSION` constant in **both** shipped scripts in lockstep with
that pair — `assets/hooks/okf-validate.py` **and** `assets/bin/specs.py` — since each one's
`--version` is what its installing align (`quenching-docs-align` for the hook,
`quenching-specs-align` for `specs.py`) compares against an already-installed copy in a target
repo. Mirror the plugin `version` in the marketplace manifest's plugin entry
(`.claude-plugin/marketplace.json`) too. A command rename or a new skill also means editing all
three `QUENCHING.md` operator manuals, since they enumerate the command surface.
