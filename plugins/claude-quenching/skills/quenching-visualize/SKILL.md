---
name: quenching-visualize
description: >-
  Renders a repository's OKF docs/ bundle as ONE self-contained, offline, interactive HTML
  diagram — a force-directed graph of the concept docs, coloured by `type`, wired by the
  bundle's own cross-links, with search, type/home filters, layout switch, and a markdown
  detail panel with backlinks. Use when the user asks to "generate the diagram", "visualize
  the knowledge base", "render the knowledge graph", "show the docs as a graph", "make an
  HTML diagram of the bundle", "draw/map the OKF bundle", or "see the docs visually". Runs
  the plugin's zero-dependency okf-visualize.py straight from the plugin root (no install
  needed; the HTML embeds Cytoscape.js + marked inline, so it opens with no network),
  reports the node/edge counts, and can optionally install/upgrade the tool into the
  target's .claude/tools/ for standalone use. Not for: installing/aligning the docs
  structure → quenching-align; adding one doc → quenching-insert; importing an external
  source into the bundle → quenching-enrich.
when_to_use: >-
  rendering an existing OKF docs/ bundle as an offline interactive HTML graph diagram.
  Read-only over the bundle; the structural install is quenching-align, content insertion
  is quenching-insert.
allowed-tools: Read, Glob, Bash
---

# quenching-visualize — render the OKF bundle as an interactive diagram

Turns an existing OKF v0.1 `docs/` bundle into **one self-contained HTML file** — a
force-directed graph of the concept docs (nodes coloured by `type`, directed edges from the
bundle's own within-bundle links) with a search box, type/home filters, a layout switch, and
a detail panel that renders each doc's markdown body and its "cited by" backlinks. The
generator is `${CLAUDE_PLUGIN_ROOT}/assets/tools/okf-visualize.py` (stdlib-only, zero
dependencies); the graph model, CLI, and offline/vendoring facts are in
[references/viz.md](references/viz.md).

The output HTML **embeds Cytoscape.js + marked inline** (both MIT, vendored under
`assets/tools/viewer/vendor/`), so it renders with **no network** — open it straight from
disk, air-gapped.

## Doctrine

- **Read-only over the bundle.** The tool only *reads* `docs/**` and *writes* the single HTML
  file; it never mutates the bundle. This skill classifies nothing and stamps nothing.
- **Never write the diagram inside `docs/`.** The `.html` is a generated artifact, not a
  concept doc — writing it under the bundle would pollute the tree and get scanned by
  `okf-validate.py`. Default output is the **repo root** (`./okf-diagram.html`); if the user
  wants it elsewhere, keep it **outside** the bundle root.
- **Regenerate, never hand-edit.** The HTML is disposable output; re-run the tool to refresh
  it. It is a good `.gitignore` candidate.
- **The bundle must already be an OKF bundle.** If `docs/` has no `index.md`/`okf_version`
  (never aligned), the graph is meaningless — route to `quenching-align` first.

## Workflow

### 1. Locate the bundle (read-only)
Find the bundle root — `docs/` by default, or the target's configured `docsDir` (check
`.claude/hooks/hooks-config.json` if the hook is installed). Confirm it looks like an OKF
bundle (`docs/index.md`, an `okf_version`, populated homes) with `Glob`. If there is no
bundle, stop and point the user at `quenching-align`.

### 2. Generate the diagram
Run the generator straight from the plugin root — **no install step**:

```bash
python3 "${CLAUDE_PLUGIN_ROOT}/assets/tools/okf-visualize.py" <docs-dir> \
  --out ./okf-diagram.html --name "<repo name>"
```

`--out` defaults to `./okf-diagram.html` in the current directory; pass an explicit path to
place it outside the bundle. `--name` sets the header label (defaults to the bundle dir
name). Add `--json` to read machine counts. Exit 0 = the diagram was written.

### 3. Report
State the **output path**, the **concept/edge/type/home counts** the tool prints, and that
the file is **self-contained and opens offline** (no network). If the graph has **0 edges**,
say so plainly — it usually means the bundle is freshly scaffolded (mostly `index.md`
listings) or its docs do not cross-link yet, not that the tool failed.

### 4. Offer to open
Offer to open the file in the default browser (e.g. `xdg-open`/`open` the `--out` path), or
just hand the user the path to open themselves.

### 5. (Optional) Install/upgrade for standalone use
Mirrors [quenching-align](../quenching-align/SKILL.md) step 6. Offer to copy the tool into
the target's `.claude/tools/` so it can be run **without** the plugin loaded:

- Copy **exactly** `${CLAUDE_PLUGIN_ROOT}/assets/tools/okf-visualize.py` **and** the whole
  `${CLAUDE_PLUGIN_ROOT}/assets/tools/viewer/` directory (it holds `viz.html/css/js` and the
  vendored libs the script inlines) into `.claude/tools/`.
- If a copy is **already installed**, compare versions
  (`python3 .claude/tools/okf-visualize.py --version` vs the plugin's `VERSION`) and offer to
  overwrite **only when the plugin is newer**. The `viewer/` payload must be upgraded
  together with the script — they are a matched pair (the script inlines those exact files).

## Invariants to never violate
- Never write the `.html` under the bundle root (`docs/**`) — it is generated output, not a
  concept doc; keep it outside so the validator/hook never scans it.
- Never hand-edit the generated HTML — regenerate it.
- Never mutate the bundle from this skill — it is strictly read-then-render.
- When installing standalone, copy the **script and its `viewer/` payload together** and pin
  the same version — a script without its matching `viewer/` cannot render.
