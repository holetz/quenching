---
description: Align docs/ to the canonical OKF bundle — install, force-conformance, validate
argument-hint: [optional-docs-path]
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task
---

# /docs:align — force the knowledge base into OKF shape

**Input**: `$ARGUMENTS` (optionally a `docs/` path or a scope; omit to align the whole bundle).

Installs and enforces **one** canonical OKF v0.1 bundle of `docs/` so every repo that
adopts this plugin looks the same. The payload (skeleton, molds, validator) lives at
`${CLAUDE_PLUGIN_ROOT}/assets/`; the contract lives in
`${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/`:

- [docs-align/okf-spec.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/okf-spec.md) — the normative OKF v0.1 rules (MUST/SHOULD/MAY).
- [docs-align/taxonomy.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/taxonomy.md) — the canonical tree, homes, `type` vocabulary, boundaries.
- [docs-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/migration.md) — variant→canonical map + blast-radius doctrine.
- [docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md) — the exact checks the validator applies.

The executable checker is `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`
(`python3 okf-validate.py <docs-dir>` → exit 0 = conforms).

## Doctrine (non-negotiable)

The sweep contract every align shares — convergence over accommodation, one plan → one OK with
code-coupled items gating individually, the cycle-authorized narration exception, the two-scan
blast-radius procedure, MERGE-never-clobber, never-delete-on-a-guess, and
align-conformance-report-the-cycle — lives once in
[align-all/sweep-doctrine.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align-all/sweep-doctrine.md).
Read it as this skill's doctrine. What follows is only what is **specific to `docs/`**:

- **Completeness of what fits, evidence-gated.** A repo without data gets no `catalog/`; a
  standard is generated only with observed `file:line` evidence; the rest is a recorded
  deferral, never a silent skip.
- **Folders over prefix-clusters.** When sibling files share a subject prefix
  (`nomenclatura-classes.md`, `nomenclatura-funcoes.md`, `nomenclatura-modulos.md`, …), that
  prefix **is** the subject and the repetition is the "filename repeats the folder" smell →
  promote the cluster into a subfolder (canonical English), strip the prefix, generate the
  folder's `index.md` (`code/symbol-naming/{classes,functions,modules,…}.md`). Keep flat files
  when a folder adds ceremony without aiding disclosure (a lone file, an incoherent prefix, two
  short siblings on an axis unlikely to grow). Favor the folder when it earns its keep, not by reflex.
- **English canonical surface — structure + frontmatter; content may be local.** Folder names
  **and concept-doc file slugs**, frontmatter keys, enum values, and the `type` vocabulary are
  canonical English, cross-repo greppable (`nomenclatura-variaveis.md` → `naming/variables.md`,
  `validacao-desenvolvimento.md` → `development-validation.md`). Frontmatter stays English; the
  **body prose MAY follow the repo's language** — only the content, never the surface.
  **Exception — identifier-derived names are verbatim, never translated:** a catalog
  `<schema>`/`<table>` slug mirrors the real object, `reference/repositories/<repo>` the real
  repo — anglicizing them would sever the greppable tie to the
  asset.

## Workflow (force-with-1-confirmation)

### 1. Derive the current shape (read-only)
Detect an existing `docs/` (or the repo's variant root), its section names, which docs carry
frontmatter, and whether an OKF bundle already exists (`index.md` / `log.md` / `okf_version`).
Use `Glob`/`Grep`; do not write anything yet.

### 2. Map → canonical + conformance sweep
Match each existing section to a canonical home via the variant→canonical map
([docs-align/migration.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/migration.md)) — top-level (`arquitetura/`→`standards/`)
and subfolder (`codigo/`→`code/`). Run the checker over the current tree
(`okf-validate.py <docs-dir>`) and read [docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md).
Produce the **alignment plan** — enumerate:
  - **(a)** homes to scaffold (only those that apply), **plus the operator manual**
    `<docs>/QUENCHING.md` — install / refresh / leave, per the rule in Step 4;
  - **(b)** variants to migrate/rename (with per-item destination);
  - **(b2)** **prefix-clusters to fold into subfolders** (`nomenclatura-*` siblings → a
    `symbol-naming/` folder, prefix stripped) — one folder per coherent cluster; note the ones
    kept flat and why;
  - **(b3)** **non-English slugs to translate** — every concept-doc file slug on a technical home
    that is not canonical English, with its English target (`convencoes.md` → `conventions.md`);
    leave identifier-derived names (catalog tables, repo names) verbatim;
  - **(c)** misfiled docs to relocate (semantic placement, per item);
  - **(d)** frontmatter to stamp/normalize — add non-empty `type`, migrate `summary:`→
    `description:` and `updated:`→`timestamp:`, normalize enums to canonical English;
  - **(e)** `index.md` files to (re)generate (reserved listings) — **one per directory that
    holds concept docs** (the `dir-no-index` set from the checker), plus any `index.md` that
    wrongly carries frontmatter, or `README.md` to convert to `index.md`;
  - **(f)** `log.md` to establish (`docs/` and `docs/standards/`);
  - **(g)** the **blast radius** of every code-coupled rename (a slug translation or a
    cluster-fold is a rename — sweep its references like any other).

### 3. Present the full plan → gate on ONE OK
Show the whole plan. For each variant rename, sweep references with **`git grep` /
`grep --no-ignore`** (never skip gitignored maps) and **report the scope**: how many files,
which reach **product code**, which non-`docs/` referrers (skills, `CLAUDE.md`, prose links)
the rename edits. When the rename set is more than a handful, delegate the sweep to **one
read-only `Task` sub-agent** (`model: haiku`, `effort: low`) that only **collects** hits —
`rename → [file:line, …]` per candidate, no judgment — and classify each hit yourself
(docs-only vs product code); the mechanical grep needs no session-model reasoning, the
classification does. The batch OK covers exactly the enumerated docs-only set. Each
**code-coupled** rename is its **own** confirmation item (it is a refactor of the target's
product, not a docs move) — alert the user, never rename silently.

### 4. Execute on OK (invasive)
- **Scaffold** missing homes from `${CLAUDE_PLUGIN_ROOT}/assets/docs/` (copy the applicable
  `index.md` listings **and any `.pages` nav sidecars**, e.g. `documentation/**`; adapt boundary
  lines to the repo). When scaffolding `knowledge/`, also copy
  its **fixed `glossary.md` seed** — the repo's A–Z term lookup — and list it in
  `knowledge/index.md` (it is the only pre-seeded concept doc the skeleton ships).
- **Install the operator manual** — copy `${CLAUDE_PLUGIN_ROOT}/assets/docs/QUENCHING.md` to
  `<docs>/QUENCHING.md`, replacing the banner's `<VERSION>` placeholder with the plugin's
  `VERSION` file. **This is the manual-install rule the other two fronts cite** (`/specs:align`,
  `/skill:align`) — same four branches, their own asset and destination:
  - **absent** → install;
  - **present, banner stamp older than the plugin** → overwrite (nothing repo-specific is lost —
    the manual is static payload);
  - **present, banner stamp same or newer** → leave it, silently;
  - **present, no `claude-quenching` banner** → a human took it over: **keep it verbatim** and
    report it. Never clobber.
  The manual is **exempt** from OKF ([docs-align/conformance.md](${CLAUDE_PLUGIN_ROOT}/assets/references/docs-align/conformance.md)) —
  never stamp it, never convert it to `index.md`. List it in the root `index.md` (Step 4's
  regeneration) so it is reachable from the bundle's front door.
- **Migrate** variants: move the folder, update every cross-ref found in Step 3 (relative
  within a home, absolute `/docs/...` across homes).
- **Stamp/merge** frontmatter with the molds in `${CLAUDE_PLUGIN_ROOT}/assets/templates/`
  (`standard-front.md` for standards, `concept-front.md` otherwise).
- **Regenerate** every `index.md` deterministically — **one for every directory that holds
  concept docs** (create the missing ones the `dir-no-index` check reports; a subject folder,
  a freshly folded cluster, and a catalog schema dir all get a front door). Each listing links
  its real children (no `dir-no-index`, no `index-broken-link`, no `index-orphan` left behind);
  strip stray frontmatter; for `standards/index.md` rebuild only the
  `<!-- BEGIN/END GENERATED -->` zone from disk.
- **Establish/append** `log.md` (`## YYYY-MM-DD`, newest first, `**Creation**/**Update**/
  **Deprecation**` prefixes).
- **Write** `okf_version: "0.1"` into the root `docs/index.md` frontmatter.

### 5. Verify against the conformance core
Re-run `okf-validate.py <docs-dir>` (add `--json` to read finding codes). Confirm: every
non-reserved doc has frontmatter + a non-empty `type`; every `index.md` is frontmatter-free
(root only `okf_version`); every `log.md` is `## YYYY-MM-DD` newest-first; and the
**structural-integrity WARNs are cleared — zero `dir-no-index`, `index-broken-link`,
`index-orphan`** (these are WARN, so exit-0 alone does not prove them clean — inspect the
findings). Report residual gaps (unresolved relocations, deferred sub-standards).

### 6. Wire the enforcement hook (offer install **or upgrade**)
Offer to install the validator so future edits stay aligned: copy **exactly**
`${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py` + `hooks-config.json` into the target's
`.claude/hooks/` (never the directory recursively), and merge `settings.snippet.json` into
`.claude/settings.json` (`PostToolUse` + `Stop` propose; opt-in `PreToolUse` hard-block via
`hardBlock: true`). Set `docsDir` if the bundle root is not `docs/`. If a copy is **already
installed**, compare its version (`python3 .claude/hooks/okf-validate.py --version`) with the
plugin's `VERSION` file and offer to overwrite **only the script** when the plugin is newer —
the target's `hooks-config.json` is preserved. See
[../../assets/hooks/README.md](../../assets/hooks/README.md).

### 7. Offer the mkdocs site setup (optional)
If the bundle has a `documentation/` home, offer to install the batteries-included
**mkdocs-material** site setup so the product docs render as a site. Copy from
`${CLAUDE_PLUGIN_ROOT}/assets/mkdocs/`:
- `mkdocs.yml.tmpl` → the repo **root** as `mkdocs.yml` **only if absent** (never clobber a
  customized one — show a diff and let the user merge); fill `site_name`/`site_description`.
- `requirements.txt` → repo root (or merge its two lines into an existing docs-requirements).
- On request, `ci-github-pages.yml` → `.github/workflows/docs.yml` (opt-in; platform-specific).
The `.pages` nav files ship **with** the `documentation/` skeleton (Step 4), so nav needs no
separate install here. See [../../assets/mkdocs/README.md](../../assets/mkdocs/README.md).

This is the **first install only** — a one-shot part of scaffolding. The site layer's owner is
`/docs:documentation:build` (`/docs:documentation:build`): every later update, nav
regeneration, config merge, and build verification is **its** job, and this step never
substitutes for it. If the install is anything more than stamping two absent files — a
customized `mkdocs.yml` to merge, a `docs_dir` pointing elsewhere, sections whose `.pages` no
longer match the tree — hand off to that skill instead of resolving it here.

## Invariants to never violate
- Never put a concept `type` on an `index.md`; never leave a concept doc without one.
- Never invent a `resource:` — derive it as a **glob set** of what the doc governs (standards) or
  the asset URI (catalog/reference); empty is disallowed, and self-pointing (`resource-self`) is
  too, except a bundle-level aggregate like `knowledge/glossary.md`.
- Never delete or rename without OK; code-coupled renames get their own confirmation. A slug
  translation and a cluster-fold are renames — same rule. A cycle-authorized run
  (convergence.md §contract) replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never translate an **identifier-derived** slug (catalog table/schema, repo name) — it mirrors
  a real asset; anglicizing it breaks the greppable tie.
- Never leave a directory that holds concept docs without an `index.md`, and never leave a
  listing that links to a nonexistent file (a lying index).
- Never hand-edit a `<!-- BEGIN/END GENERATED -->` zone — regenerate it from disk.
- Never stamp, rename, or OKF-validate `QUENCHING.md`, and never overwrite one whose
  `claude-quenching` banner a human removed — keep it and report it.
