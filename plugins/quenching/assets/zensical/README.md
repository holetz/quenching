# `assets/zensical/` — the site setup payload (Zensical)

Inert here, like the rest of `assets/`. `/quenching:knowledge:align` (Step 7) stamps these into a target
repo **once**, while scaffolding the bundle, so the `documentation/` home renders as a site;
`/quenching:knowledge:documentation:build` **owns** the layer after that — it installs, merges forward,
keeps the `nav` in step with the folder tree, and verifies the build. **The OKF
markdown stays generator-neutral; only this config layer names a generator.**

| File | Stamped to | Notes |
| --- | --- | --- |
| `zensical.toml.tmpl` | repo root `zensical.toml` | only if absent; fill `site_name`/`site_description`; `docs_dir = ".knowledge/documentation"` |
| `requirements.txt` | repo root | `zensical` |
| `quenching.css` | the `documentation/` home, at `assets/stylesheets/quenching.css` | static CSS for badges, hero, cards and reduced-motion guard; `extra_css` in `zensical.toml` wires it |
| `ci-github-pages.yml` | `.github/workflows/docs.yml` | opt-in; GitHub Pages via the Pages artifact — the repo's Pages source must be "GitHub Actions" |

**The nav lives in the config.** Zensical runs no plugins, so nothing derives the sidebar from a
sidecar file: the `nav` list in `zensical.toml` carries the order and the section titles, and a new
page is a new line in it.

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

`index.md` in each section is the section landing page (`navigation.indexes`). Links to other OKF
homes (`/.knowledge/standards/…`) do not resolve in a site rooted at `/.knowledge/documentation/`
and fail the build under `--strict` — keep `documentation/` pages self-contained.
