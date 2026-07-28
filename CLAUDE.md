# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin marketplace** with a single plugin, `quenching`
(source: [plugins/quenching/](plugins/quenching/)). The plugin forces a *target*
repository's **three fronts** — the `docs/` **Open Knowledge Format (OKF v0.1)** bundle, the
native `specs/` spec-driven workspace, and the `.claude/` command surface — into one
canonical shape and keeps them conformant, via twenty-five commands under `/docs`, `/specs`,
`/skill` and the root `/align`, plus three self-contained stdlib Python
tools (the OKF enforcement hook `okf-validate.py`, the spec-cycle CLI `specs.py`, and the
command-surface verifier `skills.py`).

**ONE FILE PER ENTRY POINT.** Claude Code merged custom commands into skills, so each
`commands/<path>.md` carries both the description that routes to it and the body that runs.
There is no `skills/` tree and no wrapper: **a command's path is its whole identity**
(`commands/docs/add.md` → `/docs:add` → `quenching:docs:add` through the Skill tool).

**The whole surface is one 1×4 column.** Every front has exactly ONE align, and one more spans
all three:

| Front | **align** |
| --- | --- |
| `docs/` | `/docs:align` |
| `specs/` | `/specs:align` |
| `.claude/` | `/skill:align` |
| all three | `/align` |

An **align** shares one interface — **probe first** (the front's own verifier, so a clean front
costs a couple of tool calls and stops), then read-only inventory → ONE plan → one OK → apply →
verify — and carries its front's **content stages**, run only when the probe finds work.
`/docs:align` keeps a real internal fixpoint loop (memory → harness → glossary feed each other);
`/align` conducts the three in dependency order on one nested OK and loops across fronts, because
they feed each other. Everything else in the plugin is a stage one of these four invokes, or a
per-item capture tool.

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
    align.md                           # /align — three fronts, one OK, looped across them
    specs/*.md                         # /specs:* — the nine specs-front commands (FLAT)
    docs/*.md                          # /docs:* — the ten OKF-bundle commands
    docs/documentation/build.md        # /docs:documentation:build — the one docs-nested command (acts on ONE home)
    skill/*.md                         # /skill:* — the five .claude-automation commands
    skill/{agent,hook}/new.md          # /skill:agent:new + /skill:hook:new — nested: they mint a different artifact
  assets/                              # everything Claude Code must NOT surface as an entry point
    references/<name>/*.md             # shared procedure, cited by ${CLAUDE_PLUGIN_ROOT} absolute path
    evals/<command-path>/              # measured case sets, mirroring the command path
    docs/                              # canonical OKF bundle skeleton (index.md listings, log.md seeds, glossary seed)
      QUENCHING.md                     # operator manual for the docs/ front — installed by /docs:align
    specs/                             # native specs/ workspace payload: schema.json, templates/, plans/ seed, QUENCHING.md
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
by front: `/docs:*` are the ten that act on the OKF `docs/` bundle (one nested a level deeper
as `/docs:documentation:build`, because it acts on a single **home**, not the bundle); `/specs:*`
the nine that act on the native `specs/` workspace; `/skill:*` the five that act on the target's
`.claude/` automation surface (two nested — `/skill:agent:new`, `/skill:hook:new` — because they
mint a different artifact); and the **root `/align`** the one that spans all three fronts —
deliberately outside the three namespaces, because it is what crosses them.

## The twenty-five commands and how they relate

| Command | Role |
| --- | --- |
| `/docs:align` | Installer + force-aligner + validator + the front's content conductor, probe-first: the validator plus two cheap out-of-band signals run before anything is read, so a conformant bundle with nothing waiting costs three calls and stops. Otherwise: migrates a target's `docs/` to the canonical tree, stamps frontmatter, regenerates every `index.md`, establishes `log.md`, then runs the content stages that have work (`import-memory`, `harness`) and OFFERS the glossary sweep on a cheap proxy, looping to a fixpoint. Invasive: one full plan, one confirmation (a code-coupled rename gets its own). |
| `/docs:add` | Adds ONE new concept doc (standard, catalog table, announcement, …) into the right home with a complete OKF stamp. |
| `/docs:import` | Imports an external source (local files/folders, or URLs) and mints MULTIPLE OKF docs in one plan→OK pass — a batch fan-out of the insert procedure (cites `homes.md`). Bounded web ingestion; additive/merge only, never deletes. |
| `/docs:learn` | Captures ONE piece of generic knowledge a human states into `knowledge/`. |
| `/docs:glossary-backfill` | Sweeps the WHOLE bundle to backfill `knowledge/glossary.md` with terms already documented but never listed; fans sub-agents out per home slice. |
| `/docs:define` | Adds/refines ONE glossary entry on demand — the single-term counterpart of `/docs:glossary-backfill`. |
| `/docs:import-memory` | Drains `~/.claude/projects/<cwd>/memory/` into the bundle, clearing each memory once its doc lands and passes conformance. |
| `/docs:harness` | Refactors a target's `CLAUDE.md`/`AGENTS.md` into thin pointers over its `docs/` bundle, MOVING (never copying) inlined durable knowledge into its home. |
| `/docs:documentation:build` | Owns the **site layer** over the `documentation/` home: the root `mkdocs.yml`/`requirements.txt`, the `.pages` nav files, `site/` gitignore, opt-in Pages CI, and a `mkdocs build --strict` verification. Installs, MERGES a customized config forward (missing keys only, as a diff), regenerates a stale nav; **never touches a page** — page-level drift is reported (`site-*` codes) with the command that fixes it. `/docs:align` step 7 does the first install and hands off here. On-demand tool, not a loop stage. |
| `/docs:status` | The `docs`-front's only **read-only** view: every conformance finding in the validator's own codes, plus bundle **density** — concept docs per home (empty homes shown as `0`), glossary size, which `standards/` subjects hold anything — split into what `/docs:align`'s structural pass fixes, what its content stages drive, and what neither closes. Density figures carry **no finding code**, so a bundle that passes every check while knowing nothing is visible without becoming a defect list. Writes nothing; owns no contract, cites `conformance.md` + `cycle.md`. The `docs` counterpart of `/specs:status`. |
| `/skill:new` | Mints or edits ONE command in a target's local automation surface (`.claude/commands/`): single-axis classification (domain-bound × generic), the command path (which is the name), writing doctrine, OKF tail (registry GENERATED zone, glossary offer, log, self-check). One plan → one OK. Owns `references/doctrine.md` + `references/taxonomy.md`. |
| `/skill:eval` | Evaluates ONE command by running its cases twice — with the command loaded and without — in isolated sub-agents, grading every assertion against **quoted evidence**, and reporting the delta over pass rate, tokens and duration. Writes `evals.json` into the tree mirroring the command's path, plus a per-case `grading.json` and a `benchmark.json`; a command whose delta is **zero is reported as teaching nothing**, never quietly passed. Description tuning runs on measured should-trigger / should-not-trigger rates, never on taste. Not for: minting or editing a command → `/skill:new`; the mechanical conformance checks → `skills.py lint`. |
| `/skill:align` | The sweep counterpart, probe-first (`skills.py doctor` + `lint`, so a conformant surface costs two calls and stops): read-only inventory of the existing command surface, ONE migration plan (**collapsing any surviving skill+wrapper pair into one file**, renames, rule + registry from the molds when missing; keep-and-report unroutables; deletion only on human word), one OK (code-coupled renames individually), post-apply verification — then a **read-only doctrine audit of every command body**, the one thing the migration itself is forbidden to fix, reported with the `/skill:new` that closes each. Cites the sibling's references. |
| `/skill:agent:new` | Mints or edits ONE subagent definition in a target's `.claude/agents/` — the delegation counterpart of `/skill:new`: the delegation test, the narrowest tool set, the always-on cost priced, the OKF tail, one plan → one OK. |
| `/skill:hook:new` | Wires ONE scoped hook: walks the scope ladder to the narrowest matcher and the cheapest handler, states the hook's cost claim, applies on one OK — warn by default, block only on the human's word. |
| `/align` | The cross-front conductor: one read-only probe of the three fronts, ONE OK, then `quenching:docs:align` → `quenching:specs:align` → `quenching:skill:align` in dependency order (docs first — the other two write OKF artifacts into it; specs before skills — it clears the CLI shadow copies the skill sweep would otherwise inventory), **looped across fronts** until nothing changes anywhere, because they feed each other (a spec's distillation is glossary work; the skill front's registry is a `docs/` listing). Authorization **nests one level** — the human confirms once for the whole repo; a code-coupled rename and an irreversible close still gate on their own. Conducts, never reimplements. Cites `align-all/convergence.md`. |
| `/specs:align` | The `specs/`-front align + installer (quenching-native), probe-first (`specs.py doctor` + `validate`, so a clean workspace costs two calls and stops): scaffolds `specs/` by copying `assets/specs/`, installs `specs.py` into `.claude/hooks/`, applies the tools' declared remedies, normalizes spec + archive names, stamps missing frontmatter, regenerates the listing zone via `specs.py plans reindex`, **folds an older `backlog/`+`ready/` layout or a v1 three-file one into `plans/`** (`specs.py migrate`), and **migrates a legacy `openspec/` workspace**. Authoring and cycle actions are REPORTED with the command that closes each, never driven. Owns `references/conformance.md`. |
| `/specs:create` | Creates ONE spec in `specs/plans/` — effort proportional to input, never an interrogation: a sentence becomes `## Problem` and nothing else, in seconds; a Claude Code plan file (`~/.claude/plans/*.md`, or a given path) becomes every section it actually supports, mapped and never invented. Dedupes, regenerates the listing zone, logs. |
| `/specs:develop` | Develops ONE spec by asking about it — one question at a time with an inline recommendation, the question bank chosen by the spec's own derived stage: raw → generative shaping; `proposed` → adversarial (alternatives, premortem, critique); `designed` → the gate's gaps (`## Impact`, `## Validation`, the `verification` policy); open `## Discoveries` → resolve each; gate met → offer the `approved: {date}` stamp. Answers land in ONE confirmed edit per bank; a real interrogation records `refined: {mode, date}`, clearing `sp-unrefined` (never gating). NEVER edits code. Owns `references/artifacts.md` + `references/spec-driven.md`. |
| `/specs:execute` | Builds ONE spec's `## Tasks` and **proves** each task — refuses to start on a dirty tree, delegates isolation to `/specs:isolate`, then per task: writes the code, runs its `verify:` under the spec's declared policy, self-reviews the diff on four items, commits it alone (the target's `docs/standards/git/**` governs when declared, read-if-present and never installed; default subject `plan/<slug>: <id> <title>`), and ticks the box **before** the commit with that commit's subject (`specs.py task --check --subject`), so code and box land in ONE commit per task and no bookkeeping commit follows. Writes ONLY the `docs/standards/` doc a task explicitly names; everything else the work reveals is one `specs.py discover` line. A task that stops converging is written `- [!] … — blocked: <reason>`. May delegate a file-scoped executor sub-agent (never `context: fork`). **Stops at the last commit** — review, merge and archive are `/specs:conclude`. Owns `references/execution.md`. |
| `/specs:conclude` | Closes ONE spec out, resumable from its records, with the **merge as its last action**: reviews the whole branch (`reviewed: {date}`), writes the emergent `docs/` the work revealed, archives with `outcome: done` (REFUSES while boxes are open unless forced) or `outcome: abandoned` (always allowed; distils at most a background note), runs ONE OKF distillation pass and stamps `merge: {strategy, subject}` — all on the work branch — and only then merges. One merge carries the code, the emergent docs, the archived spec and the distillation, and **nothing is committed to the base after it**; a squash offers to keep the branch, where the per-task commits live. The outcome is never inferred — not by staleness, not by any sweep. Owns `references/distill.md`. |
| `/specs:continue` | The router: one `specs.py next --front` call ranks every candidate (executing, closest to done, priority, age) with a reason per row, and hands off to the one command that fits — never builds, edits, or closes anything itself. Suggests `/specs:triage` when the ranking has nothing to stand on. |
| `/specs:isolate` | Takes **or reports** git isolation for ONE spec at ANY stage — created, being developed, or about to be built: the `plan/<slug>` branch or a worktree beside the repo, the `branch: {base, work}` stamp (write-once, `base` captured while it is still derivable), and moving an uncommitted spec file onto the branch so the base keeps no trace. Reporting is a complete use of it. `/specs:execute` delegates here; `create` and `develop` name it on request. **Never merges** — that keeps `conclude`'s review and archive gates. Owns `references/git.md`. |
| `/specs:status` | The front's only **read-only** view: specs by derived stage with task progress, each spec's frontmatter records as the history they narrate (ranked, interrogated, approved, built, reviewed, merged, closed), the `specs.py doctor`/`validate` results — split into what `/specs:align` would fix, what a cycle command closes, and what neither closes. Reports in the sweep's own `sp-*` vocabulary, so it doubles as an honest dry run before the OK. Near-free by construction: no sub-agents, no per-spec fan-out. Writes nothing. |
| `/specs:triage` | The prioritization sweep: reads every spec's frontmatter and derived stage directly (no sub-agents), proposes ONE ordered table with a one-line reason per row, applies on one OK, writing `priority: {level, criticality, complexity, date}` and nothing else — merging, never clobbering a human's ranking. Its output is what `continue` stands on. Never removes a spec, never infers completion, never treats staleness as abandonment. |

Each command's frontmatter `description` carries its trigger phrases and its "Not for: X →
other-command" boundary — read the target command's frontmatter before assuming which one owns a
task. Shared procedure lives once in its owner and other commands cite it by **absolute path**
(`${CLAUDE_PLUGIN_ROOT}/assets/references/<name>/<file>.md`) rather than restating it:
the insert procedure in
[`docs-add/homes.md`](plugins/quenching/assets/references/docs-add/homes.md),
the checks in
[`docs-align/conformance.md`](plugins/quenching/assets/references/docs-align/conformance.md),
the spec-driven facts (the folders and derived stages, the thirteen canonical sections, the
gates, the record vocabulary, the `specs.py` surface, the `specs/`↔`docs/` boundary) in
[`specs-develop/spec-driven.md`](plugins/quenching/assets/references/specs-develop/spec-driven.md),
the per-section authoring doctrine in
[`specs-develop/artifacts.md`](plugins/quenching/assets/references/specs-develop/artifacts.md),
the `specs/` workspace conformance contract in
[`specs-align/conformance.md`](plugins/quenching/assets/references/specs-align/conformance.md),
the execution mechanics (clean tree, the validation loop, the per-task commit and its recorded
sha, delegation bounds) in
[`specs-execute/execution.md`](plugins/quenching/assets/references/specs-execute/execution.md)
and the git defaults + read-if-present rule in
[`specs-isolate/git.md`](plugins/quenching/assets/references/specs-isolate/git.md),
the cycle-authorization + cross-front convergence contract in
[`align-all/convergence.md`](plugins/quenching/assets/references/align-all/convergence.md)
(cited by `/align`; never restated by a front align),
the **sweep contract shared by all three aligns** — probe before the inventory, convergence over
accommodation, one plan → one OK with code-coupled items gating individually, the two-scan
blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess,
align-conformance-report-the-cycle — in
[`align-all/sweep-doctrine.md`](plugins/quenching/assets/references/align-all/sweep-doctrine.md)
(each align's `## Doctrine` cites it and states **only** its own front's deltas),
the OKF distillation doctrine in
[`specs-conclude/distill.md`](plugins/quenching/assets/references/specs-conclude/distill.md),
the command-writing doctrine + automation taxonomy in
[`skill-new/doctrine.md`](plugins/quenching/assets/references/skill-new/doctrine.md)
and [`skill-new/taxonomy.md`](plugins/quenching/assets/references/skill-new/taxonomy.md),
and the **execution profile** — every Claude Code lever a command, agent or hook may use, each
stated as what it buys, what it costs and the default (`context: fork`, model/effort pins and
their cache trap, the delegation test, the hook scope and handler ladders, the
invocation-surface budget controls) — in
[`skill-new/capabilities.md`](plugins/quenching/assets/references/skill-new/capabilities.md)
(cited by `/skill:align`, never restated).

### The `specs/` front ↔ OKF relation

The `specs/` front is **entirely native** — the plugin absorbed what it used to borrow from the
external OpenSpec CLI (`@fission-ai/openspec`). There is no Node runtime, no `config.yaml`, no
main-spec store, and **no delta format**: a **spec** writes its durable rule **directly** into
`docs/standards/` (honestly `authority`-graded), isolated on a branch while it is built. Three
stdlib Python tools give the LLM deterministic rails — `okf-validate.py` (the OKF hook),
`specs.py` (the spec cycle) and `skills.py` (the command surface), all with uniform `--json` and
strict exit codes 0/1/2. The commands branch on data, never on prose.

The unit of work is a **spec** — ONE markdown file, `specs/plans/YYYY-MM-DD-<slug>.md`, living
its whole pre-archive life in `plans/` and moving exactly once, to `archive/`, never renamed.
**Frontmatter records human judgments; the filesystem, git and section presence record
everything else**: `ready` is a *derived* stage (the ten gate sections), and the records —
`priority`, `refined`, `approved`, `branch`, `reviewed`, `merge`, `outcome` — each hold a fact no
derivation can reproduce (`docs/standards/workflows/plan-lifecycle.md`). There is no separate
spec store to bridge to, so the old delta (a branch reimplemented in markdown) is gone:
isolation is a real git **branch or worktree** (taken by `/specs:isolate` at any stage, which
records `branch:`; each task records its commit's `subject:`), with merge, history, and reversion. The **OKF
bridge** splits on declared vs emergent: `docs/` is read as context going in (standards,
glossary); `execute` writes the standards a task explicitly names; `conclude` writes what the
work revealed and distils the rest at archive (never bulk-copied). `specs/` and `docs/` never
duplicate content — the boundary is owned once by
[`spec-driven.md`](plugins/quenching/assets/references/specs-develop/spec-driven.md) §Boundary.

The nine `/specs:*` commands split by grain: four work ONE spec through its life (`create` →
`develop` → `execute` → `conclude`), two read or rank the whole front (`status`, `triage`),
`continue` routes between all of them, and `align` is the front's own aligner *and* installer (it
scaffolds `specs/`, installs `specs.py`, folds older layouts, and **migrates a legacy `openspec/`
workspace** one-way). The per-spec commands are never conducted by any sweep, because each needs
fresh human intent a conducted pass does not have. Every command on this front is
quenching-native — no `metadata.generatedBy` anywhere.

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
at a quenching-managed tree that is not an OKF bundle root — today `specs/plans/`, which the
hook's `docsDir` never reaches: the scanned `index.md` is held to the plain-listing rule instead
of the bundle-root one, and `bundle-no-index` is dropped. `--version` is kept in lockstep with
`plugins/quenching/VERSION`; `/docs:align` step 6 offers to install or upgrade it
into a target's `.claude/hooks/`.

## The spec-cycle tool (`assets/bin/specs.py`)

Stdlib-only Python, the same self-contained mold as `okf-validate.py` — the deterministic rails
for the `specs/` front. Uniform contract: `--json` on every subcommand and strict exit codes
(**0** ok · **1** findings · **2** refusal), so a command branches on data, never on prose.
Subcommands: `new` (stamp `YYYY-MM-DD-<slug>.md` in `plans/`), `list`, `status --spec <slug>`
(sections, folder, derived stage, tasks with their recorded commits, the frontmatter records, the
verification policy), `section <slug> "<Heading>" [--write]`, `promote` (the one hop,
`plans/` → `archive/`), **`next --spec <slug>`** (THE single next action, carrying the task's
`verify:`/`files:`/`pattern:`/`[P]`, and **skipping a `[!]` blocked task**),
**`next --front`** (the ranked candidate list with a reason per row — the only place ranking
logic lives), **`task --spec <slug> --check|--uncheck|--block <id>`** (`--check` takes
`--commit <sha>` to write the implementing commit onto the task line; `--block` requires
`--reason` and writes a visible `- [!] … — blocked: <reason>` marker into `## Tasks`),
`discover` (append one line to `## Discoveries`),
**`parallel --spec <slug>`** (verify a `[P]` group's `files:` sets are disjoint — mechanically,
never judged in prose), **`plans reindex`**, `validate`, `doctor`, and **`migrate`** (the one-way
fold to the current layout: v2 `backlog/`+`ready/` → `plans/`, basenames unchanged, `archive/**`
untouched, exit 2 when already current). Schema and
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
fires `sk-no-description` — the layout rule's evidence). It also covers the front's other two
artifact kinds: agent definitions (`sk-agent-no-description`) and hook wiring
(`sk-hook-unmatched`, `sk-hook-llm-frequent`, `sk-hook-unparseable`), plus the fork gate
(`sk-fork-gate`) and profile values (`sk-profile-value`); `budget` counts
`disable-model-invocation` commands at 0. `/skill:align` installs it.

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
# the skeleton and the plans seed are conformant by construction
python3 assets/hooks/okf-validate.py assets/docs                          # 0 error(s), 0 warning(s)
python3 assets/hooks/okf-validate.py assets/specs/plans --listing-root    # 0 error(s), 0 warning(s)
# the command surface
python3 assets/bin/skills.py --root . doctor --json                       # 25 commands, no findings
python3 assets/bin/skills.py --root . lint --json                         # exit 0 (warnings are reported, not fatal)
python3 assets/bin/skills.py selftest                                     # the layout rule's fixture
```

**Nothing above tests that the surface actually LOADS.** The command registry is built at session
start, so no change under `commands/**` is testable in the session that writes it — a run can look
entirely green while every command body is unreachable. The three checks that catch that each spawn
their own fresh `claude -p` and assert on captured tool calls rather than on what the process claims:

```bash
./assets/bin/functional-checks.sh        # 9 assertions across 7 sandboxed sessions, exit 0 = all passed
```

It proves `${CLAUDE_PLUGIN_ROOT}` still substitutes inside a command body, that a conductor reaches
its stage by registry name (`quenching:docs:align`), and that a spoken phrase still routes by
description alone. **Run it after any change to `commands/**`, to a citation path, or to a
conductor's stage names** — those are the three things it is the only check for.

`specs.py` itself has no fixture in the repo; exercise it in a throwaway workspace
(`specs.py new x` → `status`/`next`/`task` → `promote x --outcome abandoned`) when its logic
changes.

When editing a command file, keep the `description` under the shared **1,536-character** cap
(Claude Code truncates beyond it) with trigger phrases in the frontmatter's second sentence so
truncation never eats them; keep bodies well under 500 lines and push shared procedure into the
owning `assets/references/<name>/*.md` instead of restating it in every command that cites it.

## Two rules that must survive any refactor

- **Never add `context: fork` to these commands.** Every sweep command gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`assets/references/align-all/convergence.md` §cycle-authorization) must still
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
