---
name: quenching-knowledge-documentation-build
description: "Create or update the Zensical site layer from a confirmed editorial publication map, including extensions, CSS and strict-build QA. Triggers on \"build the docs site\", \"generate the site for /.knowledge/documentation\", or \"fix the documentation site's nav\"."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/build.md -->


# quenching-knowledge-documentation-build — create/update the editorially mapped site

**Input**: `$ARGUMENTS` (optionally a `documentation/` section to focus the nav check on, or the path of an existing `zensical.toml`; omit to inventory the whole site layer).

Makes the OKF bundle's [`documentation/`](../../knowledge/documentation/index.md) home
**render as a site**, and keeps that rendering honest as the home grows. The home is a plain
Markdown tree; everything generator-specific lives in a thin **site layer** around it — the
`zensical.toml` + `requirements.txt` at the repo **root**, outside the bundle. This skill owns that
layer end to end: it installs it when absent, merges it forward when present, keeps the `nav` in
step with the folder tree, stamps the static `assets/stylesheets/quenching.css` asset, and verifies
the site actually builds. The payload it stamps from is
[`../../assets/zensical/`](../../assets/zensical/README.md); the home's own
boundaries and the `documentation` type live with `quenching-knowledge-align`
([knowledge-align/taxonomy.md](../../references/knowledge-align/taxonomy.md)) and
`quenching-knowledge-add` ([knowledge-add/homes.md](../../references/knowledge-add/homes.md)).

`quenching-knowledge-align` step 7 offers the **first** install of this layer as part of scaffolding the
bundle; every install, update, and re-verification after that is **this** skill.

## Doctrine

- **The site layer is not the bundle.** Config lives at the repo root, *outside* `/.knowledge/`;
  inside it, this skill owns exactly one file — the CSS asset. The OKF markdown stays
  **generator-neutral** — never add generator-specific syntax, a nav entry inside a page, or
  generator frontmatter to a concept doc.
- **The confirmed Mapa editorial de publicação is the publication boundary.** Keep
  `docs_dir = ".knowledge/documentation"`: Zensical does not reliably render a hidden bundle root.
  A home marked `publicar` or `publicar derivado` is exposed by an intentional route or curated
  mirror below `documentation/`; `não publicar` creates no nav entry, route or link. The map,
  not a home's name, decides this. A missing or stale derived route is reported to the planning or
  writing stage; this site-layer command never invents or rewrites Markdown.
- **The nav lives in the config, and a new page is a new line.** Zensical runs no plugins, so
  nothing derives the sidebar from a sidecar file: without `nav`, the sidebar falls back to the
  folder tree with alphabetical order and titles derived from each page. Regenerating the list from
  the folder tree is this skill's; a **title a human wrote survives untouched**, and a missing one
  is derived from the section's `index.md` H1.
- **MERGE, never clobber.** A `zensical.toml` a human has customized is authoritative: add only the
  **missing required keys** (`docs_dir`, `navigation.indexes`, the nav entry), show the edit as a
  diff, and never remove or reorder a key you did not add. Same for `requirements.txt` — merge the
  pin into whatever file already pins the docs toolchain.
- **Publication metadata has ordered evidence.** Existing non-placeholder config wins. Otherwise,
  derive `repo_url` from `git remote get-url origin`; derive `edit_uri_template` only for a host
  whose URL shape is known and testable (Azure DevOps uses `?path=/{path}&version=GB<branch>`).
  `site_url` comes only from the selected delivery destination. Language and identity come only
  from a target contract or owned asset. Missing evidence is a finding, never a public placeholder.
- **Glossary projection has one source.** When the accepted map exposes the glossary, derive the
  site-layer abbreviation snippet from root `glossary.md` and verify both `reference/glossary.md`
  and rendered `<abbr>` output. Never ask an author to edit the derived snippet or a duplicate list.
- **Catalog projections are indexed, not flattened into nav.** When the map exposes `catalog/` as
  a derived reference, require `reference/catalog/index.md` as the sole nav entry. Verify that its
  layer/schema links reach every detail route, that each detail carries a stable identifier and
  lineage source, and that the generated route count is recorded. Never add one nav line per item.
- **A legacy `mkdocs.yml` is read, never converted behind the human's back.** Zensical reads
  `mkdocs.yml` natively and says it always will, so a target that has one still builds and nothing
  is urgent. What silently stopped working there is its whole `plugins:` list, which is why any
  `.pages` sidecar in the home no longer shapes anything. Report both facts, offer the conversion
  as its **own** confirmation item, and never stamp a second config beside a live one.
- **Report page-level drift; never fix it here.** A section with no `index.md`, a page with no
  frontmatter, an absolute `/.knowledge/<other-home>/…` link that cannot resolve in a site rooted at
  `documentation/` — each is **reported** with the command that closes it (`quenching-knowledge-align`,
  `quenching-knowledge-add`), never repaired by this skill. Writing and repairing pages belongs to the skills
  that own them; this one would be guessing.
- **The build is verification, not a deliverable.** `zensical build --strict` writes to the
  configured `site_dir`, which is gitignored — that is what `site-artifacts-tracked` guarantees.
  Where `site/` is **tracked**, overwriting it would be destructive: verify instead with a
  throwaway config written **at the repo root** (`-f`), its `site_dir` pointing outside the repo,
  and delete it after. The root is not optional — a Zensical config resolves its paths relative to
  the **config file**, so a config parked elsewhere makes `docs_dir` resolve outside the repo and
  the build exits `Error: Docs directory does not exist`. Never run `zensical serve`.
- **Never claim a build that did not run.** If the toolchain is absent, say so plainly, print the
  two commands (`pip install -r requirements.txt`, `zensical build --strict`), and report the run
  as *unverified*.
- **The shell grant is deliberate.** `Bash` is unrestricted because this command runs the target
  repository's own toolchain (`zensical`, `python -m zensical`, `uv`, and package installation),
  which cannot be enumerated by the plugin; the body records the reason and keeps the built site
  out of git.
- **Plan first, execute on one confirmation.** One read-only inventory → ONE table of findings
  and fixes → one OK → apply → verify. The `docs_dir` item, the legacy-config conversion and the
  opt-in CI workflow each gate on their own.

## Findings (`site-*`) — what is FIXED and what is REPORTED

| Code | Meaning | Disposition |
| --- | --- | --- |
| `site-config-absent` | no `zensical.toml` (and no `mkdocs.yml`) at the repo root | **FIX** — stamp `zensical.toml.tmpl` |
| `site-config-placeholder` | `<YOUR PROJECT>` / `<one-line …>` still unfilled | **FIX** — derive from the repo name + `README.md` H1/tagline; ask if neither yields one |
| `site-url-absent` | a public-delivery target has no non-placeholder `site_url` | **REPORT** — source it from the approved destination; never invent an URL |
| `site-repo-url-absent` | no `repo_url` and Git remote provides a usable repository URL | **FIX** — add the derived value without replacing a human value |
| `site-edit-uri-absent` | a mapped host needs an edit URL Zensical cannot derive | **FIX** — add its tested template, preserving a human value |
| `site-config-legacy` | a root `mkdocs.yml` and no `zensical.toml` | **REPORT** — it still builds, but every MkDocs plugin in it is inert; converting is its **own confirmation** |
| `site-docs-dir-mismatch` | `docs_dir` does not point at the `documentation/` home | **FIX, own confirmation** — a hidden bundle root is not a supported substitute |
| `site-publication-map-absent` | the accepted plan has no Mapa editorial de publicação | **REPORT** → `quenching-knowledge-documentation-plan` |
| `site-publication-route-missing` | a `publicar`/`publicar derivado` row has no corresponding route below `documentation/` | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-publication-leak` | a `não publicar` home appears in nav, a route or an internal link | **FIX** only in config/nav; otherwise **REPORT** → page author |
| `site-glossary-route-missing` | the map exposes the glossary but `reference/glossary.md` is absent | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-glossary-projection-stale` | glossary entries cannot be projected to abbreviation definitions | **FIX** the generated site-layer snippet; never rewrite the source glossary |
| `site-catalog-index-missing` | a mapped catalog has no derived layer/schema index | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-catalog-lineage-missing` | a catalog detail omits its stable identifier or source lineage | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-nav-absent` | the config declares no `nav` while the home has sections to order | **FIX** — write the list from the folder tree |
| `site-nav-stale` | the `nav` names an entry that does not exist, or omits a page the home has | **FIX** — regenerate the list, keep every human title |
| `site-feature-absent` | `navigation.indexes` missing while sections use `index.md` as landing page | **FIX** — add to `theme.features` |
| `site-extension-absent` | a page uses a component syntax whose Markdown extension or Mermaid fence is absent | **FIX** — add the extension in the site layer |
| `site-extra-css-absent` | pages use `.q-badge`/`.q-hero`/card styling but `extra_css` or the CSS asset is absent | **FIX** — stamp the CSS and connect `extra_css` |
| `site-requirements-absent` | the pin is in no requirements file | **FIX** — write or merge |
| `site-pages-orphan` | a `.pages` file left inside the home by an older install | **FIX** — remove it; nothing reads it any more |
| `site-artifacts-tracked` | `site/` not gitignored (or already tracked) | **FIX** the gitignore; a tracked build is **REPORTED** for the human to remove |
| `site-scratch-tracked` | `.quenching/` not gitignored — the family's plan-of-record would land in the human's next commit | **FIX** the gitignore; an already-tracked plan is **REPORTED** for the human to remove |
| `site-section-no-index` | a section folder with no `index.md` (breaks `navigation.indexes` *and* the OKF listing rule) | **REPORT** → `quenching-knowledge-align` |
| `site-link-escapes` | a page links an exposed home by an internal bundle path instead of its mapped route | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-page-unstamped` | a page under `documentation/` with no `type: documentation` | **REPORT** → `quenching-knowledge-align` |
| `site-ci-absent` | no `.github/workflows/docs.yml` | **REPORT**; install only on request (own confirmation — platform-specific) |
| `site-build-failed` | `zensical build --strict` exits non-zero | **FIX** only what is site-layer; anything page-level is **REPORTED** |

## Workflow

### 1. Preflight — the bundle and the home
Confirm `/.knowledge/index.md` carries `okf_version`. **No bundle → stop** and offer
`quenching-knowledge-align` first; there is nothing to render. Bundle
but **no `documentation/` home** → stop and offer `quenching-knowledge-align`; never scaffold a home here.
**Done when:** the bundle and documentation home are confirmed, or the handoff is reported.

### 2. Inventory the site layer (read-only)
Collect, without writing anything:
- the accepted `.quenching/documentation/plan.md` and its **Mapa editorial de publicação**; reject
  a missing map as a planning finding, and use its routes as the only allowed cross-home surface.
- root `/.knowledge/glossary.md`, its mapped `reference/glossary.md` route and the generated
  `assets/glossary-abbreviations.md` when the map exposes the glossary.
- root `zensical.toml` — parse it: `docs_dir`, `site_name`, `site_description`, `nav`,
  `site_url`, `repo_url`, `edit_uri_template`, theme language/identity, `theme.features`,
  `markdown_extensions`, `extra_css`; note every key a human added. Also read `git remote get-url
  origin` and the selected delivery destination when the plan records one. A root
  `mkdocs.yml`/`mkdocs.yaml` is inventoried the same way and is `site-config-legacy`.
- any requirements file pinning the docs toolchain (`requirements.txt`, one under `/.knowledge/`,
  `pyproject.toml`, `uv.lock` …) — the pin may already live somewhere else.
- every folder under `/.knowledge/documentation/**` with its `index.md` and its pages, including
  curated mirrors for mapped homes, plus any leftover `.pages`.
- `.gitignore` (are `site/` and `.quenching/` ignored?) and `git ls-files site .quenching` (is either already tracked?).
- `.github/workflows/docs.yml`.
- `assets/stylesheets/quenching.css` under the documentation home and the `extra_css` connection.
- the toolchain: `zensical --version` (fall back to `python -m zensical --version`,
  `uv run zensical --version`) — absence is a fact to report, not an error to fix. If `$ARGUMENTS`
  names a section, restrict drift comparison and nav regeneration to that section while still
  checking root config; if it names a config path, use that file. **Done when:** the site-layer
  inventory and focus are fixed.

### 3. Detect drift
Walk the `site-*` table above over the inventory. Compare every map row with the real routes: an
exposed row needs a route below `documentation/`; a `não publicar` row must be absent from nav and
published links. For `site-link-escapes`, grep for bundle paths that should instead target a mapped
route. For `site-nav-stale`, compare the config's `nav` against the allowed tree. Record the **evidence** for every finding —
a file:line or the parsed key — never a suspicion. **Done when:** every site finding has evidence
and a disposition.

For a mapped catalog, additionally parse `reference/catalog/index.md` and count its detail links.
Every linked detail must expose `id`, `layer`, `schema` and `lineage`; report the expected versus
actual route count in the build result. The index alone enters `nav`, so item growth does not require
configuration churn.

### 4. Derive the values you will write
`site_name` from the repo (directory name, `package.json` `name`, or the root `README.md` H1) and
`site_description` from the README's tagline; if neither yields a usable line, **ask** — never
ship a placeholder as if it were filled. For publication metadata, apply this precedence: existing
non-placeholder config → target-owned contract/delivery record → usable Git remote (`repo_url`
only) → explicit gap. Never overwrite the first case, never derive `site_url` from a Git URL, and
only write an Azure `edit_uri_template` after proving its branch/path syntax against the fixture.
A section's nav title comes from its `index.md`
H1, stripped of backticks and the trailing `— …` gloss (`` # `how-to/` — task recipes`` →
`How-to guides`, matching the shipped skeleton). **Done when:** every writable value has a source or
an explicit question.

### 5. Present ONE plan → gate on one OK
One table: `finding → fix or report → file`, including every editorial-map row and its route. Show, in full, the **diff** of every edit to a file
a human has customized. `site-docs-dir-mismatch`, the `site-config-legacy` conversion and the
opt-in CI workflow are **separate** confirmation items. If the plan is empty, say so and go
straight to step 7's verification. **Done when:** one plan and all separate confirmations are presented.

### 6. Apply
In order: `zensical.toml` (stamp from `../../assets/zensical/zensical.toml.tmpl` when
absent, else merge the missing keys and only the map-approved nav entries) → requirements →
the generated glossary-abbreviation snippet when mapped → `assets/stylesheets/quenching.css` from the payload → any orphan `.pages` → `.gitignore` → the CI
workflow **only if** its own OK was given (copy `ci-github-pages.yml` → `.github/workflows/docs.yml`).
The CSS asset is the one file this skill writes inside the docs home; Markdown pages remain
untouched. **Done when:** only approved site-layer edits are applied and `extra_css` points at the
stamped CSS.

### 7. Verify with a real build and rendered QA
If the toolchain is present, run `zensical build --clean --strict` and then run
`python3 ../../checks/documentation-site-check.py <site_dir>`. A non-zero
checker result is a structural finding: `site-asset-missing`, `site-anchor-missing`,
`site-sitemap-empty`, `site-page-orphan` or `site-remote-resource`, each reported with its path.
Read the Zensical output: every
warning is either a site-layer finding you fix now (a nav entry, a feature, an extension) or a
page-level one you **report**. Where `site/` is tracked, run it against the throwaway root config
instead (Doctrine), and delete that config afterwards. Inspect the rendered HTML for the title,
`class="mermaid"`, `class="q-badge"`, the connected CSS and the `prefers-reduced-motion` guard. If
no browser is available, use the static checks in `knowledge-documentation/validation.md` and state
that pixel-level dark/light/mobile QA was not run. If the toolchain is absent, report `unverified`
and print the two commands. Never run `zensical serve`; never commit a built site. **Done when:**
the build and rendered QA are real or explicitly unverified/static-only. Where the glossary is
mapped, also assert that the route exists and a known term renders as `<abbr>`.

### 8. Report
Report: findings **fixed** / **reported** (each with its command), whether the build ran
and its result. **Done when:** every fixed/reported finding, build status, and result is named.

## Invariants to never violate

- Never write, rewrite, move, delete, or stamp a `documentation/` page — the site layer **only**
  (the CSS asset, an orphan nav sidecar, and the root config files). Page-level drift is reported to
  `quenching-knowledge-documentation-write`, never repaired here.
- Never clobber a customized `zensical.toml` or requirements file; add only missing required keys,
  always shown as a diff, and never reorder or drop a key you did not add.
- Never convert a legacy `mkdocs.yml` without its own confirmation, and never leave two configs at
  the root.
- Never re-aim `docs_dir` to the bundle root. Never expose a home without an accepted map row, or
  expose a `não publicar` row; creating its Markdown route belongs to the page-owning stage.
- Never put generator-specific syntax or generator frontmatter into an OKF page — the markdown stays
  generator-neutral.
- Never run `zensical serve` and never commit the built `site/`.
- Never report a site as building when no build ran — an unverified run says `unverified`.
- Never scaffold the bundle, the `documentation/` home, or a missing `index.md` here → `quenching-knowledge-align`.
