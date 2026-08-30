---
name: quenching-knowledge-documentation-build
description: "Create or update the Zensical site layer from a confirmed editorial publication map, including extensions, CSS and strict-build QA. Triggers on \"build the docs site\", \"generate the site for /docs\", or \"fix the documentation site's nav\". Not for: planning pages → quenching-knowledge-documentation-plan; writing documentation prose → quenching-knowledge-documentation-write; reviewing page quality → quenching-knowledge-documentation-review; conducting the complete pipeline → quenching-knowledge-documentation-produce."
---

<!-- GENERATED FROM plugins/quenching/commands/knowledge/documentation/build.md -->


# quenching-knowledge-documentation-build — create/update the editorially mapped site

**Input**: `$ARGUMENTS` (optionally a bundle home to focus the nav check on, or the path of an existing `zensical.toml`; omit to inventory the whole site layer).

Makes the OKF bundle [`/docs/`](../../knowledge/index.md) feed a bounded
**Zensical site** and keeps that rendering honest as it grows. The whole bundle remains the
knowledge source; `site-source/` is the generated publication input. The home is a plain
Markdown tree; everything generator-specific lives in a thin **site layer** around it — the
`zensical.toml` plus exactly one dependency source at the repo **root**, outside the bundle. This
skill owns that layer end to end: it installs it when absent, merges it forward when present,
resolves the existing Python toolchain, keeps the `nav` in step with the folder tree, stamps the
static `assets/stylesheets/quenching.css` asset, and verifies the site actually builds. The payload it stamps from is
[`../../assets/zensical/`](../../assets/zensical/README.md); the home's own
boundaries and the `documentation` type live with `quenching-knowledge-align`
([knowledge-align/taxonomy.md](../../references/knowledge-align/taxonomy.md)) and
`quenching-knowledge-add` ([knowledge-add/homes.md](../../references/knowledge-add/homes.md)).

`quenching-knowledge-align` step 7 offers the **first** install of this layer as part of scaffolding the
bundle; every install, update, and re-verification after that is **this** skill.

## Doctrine

- **The site layer is not the bundle.** Config lives at the repo root, *outside* `/docs/`;
  inside it, this skill owns exactly one file — the CSS asset. The OKF markdown stays
  **generator-neutral** — never add generator-specific syntax, a nav entry inside a page, or
  generator frontmatter to a concept doc.
- **The confirmed Mapa editorial de publicação is the publication boundary.** Zensical 0.0.57
  builds every Markdown below `docs_dir` and does not support `exclude_docs`, `draft_docs` or
  `not_in_nav`. Therefore `docs_dir = "site-source"` and the command stages only the shared
  publication allow-list with `cq knowledge site-source docs site-source --write`; it never points
  at the complete bundle. Raw `catalog/` and `external/` homes are excluded from that tree even
  when they remain useful knowledge sources. A home marked `publicar` or `publicar derivado` is
  exposed only when its content is in the allow-list or is curated into an allowlisted page;
  `não publicar` creates no nav entry, staged file or published link. The map, not a home's name,
  decides editorial intent, while the staging boundary enforces the generator's file semantics.
  A missing or stale derived route is reported to the planning or writing stage; this site-layer
  command never invents or rewrites Markdown.
- **The nav is GENERATED, not maintained.** Zensical runs no plugins, so nothing derives the
  sidebar from a sidecar file: without `nav`, it falls back to the folder tree — alphabetical,
  which is not a Diátaxis reading order. `cq knowledge nav --write` generates the allowlisted list
  from the bundle in reading order and is idempotent to the byte, so `--check` is a diff rather than an
  opinion. A **title a human wrote survives regeneration untouched**; a missing one is derived
  from the section's `index.md` H1.
- **MERGE, never clobber.** A `zensical.toml` a human has customized is authoritative: add only the
  **missing required keys** (`docs_dir`, `navigation.indexes`, the nav entry), show the edit as a
  diff, and never remove or reorder a key you did not add. Preserve the target's dependency
  manager too: a `pyproject.toml`/`uv.lock` pair is authoritative over `requirements.txt`, and a
  target with no `pyproject.toml` receives the payload's pinned `requirements.txt`. Never create a
  second dependency source just because the payload has one.
- **Publication metadata has ordered evidence.** Existing non-placeholder config wins. Otherwise,
  derive `repo_url` from `git remote get-url origin`; derive `edit_uri_template` only for a host
  whose URL shape is known and testable (Azure DevOps uses `?path=/{path}&version=GB<branch>`).
  `site_url` comes only from the selected delivery destination. Language and identity come only
  from a target contract or owned asset. Missing evidence is a finding, never a public placeholder.
- **Glossary projection has one source.** When the accepted map exposes the glossary, derive the
  site-layer abbreviation snippet from root `glossary.md`, then stage both into `site-source/`.
  The glossary publishes as `glossary.md` in that bounded tree. `cq knowledge project --check` and
  `cq knowledge site-source --check` prove the projection and staging; the rendered checker proves
  a known `<abbr>`. Never
  ask an author to edit the derived snippet or a duplicate term list. A non-empty canonical glossary is required by default;
  only an accepted `não publicar` map row can exclude it.
- **The whole bundle is the knowledge inventory, not the generator input.** Inventory every `docs` home —
  `tutorials/`, `how-to/`, `explanation/`, `project/`, `standards/`, `concepts/`, `external/`,
  `catalog/`, `vision/` and the root glossary — and compare coverage **document by document** in the
  staged tree. Raw `catalog/` and `external/` files are explicitly excluded from this Zensical
  denominator; they remain inventoried as knowledge. Coverage is not the number of pages the plan
  happened to select, and it is not a per-home tick.
- **Catalogues are outside this Zensical site.** Keep raw `catalog/` files out of `site-source/`
  and `nav`. If their information is needed by readers, curate only the approved facts into an
  allowlisted reader-facing page with source lineage; do not flatten the catalogue into routes.
- **Delivery payloads are opt-in and host-specific.** Detect an Azure DevOps remote from its URL,
  offer `azure-pipelines-docs.yml` as a separate confirmation, and preserve any existing pipeline.
  The payload only publishes the strict `site/` directory as `documentation-site`; it is not a
  remote deployment.
- **Capability register is the allow-list.** Read the accepted plan's capability register before
  changing `zensical.toml` or requirements. For each `enabled` row, prove its prerequisite and merge
  only its missing keys/dependency; `disabled` rows produce no configuration or install action.
- **A legacy `mkdocs.yml` is read, never converted behind the human's back.** Zensical reads
  `mkdocs.yml` natively and says it always will, so a target that has one still builds and nothing
  is urgent. What silently stopped working there is its whole `plugins:` list, which is why any
  `.pages` sidecar in the home no longer shapes anything. Report both facts, offer the conversion
  as its **own** confirmation item, and never stamp a second config beside a live one.
- **Report page-level drift; never fix it here.** A section with no `index.md`, a page with no
  frontmatter, an absolute `/docs/<other-home>/…` link that cannot resolve in a site rooted at
  another home — each is **reported** with the command that closes it (`quenching-knowledge-align`,
  `quenching-knowledge-add`), never repaired by this skill. Writing and repairing pages belongs to the skills
  that own them; this one would be guessing.
- **The build is verification, not a deliverable.** `zensical build --strict` reads the generated
  bounded `site-source/` input and writes to the configured `site_dir`, which is gitignored — that
  is what `site-source-tracked` and `site-artifacts-tracked` guarantee. The `.quenching/` working
  state is gitignored as well, under `site-scratch-tracked`.
  Where `site/` is **tracked**, overwriting it would be destructive: verify instead with a
  throwaway config written **at the repo root** (`-f`), its `site_dir` a gitignored path **inside**
  the repo, and delete both after. Neither end is optional: a Zensical config resolves its paths
  relative to the **config file**, so a config parked elsewhere makes `docs_dir` resolve outside the
  repo and the build exits `Error: Docs directory does not exist`; and a `site_dir` outside the
  project root aborts with `Error: site_dir must be within project root`, which `build` has no
  `--site-dir` to override. Never run `zensical serve`.
- **Never claim a build that did not run.** If the toolchain is absent, say so plainly, print the
  selected install/build pair (`uv sync` + `uv run zensical build --clean --strict`, or
  `pip install -r requirements.txt` + `zensical build --clean --strict`), and report the run as
  *unverified*. When a `pyproject.toml` exists but `uv` is unavailable, do not install a parallel
  `requirements.txt` as a workaround.

**Why `Bash` is unrestricted here.** `Bash` is unrestricted because this command runs the target
repository's own toolchain (`zensical`, `python -m zensical`, `uv`, and package installation),
which cannot be enumerated by the plugin; the body records the reason and keeps the built site out
of git.
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
| `site-docs-dir-mismatch` | `docs_dir` does not point at generated `site-source/` | **FIX, own confirmation** — pointing at the bundle would process excluded homes |
| `site-source-missing` | generated bounded source tree is absent | **FIX** — run `cq knowledge site-source docs site-source --write` |
| `site-source-stale` | generated source manifest differs from the allowlisted bundle files | **FIX** — restage with `cq knowledge site-source docs site-source --write` |
| `site-publication-map-absent` | the accepted plan has no Mapa editorial de publicação | **REPORT** → `quenching-knowledge-documentation-plan` |
| `site-publication-route-missing` | a `publicar`/`publicar derivado` row has no corresponding built page | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-publication-leak` | a `não publicar` home appears in nav, a route or an internal link | **FIX** only in config/nav; otherwise **REPORT** → page author |
| `site-glossary-projection-stale` | route/snippet origin or source hash differs from the canonical glossary | **FIX** with `cq knowledge project --write`; never rewrite the source glossary |
| `site-glossary-snippet-missing` | the accepted glossary projection has no generated abbreviation snippet | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-glossary-term-unrendered` | a known canonical term is not present as rendered `<abbr>` | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-coverage-incomplete` | a publishable document has no built, non-empty page and no explicit `não publicar` row of its own | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-skeleton-stub` | a mandatory route's page is byte-identical to the shipped skeleton's section descriptor, or carries only that descriptor's boilerplate | **REPORT** → `quenching-knowledge-documentation-write`; the route is not coverage |
| `site-catalog-index-missing` | a catalog is incorrectly proposed as a Zensical route | **REPORT** → revise the map; keep raw catalog outside `site-source/` |
| `site-catalog-lineage-missing` | a catalog fact is being curated without stable source lineage | **REPORT** → `quenching-knowledge-documentation-write`; do not stage raw detail |
| `site-nav-absent` | the config declares no `nav` while the home has sections to order | **FIX** — write the list from the folder tree |
| `site-nav-stale` | the `nav` names an entry that does not exist, or omits a page the home has | **FIX** — regenerate the list, keep every human title |
| `site-feature-absent` | `navigation.indexes` missing while sections use `index.md` as landing page | **FIX** — add to `theme.features` |
| `site-extension-absent` | a page uses a component syntax whose Markdown extension or Mermaid fence is absent | **FIX** — add the extension in the site layer |
| `site-extra-css-absent` | pages use `.q-badge`/`.q-hero`/card styling but `extra_css` or the CSS asset is absent | **FIX** — stamp the CSS and connect `extra_css` |
| `site-requirements-absent` | no supported pin exists in `pyproject.toml`/`uv.lock` or `requirements.txt` | **FIX** — write or merge exactly one source |
| `site-dependency-source-duplicate` | `zensical` is independently pinned in `pyproject.toml` and `requirements.txt` | **REPORT** the conflict; preserve the target's chosen source and remove only with its confirmation |
| `site-uv-lock-stale` | `uv.lock` does not resolve the current `pyproject.toml` | **FIX** — run `uv lock`, never hand-edit the lock |
| `site-uv-unavailable` | `pyproject.toml` is the selected source but `uv` cannot run | **REPORT** as *unverified*; never create a parallel requirements file |
| `site-pages-orphan` | a `.pages` file left inside the home by an older install | **FIX** — remove it; nothing reads it any more |
| `site-artifacts-tracked` | `site/` not gitignored (or already tracked) | **FIX** the gitignore; a tracked build is **REPORTED** for the human to remove |
| `site-scratch-tracked` | `.quenching/` not gitignored — the family's plan-of-record would land in the human's next commit | **FIX** the gitignore; an already-tracked plan is **REPORTED** for the human to remove |
| `site-source-tracked` | generated bounded `site-source/` is not gitignored (or is already tracked) | **FIX** the gitignore; an already-tracked generated source is **REPORTED** for the human to remove |
| `site-section-no-index` | a section folder with no `index.md` (breaks `navigation.indexes` *and* the OKF listing rule) | **REPORT** → `quenching-knowledge-align` |
| `site-link-escapes` | a page links an exposed home by an internal bundle path instead of its mapped route | **REPORT** → `quenching-knowledge-documentation-write` |
| `site-page-unstamped` | a page in a reader-facing quadrant with no `type` matching its home | **REPORT** → `quenching-knowledge-align` |
| `site-ci-absent` | no `.github/workflows/docs.yml` | **REPORT**; install only on request (own confirmation — platform-specific) |
| `site-azure-payload-available` | Azure DevOps remote has no documented opt-in pipeline payload | **OFFER** `azure-pipelines-docs.yml` under its own confirmation; never overwrite an existing pipeline |
| `site-capability-prerequisite-missing` | an enabled capability lacks its declared prerequisite or fixture | **REPORT** and leave it disabled; do not guess support |
| `site-build-failed` | `zensical build --strict` exits non-zero | **FIX** only what is site-layer; anything page-level is **REPORTED** |

## Workflow

### Toolchain resolution — one source, one runner

Resolve the dependency source before proposing any write. Apply this precedence and record the
selected branch in the plan:

| Evidence at the target root | Dependency action | Build runner |
| --- | --- | --- |
| `uv.lock` exists and `pyproject.toml` declares `zensical` | `uv sync --locked` (fail and report if the lock is stale) | `uv run zensical` |
| `pyproject.toml` has `[tool.uv]`, declares `zensical`, and has no lock | `uv lock` then `uv sync` | `uv run zensical` |
| uv project (`uv.lock` or `[tool.uv]`) does not declare `zensical` | one approved `uv add --dev "zensical>=0.0.57"`, then `uv lock` + `uv sync` | `uv run zensical` |
| `pyproject.toml` is owned by another manager and declares `zensical` | preserve its lock/install command; never copy requirements | that manager's run command |
| `pyproject.toml` has no recognized manager | report the manager gap; do not invent a lock or requirements file | target's documented runner |
| no `pyproject.toml`, `requirements.txt` declares `zensical` | use the existing requirements install | `zensical` or `python -m zensical` |
| neither file declares the tool | stamp/merge **one** `requirements.txt` (or ask to adopt uv) | selected runner after install |

Never choose a runner from `PATH` alone when a project-managed runner is available. A failed
`uv sync --locked` is a stale-lock finding, not permission to install from `requirements.txt`.
`uv add`/`uv lock` are writes and therefore appear in the single confirmation plan; probing with
`uv run zensical --version` is read-only and may happen during inventory.

### 1. Preflight — the bundle and the home
Confirm `/docs/index.md` carries `okf_version`. **No bundle → stop** and offer
`quenching-knowledge-align` first; there is nothing to render. Bundle
but **no reader-facing quadrant** (`tutorials/`, `how-to/`, `explanation/`, `project/`) → stop and
offer `quenching-knowledge-align`; never scaffold a home here.
**Done when:** the bundle and documentation home are confirmed, or the handoff is reported.

### 2. Inventory the site layer (read-only)
Collect, without writing anything:
- the accepted `.quenching/documentation/plan.md` and its **Mapa editorial de publicação**; reject
  a missing map as a planning finding, and use its routes as the only allowed cross-home surface.
- every source home and every `.md` source under `/docs/`; count the mandatory
  `publicar`/`publicar derivado` rows separately from intentional `não publicar` rows. If the
  root glossary exists and has content, treat it as mandatory unless the accepted map explicitly
  excludes it.
- root `/docs/glossary.md` and the generated `assets/glossary-abbreviations.txt`.
- root `zensical.toml` — parse it: `docs_dir`, `site_name`, `site_description`, `nav`,
  `site_url`, `repo_url`, `edit_uri_template`, theme language/identity, `theme.features`,
  `markdown_extensions`, `extra_css`; note every key a human added. Also read `git remote get-url
  origin` and the selected delivery destination when the plan records one. A root
  `mkdocs.yml`/`mkdocs.yaml` is inventoried the same way and is `site-config-legacy`.
- the dependency source and manager pinning the docs toolchain (`pyproject.toml` + `uv.lock`,
  `requirements.txt`, or another target-owned manifest); record which one wins and whether a
  duplicate source exists.
- every folder under `/docs/**` with its `index.md` and its pages, plus any leftover `.pages`.
- `.gitignore` (are `site/`, `.quenching/`, and `site-source/` ignored?) and `git ls-files site .quenching site-source` (is any generated path already tracked?).
- `.github/workflows/docs.yml`.
- Azure DevOps remotes (`dev.azure.com`, `visualstudio.com`) and any existing `azure-pipelines*.yml`;
  record whether the payload is absent, already installed, or declined.
- `assets/stylesheets/quenching.css` under the documentation home and the `extra_css` connection.
- the toolchain: `zensical --version` (fall back to `python -m zensical --version`,
  `uv run zensical --version`) — absence is a fact to report, not an error to fix. If `$ARGUMENTS`
  names a section, restrict drift comparison and nav regeneration to that section while still
  checking root config; if it names a config path, use that file. **Done when:** the site-layer
  inventory and focus are fixed.

- the generated `site-source/` tree and its manifest; compare it with
  `cq knowledge site-source docs site-source --check` before any build. The source inventory still
  lists `catalog/` and `external/`, but their raw files must not be copied into or counted as
  Zensical pages.

### 3. Detect drift
Read the capability register alongside the map. An enabled row must have a tested prerequisite,
configuration source and expected HTML effect; an unsupported row is a reported disabled decision.
Walk the `site-*` table above over the inventory. Compare every map row with the real routes: every
exposed row needs a non-empty built page; a `não publicar` row must be absent from nav and
published links. For `site-link-escapes`, grep for bundle paths that should instead target a mapped
route. For `site-coverage-incomplete`, the denominator is **every publishable `.md` in the staged
`site-source/` tree**, not raw `catalog/` or `external/` files, the map's rows or the pages assigned
in the plan. For `site-skeleton-stub`, diff each mandatory route against its
counterpart under `../../knowledge/` — an identical page, or
one whose only content is the home's own descriptor, proves the site was never written, exactly
the state a green strict build cannot see. For `site-nav-stale`, compare the config's `nav` against the allowed tree. Record the **evidence** for every finding —
a file:line or the parsed key — never a suspicion. **Done when:** every site finding has evidence
and a disposition.

For `catalog/` and `external/`, record the source count and confirm they are absent from
`site-source/` and `nav`; do not parse or render the raw detail set during a site build. If a
reader-facing page curates facts from either home, verify its source lineage in the page ledger.

Run `catalog-publication-check.py` only when the accepted publication map contains an approved
catalog route. When `catalog/` is intentionally outside the bounded site, classify that checker as
`not-applicable`, keep the raw files out of `site-source/` and `nav`, and do not create a fake
`reference/catalog/index.md` merely to satisfy it. The capability register is the same allow-list:
disabled rows do not add configuration, dependencies or checker arguments.

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
absent, else merge the missing keys and only the map-approved nav entries) → the selected dependency
source (`uv add --dev`/`uv lock`/`uv sync` for an identified uv project, otherwise preserve the
target manager or merge the pinned `requirements.txt`) → the generated glossary-abbreviation snippet when mapped →
`assets/stylesheets/quenching.css` from the payload → any orphan `.pages` → `.gitignore` → the CI
workflow **only if** its own OK was given (copy `ci-github-pages.yml` → `.github/workflows/docs.yml`).
For an Azure remote, the equivalent opt-in copies `azure-pipelines-docs.yml` only when its separate
confirmation is granted and the target path is absent; report `documentation-site` as an artifact,
not as deployed content.
The CSS asset is the one file this skill writes inside the docs home; Markdown pages remain
untouched. Finally run `cq knowledge site-source docs site-source --write` so Zensical receives
only the bounded publication tree. **Done when:** only approved site-layer edits are applied,
`docs_dir` is `site-source`, and the staged manifest is current.

### 7. Verify with a real build and rendered QA
Before the build, require `cq knowledge site-source docs site-source --check`; a missing or stale
manifest is `site-source-missing`/`site-source-stale` and must be fixed by staging. If the toolchain
is present, run the selected runner (`uv run zensical`, `python -m zensical`, or
the executable) with `build --clean --strict`. **Always, immediately after every build**, run
`python3 ../../checks/documentation-site-check.py <site_dir>`; this is
mandatory even when the strict build is green. A non-zero
checker result is a structural finding: `site-asset-missing`, `site-anchor-missing`,
`site-sitemap-empty`, `site-page-orphan` or `site-remote-resource`, each reported with its path.
When the map makes the glossary mandatory, run the same checker with
`--require-glossary --glossary-source docs/glossary.md
--glossary-snippet site-source/assets/glossary-abbreviations.txt --glossary-route glossary.md
--glossary-term <term explicitly evidenced by the accepted map>`; run
`cq knowledge project docs --check`, `cq knowledge nav docs --check` and
`cq knowledge site-source docs site-source --check` beside it. For a local-only build
whose config has no `site_url`, add `--local`; this accepts a relative or empty local sitemap but
still checks malformed XML and page/assets integrity. Never infer public delivery from a local run.
Read the Zensical output: every
warning is either a site-layer finding you fix now (a nav entry, a feature, an extension) or a
page-level one you **report**. Where `site/` is tracked, run it against the throwaway root config
instead (Doctrine), and delete that config afterwards. Inspect the rendered HTML for the title,
`class="mermaid"`, `class="q-badge"`, the connected CSS and the `prefers-reduced-motion` guard. If
no browser is available, use the static checks in `knowledge-documentation/validation.md` and state
that pixel-level dark/light/mobile QA was not run. If the toolchain is absent, report `unverified`
and print the two commands. Never run `zensical serve`; never commit a built site. **Done when:**
the build and rendered QA are real or explicitly unverified/static-only. Where the glossary is
mandatory, the projection check and rendered `<abbr>` check must both be green; otherwise the
pipeline fails rather than counting only the pages the plan selected.

The `--glossary-term` value is mandatory for this QA mode and must be a known term that the
published pages render as an abbreviation (for example `SCD2` when the source and map evidence
it). Never omit it and let the checker select the first lexical glossary entry: that proxy can be
unrenderable and would produce a false publication defect. If no compatible term is evidenced,
report the QA as a source gap instead of choosing one by position.

If the human separately confirms a local preview after the strict build, start a loopback-only,
ephemeral server from `site/`, report its URL and PID, and stop it when the preview window ends:

```bash
python3 -m http.server 0 --bind 127.0.0.1 --directory site & preview_pid=$!
echo "Preview: http://127.0.0.1:<allocated-port>/ (PID ${preview_pid})"
# after inspection:
kill "${preview_pid}"
```

Preview is never a substitute for strict build, never binds a public interface, and never survives
the run without an explicit stop report.

### 8. Report
Report: findings **fixed** / **reported** (each with its command), whether the build ran
and its result. **Done when:** every fixed/reported finding, build status, and result is named.

## Invariants to never violate

- Never write, rewrite, move, delete, or stamp a bundle page — the site layer **only**
  (the CSS asset, an orphan nav sidecar, and the root config files). Page-level drift is reported to
  `quenching-knowledge-documentation-write`, never repaired here.
- Never clobber a customized `zensical.toml` or requirements file; add only missing required keys,
  always shown as a diff, and never reorder or drop a key you did not add.
- Never convert a legacy `mkdocs.yml` without its own confirmation, and never leave two configs at
  the root.
- Never point `docs_dir` at the complete bundle or a dot-prefixed path. Zensical has no supported
  file exclusion setting, so raw `catalog/` and `external/` must be absent from `site-source/`, not
  merely absent from `nav`. Never expose a home without an accepted map row, or
  expose a `não publicar` row; creating its Markdown route belongs to the page-owning stage.
- Never put generator-specific syntax or generator frontmatter into an OKF page — the markdown stays
  generator-neutral.
- Never run `zensical serve` and never commit the built `site/`.
- Never report a site as building when no build ran — an unverified run says `unverified`.
- Never scaffold the bundle, a home, or a missing `index.md` here → `quenching-knowledge-align`.
