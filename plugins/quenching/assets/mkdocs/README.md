# `assets/mkdocs/` — the site setup payload (mkdocs-material)

Inert here, like the rest of `assets/`. `/quenching:knowledge:align` (Step 7) stamps these into a target
repo **once**, while scaffolding the bundle, so the `documentation/` home renders as a site;
`/quenching:knowledge:documentation:build` **owns** the layer after that — it installs, merges forward,
regenerates the `.pages` nav, and verifies the build. **The OKF
markdown stays generator-neutral; only this config layer is mkdocs-specific.**

| File | Stamped to | Notes |
| --- | --- | --- |
| `mkdocs.yml.tmpl` | repo root `mkdocs.yml` | only if absent; fill `site_name`/`site_description`; `docs_dir: .knowledge/documentation` |
| `requirements.txt` | repo root | `mkdocs-material` + `mkdocs-awesome-pages-plugin` |
| `quenching.css` | the `documentation/` home, at `assets/stylesheets/quenching.css` | static CSS for badges, hero, cards and reduced-motion guard; `extra_css` in `mkdocs.yml` wires it |
| `ci-github-pages.yml` | `.github/workflows/docs.yml` | opt-in; GitHub Pages via `mkdocs gh-deploy` |

Nav needs no file here — the `.pages` files ship inside `assets/knowledge/documentation/**` and the
`awesome-pages` plugin builds the nav from the folder tree.

## Validate locally

```bash
pip install -r requirements.txt
mkdocs build --strict --site-dir .mkdocs-check
# fallback: python -m mkdocs build --strict --site-dir .mkdocs-check
rm -rf .mkdocs-check
```

The build command is the verification path; the documentation family reports `unverified` when
the toolchain is not installed. Use a separate local preview only when explicitly requested.

`index.md` in each section is the section landing page (`navigation.indexes`). Absolute OKF
links (`/.knowledge/…`) to other homes will not resolve in a site rooted at
`/.knowledge/documentation/` — keep `documentation/` pages self-contained.
