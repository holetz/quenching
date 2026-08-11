# `assets/mkdocs/` — the site setup payload (mkdocs-material)

Inert here, like the rest of `assets/`. `/quenching:knowledge:align` (Step 7) stamps these into a target
repo **once**, while scaffolding the bundle, so the `documentation/` home renders as a site;
`/quenching:knowledge:documentation:build` **owns** the layer after that — it installs, merges forward,
regenerates the `.pages` nav, and verifies the build. **The OKF
markdown stays generator-neutral; only this config layer is mkdocs-specific.**

| File | Stamped to | Notes |
| --- | --- | --- |
| `mkdocs.yml.tmpl` | repo root `mkdocs.yml` | only if absent; fill `site_name`/`site_description`; `docs_dir: .docs/documentation` |
| `requirements.txt` | repo root | `mkdocs-material` + `mkdocs-awesome-pages-plugin` |
| `ci-github-pages.yml` | `.github/workflows/docs.yml` | opt-in; GitHub Pages via `mkdocs gh-deploy` |

Nav needs no file here — the `.pages` files ship inside `assets/docs/documentation/**` and the
`awesome-pages` plugin builds the nav from the folder tree.

## Build locally

```bash
pip install -r requirements.txt
mkdocs serve      # live preview at http://127.0.0.1:8000
mkdocs build      # static site into ./site
```

`index.md` in each section is the section landing page (`navigation.indexes`). Absolute OKF
links (`/.docs/…`) to other homes will not resolve in a site rooted at `/.docs/documentation/` —
keep `documentation/` pages self-contained.
