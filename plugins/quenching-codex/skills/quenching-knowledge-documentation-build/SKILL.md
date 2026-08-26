---
name: quenching-knowledge-documentation-build
description: "Create or update the mkdocs-material site layer over the /.knowledge/documentation home, including extensions, CSS and strict-build QA. Triggers on \"build the docs site\", \"generate the mkdocs site for /.knowledge/documentation\", or \"fix the documentation site's nav\"."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/build.md -->


# quenching-knowledge-documentation-build — create/update the `documentation/` site

**Input**: `$ARGUMENTS` (optionally a `documentation/` section to focus the nav check on, or the path of an existing `mkdocs.yml`; omit to inventory the whole site layer).

Makes the OKF bundle's [`documentation/`](../../knowledge/documentation/index.md) home
**render as a site**, and keeps that rendering honest as the home grows. The home is a plain
Markdown tree; everything generator-specific lives in a thin **site layer** around it — the
`mkdocs.yml` + `requirements.txt` at the repo **root** (outside the bundle) and one `.pages`
nav file per section (inside it). This skill owns that layer end to end: it installs it when
absent, merges it forward when present, regenerates the nav after pages come and go, stamps the
static `assets/stylesheets/quenching.css` asset, and verifies the site actually builds. The payload it stamps from is
[`../../assets/mkdocs/`](../../assets/mkdocs/README.md); the home's own
boundaries and the `documentation` type live with `quenching-knowledge-align`
([knowledge-align/taxonomy.md](../../references/knowledge-align/taxonomy.md)) and
`quenching-knowledge-add` ([knowledge-add/homes.md](../../references/knowledge-add/homes.md)).

`quenching-knowledge-align` step 7 offers the **first** install of this layer as part of scaffolding the
bundle; every install, update, and re-verification after that is **this** skill.

## Doctrine

- **The site layer is not the bundle.** Config lives at the repo root, *outside* `/.knowledge/`; only
  the `.pages` files live inside, and they are nav metadata, not concept docs (never stamped,
  never indexed, never listed in an `index.md`). The OKF markdown stays **generator-neutral** —
  never add mkdocs-specific syntax, a `nav:` entry inside a page, or generator frontmatter to a
  concept doc.
- **The site is rooted at `documentation/`, not at the bundle.** `docs_dir: .knowledge/documentation`.
  The other homes (`standards/`, `concepts/`, `catalog/`, …) are the team's internal surface and
  are **not published** by this skill. A repo that wants the whole bundle online is a deliberate
  human decision, and re-aiming `docs_dir` is its **own** confirmation item (step 5) — it can
  break a published site.
- **MERGE, never clobber.** A `mkdocs.yml` a human has customized is authoritative: add only the
  **missing required keys** (`docs_dir`, `navigation.indexes`, the `awesome-pages` plugin), show
  the edit as a diff, and never remove or reorder a key you did not add. Same for
  `requirements.txt` — merge the two lines into whatever file already pins the docs toolchain.
- **`.pages` is derived; its `title:` is human.** Regenerate the `nav:` list from the folder
  tree, always ending it with `- ...`.
  A `title:` a human wrote survives untouched; a missing one is derived from the section's
  `index.md` H1.
- **Report page-level drift; never fix it here.** A section with no `index.md`, a page with no
  frontmatter, an absolute `/.knowledge/<other-home>/…` link that cannot resolve in a site rooted at
  `documentation/` — each is **reported** with the command that closes it (`quenching-knowledge-align`,
  `quenching-knowledge-add`), never repaired by this skill. Writing and repairing pages belongs to the skills
  that own them; this one would be guessing.
- **The build is verification, not a deliverable.** `mkdocs build --strict` runs into a throwaway
  `--site-dir`; the built site is never committed. Never run `mkdocs serve`.
- **Never claim a build that did not run.** If the toolchain is absent, say so plainly, print the
  two commands (`pip install -r requirements.txt`, `mkdocs build --strict`), and report the run
  as *unverified*.
- **The shell grant is deliberate.** `Bash` is unrestricted because this command runs the target
  repository's own MkDocs toolchain (`mkdocs`, `python -m mkdocs`, `uv`, and package installation),
  which cannot be enumerated by the plugin; the body records the reason and keeps builds throwaway.
- **Plan first, execute on one confirmation.** One read-only inventory → ONE table of findings
  and fixes → one OK → apply → verify. The `docs_dir` item and the opt-in CI workflow each gate
  on their own.

## Findings (`site-*`) — what is FIXED and what is REPORTED

| Code | Meaning | Disposition |
| --- | --- | --- |
| `site-config-absent` | no `mkdocs.yml` (or `.yaml`) at the repo root | **FIX** — stamp `mkdocs.yml.tmpl` |
| `site-config-placeholder` | `<YOUR PROJECT>` / `<one-line …>` still unfilled | **FIX** — derive from the repo name + `README.md` H1/tagline; ask if neither yields one |
| `site-docs-dir-mismatch` | `docs_dir` does not point at the `documentation/` home | **FIX, own confirmation** — never silently re-aim a live site |
| `site-plugin-absent` | `awesome-pages` (or `search`) missing while `.pages` files exist | **FIX** — add to `plugins:` |
| `site-feature-absent` | `navigation.indexes` missing while sections use `index.md` as landing page | **FIX** — add to `theme.features` |
| `site-extension-absent` | a page uses a component syntax whose Markdown extension or Mermaid fence is absent | **FIX** — add the extension in the site layer |
| `site-extra-css-absent` | pages use `.q-badge`/`.q-hero`/card styling but `extra_css` or the CSS asset is absent | **FIX** — stamp the CSS and connect `extra_css` |
| `site-requirements-absent` | the two pins are in no requirements file | **FIX** — write or merge |
| `site-pages-absent` | a folder under `documentation/` with no `.pages` | **FIX** — write one (title from its `index.md` H1) |
| `site-nav-stale` | a `.pages` `nav:` names a missing entry, or omits a section **and** has no `- ...` | **FIX** — regenerate the list, keep the human `title:` |
| `site-artifacts-tracked` | `site/` not gitignored (or already tracked) | **FIX** the gitignore; a tracked build is **REPORTED** for the human to remove |
| `site-scratch-tracked` | `.quenching/` not gitignored — the family's plan-of-record would land in the human's next commit | **FIX** the gitignore; an already-tracked plan is **REPORTED** for the human to remove |
| `site-section-no-index` | a section folder with no `index.md` (breaks `navigation.indexes` *and* the OKF listing rule) | **REPORT** → `quenching-knowledge-align` |
| `site-link-escapes` | a `documentation/` page links `/.knowledge/<other-home>/…` — dead in the built HTML | **REPORT** → `quenching-knowledge-add` / the page's author |
| `site-page-unstamped` | a page under `documentation/` with no `type: documentation` | **REPORT** → `quenching-knowledge-align` |
| `site-ci-absent` | no `.github/workflows/docs.yml` | **REPORT**; install only on request (own confirmation — platform-specific) |
| `site-build-failed` | `mkdocs build --strict` exits non-zero | **FIX** only what is site-layer; anything page-level is **REPORTED** |

## Workflow

### 1. Preflight — the bundle and the home
Confirm `/.knowledge/index.md` carries `okf_version`. **No bundle → stop** and offer
`quenching-knowledge-align` first; there is nothing to render. Bundle
but **no `documentation/` home** → stop and offer `quenching-knowledge-align`; never scaffold a home here.
**Done when:** the bundle and documentation home are confirmed, or the handoff is reported.

### 2. Inventory the site layer (read-only)
Collect, without writing anything:
- root `mkdocs.yml` / `mkdocs.yaml` — parse it: `docs_dir`, `site_name`, `site_description`,
  `theme.features`, `plugins`, `markdown_extensions`; note every key a human added.
- any requirements file pinning the docs toolchain (`requirements.txt`, one under `/.knowledge/`,
  `pyproject.toml`, `uv.lock` …) — the pins may already live somewhere else.
- every folder under `/.knowledge/documentation/**` with its `.pages`, its `index.md`, and its pages.
- `.gitignore` (are `site/` and `.quenching/` ignored?) and `git ls-files site .quenching` (is either already tracked?).
- `.github/workflows/docs.yml`.
- `assets/stylesheets/quenching.css` under the documentation home and the `extra_css` connection.
- the toolchain: `mkdocs --version` (fall back to `python -m mkdocs --version`,
  `uv run mkdocs --version`) — absence is a fact to report, not an error to fix. If `$ARGUMENTS`
  names a section, restrict drift comparison and nav regeneration to that section while still
  checking root config; if it names a config path, use that file. **Done when:** the site-layer
  inventory and focus are fixed.

### 3. Detect drift
Walk the `site-*` table above over the inventory. For `site-link-escapes`, `Grep` the home for
`](/.knowledge/` and keep only targets **outside** `documentation/`. For `site-nav-stale`, compare each
`.pages` `nav:` against the folder's real entries. Record the **evidence** for every finding —
a file:line or the parsed key — never a suspicion. **Done when:** every site finding has evidence
and a disposition.

### 4. Derive the values you will write
`site_name` from the repo (directory name, `package.json` `name`, or the root `README.md` H1) and
`site_description` from the README's tagline; if neither yields a usable line, **ask** — never
ship a placeholder as if it were filled. A `.pages` `title:` comes from the section's `index.md`
H1, stripped of backticks and the trailing `— …` gloss (`` # `how-to/` — task recipes`` →
`How-to guides`, matching the shipped skeleton). **Done when:** every writable value has a source or
an explicit question.

### 5. Present ONE plan → gate on one OK
One table: `finding → fix or report → file`. Show, in full, the **diff** of every edit to a file
a human has customized. `site-docs-dir-mismatch` and the opt-in CI workflow are **separate**
confirmation items. If the plan is empty, say so and go straight to step 7's verification.
**Done when:** one plan and all separate confirmations are presented.

### 6. Apply
In order: `mkdocs.yml` (stamp from `../../assets/mkdocs/mkdocs.yml.tmpl` when
absent, else merge the missing keys) → requirements → the `.pages` files →
`assets/stylesheets/quenching.css` from the payload → `.gitignore` → the CI workflow **only if**
its own OK was given (copy `ci-github-pages.yml` → `.github/workflows/docs.yml`). The CSS asset is
the one static exception inside the docs home; Markdown pages remain untouched. **Done when:**
only approved site-layer edits are applied and `extra_css` points at the stamped CSS.

### 7. Verify with a real build and rendered QA
If the toolchain is present, run
`mkdocs build --strict --site-dir <throwaway-dir-outside-the-repo>` and read the output: every
warning is either a site-layer finding you fix now (a nav entry, a plugin, a feature) or a
page-level one you **report**. Inspect the rendered HTML for the title, `class="mermaid"`,
`class="q-badge"`, the connected CSS and the `prefers-reduced-motion` guard. If no browser is
available, use the static checks in `knowledge-documentation/validation.md` and state that
pixel-level dark/light/mobile QA was not run. If the toolchain is absent, report `unverified`
and print the two commands. Never run `mkdocs serve`; never commit a built site. **Done when:**
the build and rendered QA are real or explicitly unverified/static-only.

### 8. Report
Report: findings **fixed** / **reported** (each with its command), whether the build ran
and its result. **Done when:** every fixed/reported finding, build status, and result is named.

## Invariants to never violate

- Never write, rewrite, move, delete, or stamp a `documentation/` page — the site layer **only**
  (`.pages`, the CSS asset, and the root config files). Page-level drift is reported to
  `quenching-knowledge-documentation-write`, never repaired here.
- Never clobber a customized `mkdocs.yml` or requirements file; add only missing required keys,
  always shown as a diff, and never reorder or drop a key you did not add.
- Never re-aim `docs_dir`, and never publish a home other than `documentation/`, without that
  item's **own** confirmation.
- Never put mkdocs-specific syntax or generator frontmatter into an OKF page — the markdown stays
  generator-neutral.
- Never give a `.pages` file OKF frontmatter, and never list it in an `index.md` — it is nav
  metadata, not a concept doc.
- Never run `mkdocs serve` and never commit the built `site/`.
- Never report a site as building when no build ran — an unverified run says `unverified`.
- Never scaffold the bundle, the `documentation/` home, or a missing `index.md` here → `quenching-knowledge-align`.
