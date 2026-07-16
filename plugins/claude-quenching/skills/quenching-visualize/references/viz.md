# The diagram generator — CLI, graph model, offline vendoring

`quenching-visualize` is a thin driver over one tool. This file is the detail the SKILL.md
body cites so it stays lean.

## The tool

`${CLAUDE_PLUGIN_ROOT}/assets/tools/okf-visualize.py` — stdlib-only Python, **zero
dependencies**, self-contained (it reuses the same frontmatter parser and link resolver
`assets/hooks/okf-validate.py` uses, but imports nothing from it, so it is drop-in).

```
python3 okf-visualize.py <bundle-or-docs-dir> [--out okf-diagram.html] [--name NAME] [--json]
python3 okf-visualize.py --version        # lockstep with the plugin VERSION file
```

- `<docs-dir>` — the OKF bundle root (walks every `.md`).
- `--out` — output path (default `./okf-diagram.html` in the CWD). **Keep it outside the
  bundle** so `okf-validate.py` never scans it.
- `--name` — header label (default: the bundle directory's name).
- `--json` — print `{concepts, edges, types, homes, bytes, out}` instead of the text summary.
- Exit **0** = diagram written; **1** = usage/IO error (e.g. the dir does not exist, or the
  `viewer/` payload is missing next to the script).

The layout files live next to the script under `assets/tools/viewer/`
(`viz.html`, `viz.css`, `viz.js`, `vendor/cytoscape.min.js`, `vendor/marked.min.js`); the
script resolves them relative to its own location, so it must travel **with** that directory.

## The graph model (mirrors okf-validate's link graph)

- **Nodes** — one per **concept doc**. Excluded: `index.md`, `log.md`, `CLAUDE.md`,
  `AGENTS.md`, `README.md`, and any `_`-prefixed / dotfolder / asset dir (the same prune set
  the validator uses). Node fields: `id` (relpath from the bundle root, no `.md`), `label`
  (`title` → first `#` heading → slug), `type` (drives colour), `home` (top-level folder),
  `color`, `size` (scaled by body length), and the selected frontmatter (`description`,
  `resource`, `timestamp`, `tags`).
- **Edges** — for each doc, every within-bundle markdown link is resolved with the **same
  resolver `okf-validate.py` uses** (`_resolve_link`), which handles relative links **and**
  `/docs/...` bundle-absolute links. A link that resolves to another concept doc becomes a
  directed edge `source → target` (deduped). Links to directories / `index.md` / external
  URLs / anchors are not edges. The detail panel rewrites in-body links that resolve to a
  node into internal navigation (via a per-doc link map the generator precomputes).
- **Colours** — keyed on the OKF v0.1 `type` vocabulary (`standard`, `system`, `schema`,
  `table`, `decision`, `vision`, `task`, `documentation`, `knowledge`, `reference`,
  `sidecar`); an unknown/absent `type` falls back
  to a neutral slate. The retired `idea` type keeps its legacy colour so an un-migrated
  bundle still renders. The in-page legend lists every type present and toggles its nodes.

## Offline / self-contained

The generator inlines the vendored `cytoscape.min.js` and `marked.min.js` (both MIT) directly
into the output, replacing the CDN `<script src>` tags — so the HTML renders with **no
network**. Doc bodies are JSON-embedded with `<` escaped to `<`, so a doc containing
`</script>` cannot break out of the page. Provenance and library notices are in
[`assets/tools/viewer/vendor/LICENSES.md`](../../../assets/tools/viewer/vendor/LICENSES.md):
the tool and `viewer/` shell are adapted from the OKF reference implementation's `visualize`
command (`GoogleCloudPlatform/knowledge-catalog`, Apache-2.0).

## Verify the tool itself

```bash
cd plugins/claude-quenching
python3 assets/tools/okf-visualize.py assets/docs --out /tmp/okf-diagram.html   # exit 0 + counts
python3 assets/tools/okf-visualize.py --version                                 # == VERSION
```
