# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin marketplace** with a single plugin, `quenching`
(source: [plugins/quenching/](plugins/quenching/)). The plugin forces a *target*
repository's **three fronts** — the `docs/` **Open Knowledge Format (OKF v0.1)** bundle, the
native `specs/` spec-driven workspace, and the `.claude/` command surface — into one
canonical shape and keeps them conformant, via twenty-eight commands under `/docs`, `/specs`,
`/skill` and the root `/align`, `/align-and-update`, plus three self-contained stdlib Python
tools (the OKF enforcement hook `okf-validate.py`, the spec-cycle CLI `specs.py`, and the
command-surface verifier `skills.py`).

**ONE FILE PER ENTRY POINT.** Claude Code merged custom commands into skills, so each
`commands/<path>.md` carries both the description that routes to it and the body that runs.
There is no `skills/` tree and no wrapper: **a command's path is its whole identity**
(`commands/docs/add.md` → `/docs:add` → `quenching:docs:add` through the Skill tool).

**The whole surface is one 2×4 matrix.** Every front has exactly two entry points, and two more
span all three:

| Front | **align** — structure, ONE pass | **align-and-update** — + content, LOOPED |
| --- | --- | --- |
| `docs/` | `/docs:align` | `/docs:align-and-update` |
| `specs/` | `/specs:align` | `/specs:align-and-update` |
| `.claude/` | `/skill:align` | `/skill:align-and-update` |
| all three | `/align` | `/align-and-update` |

An **align** shares one interface — read-only inventory → ONE plan → one OK → apply → verify —
and stops. An **align-and-update** runs that align as Stage 1, then pulls in the content sitting
out-of-band for that front, and **loops to a fixpoint**. Everything else in the plugin is a stage
one of these eight invokes, or a per-item capture tool.

There is no application code, no build step, and no test framework here — the repo is
markdown command files (instructions for Claude) plus three dependency-free Python scripts.
Treat command bodies (`commands/**/*.md`, `assets/references/**/*.md`) as the "source code":
they are prose instructions a future Claude session executes literally, so precision in wording
matters as much as correctness in a normal codebase.

## Repository layout

```
.claude-plugin/marketplace.json        # marketplace manifest, lists the one plugin
plugins/quenching/
  .claude-plugin/plugin.json           # plugin manifest (name, version, keywords)
  VERSION                              # plugin version, kept in lockstep with plugin.json
  commands/                            # THE SURFACE — the only tree Claude Code registers
    align.md                           # /align — three fronts, one pass
    align-and-update.md                # /align-and-update — three fronts, looped
    specs/*.md                         # /specs:* — the eleven specs-front commands (FLAT)
    docs/*.md                          # /docs:* — the eleven OKF-bundle commands
    docs/documentation/build.md        # /docs:documentation:build — the one nested command (acts on ONE home)
    skill/*.md                         # /skill:* — the four .claude-automation commands
  assets/                              # everything Claude Code must NOT surface as an entry point
    references/<name>/*.md             # shared procedure, cited by ${CLAUDE_PLUGIN_ROOT} absolute path
    evals/<command-path>/              # measured case sets, mirroring the command path
    docs/                              # canonical OKF bundle skeleton (index.md listings, log.md seeds, glossary seed)
      QUENCHING.md                     # operator manual for the docs/ front — installed by /docs:align
    specs/                             # native specs/ workspace payload: schema.json, templates/, backlog/ seed, QUENCHING.md
      QUENCHING.md                     # operator manual for the specs/ front — installed by /specs:align
    claude/QUENCHING.md                # operator manual for the .claude/ front — installed by /skill:align
    templates/                         # molds: concept-front, standard-front, catalog/*, backlog/task, harness/*, automation/*, ...
    bin/
      specs.py                         # zero-dependency native spec-cycle CLI
      skills.py                        # zero-dependency command-surface verifier (lint/doctor/registry/budget/selftest)
    hooks/
      okf-validate.py                  # zero-dependency OKF v0.1 conformance checker (CLI + hook)
      hooks-config.json                # checker config (block `okfValidate`)
      settings.snippet.json            # hook wiring to merge into a target's .claude/settings.json
```

**`commands/**` is the only tree Claude Code registers, so nothing else may live in it.** A
`references/` folder placed beside a command file would register every reference as a phantom
entry (`/docs:align:references:conformance`) — which does not error, it just appears in the `/`
menu and does nothing. That is why shared procedure lives under `assets/`, whose meaning is
exactly *"everything Claude Code must not surface as an entry point"* — the installable payload
is a subset of that, not the whole of it. Rule and rationale:
[docs/standards/architecture/plugin-layout.md](docs/standards/architecture/plugin-layout.md).

Every command keeps **default invocation** — typable at `/`, and reachable by name by a conductor
or a spoken trigger. No `user-invocable: false`, no `disable-model-invocation`. The surface splits
by front: `/docs:*` are the eleven that act on the OKF `docs/` bundle (one nested a level deeper
as `/docs:documentation:build`, because it acts on a single **home**, not the bundle); `/specs:*`
the eleven that act on the native `specs/` workspace; `/skill:*` the four that act on the target's
`.claude/` automation surface; and the **root `/align`** + **`/align-and-update`** the two that
span all three fronts — deliberately outside the three namespaces, because they are what cross
them.

## The twenty-eight commands and how they relate

| Command | Role |
| --- | --- |
| `/docs:align` | Installer + force-aligner + validator. Migrates a target's `docs/` to the canonical tree, stamps frontmatter, regenerates every `index.md`, establishes `log.md`. Invasive: one full plan, one confirmation (a code-coupled rename gets its own). |
| `/docs:add` | Adds ONE new concept doc (standard, catalog table, announcement, …) into the right home with a complete OKF stamp. |
| `/docs:import` | Imports an external source (local files/folders, or URLs) and mints MULTIPLE OKF docs in one plan→OK pass — a batch fan-out of the insert procedure (cites `homes.md`). Bounded web ingestion; additive/merge only, never deletes. |
| `/docs:learn` | Captures ONE piece of generic knowledge a human states into `knowledge/`. |
| `/docs:glossary-backfill` | Sweeps the WHOLE bundle to backfill `knowledge/glossary.md` with terms already documented but never listed; fans sub-agents out per home slice. |
| `/docs:define` | Adds/refines ONE glossary entry on demand — the single-term counterpart of `/docs:glossary-backfill`. |
| `/docs:import-memory` | Drains `~/.claude/projects/<cwd>/memory/` into the bundle, clearing each memory once its doc lands and passes conformance. |
| `/docs:harness` | Refactors a target's `CLAUDE.md`/`AGENTS.md` into thin pointers over its `docs/` bundle, MOVING (never copying) inlined durable knowledge into its home. |
| `/docs:documentation:build` | Owns the **site layer** over the `documentation/` home: the root `mkdocs.yml`/`requirements.txt`, the `.pages` nav files, `site/` gitignore, opt-in Pages CI, and a `mkdocs build --strict` verification. Installs, MERGES a customized config forward (missing keys only, as a diff), regenerates a stale nav; **never touches a page** — page-level drift is reported (`site-*` codes) with the command that fixes it. `/docs:align` step 7 does the first install and hands off here. On-demand tool, not a loop stage. |
| `/docs:status` | The `docs`-front's only **read-only** view: every conformance finding in the validator's own codes, plus bundle **density** — concept docs per home (empty homes shown as `0`), glossary size, which `standards/` subjects hold anything — split into what `/docs:align` fixes, what `/docs:align-and-update` drives, and what neither closes. Density figures carry **no finding code**, so a bundle that passes every check while knowing nothing is visible without becoming a defect list. Writes nothing; owns no contract, cites `conformance.md` + `cycle.md`. The `docs` counterpart of `/specs:status`. |
| `/skill:new` | Mints or edits ONE command in a target's local automation surface (`.claude/commands/`): single-axis classification (domain-bound × generic), the command path (which is the name), writing doctrine, OKF tail (registry GENERATED zone, glossary offer, log, self-check). One plan → one OK. Owns `references/doctrine.md` + `references/taxonomy.md`. |
| `/skill:eval` | Evaluates ONE command by running its cases twice — with the command loaded and without — in isolated sub-agents, grading every assertion against **quoted evidence**, and reporting the delta over pass rate, tokens and duration. Writes `evals.json` into the tree mirroring the command's path, plus a per-case `grading.json` and a `benchmark.json`; a command whose delta is **zero is reported as teaching nothing**, never quietly passed. Description tuning runs on measured should-trigger / should-not-trigger rates, never on taste. Not for: minting or editing a command → `/skill:new`; the mechanical conformance checks → `skills.py lint`. |
| `/skill:align` | The sweep counterpart: read-only inventory of the existing command surface, ONE migration plan (**collapsing any surviving skill+wrapper pair into one file**, renames, rule + registry from the molds when missing; keep-and-report unroutables; deletion only on human word), one OK (code-coupled renames individually), post-apply verification. Cites the sibling's references. |
| `/docs:align-and-update` | The `docs`-front conductor: runs `align` → `import-memory` → `harness` → `glossary-backfill` as a dependency pipeline, pass after pass, until a fixpoint (nothing changes and the validator is clean) or a pass cap. (`import` and `/docs:documentation:build` are on-demand tools, not loop stages.) |
| `/skill:align-and-update` | The `.claude`-front conductor: Stage 1 `/skill:align`, Stage 2 a **read-only doctrine audit of every command body** — the one thing the align is forbidden to touch — reported with the `/skill:new` that fixes it, never rewritten. No out-of-band store to drain, so it converges in 1–2 passes and says so. |
| `/align` | The **structural** cross-front conductor: one read-only probe of the three fronts, ONE OK, then `quenching:docs:align` → `quenching:specs:align` → `quenching:skill:align` in dependency order (docs first — the other two write OKF artifacts into it; specs before skills — it clears the CLI shadow copies the skill sweep would otherwise inventory). One pass, not a fixpoint; conducts, never reimplements. |
| `/align-and-update` | The **looping** cross-front conductor: invokes the three FRONT CONDUCTORS in the same order and loops across fronts, because they feed each other (an archive's distillation is glossary work; the skill front's registry is a `docs/` listing). Authorization **nests one level** — the human confirms once for the whole repo. Owns `references/convergence.md`, the contract every conductor cites. Cross-front pass cap 3. |
| `/specs:align-and-update` | The `specs/`-front conductor: `/specs:align` → `/specs:archive` (each complete spec, **its own confirmation**) → `/specs:triage`, looped. A **3-stage** pipeline — there is no sync stage, because a spec writes its rule straight into `docs/standards/`. Drives exactly the cycle actions `/specs:align` only reports. Never proposes, never implements, never infers completion. Owns `references/cycle.md`. |
| `/specs:align` | The `specs/`-front align + installer (quenching-native): scaffolds `specs/` by copying `assets/specs/`, installs `specs.py` into `.claude/hooks/`, runs `specs.py doctor`/`validate` and applies their declared remedies, normalizes spec + archive names, seeds/stamps the `backlog/` inbox and regenerates its zone via `specs.py backlog reindex`, **migrates a legacy `openspec/` workspace** to `specs/`. Cycle actions are REPORTED, never driven. Owns `references/conformance.md`. |
| `/specs:capture` | Captures ONE spec into `specs/backlog/` (the definition phase) in seconds — `## Problem` and nothing else; zero interrogation. Dedupes, regenerates the listing zone, logs. |
| `/specs:triage` | The prioritization sweep: reads spec frontmatter directly (no sub-agents), proposes ONE triage plan (staleness, duplicates, stage), applies on one OK, regenerates the zone. Completion only when human-stated. Stage 3 of the front's pipeline. |
| `/specs:status` | The front's only **read-only** view: specs by phase with task progress, the backlog, the `specs.py doctor`/`validate` results — split into what `/specs:align` would fix, what `/specs:align-and-update` would drive, and what neither closes. Reports in the sweep's own `sp-*` vocabulary, so it doubles as an honest dry run before the OK. Writes nothing; owns no contract, cites all three. |
| `/specs:archive` | Closes a spec out — promotes it to `archive/` with `outcome: done` or `outcome: abandoned`, then offers ONE OKF distillation pass. `done` REFUSES while boxes are open unless forced; `abandoned` is always allowed and distils at most a background note. Never inferred from staleness by any sweep. |
| `/specs:explore` | Thinking partner before/during a spec; spec-driven + OKF awareness (reads active specs + glossary/knowledge/standards, routes durable insights to the `/docs:*` commands). Never implements. |
| `/specs:develop` | Advances ONE spec's sections toward the ready gate — filling what is missing, revising what is there, offering the promote when the gate is met. Every section is required-with-explicit-fallback (`- none — <reason>`), the `docs/standards/` docs it will write appear under `## Impact`, and the spec's `verification` policy is declared here. Reads the OKF bundle as context. NEVER edits code. Owns `references/artifacts.md` + `references/spec-driven.md`. |
| `/specs:refine` | The **generative** counterpart of `develop`: interrogates a spec in four modes (`interview`, `critic`, `premortem`, `alternatives`), ONE question at a time with an inline recommendation, accumulating answers and applying them in a SINGLE edit at the end, under a declared stop condition. Records `refined: {mode, date}`, which clears `sp-unrefined`. Never gates — a spec may always be built unrefined. Owns `references/techniques.md`. |
| `/specs:apply` | Implements a spec's `## Tasks` and **proves** each task — refuses to start on a dirty tree, offers branch/worktree isolation, then per task: writes the code, runs its `verify:` under the spec's declared policy, self-reviews the diff on four items, commits it alone as `plan/<name>: <id> <title>`, and only then ticks the box via `specs.py task --check`. Reads the touched subjects' `standards/` as binding contracts; writes durable rules straight into `docs/standards/`, honestly `authority`-graded. A task that stops converging is written `- [!] … — blocked: <reason>` into `## Tasks`. May delegate a file-scoped executor sub-agent (never `context: fork`); offers the whole-branch review and chains into archive at 100%. Owns `references/execution.md`. |
| `/specs:from-claude` | Converts a Claude Code native plan (`~/.claude/plans/*.md`, or a given path) into a spec, so the work gains the archive-time distillation instead of dying in the plan file. Runs `specs.py new`, one confirmation; offers to link and retire a seeding backlog spec. |

Each command's frontmatter `description` carries its trigger phrases and its "Not for: X →
other-command" boundary — read the target command's frontmatter before assuming which one owns a
task. Shared procedure lives once in its owner and other commands cite it by **absolute path**
(`${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md`) rather than restating it:
the insert procedure in
[`docs-add/homes.md`](plugins/quenching/assets/references/docs-add/homes.md),
the checks in
[`docs-align/conformance.md`](plugins/quenching/assets/references/docs-align/conformance.md),
the spec-driven facts (the three phase folders, the thirteen canonical sections, the phase gates,
the `specs.py` surface, the `specs/`↔`docs/` boundary) in
[`specs-develop/spec-driven.md`](plugins/quenching/assets/references/specs-develop/spec-driven.md),
the per-section authoring doctrine in
[`specs-develop/artifacts.md`](plugins/quenching/assets/references/specs-develop/artifacts.md),
the `specs/` workspace conformance contract in
[`specs-align/conformance.md`](plugins/quenching/assets/references/specs-align/conformance.md),
the cycle-authorization + convergence contract shared by **all five** conductors in
[`align-and-update-all/convergence.md`](plugins/quenching/assets/references/align-and-update-all/convergence.md)
(each front conductor's own `cycle.md` holds **only** that front's pipeline and routing table —
never the contract),
the **sweep contract shared by all three aligns** — convergence over accommodation, one plan →
one OK with code-coupled items gating individually, the two-scan blast-radius procedure,
MERGE-never-clobber, never-delete-on-a-guess, align-conformance-report-the-cycle — in
[`align-all/sweep-doctrine.md`](plugins/quenching/assets/references/align-all/sweep-doctrine.md)
(each align's `## Doctrine` cites it and states **only** its own front's deltas),
the OKF distillation doctrine in
[`specs-archive/distill.md`](plugins/quenching/assets/references/specs-archive/distill.md),
and the command-writing doctrine + automation taxonomy in
[`skill-new/doctrine.md`](plugins/quenching/assets/references/skill-new/doctrine.md)
and [`skill-new/taxonomy.md`](plugins/quenching/assets/references/skill-new/taxonomy.md)
(cited by `/skill:align`, never restated).

### The `specs/` front ↔ OKF relation

The `specs/` front is **entirely native** — the plugin absorbed what it used to borrow from the
external OpenSpec CLI (`@fission-ai/openspec`). There is no Node runtime, no `config.yaml`, no
main-spec store, and **no delta format**: a **spec** writes its durable rule **directly** into
`docs/standards/` (honestly `authority`-graded), isolated on a branch while it is built. Three
stdlib Python tools give the LLM deterministic rails — `okf-validate.py` (the OKF hook),
`specs.py` (the spec cycle) and `skills.py` (the command surface), all with uniform `--json` and
strict exit codes 0/1/2. The commands branch on data, never on prose.

The unit of work is a **spec** — ONE markdown file, `specs/<phase>/YYYY-MM-DD-<slug>.md`, moving
through three phase folders (`backlog/` → `ready/` → `archive/`) and never renamed. There is no
separate spec store to bridge to, so the old delta (a branch reimplemented in markdown) is gone:
isolation-while-building is a real git **branch or worktree** (offered by `/specs:apply`), with
merge, history, and reversion. The **OKF bridge** is a single pass at archive time: `docs/` is
read as context going in (standards, glossary), and the by-products the spec did not already
commit to `docs/` are distilled out at archive (never bulk-copied). `specs/` and `docs/` never
duplicate content — the boundary is owned once by
[`spec-driven.md`](plugins/quenching/assets/references/specs-develop/spec-driven.md) §Boundary.

Of the eleven `/specs:*` commands, **two** are stages of the front's 3-stage pipeline when
`/specs:align-and-update` conducts it — `/specs:archive` and `/specs:triage`; the per-spec
commands (`capture`, `develop`, `refine`, `apply`, `from-claude`) and `explore` never are, because
each needs fresh human intent a conducted pass does not have. `/specs:align` is the front's own
aligner *and* installer (it scaffolds `specs/` and installs `specs.py`; it also **migrates a
legacy `openspec/` workspace** one-way). Every command on this front is quenching-native — no
`metadata.generatedBy` anywhere.

## The OKF bundle contract

Every target repo the plugin aligns converges to the **same tree** under `docs/`:
`standards/` (current contracts, subject subfolders — an agreed-but-unproven rule sits here as
`authority: background`; there is no separate `decisions/` home), `catalog/` (own data),
`vision/`, `documentation/`, `knowledge/` (incl. fixed `glossary.md`),
`reference/` (external facts). The **spec workspace** lives **outside** the bundle at `specs/`
(a quenching-managed sibling, not scanned by the OKF validator). Rules the plugin
enforces everywhere:

- `index.md` is a reserved, frontmatter-free listing (exception: root `docs/index.md`
  carries only `okf_version: "0.1"`).
- Every other concept doc MUST have YAML frontmatter with a non-empty `type` from the
  fixed vocabulary.
- `log.md` uses `## YYYY-MM-DD` headings, newest first, and an entry goes under **its own** date.
- Folder names, concept-doc file slugs, frontmatter keys, and `type` values are canonical
  English (cross-repo greppable); body prose may follow the target repo's language;
  identifier-derived slugs (catalog tables, repo names) stay verbatim.
- `CLAUDE.md`, `AGENTS.md`, **and `QUENCHING.md`** are **exempt** basenames — harness pointers
  and the plugin's own operator manual, never OKF concepts. Never stamp a `QUENCHING.md`, never
  convert it to `index.md`, and never overwrite one whose banner a human removed.

The full normative spec is under `assets/references/docs-align/` (`okf-spec.md`, `taxonomy.md`,
`migration.md`, `conformance.md`).

## The three operator manuals (`QUENCHING.md`)

Each align installs a static, repo-agnostic **operator manual** beside the front it owns —
`assets/docs/QUENCHING.md` → `docs/` (`/docs:align`), `assets/specs/QUENCHING.md` →
`specs/` (`/specs:align`), `assets/claude/QUENCHING.md` → `.claude/` (`/skill:align`). They
explain to a *target repo's* reader how the commands operate: the command surface, the
one-plan-one-OK model, generated zones, the hook, recipes, troubleshooting. They
are written in **English** (the canonical-surface rule) and must stay repo-agnostic — no fact
about any particular repository ever goes in them.

The four-branch refresh rule is owned **once**, by `commands/docs/align.md` §4 (absent →
install · older banner → overwrite · same-or-newer → leave · banner removed by a human → keep
and report); the other two aligns **cite** it. The banner's `<VERSION>` placeholder is filled
from the `VERSION` file at copy time, so a release adds no lockstep item — but a command rename
or a new command **does** mean editing all three manuals, since they enumerate the command surface.

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
of the bundle-root one, and `bundle-no-index` is dropped. `--version` is kept in lockstep with
`plugins/quenching/VERSION`; `/docs:align` step 6 offers to install or upgrade it
into a target's `.claude/hooks/`.

## The spec-cycle tool (`assets/bin/specs.py`)

Stdlib-only Python, the same self-contained mold as `okf-validate.py` — the deterministic rails
for the `specs/` front. Uniform contract: `--json` on every subcommand and strict exit codes
(**0** ok · **1** findings · **2** refusal), so a command branches on data, never on prose.
Subcommands: `new` (stamp `YYYY-MM-DD-<slug>.md` in `backlog/`), `list`, `status --spec <slug>`
(sections, phase, tasks, blocked tasks, the verification policy, the refinement record),
`section <slug> "<Heading>" [--write]`, `promote`, **`next --spec <slug>`** (THE single next
action, carrying the task's `verify:`/`files:`/`pattern:`/`[P]`, and **skipping a `[!]` blocked
task**), **`task --spec <slug> --check|--uncheck|--block <id>`** (`--block` requires `--reason`
and writes a visible `- [!] … — blocked: <reason>` marker into `## Tasks`),
**`parallel --spec <slug>`** (verify a `[P]` group's `files:` sets are disjoint — mechanically,
never judged in prose), **`backlog reindex`**, `validate`, `archive`, `doctor`. Schema and
templates load from `assets/specs/` when adjacent, else from embedded fallbacks, so an installed
copy under a target's `.claude/hooks/` still works — which is why **the templates are duplicated
in `specs.py` as constants and must be edited in lockstep**. `/specs:align` installs it; its
`--version` is kept in lockstep with `VERSION`.

## The command-surface verifier (`assets/bin/skills.py`)

The third tool, same mold, for the `.claude/` front. Reads `commands/**` and nothing else — one
row per command file. Subcommands: `lint [path]` (the description cap, trigger position, the
`Not for:` boundary, body length, a `**Done when:**` per numbered step, unscoped `Bash`,
invocation coherence), `doctor` (the surface invariant: a non-empty `description` on every
command, no two resolving to the same `/` path, kebab-case segments), `registry reindex` (owns
the registry's GENERATED zone format), `budget` (what the surface costs before anything fires),
and `selftest` (builds a throwaway surface and proves a non-entry-point file under `commands/`
fires `sk-no-description` — the layout rule's evidence). `/skill:align` installs it.

## Verifying changes

There is no test suite. To verify the plugin's own shipped skeleton is still conformant
after touching anything under `plugins/quenching/`:

```bash
cd plugins/quenching
# version lockstep — VERSION and all three shipped scripts must agree
cat VERSION
python3 assets/bin/specs.py --version
python3 assets/bin/skills.py --version
python3 assets/hooks/okf-validate.py --version
# the skeleton and the backlog seed are conformant by construction
python3 assets/hooks/okf-validate.py assets/docs                          # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/backlog --listing-root  # 0 error(s), 0 warning(s)
# the command surface
python3 assets/bin/skills.py --root . doctor --json                       # 28 commands, no findings
python3 assets/bin/skills.py --root . lint --json                         # exit 0 (warnings are reported, not fatal)
python3 assets/bin/skills.py selftest                                     # the layout rule's fixture
```

**Nothing above tests that the surface actually LOADS.** The command registry is built at session
start, so no change under `commands/**` is testable in the session that writes it — a run can look
entirely green while every command body is unreachable. The three checks that catch that each spawn
their own fresh `claude -p` and assert on captured tool calls rather than on what the process claims:

```bash
./assets/bin/functional-checks.sh        # ~5 min, 7 assertions, exit 0 = all passed
```

It proves `${CLAUDE_PLUGIN_ROOT}` still substitutes inside a command body, that a conductor reaches
its stage by registry name (`quenching:docs:align`), and that a spoken phrase still routes by
description alone. **Run it after any change to `commands/**`, to a citation path, or to a
conductor's stage names** — those are the three things it is the only check for.

`specs.py` itself has no fixture in the repo; exercise it in a throwaway workspace
(`specs.py new x` → `status`/`next`/`task` → `archive x --force`) when its logic changes.

When editing a command file, keep the `description` under the shared **1,536-character** cap
(Claude Code truncates beyond it) with trigger phrases in the frontmatter's second sentence so
truncation never eats them; keep bodies well under 500 lines and push shared procedure into the
owning `assets/references/<name>/*.md` instead of restating it in every command that cites it.

## Two rules that must survive any refactor

- **Never add `context: fork` to these commands.** Every sweep command gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`assets/references/align-and-update-all/convergence.md` §cycle-authorization) must still
  surface code-coupled confirmations mid-flow, which a forked context cannot present.
- **Never downgrade classification or executor sub-agents to `haiku` in
  `/docs:import-memory`.** A misclassification there becomes a wrong memory deletion —
  see the model-policy table in
  [plugins/quenching/README.md](plugins/quenching/README.md#cost-model) for
  which sub-agent calls in the other commands are safe to run on cheaper models/effort.

## Releasing

Bump `version` in `plugins/quenching/.claude-plugin/plugin.json` **and**
`plugins/quenching/VERSION` together — that pair is what Claude Code uses to detect
and apply an upgrade. Keep the `VERSION` constant in **all three** shipped scripts in lockstep
with that pair — `assets/hooks/okf-validate.py`, `assets/bin/specs.py` **and**
`assets/bin/skills.py` — since each one's `--version` is what its installing align
(`/docs:align` for the hook, `/specs:align` for `specs.py`, `/skill:align` for `skills.py`)
compares against an already-installed copy in a target repo. Mirror the plugin `version` in the
marketplace manifest's plugin entry (`.claude-plugin/marketplace.json`) too. A command rename or
a new command also means editing all three `QUENCHING.md` operator manuals, since they enumerate
the command surface.
