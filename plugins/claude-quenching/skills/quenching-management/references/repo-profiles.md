# Repo profiles — catalog of signals → emphasis (guide, not enum)

> **Way back:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

> **EXAMPLES catalog, not a closed enum.** These profiles are a **prioritization
> guide** for the "Emphasis modulation by repo profile" (Step 4 of
> [SKILL.md](../SKILL.md)). A repo can match **several** profiles or **none** —
> it is a heuristic for choosing where the method yields **more**, **never** a
> gate that toggles a dimension on/off. **Full coverage remains**: the profile
> **reorders** the P1/P2 queue and installation plan; it never hides a dimension
> from the scorecard. Every signal below is **observable in Step 1**
> (file/structure/dependency), and every report recommendation is **anchored in
> an actually seen trigger** (`file:line`/fact), not in the profile name. Where
> two profiles match, **add the emphases** (they are additive).

The official source gives the principle that justifies modulating instead of
spreading: *"you don't need to configure everything upfront — each feature has a
recognizable trigger… start with CLAUDE.md and add the others as the triggers
appear"* and *"every feature you add consumes context… too many can fill the
window, but also add noise"*
([features-overview](https://code.claude.com/docs/en/features-overview),
accessed 2026-06-29). Investing in a dimension the repo **does not show a trigger
for** is the same waste as omitting one it does show.

## How to use

1. In Step 1, note the **profile signals** (already foreseen at the close of
   Step 1).
2. Match the repo with 0-N profiles below (freely — don't force a single label).
3. In Step 4, the "For THIS repo, invest first in…" block receives the **summed
   emphases** of the matching profiles, each anchored in the observed trigger.
4. No match → flat emphasis is **correct** (small/neutral-shape repo); don't
   invent a profile just to have something to prioritize.
5. The profile also suggests **what TYPE of DOMAIN skill/sub-agent** often pays
   off to create when the repo shows a **recurring need** (dim 6/7, criterion
   "when to CREATE a domain artifact"): in an MLOps repo, a skill "train/validate
   model X"; in a data-pipeline, a skill "create new domain task" and a sub-agent
   "diagnose run/log"; in a service, a skill "incident runbook". These are
   **trigger examples**, not package payloads — the method **proposes the
   skeleton**, the repo fills the content (Boundary limit).

## Catalog

### MLOps / model-heavy
- **Signals:** training/inference pipeline folder; `mlflow`/`sklearn`/`torch`
  pinned in the manifest; model artifacts, samples/slices/exclusions;
  model release by cadence.
- **Emphasis:** **dim 8** (Stop hook + Step 8 trigger (2) — *"revisit after
  major model releases… instructions that worked around an older model's
  limitation may become overhead"*: re-modulate emphasis at each release);
  **dim 14** (don't touch model pins/code = guardrail). Dims 3 (direction)
  and 10 (memory) tend to be **dense** in a model repo (model decisions
  accumulate), but this weighs only toward **proposing the home** for that
  content (Step 6) — the profile **does not** prescribe *what* the VISION/memory
  should say (see "Boundary").

### Data-pipeline / ETL
- **Signals:** bronze/silver/gold layers (or raw/staging/mart); jobs/DAGs;
  **generated** artifacts (catalog, schemas, manifests) co-located with the
  source.
- **Emphasis:** **dim 11** (catalog/domain); **dim 14** (PreToolUse that
  PROTECTS the GENERATED artifact — the "X defines Y" rule: the source is the
  truth, the generated is disposable); **dim 1** (map "source × generated"
  per layer).

### Library / SDK
- **Signals:** `src-layout` or `lib/`; public API surface; no runtime app;
  package manifest (`pyproject`/`package.json`) with `version`.
- **Emphasis:** **LEAN dim 1** — *"20-80 lines (lib)"* (size guideline,
  04-claude-md-memory.md);
  **dim 2** (`standards/` of the API as contract); **dim 6** (skill = API
  style-guide, *"reference skills provide knowledge… like your API style
  guide"*). Code intelligence if the language is typed (*"typed languages,
  large codebases where grep is slow"*).

### Service / runtime app
- **Signals:** server/CLI entrypoint; deploy targets; env vars; external
  services (database, queue, SQL warehouse) outside the repo.
- **Emphasis:** **medium dim 1** — *"80-200 lines (service)"*; **dim 15
  (MCP)** for external data/systems (*"external data or actions → connect that
  system as an MCP server"*); **dim 14** (deploy/secret guardrail via hook).

### Monorepo / large codebase
- **Signals:** multiple packages/subsystems (`packages/*`, `src/<lib>/`); many
  CLAUDE.md files; thousands of files; generated/vendored code versioned.
- **Emphasis:** **dim 1** (per-directory CLAUDE.md per scope +
  `claudeMdExcludes` + `Read` deny rules for generated/vendored); **fan-out**
  to auditor sub-agent (Step 2); **per-directory skills**; **rollout plugin**
  when layering *"stops scaling"* (*"replace many per-directory CLAUDE.md files
  with one set of conventions everyone installs"*). Gotcha: project settings
  *"load only from the starting directory… not inherited from parents"* → one
  settings per startup subfolder (hook wiring).
  Source: [large-codebases](https://code.claude.com/docs/en/large-codebases)
  (accessed 2026-06-29).

### Multi-contributor cross-tool
- **Signals:** `AGENTS.md`/`.cursorrules`/`GEMINI.md`/`.github/copilot-instructions.md`
  present (or expected); team uses more than one agent tool.
- **Emphasis:** **dim 1** on the CLAUDE.md × AGENTS.md boundary (`@AGENTS.md`
  import or symlink; thin CLAUDE.md with only Claude-exclusive content); **dim
  12** (single-home: what's in the shared AGENTS.md doesn't duplicate inline).
  Source: 10-agents-md-interop.md.
  (Candidate for its own advance in the backlog — the profile only signals the
  emphasis.)

### Mature `.claude/` (populated surface)
- **Signals:** many skills/agents/hooks/commands already in `.claude/`;
  overlapping descriptions; hooks in the directory without an entry in
  `settings.json`.
- **Emphasis:** **dim 6** (bloat/merge, trigger, outgrowth), **dim 7**
  (`tools` absent), **dim 8** (wiring — *"a script file alone does
  nothing"*), **dim 9** (composability/budget) **rise**. The cost of excess
  is real: *"too much can… add noise that makes Claude less effective; skills
  may not trigger correctly"*.

### Greenfield / repo from scratch
- **Signals:** no `.claude/` (or only `/init`); few docs; almost everything
  **Absent** in the scorecard.
- **Emphasis:** here emphasis **shifts from "which dimensions" to "in what
  ORDER"** — *"start with CLAUDE.md for project conventions, then add other
  extensions as specific triggers come up"*. The **canonical adoption sequence**
  (foundation that unlocks → skills → MCP → hooks → plugin) **is not repeated
  here**: it has **one unique home**, the **"Base-Order"** of the payload
  [`quenching-roadmap`](../assets/skills/quenching-roadmap/SKILL.md), which Step 4
  fires for greenfield. The profile only **signals** that this is the case where
  sequence matters **most** (scorecard almost all Absent, no triggers yet) —
  the roadmap is what produces and keeps it updated. Rule that survives without
  duplicating the order: **don't install hook/MCP/sub-agent without the trigger**
  — that would be noise before its time.

## Boundary (what the profile does NOT do)

- **Does not become dimension 16** or a knob in the template — it is only input
  for Step 4.
- **Does not decide content** (VISION/memory/boundary of the repo — that's only
  Step 6): the profile weighs **which METHOD dimension to invest in**, never
  *what* the repo should say.
- **Does not filter the scorecard:** reorders/recommends; full coverage intact.
- **Is not canonical taxonomy** (distinct from the `docs/` one in
  [docs-taxonomy.md](docs-taxonomy.md), which **prescribes names**): here
  profiles are **free examples**, without a fixed name to impose on the repo.
