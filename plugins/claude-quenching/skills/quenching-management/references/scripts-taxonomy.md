# Canonical taxonomy of `scripts/` — the home of executable logic

> **Path back:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

> **This is the CANONICAL specification of `scripts/`** — the home of **deterministic
> executable logic** at the repo level (build/deploy, generators, checks,
> maintenance, dev tooling). Dimension 8 ([dimensions-template.md](dimensions-template.md))
> and detection ([detection-and-smells.md](detection-and-smells.md)) **point here** —
> they do not repeat the tree. It is the sibling of [docs-taxonomy.md](docs-taxonomy.md): that one
> governs **knowledge** (`docs/`), this one governs the **executables** (`scripts/`) that the
> knowledge surface **invokes**.

## Why `scripts/` is a first-class element

The knowledge surface **is not just prose**: it **invokes executables**. The
method already mandates that deterministic logic lives in **code**, not inline in
the description — *«hooks are shell commands… deterministic control»*, and the official
doc is explicit in showing the hook calling **a separate script file**
(*«This example uses a separate script file that the hook calls»*). What calls
these executables is the surface itself:

- **hooks** trigger scripts (dim 8) — *«use… `${CLAUDE_PROJECT_DIR}` to reference
  scripts»*;
- the **"common commands" that CLAUDE.md documents** (dim 1) are script invocations
  (`python -m scripts.<package>.<module>`, `make …`);
- **skills/commands** load `scripts/` that execute;
- **CI** runs scripts (build/deploy, artifact generation, "X defines Y").

If this logic lives **scattered and without a home** — hook logic embedded inline, a
repo-level `scripts/` invisible to auditing, loose scripts at the root — the method
audits only half the surface. `scripts/` is the **canonical home** of that logic.

## Prescriptive rule

Like `docs/`, `scripts/` has a **canonical organization**: subfolders **by
PURPOSE**, a README-map, a single execution convention, and the boundary that distinguishes
this home from its neighbors. The repo **converges** to this organization; a loose script at the
root without a purpose subfolder is a **disorganization smell**.

**Difference in force vs. `docs/`:** the **names of `docs/` homes are locked**
(the repo converges to the identical name). In `scripts/`, the **locked axis is PURPOSE**
(there is one subfolder per purpose), not the exact label: `ci/` may be called `build/`,
`checks/` may be called `quality/` — what is **not** acceptable is **not having** the separation
by purpose (everything in one bag, or loose at the root). Derive the label from the repo's
convention; **lock the separation**, not the string.

**Language:** subfolder names in **English kebab-case** (stable across repos); the
content/docstrings follow the repo's language (the repo convention wins — e.g.: PT-BR
outside the library).

## The canonical tree (organization by purpose)

```
scripts/
  ci/             # build & deploy — generates the deployable artifact, validates, runs in CI ("X defines Y")
  <gen>/          # GENERATORS of derived artifacts (catalog, docs, manifest) from the source
  checks/         # quality validations (data/code) — exit with error if a problem is found
  maintenance/    # one-off operational routines (clones, backup, migration) — flags-off by default
  dev/            # LOCAL development tooling — OUTSIDE the scope of Ruff/lint/CI
  README.md       # MAP (module → what-it-does → entrypoint), per subfolder — derivable from disk
```

> The labels above are **examples of the purpose axis**, not a closed enum: a
> repo matches a subset (a pure lib may have only `ci/` + `dev/`; a data repo gains `checks/`).
> Install **only the purposes that apply** — completeness of what fits, not a blind checklist
> (as in `docs/`).

## The purposes, one by one

For each one: **purpose**, the **boundary rule** that separates it from its neighbors, and the
**CI/lint scope** (the decisive label for `dev/` vs. the rest).

### `ci/` — build & deploy
- **Purpose:** what **generates the deployable artifact** and validates it — the
  build entrypoint, YAML/manifest generation from the source, CI lint/format, deploy.
- **Boundary / «X defines Y»:** it is the home of the rule *«the source (Python/config) defines the
  artifact (YAML/manifest), which is generated and **never edited by hand»** — the generated artifact is
  disposable, protected by code (crosses dim 8/14: the `protect-generated.py` that
  blocks editing the generated artifact and the `ci/` that **generates** it are the two ends of the same
  rule). Distinct from `dev/`: `ci/` runs in the pipeline and **is** within the lint scope.
- **CI scope:** within Ruff/lint/CI.

### `<gen>/` — derived artifact generators
- **Purpose:** scripts that **produce a derived artifact** read by human/agent
  (offline data catalog, generated docs, manifest) from the source of truth.
- **Boundary:** the generated artifact is **never edited by hand** (the «X defines Y» rule);
  human curation lives **separately** from the generated output (crosses dim 11/catalog). It is a
  purpose distinct from `ci/` when the repo separates "building the deployable" from "generating
  documentation/catalog"; in a simple repo, both collapse into `ci/`.
- **CI scope:** within lint (produces a versioned artifact).

### `checks/` — quality
- **Purpose:** **data/code quality** validations run on demand or in CI — they check
  invariants and **exit with error** (`SystemExit`/exit≠0) if a problem is found, to fail the pipeline.
- **Boundary:** *validates*, does not *generate* nor *mutate* (distinct from `ci/`/`maintenance/`).
  It is the natural home for a **generic validation runner** that a validation hook
  can invoke (the hooks-call-scripts doctrine applied to "validate before finishing").
- **CI scope:** within lint; typically also run by hook/CI.

### `maintenance/` — one-off operational
- **Purpose:** **one-off and potentially destructive operational routines** —
  sandbox clones, backup, data migration, permission setting.
- **Boundary:** **flags-off by default** (each step gated by a flag at the top of
  `main()`, most disabled) to avoid accidental destructive execution — this is the
  poka-yoke of dim 14 applied to operations. Distinct from `ci/` (idempotent,
  always runs) and `checks/` (read-only, validates only).
- **CI scope:** within lint, but does **not** run in the automatic pipeline.

### `dev/` — local tooling
- **Purpose:** **local development** tools — run diagnostics,
  converters, REPL/notebook startup helpers. Developer convenience, not part
  of the product.
- **Boundary (the most decisive one):** **OUTSIDE the scope of Ruff/lint/CI** (goes in the
  linter's `exclude`). This is what distinguishes `dev/` from all others: local tooling
  does not need to pass the product's quality gate. A `dev/` that the repo treats
  as product code (in lint, in CI) is in the wrong home; a product script dumped in `dev/` escapes the gate.
- **CI scope:** **excluded.**

## Execution convention (single, derived from the repo)

There is **one** documented way to run scripts, and the README declares it. The most
common standard in Python repos is to run **from the root** with `-m` so that
`scripts.*` imports resolve:

```
python -m scripts.<package>.<module>
```

But the convention is **derived from the repo**: it may be `make <target>`, `npm run <script>`,
`just <recipe>`, a `Taskfile`. The invariant is: **one** convention, **documented in the
README**, and **every invocation in the knowledge surface (CLAUDE.md "common commands",
hooks, commands/skills, CI) uses it** — not three diverging forms.

## README-as-map (the index derivable from disk)

`scripts/README.md` is a **MAP**, not prose: a **table per subfolder** (module →
what-it-does → entrypoint), mirroring exactly what is on disk. Like the `INDEX.md`
of `standards/`, it must be **derivable from disk** — a new module without a row in the map,
or a map row pointing to a non-existent module, is drift (the map **lies**). The
`CLAUDE.md` of `scripts/` (if present) is a short directive + link to the README (the
map role of dim 1), and never duplicates the table.

## Boundaries (what distinguishes this home from its neighbors)

- **repo-level `scripts/` × `.claude/hooks/*.py` (the central boundary):** **reusable
  deterministic logic** lives in `scripts/`; the **hook is THIN and CALLS IT**. The official
  doc fixes the form — *«This example uses a separate script file that the hook calls»*
  + *«use… `${CLAUDE_PROJECT_DIR}` to reference scripts»* — and the method's own
  doctrine (dim 1): *«hooks convert governance from
  probabilistic to deterministic»*, with the logic in **code**, not in prose. A
  hook with **validation/build logic embedded inline** in the `command` (or a
  `.claude/hooks/<x>.py` that reimplements what a `scripts/checks/<x>` already does) is
  **logic that should be extracted to a script** — the hook's `command` must resolve
  to a called `scripts/…`, not carry the rule. (Exception: a `.claude/hooks/` that
  is **only** the thin stdin-JSON→exit-code adapter is acceptable; what cannot happen is the
  **business rule** living there.)
- **repo-level `scripts/` × a skill's internal `scripts/`
  (`.claude/skills/<n>/scripts/`):** a skill carries its **own** `scripts/`
  for its **own** executables (conventional Agent Skills layout: *«`scripts/`
  for executables»*, loaded on demand when the skill activates). That is the home of
  an executable **specific to that skill**; the repo-level `scripts/` is the home of
  **repo** executables (build/checks/maintenance/dev) that **any** surface
  (CLAUDE.md, hooks, CI) invokes. A repo utility buried in a skill's `scripts/` (and
  called from outside it) is in the wrong home — promote it to the repo's `scripts/`;
  a helper used only by skill X does not need to pollute the repo's `scripts/`.
- **`scripts/` × `src/` (the library):** `scripts/` is **outside the deployable
  artifact** — utilities that orchestrate/generate/validate; **reusable product
  logic** lives in the library (`src/`). A script that has become a de-facto library
  (imported by many) distills into `src/`; orchestration logic does not pollute the lib.

## Organization doctrine (existing repo)

In a repo with scripts **loose at the root** or in a single bag without purpose, the method
**proposes organization to the canonical axis** — deterministic and safe, as in
`docs/`:

1. **Classify each script by purpose** (does it generate an artifact? validate? one-off
   operational? local tooling?) → the home (`ci`/`<gen>`/`checks`/`maintenance`/`dev`).
2. **Flag the loose-at-root / single-bag as organizable** (DEPRECATABLE in the
   report, with the proposed destination) — not a convention to keep.
3. **PROPOSE moving; NEVER move/rename without OK** (same deprecation doctrine
   as [installation.md](installation.md); the Step 5 confirmation remains).
4. **Install only the purposes that apply** (a pure lib does not get `checks/`);
   completeness of what fits, not a blind checklist.

The scaffold payload (README-map template + purpose subfolder skeleton,
**with no concrete scripts**) is at [../assets/scripts/](../assets/scripts/).
