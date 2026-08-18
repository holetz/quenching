---
name: quenching-knowledge-documentation-build
description: "Create or update the mkdocs-material site over the /.knowledge/documentation home. Triggers on \"build the docs site\", \"generate the mkdocs site for /.knowledge/documentation\", \"fix the documentation site's nav\". Not for: page-level content inside /.knowledge/ → quenching-knowledge-align."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/build.md -->


# quenching-knowledge-documentation-build — create/update the `documentation/` site

**Input**: `$ARGUMENTS` (optionally a `documentation/` section to focus the nav check on, or the path of an existing `mkdocs.yml`; omit to inventory the whole site layer).

Makes the OKF bundle's [`documentation/`](../../knowledge/documentation/index.md) home
**render as a site**, and keeps that rendering honest as the home grows. The home is a plain
Markdown tree; everything generator-specific lives in a thin **site layer** around it — the
`mkdocs.yml` + `requirements.txt` at the repo **root** (outside the bundle) and one `.pages`
nav file per section (inside it). This skill owns that layer end to end: it installs it when
absent, merges it forward when present, regenerates the nav after pages come and go, and
verifies the site actually builds. The payload it stamps from is
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
  concept doc to make the site look better.
- **The site is rooted at `documentation/`, not at the bundle.** `docs_dir: .knowledge/documentation`.
  The other homes (`standards/`, `concepts/`, `catalog/`, …) are the team's internal surface and
  are **not published** by this skill. A repo that wants the whole bundle online is a deliberate
  human decision, and re-aiming `docs_dir` is its **own** confirmation item (step 5) — it can
  break an already-published site and any CI pinned to it.
- **MERGE, never clobber.** A `mkdocs.yml` a human has customized is authoritative: add only the
  **missing required keys** (`docs_dir`, `navigation.indexes`, the `awesome-pages` plugin), show
  the edit as a diff, and never remove or reorder a key you did not add. Same for
  `requirements.txt` — merge the two lines into whatever file already pins the docs toolchain.
- **`.pages` is derived; its `title:` is human.** Regenerate the `nav:` list from the folder
  tree, always ending it with `- ...` so a page added tomorrow appears without another edit.
  A `title:` a human wrote survives untouched; a missing one is derived from the section's
  `index.md` H1.
- **Report page-level drift; never fix it here.** A section with no `index.md`, a page with no
  frontmatter, an absolute `/.knowledge/<other-home>/…` link that cannot resolve in a site rooted at
  `documentation/` — each is **reported** with the command that closes it (`quenching-knowledge-align`,
  `quenching-knowledge-add`), never repaired by this skill. Writing and repairing pages belongs to the skills
  that own them; this one would be guessing.
- **The build is verification, not a deliverable.** `mkdocs build --strict` runs into a throwaway
  `--site-dir` to prove the layer is coherent; the built site is never committed. Never run
  `mkdocs serve` — it blocks forever; hand the command to the human.
- **Never claim a build that did not run.** If the toolchain is absent, say so plainly, print the
  two commands (`pip install -r requirements.txt`, `mkdocs build --strict`), and report the run
  as *unverified* — an install without a build is an honest half, a fabricated "site builds" is
  a lie.
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
| `site-requirements-absent` | the two pins are in no requirements file | **FIX** — write or merge |
| `site-pages-absent` | a folder under `documentation/` with no `.pages` | **FIX** — write one (title from its `index.md` H1) |
| `site-nav-stale` | a `.pages` `nav:` names a missing entry, or omits a section **and** has no `- ...` | **FIX** — regenerate the list, keep the human `title:` |
| `site-artifacts-tracked` | `site/` not gitignored (or already tracked) | **FIX** the gitignore; a tracked build is **REPORTED** for the human to remove |
| `site-section-no-index` | a section folder with no `index.md` (breaks `navigation.indexes` *and* the OKF listing rule) | **REPORT** → `quenching-knowledge-align` |
| `site-link-escapes` | a `documentation/` page links `/.knowledge/<other-home>/…` — dead in the built HTML | **REPORT** → `quenching-knowledge-add` / the page's author |
| `site-page-unstamped` | a page under `documentation/` with no `type: documentation` | **REPORT** → `quenching-knowledge-align` |
| `site-ci-absent` | no `.github/workflows/docs.yml` | **REPORT**; install only on request (own confirmation — platform-specific) |
| `site-build-failed` | `mkdocs build --strict` exits non-zero | **FIX** only what is site-layer; anything page-level is **REPORTED** |

**Why `Bash` is unrestricted here.** This command drives an external toolchain the plugin does
not own — `mkdocs build --strict` is the verification, and the environment reaching it may be
`pip`, `uv`, or a bare `python -m`. A prefix grant would have to enumerate every installer a
target might use, and would fail closed on the one it did not. Its read-only siblings are scoped
to `python3`/`py`.

## Workflow

### 1. Preflight — the bundle and the home
Confirm `/.knowledge/index.md` carries `okf_version`. **No bundle → stop** and offer
`quenching-knowledge-align` first; there is nothing to render. Bundle
but **no `documentation/` home** → stop and offer `quenching-knowledge-align` (the skeleton ships the home,
its four Diátaxis sections, and their `.pages`); never scaffold a home here.

### 2. Inventory the site layer (read-only)
Collect, without writing anything:
- root `mkdocs.yml` / `mkdocs.yaml` — parse it: `docs_dir`, `site_name`, `site_description`,
  `theme.features`, `plugins`, `markdown_extensions`; note every key a human added.
- any requirements file pinning the docs toolchain (`requirements.txt`, one under `/.knowledge/`,
  `pyproject.toml`, `uv.lock` …) — the pins may already live somewhere else.
- every folder under `/.knowledge/documentation/**` with its `.pages`, its `index.md`, and its pages.
- `.gitignore` (is `site/` ignored?) and `git ls-files site` (is a build already tracked?).
- `.github/workflows/docs.yml`.
- the toolchain: `mkdocs --version` (fall back to `python -m mkdocs --version`,
  `uv run mkdocs --version`) — absence is a fact to report, not an error to fix.

### 3. Detect drift
Walk the `site-*` table above over the inventory. For `site-link-escapes`, `Grep` the home for
`](/.knowledge/` and keep only targets **outside** `documentation/`. For `site-nav-stale`, compare each
`.pages` `nav:` against the folder's real entries. Record the **evidence** for every finding —
a file:line or the parsed key — never a suspicion.

### 4. Derive the values you will write
`site_name` from the repo (directory name, `package.json` `name`, or the root `README.md` H1) and
`site_description` from the README's tagline; if neither yields a usable line, **ask** — never
ship a placeholder as if it were filled. A `.pages` `title:` comes from the section's `index.md`
H1, stripped of backticks and the trailing `— …` gloss (`` # `how-to/` — task recipes`` →
`How-to guides`, matching the shipped skeleton).

### 5. Present ONE plan → gate on one OK
One table: `finding → fix or report → file`. Show, in full, the **diff** of every edit to a file
a human has customized. `site-docs-dir-mismatch` and the opt-in CI workflow are **separate**
confirmation items. If the plan is empty, say so — "the site layer is already conformant" is a
complete, valid outcome — and go straight to step 7's verification.

### 6. Apply
In order: `mkdocs.yml` (stamp from `../../assets/mkdocs/mkdocs.yml.tmpl` when
absent, else merge the missing keys) → requirements → the `.pages` files → `.gitignore` → the CI
workflow **only if** its own OK was given (copy `ci-github-pages.yml` → `.github/workflows/docs.yml`).
Nothing under `/.knowledge/documentation/**` other than `.pages` is touched.

### 7. Verify with a real build
If the toolchain is present, run
`mkdocs build --strict --site-dir <throwaway-dir-outside-the-repo>` and read the output: every
warning is either a site-layer finding you fix now (a nav entry, a plugin, a feature) or a
page-level one you **report**. If it is absent, report `unverified` and print the exact two
commands. Never run `mkdocs serve`; never commit a built site.

### 8. Report
Report: findings **fixed** / **reported** (each with its command), whether the build ran
and its result, and the two commands the human uses next (`pip install -r requirements.txt`,
`mkdocs serve`).

## Invariants to never violate

- Never write, rewrite, move, delete, or stamp a `documentation/` page — the site layer **only**
  (`.pages`, and the root config files). Page-level drift is reported, never repaired here.
- Never clobber a customized `mkdocs.yml` or requirements file; add only missing required keys,
  always shown as a diff, and never reorder or drop a key you did not add.
- Never re-aim `docs_dir`, and never publish a home other than `documentation/`, without that
  item's **own** confirmation.
- Never put mkdocs-specific syntax or generator frontmatter into an OKF page — the markdown stays
  generator-neutral.
- Never give a `.pages` file OKF frontmatter, and never list it in an `index.md` — it is nav
  metadata, not a concept doc.
- Never run `mkdocs serve` (it blocks) and never commit the built `site/`.
- Never report a site as building when no build ran — an unverified run says `unverified`.
- Never scaffold the bundle, the `documentation/` home, or a missing `index.md` here → `quenching-knowledge-align`.
