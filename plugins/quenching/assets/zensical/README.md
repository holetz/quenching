# `assets/zensical/` — the site setup payload (Zensical)

Inert here, like the rest of `assets/`. `/quenching:knowledge:align` (Step 7) stamps these into a target
repo **once**, while scaffolding the bundle, so the editorially mapped `documentation/` tree renders as a site;
`/quenching:knowledge:documentation:build` **owns** the layer after that — it installs, merges forward,
keeps the `nav` in step with the folder tree, and verifies the build. **The OKF
markdown stays generator-neutral; only this config layer names a generator.**

| File | Stamped to | Notes |
| --- | --- | --- |
| `zensical.toml.tmpl` | repo root `zensical.toml` | only if absent; fill `site_name`/`site_description`; keep `docs_dir = ".knowledge/documentation"` and add only map-approved routes |
| `requirements.txt` | repo root | `zensical` |
| `quenching.css` | the `documentation/` home, at `assets/stylesheets/quenching.css` | static CSS for badges, hero, cards and reduced-motion guard; `extra_css` in `zensical.toml` wires it |
| `ci-github-pages.yml` | `.github/workflows/docs.yml` | opt-in; GitHub Pages via the Pages artifact — the repo's Pages source must be "GitHub Actions" |
| `azure-pipelines-docs.yml` | `azure-pipelines-docs.yml` | opt-in; Azure DevOps publishes the strict `site/` output as `documentation-site` |

**The nav lives in the config.** Zensical runs no plugins, so nothing derives the sidebar from a
sidecar file: the `nav` list in `zensical.toml` carries the order and the section titles, and a new
page is a new line in it.

## Publication and identity contract

`site_url` is required before a site is delivered publicly: derive it from the approved destination
or leave it as an explicit configuration gap. `repo_url` comes from the target's Git remote when it
is a usable public/repository URL. Zensical does not derive Azure DevOps edit links, so an Azure
target uses a tested `edit_uri_template` such as `?path=/{path}&version=GB<branch>`; replace
`<branch>` with the target's actual branch.

Set `language`, palette colors, logo and favicon only from a target-owned language or brand
contract. The template deliberately comments these values rather than making a plausible-looking
placeholder public metadata.

The Azure template is deliberately opt-in. It installs the pinned toolchain, runs the strict build,
and publishes `documentation-site` as a pipeline artifact; it does not deploy to a remote host.
Treat the artifact as an immutable handoff, a local preview as a developer convenience, and a remote
deployment as a separate platform-owned stage with its own credentials and approval.

## Validate locally

```bash
pip install -r requirements.txt
zensical build --clean --strict
# fallbacks: python -m zensical build --clean --strict · uv run zensical build --clean --strict
```

The build command is the verification path; the documentation family reports `unverified` when
the toolchain is not installed. `zensical build` has no `--site-dir`: it writes to the configured
`site_dir` (gitignored), and `.cache/` beside the config ignores itself. Use `zensical serve` only
when a local preview is explicitly requested.

`index.md` in each section is the section landing page (`navigation.indexes`). The plan's **Mapa
editorial de publicação** decides whether another OKF home is published, published through a
curated mirror below `documentation/`, or absent. Links use that mapped route — never an internal
`/.knowledge/<home>/…` path. A `não publicar` home has no route or nav entry.

The glossary route is `reference/glossary.md`. When the plan maps it to publication, `build`
derives `assets/glossary-abbreviations.md` from the canonical root `glossary.md`; the template's
`abbr` and `pymdownx.snippets.auto_append` load those definitions on every page. The derived file
is generated site-layer data, never a second hand-maintained glossary.
