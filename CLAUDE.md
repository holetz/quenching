# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this repository is

A **Claude Code plugin marketplace** with a single plugin, `claude-quenching`
(source: [plugins/claude-quenching/](plugins/claude-quenching/)). The plugin forces any
*target* repository's `docs/` into one canonical **Open Knowledge Format (OKF v0.1)**
bundle and keeps it conformant, via eighteen skills (twelve `quenching-*` plus six
`openspec-*`) plus `/opsx` commands, a self-contained enforcement hook, and an offline
HTML diagram generator.

There is no application code, no build step, and no test framework here — the repo is
markdown skills (instructions for Claude) plus two dependency-free Python scripts (the
validator and the diagram generator) and a pair of vendored MIT JS libraries the generator
inlines. Treat
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
  commands/opsx/*.md                   # /opsx:* — thin wrappers that invoke the openspec-* skills
  assets/                              # the INSTALLABLE PAYLOAD — copied into target repos, never executed here
    docs/                              # canonical OKF bundle skeleton (index.md listings, log.md seeds, glossary seed)
    templates/                         # molds: concept-front, standard-front, catalog/*, decisions/adr, harness/*, ...
    hooks/
      okf-validate.py                  # zero-dependency OKF v0.1 conformance checker (CLI + hook)
      hooks-config.json                # checker config (block `okfValidate`)
      settings.snippet.json            # hook wiring to merge into a target's .claude/settings.json
    tools/
      okf-visualize.py                 # zero-dependency OKF v0.1 → interactive HTML diagram generator (CLI)
      viewer/                          # viz.html/css/js + vendor/ (Cytoscape.js & marked, MIT) it inlines offline
```

`assets/` is inert here (≥2 levels below any `SKILL.md`, so Claude Code does not surface it
as a live skill) — it is the payload the skills stamp into *other* repositories.

## The eighteen skills and how they relate

| Skill | Role |
| --- | --- |
| `quenching-align` | Installer + force-aligner + validator. Migrates a target's `docs/` to the canonical tree, stamps frontmatter, regenerates every `index.md`, establishes `log.md`. Invasive: one full plan, one confirmation (a code-coupled rename gets its own). |
| `quenching-insert` | Adds ONE new concept doc (standard, ADR, catalog table, announcement, …) into the right home with a complete OKF stamp. |
| `quenching-backlog` | Captures ONE task into `backlog/` in seconds — minimal `type: task` stamp; inline-stated `priority`/`tags`/`complexity` (rough dev hours) only (zero interrogation; untriaged is a valid state); dedupes, regenerates the index's derived zone, logs. |
| `quenching-backlog-triage` | The prioritization sweep: reads task frontmatter directly (no sub-agents), proposes ONE triage plan (priority/tags/optional complexity with rationale, staleness, duplicates), applies on one OK, regenerates the zone. Completion only when human-stated. On-demand tool, not a cycle stage. |
| `quenching-enrich` | Imports an external source (local files/folders, or URLs) and mints MULTIPLE OKF docs in one plan→OK pass — a batch fan-out of the insert procedure (cites `homes.md`). Bounded web ingestion; additive/merge only, never deletes. |
| `quenching-knowledge` | Captures ONE piece of generic knowledge a human states into `knowledge/`. |
| `quenching-knowledge-scan` | Sweeps the WHOLE bundle to backfill `knowledge/glossary.md` with terms already documented but never listed; fans sub-agents out per home slice. |
| `quenching-glossary` | Adds/refines ONE glossary entry on demand — the single-term counterpart of `quenching-knowledge-scan`. |
| `quenching-memory-to-docs` | Drains `~/.claude/projects/<cwd>/memory/` into the bundle, clearing each memory once its doc lands and passes conformance. |
| `quenching-harness` | Refactors a target's `CLAUDE.md`/`AGENTS.md` into thin pointers over its `docs/` bundle, MOVING (never copying) inlined durable knowledge into its home. |
| `quenching-visualize` | Renders the bundle as ONE self-contained, offline HTML diagram (force-directed graph, coloured by `type`, edges from cross-links) via `assets/tools/okf-visualize.py`. Read-only; the `.html` is written outside `docs/`. |
| `quenching-cycle` | The conductor: runs `align` → `memory-to-docs` → `harness` → `knowledge-scan` as a dependency pipeline, pass after pass, until a fixpoint (nothing changes and the validator is clean) or a pass cap. (`enrich`/`visualize` are on-demand tools, not loop stages.) |
| `openspec-explore` | Thinking partner before/during an OpenSpec change; OpenSpec + OKF awareness (reads glossary/knowledge/standards, routes durable insights to the quenching skills). Never implements. |
| `openspec-propose` | Creates an OpenSpec change and generates all artifacts (proposal, delta specs, design, tasks) until apply-ready; reads the OKF bundle as context; retires a seed `backlog/` task into the Completed ledger. |
| `openspec-apply-change` | Implements a change's `tasks.md`; reads the touched subjects' `standards/` as binding contracts; routes durable learning to its OKF home. |
| `openspec-update-change` | Revises a change's existing planning artifacts and keeps them coherent; never edits code. |
| `openspec-sync-specs` | Merges delta specs into `openspec/specs/` (current behavior). Boundary: `openspec/specs/` = WHAT the product does; `docs/standards/` = HOW we build. |
| `openspec-archive-change` | Checks completion, offers the sync, moves the change to `changes/archive/`, then offers ONE OKF distillation pass (durable knowledge → `docs/`, per its `references/distill.md`). |

Each `SKILL.md` frontmatter `description` carries its own trigger phrases and its "Not
for: X → other-skill" boundary — read the target skill's frontmatter before assuming
which one owns a task. Shared procedure lives once in its owner and other skills cite it
rather than restating it: the insert procedure in
[`quenching-insert/references/homes.md`](plugins/claude-quenching/skills/quenching-insert/references/homes.md),
the checks in
[`quenching-align/references/conformance.md`](plugins/claude-quenching/skills/quenching-align/references/conformance.md),
the OpenSpec facts (layout, artifact graph, CLI surface, store selection) in
[`openspec-propose/references/openspec.md`](plugins/claude-quenching/skills/openspec-propose/references/openspec.md),
and the OKF distillation doctrine in
[`openspec-archive-change/references/distill.md`](plugins/claude-quenching/skills/openspec-archive-change/references/distill.md).

### The OpenSpec ↔ OKF relation

The six `openspec-*` skills are adapted 1:1 from the skills the OpenSpec CLI
(`@fission-ai/openspec` 1.6.0, `metadata.generatedBy`) generates, so target repos drop
their local `.claude/skills/openspec-*` / `.claude/commands/opsx/` copies and get them from
the plugin. The upstream CLI-driven mechanics (`openspec new change`, `status --json`,
`instructions --json`, `list --json`) are the contract that survives upgrades — keep them
intact. The adaptation is the **OKF bridge**: `docs/` is read as context going in
(standards, ADRs, glossary; a `backlog/` idea as seed), and durable knowledge is distilled
back out at archive time (never bulk-copied). `openspec/specs/` and `docs/` never duplicate
content. These skills are on-demand tools, **not** `quenching-cycle` loop stages, and the
scaffold in target repos comes from `openspec init` (no setup skill).

## The OKF bundle contract

Every target repo the plugin aligns converges to the **same tree** under `docs/`:
`standards/` (current contracts, subject subfolders), `catalog/` (own data), `decisions/`
(ADRs), `vision/`, `backlog/` (task inbox: `type: task`, optional `priority`/`tags`/`complexity`,
derived index zone), `documentation/`, `knowledge/` (incl. fixed `glossary.md`),
`reference/` (external facts). Rules the plugin
enforces everywhere:

- `index.md` is a reserved, frontmatter-free listing (exception: root `docs/index.md`
  carries only `okf_version: "0.1"`).
- Every other concept doc MUST have YAML frontmatter with a non-empty `type` from the
  fixed vocabulary.
- `log.md` uses `## YYYY-MM-DD` headings, newest first.
- Folder names, concept-doc file slugs, frontmatter keys, and `type` values are canonical
  English (cross-repo greppable); body prose may follow the target repo's language;
  identifier-derived slugs (catalog tables, repo names, ADR `NNNN-` prefixes) stay verbatim.

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

## The diagram generator (`assets/tools/okf-visualize.py`)

Stdlib-only Python, zero dependencies. Self-contained: it reuses the same frontmatter parser
and link resolver as `okf-validate.py` (so the diagram's edges are exactly the within-bundle
link graph the validator models — relative AND `/docs/...` links) but imports nothing from it.
CLI: `okf-visualize.py <docs-dir> [--out okf-diagram.html] [--name NAME] [--json] [--version]`,
exit 0 = written. It walks the bundle's concept docs, builds a graph (nodes coloured by the OKF
`type` vocabulary, directed edges from cross-links), and injects it plus `viewer/viz.{html,css,js}`
and the two **vendored MIT libraries** (`viewer/vendor/cytoscape.min.js`, `marked.min.js`)
**inline** into one HTML file — so the output renders **offline**. Doc bodies are JSON-embedded
with `<` escaped so a body containing `</script>` cannot break the page. The `.html` is written
**outside** `docs/` (default `./okf-diagram.html`) — never inside the bundle, or the validator
would scan generated output. `--version` is kept in lockstep with `VERSION`; the
`quenching-visualize` skill drives it (and `quenching-align` step 7 offers it). The tool and the
`viewer/` shell are adapted from the OKF reference implementation's `visualize` command
(`GoogleCloudPlatform/knowledge-catalog`, Apache-2.0) — see `assets/tools/viewer/vendor/LICENSES.md`.

## Verifying changes

There is no test suite. To verify the plugin's own shipped skeleton is still conformant
after touching anything under `plugins/claude-quenching/assets/docs/`:

```bash
cd plugins/claude-quenching
python3 assets/hooks/okf-validate.py assets/docs
```

This must report `0 error(s), 0 warning(s)` — the skeleton is conformant by construction.

And to verify the diagram generator still builds an offline diagram of the skeleton and its
`--version` matches `VERSION`:

```bash
python3 assets/tools/okf-visualize.py assets/docs --out /tmp/okf-diagram.html   # exit 0 + node/edge counts
python3 assets/tools/okf-visualize.py --version                                 # == VERSION
```

Write the generated `.html` to `/tmp` or the repo root — **never** under `assets/docs/`, or the
validator would flag generated output. Re-run `okf-validate.py assets/docs` after, to confirm the
skeleton is untouched.

When editing a `SKILL.md`, keep the `description` under the shared **1,536-character**
per-skill cap (Claude Code truncates beyond it) with trigger phrases in the frontmatter's
second sentence so truncation never eats them; keep skill bodies well under 500 lines and
push shared procedure into the owning `references/*.md` instead of restating it in every
skill that cites it.

## Two rules that must survive any refactor

- **Never add `context: fork` to these skills.** Every sweep skill gates on a mid-flow
  confirmation (one plan → one OK) when run standalone — and even a cycle-authorized run
  (`quenching-cycle/references/cycle.md` §cycle-authorization) must still surface code-coupled
  confirmations mid-flow, which a forked context cannot present.
- **Never downgrade classification or executor sub-agents to `haiku` in
  `quenching-memory-to-docs`.** A misclassification there becomes a wrong memory deletion —
  see the model-policy table in
  [plugins/claude-quenching/README.md](plugins/claude-quenching/README.md#cost-model) for
  which sub-agent calls in the other skills are safe to run on cheaper models/effort.

## Releasing

Bump `version` in `plugins/claude-quenching/.claude-plugin/plugin.json` **and**
`plugins/claude-quenching/VERSION` together — that pair is what Claude Code uses to detect
and apply an upgrade. Keep the `VERSION` constant in **both** shipped scripts in lockstep with
that pair — `assets/hooks/okf-validate.py` and `assets/tools/okf-visualize.py` — since each
script's `--version` is what `quenching-align` (the hook) and `quenching-visualize` (the tool)
compare against an already-installed copy in a target repo. Mirror the plugin `version` in the
marketplace manifest's plugin entry (`.claude-plugin/marketplace.json`) too.
