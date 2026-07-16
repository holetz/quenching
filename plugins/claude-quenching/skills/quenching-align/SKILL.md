---
name: quenching-align
description: >-
  Forces a repository's docs/ knowledge base into the canonical Open Knowledge Format
  (OKF v0.1) bundle this plugin defines, and keeps it conformant. Use when the user asks
  to "align the knowledge base to OKF", "install the docs structure", "force OKF
  conformance", "migrate docs/ to the standard", "make docs/ OKF-compliant", "organize
  docs/ into the canonical tree", or when docs/ has variant names / missing frontmatter /
  a lying index. Installs the canonical homes (standards/ decisions/ vision/ backlog/
  documentation/ knowledge/ reference/ catalog/), migrates
  variant folder names, folds prefix-clusters into subject subfolders, translates
  non-English slugs, stamps OKF frontmatter, regenerates every index.md, establishes
  log.md, and validates. Invasive by design: ONE full plan, one confirmation; a rename
  reaching product code confirms on its own. Not for: adding content → quenching-insert.
when_to_use: >-
  installing and force-aligning a repo's docs/ structure to the canonical OKF bundle.
  The structural half; content insertion is quenching-insert.
allowed-tools: Read, Grep, Glob, Bash, Write, Edit, Task
---

# quenching-align — force the knowledge base into OKF shape

Installs and enforces **one** canonical OKF v0.1 bundle of `docs/` so every repo that
adopts this plugin looks the same. The payload (skeleton, molds, validator) lives at
`${CLAUDE_PLUGIN_ROOT}/assets/`; the contract lives in `references/`:

- [references/okf-spec.md](references/okf-spec.md) — the normative OKF v0.1 rules (MUST/SHOULD/MAY).
- [references/taxonomy.md](references/taxonomy.md) — the canonical tree, homes, `type` vocabulary, boundaries.
- [references/migration.md](references/migration.md) — variant→canonical map + blast-radius doctrine.
- [references/conformance.md](references/conformance.md) — the exact checks the validator applies.

The executable checker is `${CLAUDE_PLUGIN_ROOT}/assets/hooks/okf-validate.py`
(`python3 okf-validate.py <docs-dir>` → exit 0 = conforms).

## Doctrine (non-negotiable)

- **Convergence, not accommodation.** The repo converges to the plugin's fixed names; a
  variant name (`docs/arquitetura/`) is a **non-convergence smell** — a migration
  candidate, never a convention to preserve. Every aligned repo ends with the **same tree**.
- **Force with ONE confirmation.** Present the **complete** plan; a single OK executes the
  whole batch. **Exception:** a rename whose blast radius reaches **product code** (path
  constants, imports, docstrings) is a **distinct** confirmation item with its scope shown —
  **never** folded into the batch OK. **Exception — cycle-authorized runs:** invoked by
  `quenching-cycle` under its cycle-authorization contract
  ([../quenching-cycle/references/cycle.md](../quenching-cycle/references/cycle.md)), the plan
  is presented as narration, not a gate; a code-coupled item still confirms on its own, always.
- **Stamp = MERGE, never clobber.** Fill a missing key; preserve a filled one and any
  third-party key (OKF consumers, a legacy `status:`, site generators).
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
  repo, an ADR keeps its `NNNN-` prefix — anglicizing them would sever the greppable tie to the
  asset.

## Workflow (force-with-1-confirmation)

### 1. Derive the current shape (read-only)
Detect an existing `docs/` (or the repo's variant root), its section names, which docs carry
frontmatter, and whether an OKF bundle already exists (`index.md` / `log.md` / `okf_version`).
Use `Glob`/`Grep`; do not write anything yet.

### 2. Map → canonical + conformance sweep
Match each existing section to a canonical home via the variant→canonical map
([references/migration.md](references/migration.md)) — top-level (`arquitetura/`→`standards/`)
and subfolder (`codigo/`→`code/`). Run the checker over the current tree
(`okf-validate.py <docs-dir>`) and read [references/conformance.md](references/conformance.md).
Produce the **alignment plan** — enumerate:
  - **(a)** homes to scaffold (only those that apply);
  - **(b)** variants to migrate/rename (with per-item destination);
  - **(b2)** **prefix-clusters to fold into subfolders** (`nomenclatura-*` siblings → a
    `symbol-naming/` folder, prefix stripped) — one folder per coherent cluster; note the ones
    kept flat and why;
  - **(b3)** **non-English slugs to translate** — every concept-doc file slug on a technical home
    that is not canonical English, with its English target (`convencoes.md` → `conventions.md`);
    leave identifier-derived names (catalog tables, repo names, ADR prefixes) verbatim;
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
separate install and no regeneration. See [../../assets/mkdocs/README.md](../../assets/mkdocs/README.md).

### 8. Offer the diagram (optional)
Once the bundle conforms, offer to render it as a **self-contained, offline HTML diagram** —
the [quenching-visualize](../quenching-visualize/SKILL.md) skill's job — by running the
plugin's zero-dependency generator straight from the plugin root (no install):

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/tools/okf-visualize.py" <docs-dir> --out ./okf-diagram.html
```

Write the `.html` **outside** the bundle (default `./okf-diagram.html`), **never** under
`docs/` — it is generated output the validator must not scan. As with the hook (step 6), also
offer to install/upgrade the tool into the target's `.claude/tools/` for standalone use: copy
`okf-visualize.py` **and** its `viewer/` payload together, comparing `--version` with the
plugin's `VERSION`.

## Invariants to never violate
- Never put a concept `type` on an `index.md`; never leave a concept doc without one.
- Never invent a `resource:` — derive it from the doc's `file:line` anchors (standards) or
  the asset URI (catalog/reference); empty/self-pointing is disallowed.
- Never delete or rename without OK; code-coupled renames get their own confirmation. A slug
  translation and a cluster-fold are renames — same rule. A cycle-authorized run
  (cycle.md §contract) replaces only the batch gate with narration — never a code-coupled
  item's own OK.
- Never translate an **identifier-derived** slug (catalog table/schema, repo name, ADR `NNNN-`
  prefix) — it mirrors a real asset; anglicizing it breaks the greppable tie.
- Never leave a directory that holds concept docs without an `index.md`, and never leave a
  listing that links to a nonexistent file (a lying index).
- Never hand-edit a `<!-- BEGIN/END GENERATED -->` zone — regenerate it from disk.
