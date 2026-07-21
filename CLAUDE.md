# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin marketplace** with a single plugin, `claude-quenching`
(source: [plugins/claude-quenching/](plugins/claude-quenching/)). The plugin forces any
*target* repository's `docs/` into one canonical **Open Knowledge Format (OKF v0.1)**
bundle and keeps it conformant, via nineteen skills (eleven `quenching-*` plus eight
`openspec-*`) plus `/opsx` and `/docs` commands and a self-contained enforcement hook.

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
  commands/opsx/*.md                   # /opsx:* — thin wrappers over the eight openspec-* skills
  commands/docs/*.md                   # /docs:* — thin wrappers over the nine OKF-bundle quenching-* skills
  commands/skill/*.md                  # /skill:* — thin wrappers over the two .claude-automation quenching-skill* skills
  assets/                              # the INSTALLABLE PAYLOAD — copied into target repos, never executed here
    docs/                              # canonical OKF bundle skeleton (index.md listings, log.md seeds, glossary seed)
    openspec/                          # backlog/ seed — the task inbox (type: task), a quenching-managed openspec/ sibling OUTSIDE the OKF bundle
    templates/                         # molds: concept-front, standard-front, catalog/*, backlog/task, harness/*, automation/*, ...
    hooks/
      okf-validate.py                  # zero-dependency OKF v0.1 conformance checker (CLI + hook)
      hooks-config.json                # checker config (block `okfValidate`)
      settings.snippet.json            # hook wiring to merge into a target's .claude/settings.json
```

`assets/` is inert here (≥2 levels below any `SKILL.md`, so Claude Code does not surface it
as a live skill) — it is the payload the skills stamp into *other* repositories.

Every skill is `user-invocable: false` — hidden from the `/` menu, but still invoked by Claude
via its description or by a thin **command wrapper**. `/opsx:*` mirrors the eight `openspec-*`
skills; the eleven `quenching-*` skills split across two command namespaces by the artifact they
touch — `/docs:*` mirrors the nine that act on the OKF `docs/` bundle, `/skill:*` mirrors the two
that act on the target's `.claude/` automation surface (`quenching-skill` → `/skill:new`,
`quenching-skill-align` → `/skill:align`); the wrappers under `commands/` are the explicit user
entry points, the skills are the implementation. Every skill has exactly one wrapper.

## The nineteen skills and how they relate

| Skill | Role |
| --- | --- |
| `quenching-align` | Installer + force-aligner + validator. Migrates a target's `docs/` to the canonical tree, stamps frontmatter, regenerates every `index.md`, establishes `log.md`. Invasive: one full plan, one confirmation (a code-coupled rename gets its own). |
| `quenching-add` | Adds ONE new concept doc (standard, catalog table, announcement, …) into the right home with a complete OKF stamp. |
| `quenching-import` | Imports an external source (local files/folders, or URLs) and mints MULTIPLE OKF docs in one plan→OK pass — a batch fan-out of the insert procedure (cites `homes.md`). Bounded web ingestion; additive/merge only, never deletes. |
| `quenching-learn` | Captures ONE piece of generic knowledge a human states into `knowledge/`. |
| `quenching-glossary-backfill` | Sweeps the WHOLE bundle to backfill `knowledge/glossary.md` with terms already documented but never listed; fans sub-agents out per home slice. |
| `quenching-define` | Adds/refines ONE glossary entry on demand — the single-term counterpart of `quenching-glossary-backfill`. |
| `quenching-import-memory` | Drains `~/.claude/projects/<cwd>/memory/` into the bundle, clearing each memory once its doc lands and passes conformance. |
| `quenching-harness` | Refactors a target's `CLAUDE.md`/`AGENTS.md` into thin pointers over its `docs/` bundle, MOVING (never copying) inlined durable knowledge into its home. |
| `quenching-skill` | Mints or edits ONE skill in a target's local automation surface (`.claude/skills/` + `.claude/commands/`): single-axis classification (domain-bound × generic), canonical name, mirrored command wrapper, writing doctrine, OKF tail (registry GENERATED zone, glossary offer, log, self-check). One plan → one OK. Owns `references/doctrine.md` + `references/taxonomy.md`. |
| `quenching-skill-align` | The sweep counterpart: read-only inventory of the existing skill/command surface, ONE migration plan (renames, wrapper mirroring, rule + registry from the molds when missing; keep-and-report unroutables; deletion only on human word), one OK (code-coupled renames individually), post-apply verification. Cites the sibling's references. |
| `quenching-converge` | The conductor: runs `align` → `import-memory` → `harness` → `glossary-backfill` as a dependency pipeline, pass after pass, until a fixpoint (nothing changes and the validator is clean) or a pass cap. (`import` is an on-demand tool, not a loop stage.) |
| `openspec-backlog` | Captures ONE task into `openspec/backlog/` (the task inbox, outside the OKF bundle) in seconds — minimal `type: task` stamp; inline-stated `priority`/`tags`/`complexity` (rough dev hours) only (zero interrogation; untriaged is a valid state); dedupes, regenerates the index's derived zone, logs. Quenching-native (no `generatedBy`). |
| `openspec-backlog-triage` | The prioritization sweep: reads task frontmatter directly (no sub-agents), proposes ONE triage plan (priority/tags/optional complexity with rationale, staleness, duplicates), applies on one OK, regenerates the zone. Completion only when human-stated. On-demand tool, not a cycle stage. Quenching-native. |
| `openspec-explore` | Thinking partner before/during an OpenSpec change; OpenSpec + OKF awareness (reads glossary/knowledge/standards, routes durable insights to the quenching skills). Never implements. |
| `openspec-propose` | Creates an OpenSpec change and generates all artifacts (proposal, delta specs, design, tasks) until apply-ready; reads the OKF bundle as context; retires a seed `openspec/backlog/` task into the Completed ledger. |
| `openspec-apply-change` | Implements a change's `tasks.md`; reads the touched subjects' `standards/` as binding contracts; routes durable learning to its OKF home. |
| `openspec-update-change` | Revises a change's existing planning artifacts and keeps them coherent; never edits code. |
| `openspec-sync-specs` | Merges delta specs into `openspec/specs/` (current behavior). Boundary: `openspec/specs/` = WHAT the product does; `docs/standards/` = HOW we build. |
| `openspec-archive-change` | Checks completion, offers the sync, moves the change to `changes/archive/`, then offers ONE OKF distillation pass (durable knowledge → `docs/`, per its `references/distill.md`). |

Each `SKILL.md` frontmatter `description` carries its own trigger phrases and its "Not
for: X → other-skill" boundary — read the target skill's frontmatter before assuming
which one owns a task. Shared procedure lives once in its owner and other skills cite it
rather than restating it: the insert procedure in
[`quenching-add/references/homes.md`](plugins/claude-quenching/skills/quenching-add/references/homes.md),
the checks in
[`quenching-align/references/conformance.md`](plugins/claude-quenching/skills/quenching-align/references/conformance.md),
the OpenSpec facts (layout, artifact graph, CLI surface, store selection) in
[`openspec-propose/references/openspec.md`](plugins/claude-quenching/skills/openspec-propose/references/openspec.md),
the OKF distillation doctrine in
[`openspec-archive-change/references/distill.md`](plugins/claude-quenching/skills/openspec-archive-change/references/distill.md),
and the skill-writing doctrine + automation taxonomy in
[`quenching-skill/references/doctrine.md`](plugins/claude-quenching/skills/quenching-skill/references/doctrine.md)
and [`quenching-skill/references/taxonomy.md`](plugins/claude-quenching/skills/quenching-skill/references/taxonomy.md)
(cited by `quenching-skill-align`, never restated).

### The OpenSpec ↔ OKF relation

**Six** of the eight `openspec-*` skills — `explore`, `propose`, `apply-change`,
`update-change`, `sync-specs`, `archive-change` — are adapted 1:1 from the skills the OpenSpec
CLI (`@fission-ai/openspec` 1.6.0, `metadata.generatedBy`) generates, so target repos drop
their local `.claude/skills/openspec-*` / `.claude/commands/opsx/` copies and get them from
the plugin. The upstream CLI-driven mechanics (`openspec new change`, `status --json`,
`instructions --json`, `list --json`) are the contract that survives upgrades — keep them
intact. The adaptation is the **OKF bridge**: `docs/` is read as context going in
(standards, glossary; an `openspec/backlog/` task as seed), and durable knowledge is distilled
back out at archive time (never bulk-copied). `openspec/specs/` and `docs/` never duplicate
content. These skills are on-demand tools, **not** `quenching-converge` loop stages, and the
scaffold in target repos comes from `openspec init` (no setup skill). The other **two** —
`openspec-backlog` and `openspec-backlog-triage` — are **quenching-native** (no `generatedBy`
in frontmatter), owning the `openspec/backlog/` task inbox: a quenching-managed `openspec/`
sibling **outside** the OKF bundle, seeded on-demand by `openspec-backlog` and prioritized by
`openspec-backlog-triage`.

## The OKF bundle contract

Every target repo the plugin aligns converges to the **same tree** under `docs/`:
`standards/` (current contracts, subject subfolders — an agreed-but-unproven rule sits here as
`authority: background`; there is no separate `decisions/` home), `catalog/` (own data),
`vision/`, `documentation/`, `knowledge/` (incl. fixed `glossary.md`),
`reference/` (external facts). The **task inbox** lives **outside** the bundle at
`openspec/backlog/` (`type: task`, optional `priority`/`tags`/`complexity`, derived index zone —
a quenching-managed `openspec/` sibling, not scanned by the OKF validator). Rules the plugin
enforces everywhere:

- `index.md` is a reserved, frontmatter-free listing (exception: root `docs/index.md`
  carries only `okf_version: "0.1"`).
- Every other concept doc MUST have YAML frontmatter with a non-empty `type` from the
  fixed vocabulary.
- `log.md` uses `## YYYY-MM-DD` headings, newest first.
- Folder names, concept-doc file slugs, frontmatter keys, and `type` values are canonical
  English (cross-repo greppable); body prose may follow the target repo's language;
  identifier-derived slugs (catalog tables, repo names) stay verbatim.

The full normative spec is in each skill's `references/` (`okf-spec.md`, `taxonomy.md`,
`migration.md`, `conformance.md`).

## The enforcement hook (`assets/hooks/okf-validate.py`)

Stdlib-only Python; runs as a CLI (`okf-validate.py <docs-dir> [--json]`, exit 0 = conforms)
or as a hook (reads hook JSON on stdin, dispatches on `hook_event_name`):
`PostToolUse` and `Stop` propose fixes via `additionalContext`; an opt-in `PreToolUse`
(`hardBlock: true`) denies the two hard violations (a typed `index.md`, an untyped concept
doc). The `Stop` sweep is dirty-gated by default (`stopScan: "dirty"`) via a marker file so
a turn touching no `docs/**` file costs one stat. `--version` is kept in lockstep with
`plugins/claude-quenching/VERSION`; `quenching-align` step 6 offers to install or upgrade it
into a target's `.claude/hooks/`.

## Verifying changes

There is no test suite. To verify the plugin's own shipped skeleton is still conformant
after touching anything under `plugins/claude-quenching/assets/docs/`:

```bash
cd plugins/claude-quenching
python3 assets/hooks/okf-validate.py assets/docs
```

This must report `0 error(s), 0 warning(s)` — the skeleton is conformant by construction.

When editing a `SKILL.md`, keep the `description` under the shared **1,536-character**
per-skill cap (Claude Code truncates beyond it) with trigger phrases in the frontmatter's
second sentence so truncation never eats them; keep skill bodies well under 500 lines and
push shared procedure into the owning `references/*.md` instead of restating it in every
skill that cites it.

## Two rules that must survive any refactor

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`quenching-converge/references/cycle.md` §cycle-authorization) must still surface code-coupled
  confirmations mid-flow, which a forked context cannot present.
- **Never downgrade classification or executor sub-agents to `haiku` in
  `quenching-import-memory`.** A misclassification there becomes a wrong memory deletion —
  see the model-policy table in
  [plugins/claude-quenching/README.md](plugins/claude-quenching/README.md#cost-model) for
  which sub-agent calls in the other skills are safe to run on cheaper models/effort.

## Releasing

Bump `version` in `plugins/claude-quenching/.claude-plugin/plugin.json` **and**
`plugins/claude-quenching/VERSION` together — that pair is what Claude Code uses to detect
and apply an upgrade. Keep the `VERSION` constant in the shipped script in lockstep with
that pair — `assets/hooks/okf-validate.py` — since its `--version` is what `quenching-align`
(the hook) compares against an already-installed copy in a target repo. Mirror the plugin
`version` in the marketplace manifest's plugin entry (`.claude-plugin/marketplace.json`) too.
