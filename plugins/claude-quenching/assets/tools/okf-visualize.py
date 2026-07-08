#!/usr/bin/env python3
"""okf-visualize.py — self-contained OKF v0.1 bundle -> interactive HTML diagram.

Payload of the `claude-quenching` plugin. Generic, portable, ZERO dependencies
(a minimal frontmatter parser + the same link resolver `okf-validate.py` uses — no
PyYAML, no network). It walks a `docs/` OKF bundle and writes ONE self-contained,
**offline** HTML file: a force-directed graph of the bundle's concept docs (nodes
coloured by `type`, directed edges from the bundle's own cross-links) with a search
box, type/home filters, layout switch, and a detail panel that renders each doc's
markdown body and its "cited by" backlinks.

    okf-visualize.py <bundle-or-docs-dir> [--out okf-diagram.html] [--name NAME] [--json]
    okf-visualize.py --version

Exit 0 on success (diagram written), 1 on a usage/IO error. The generated `.html`
embeds Cytoscape.js and marked (both MIT, vendored under `viewer/vendor/`) inline, so
it renders with **no network** — open the file straight from disk.

PROVENANCE / ATTRIBUTION
------------------------
The graph model (walk concept docs -> build nodes/edges from `.md` cross-links ->
inject a JSON graph + CSS/JS into an HTML template via placeholder replacement) and
the `viewer/` shell (viz.html / viz.css / viz.js) are ADAPTED from the OKF reference
implementation's `visualize` command, `okf/src/reference_agent/viewer/` in
https://github.com/GoogleCloudPlatform/knowledge-catalog (Apache License 2.0).
Changes here: (a) the upstream `OKFDocument` parser is replaced by this plugin's own
zero-dependency frontmatter parser and the exact link resolver `okf-validate.py`
uses, so the diagram's edges are the SAME within-bundle link graph the validator
models (relative links AND `/docs/...` bundle-absolute links); (b) the CDN
`<script src>` tags are replaced by inlined vendored libraries for an offline,
air-gapped file; (c) the type palette is keyed on the OKF v0.1 `type` vocabulary;
(d) built-in Cytoscape layouts only (no vendored layout extension). See
`viewer/vendor/LICENSES.md` for the upstream and vendored-library notices.

VERSION is kept in lockstep with the plugin `VERSION` file (and `okf-validate.py`).
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys

VERSION = "0.10.0"  # kept in lockstep with the plugin VERSION file

HERE = os.path.dirname(os.path.abspath(__file__))
VIEWER = os.path.join(HERE, "viewer")

# Reserved / exempt filenames are never concept nodes (mirrors okf-validate.py).
RESERVED = ("index.md", "log.md")
EXEMPT = ("CLAUDE.md", "AGENTS.md")
# Directories pruned from the walk: `_`-prefixed private sidecars, dotfolders, assets.
ASSET_DIRS = ("img", "imgs", "images", "assets", "static", "media", "node_modules", "__pycache__")
LINK_RE = re.compile(r"\]\(([^)]+)\)")
HEADING_RE = re.compile(r"^#{1,6}\s+(.*\S)\s*$")

# One colour per OKF v0.1 `type` (the greppable signature — see taxonomy.md). Grouped
# by home family: standards indigo, catalog blues, decisions amber, knowledge/reference
# greens, communications pinks, presentations slate.
TYPE_PALETTE = {
    "standard": "#6366f1",
    "system": "#8b5cf6",
    "schema": "#3b82f6",
    "table": "#0ea5e9",
    "decision": "#f59e0b",
    "vision": "#14b8a6",
    "idea": "#ef4444",
    "documentation": "#22c55e",
    "knowledge": "#06b6d4",
    "reference": "#10b981",
    "communication-template": "#ec4899",
    "communication": "#d946ef",
    "sidecar": "#94a3b8",
}
DEFAULT_NODE_COLOR = "#64748b"


# --------------------------------------------------------------------------- #
# minimal frontmatter parser (no external deps) — returns the body too
# --------------------------------------------------------------------------- #
def parse_frontmatter(text: str):
    """Return (fm, body).

    fm   -- dict of the top-level `key: value` scalar pairs (quotes stripped);
            nested/list values are skipped (only the keys the diagram reads).
    body -- everything after the closing `---` fence (the whole text when there
            is no well-formed frontmatter block).
    """
    if not text.startswith("---"):
        return {}, text
    lines = text.splitlines(keepends=True)
    if lines[0].strip() != "---":
        return {}, text
    close = None
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            close = i
            break
    if close is None:
        return {}, text  # opened a fence, never closed → treat as no frontmatter
    fm: dict = {}
    for raw in lines[1:close]:
        s = raw.rstrip("\n")
        if not s.strip() or s.lstrip().startswith("#"):
            continue
        if s[:1] in (" ", "\t"):  # nested value — skip (top-level scalar keys only)
            continue
        if ":" not in s:
            continue
        key, _, val = s.partition(":")
        key = key.strip()
        val = val.strip()
        if len(val) >= 2 and val[0] == val[-1] and val[0] in ("'", '"'):
            val = val[1:-1]
        fm[key] = val
    return fm, "".join(lines[close + 1:])


def _parse_tags(raw: str) -> list[str]:
    """Best-effort inline tag list — `a, b` or `[a, b]`. A multi-line YAML list is
    skipped by the scalar-only parser, so tags simply come back empty then."""
    raw = (raw or "").strip()
    if raw.startswith("[") and raw.endswith("]"):
        raw = raw[1:-1]
    return [t.strip().strip("'\"") for t in raw.split(",") if t.strip()]


# --------------------------------------------------------------------------- #
# link resolution — the SAME logic okf-validate.py uses, so the diagram's edges
# are exactly the within-bundle link graph the validator models.
# --------------------------------------------------------------------------- #
def _is_skipped_dir(name: str) -> bool:
    return name.startswith(".") or name.startswith("_") or name in ASSET_DIRS


def _strip_noise(text: str) -> str:
    """Drop HTML comments, fenced blocks, and inline code before link extraction so
    example links (e.g. inside a `<!-- GENERATED -->` mold) are not read as real edges."""
    text = re.sub(r"<!--.*?-->", "", text, flags=re.DOTALL)
    text = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    text = re.sub(r"`[^`\n]*`", "", text)
    return text


def _link_targets(text: str) -> list[str]:
    """Every markdown inline-link target, noise stripped (raw href kept for the linkmap)."""
    out: list[str] = []
    for m in LINK_RE.finditer(_strip_noise(text)):
        raw = m.group(1).strip()
        raw = raw.split()[0] if raw.split() else ""   # drop an optional "title"
        raw = raw.strip("<>")
        if raw:
            out.append(raw)
    return out


def _resolve_link(target: str, file_dir: str, root: str):
    """Resolve a WITHIN-BUNDLE markdown/dir link to (abspath, kind) or None to skip.

    kind is 'md' or 'dir'. Returns None for anything OKF does not govern: external
    URLs, anchors, mailto/tel, non-markdown assets, links that escape the bundle
    root, and repo-absolute `/…` links not in the bundle's own `/docs/…` form.
    """
    t = target.split("#", 1)[0].strip()
    if not t:
        return None
    low = t.lower()
    if "://" in t or low.startswith(("mailto:", "tel:")):
        return None
    if t.startswith("/"):
        rest = t[1:]
        first, _, tail = rest.partition("/")
        if first == os.path.basename(root):          # `/docs/…` — the bundle-absolute form
            rest = tail
        elif not os.path.isdir(os.path.join(root, first)):
            return None                              # repo-absolute `/…` — not bundle-governed
        path = os.path.normpath(os.path.join(root, rest)) if rest else root
    else:
        path = os.path.normpath(os.path.join(file_dir, t))
    try:
        if os.path.commonpath([os.path.abspath(path), os.path.abspath(root)]) != os.path.abspath(root):
            return None
    except ValueError:
        return None
    if t.endswith("/"):
        return (path, "dir")
    if low.endswith(".md"):
        return (path, "md")
    if os.path.splitext(os.path.basename(t))[1] == "":   # extensionless → a directory listing
        return (path, "dir")
    return None


# --------------------------------------------------------------------------- #
# graph model — walk concept docs, build nodes + edges from cross-links
# --------------------------------------------------------------------------- #
def _concept_id(abspath: str, root: str) -> str:
    rel = os.path.relpath(abspath, root).replace(os.sep, "/")
    return rel[:-3] if rel.endswith(".md") else rel


def _first_heading(body: str) -> str:
    for line in body.splitlines():
        m = HEADING_RE.match(line)
        if m:
            return m.group(1).strip()
    return ""


def _walk_concepts(root: str) -> dict:
    """One walk over the bundle → {concept_id: {"path", "fm", "body"}}. Excludes the
    reserved listings (`index.md`/`log.md`), harness files, and `README.md`."""
    docs: dict = {}
    for dirpath, dirnames, filenames in os.walk(root):
        dirnames[:] = [d for d in dirnames if not _is_skipped_dir(d)]
        for fn in sorted(filenames):
            if not fn.endswith(".md"):
                continue
            if fn in RESERVED or fn in EXEMPT or fn == "README.md":
                continue
            ap = os.path.join(dirpath, fn)
            try:
                text = pathlib.Path(ap).read_text(encoding="utf-8")
            except (OSError, UnicodeDecodeError):
                continue
            fm, body = parse_frontmatter(text)
            docs[_concept_id(ap, root)] = {"path": ap, "fm": fm, "body": body}
    return docs


def _node(cid: str, doc: dict) -> dict:
    fm = doc["fm"]
    body = doc["body"]
    typ = str(fm.get("type") or "").strip() or "untyped"
    label = str(fm.get("title") or "").strip() or _first_heading(body) or cid.split("/")[-1]
    home = cid.split("/")[0] if "/" in cid else cid
    return {
        "data": {
            "id": cid,
            "label": label,
            "type": typ,
            "home": home,
            "color": TYPE_PALETTE.get(typ, DEFAULT_NODE_COLOR),
            "size": 28 + min(46, len(body) // 220),
            "description": str(fm.get("description") or "").strip(),
            "resource": str(fm.get("resource") or "").strip(),
            "timestamp": str(fm.get("timestamp") or "").strip(),
            "tags": _parse_tags(str(fm.get("tags") or "")),
        }
    }


def build_graph(root: str) -> dict:
    root = os.path.abspath(root)
    docs = _walk_concepts(root)
    nodes = [_node(cid, docs[cid]) for cid in sorted(docs)]
    bodies = {cid: docs[cid]["body"] for cid in docs}
    edges: list[dict] = []
    linkmaps: dict = {}
    seen_edges: set = set()
    for cid in sorted(docs):
        doc = docs[cid]
        fdir = os.path.dirname(doc["path"])
        lm: dict = {}
        for raw in _link_targets(doc["body"]):
            res = _resolve_link(raw, fdir, root)
            if not res:
                continue
            path, kind = res
            if kind != "md":
                continue  # dir/index targets have no concept node
            tid = _concept_id(path, root)
            if tid not in docs or tid == cid:
                continue
            lm[raw] = tid
            key = (cid, tid)
            if key in seen_edges:
                continue
            seen_edges.add(key)
            edges.append({"data": {"id": f"{cid}→{tid}", "source": cid, "target": tid}})
        if lm:
            linkmaps[cid] = lm
    types = sorted({n["data"]["type"] for n in nodes})
    homes = sorted({n["data"]["home"] for n in nodes})
    return {
        "nodes": nodes,
        "edges": edges,
        "bodies": bodies,
        "linkmaps": linkmaps,
        "types": types,
        "homes": homes,
        "palette": TYPE_PALETTE,
    }


# --------------------------------------------------------------------------- #
# rendering — inject graph + CSS/JS + vendored libs into the HTML shell
# --------------------------------------------------------------------------- #
def _read_asset(*parts: str) -> str:
    return pathlib.Path(os.path.join(VIEWER, *parts)).read_text(encoding="utf-8")


def _json_for_script(obj) -> str:
    """JSON safe to inline in a <script> — escape `<` so a doc body containing
    `</script>` (e.g. a code sample) cannot break out of the tag."""
    return json.dumps(obj, ensure_ascii=False).replace("<", "\\u003c")


def render_html(graph: dict, bundle_name: str) -> str:
    try:
        template = _read_asset("viz.html")
        css = _read_asset("viz.css")
        js = _read_asset("viz.js")
        cyto = _read_asset("vendor", "cytoscape.min.js")
        marked = _read_asset("vendor", "marked.min.js")
    except OSError as exc:
        raise FileNotFoundError(
            f"viewer asset missing next to okf-visualize.py ({exc}); expected "
            f"{VIEWER}/viz.html, viz.css, viz.js, vendor/cytoscape.min.js, vendor/marked.min.js"
        ) from exc
    # Inject the code blobs first (str.replace is literal — no regex/backref hazard),
    # then the user data LAST so a doc body can never smuggle in a code placeholder.
    return (
        template
        .replace("/*__VIZ_CSS__*/", css)
        .replace("/*__CYTOSCAPE_JS__*/", cyto)
        .replace("/*__MARKED_JS__*/", marked)
        .replace("/*__VIZ_JS__*/", js)
        .replace("__BUNDLE_NAME__", _json_for_script(bundle_name))
        .replace("__BUNDLE_DATA__", _json_for_script(graph))
    )


def generate(docs_dir: str, out_path: str, bundle_name: str | None = None) -> dict:
    root = pathlib.Path(docs_dir)
    if not root.is_dir():
        raise FileNotFoundError(f"bundle directory not found: {docs_dir}")
    graph = build_graph(str(root))
    name = bundle_name or root.resolve().name
    html = render_html(graph, name)
    out = pathlib.Path(out_path)
    if out.parent and str(out.parent):
        out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(html, encoding="utf-8")
    return {
        "concepts": len(graph["nodes"]),
        "edges": len(graph["edges"]),
        "types": len(graph["types"]),
        "homes": len(graph["homes"]),
        "bytes": len(html.encode("utf-8")),
        "out": str(out),
    }


# --------------------------------------------------------------------------- #
# CLI
# --------------------------------------------------------------------------- #
def _usage() -> str:
    return ("usage: okf-visualize.py <bundle-or-docs-dir> [--out okf-diagram.html] "
            "[--name NAME] [--json] [--version]")


def run_cli(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"okf-visualize {VERSION}")
        return 0
    if "-h" in argv or "--help" in argv:
        print(_usage())
        return 0
    as_json = "--json" in argv
    docs_dir = None
    out_path = None
    name = None
    i = 0
    while i < len(argv):
        a = argv[i]
        if a in ("--json",):
            i += 1
            continue
        if a == "--out":
            if i + 1 >= len(argv):
                print(f"error: --out needs a path\n{_usage()}", file=sys.stderr)
                return 1
            out_path = argv[i + 1]
            i += 2
            continue
        if a == "--name":
            if i + 1 >= len(argv):
                print(f"error: --name needs a value\n{_usage()}", file=sys.stderr)
                return 1
            name = argv[i + 1]
            i += 2
            continue
        if a.startswith("-"):
            print(f"error: unknown option {a}\n{_usage()}", file=sys.stderr)
            return 1
        if docs_dir is None:
            docs_dir = a
        else:
            print(f"error: unexpected argument {a}\n{_usage()}", file=sys.stderr)
            return 1
        i += 1
    if docs_dir is None:
        print(f"error: missing bundle directory\n{_usage()}", file=sys.stderr)
        return 1
    if out_path is None:
        out_path = os.path.join(os.getcwd(), "okf-diagram.html")
    try:
        counts = generate(docs_dir, out_path, name)
    except (FileNotFoundError, OSError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    if as_json:
        print(json.dumps(counts, indent=2))
    else:
        kb = counts["bytes"] // 1024
        print(f"OKF diagram — {counts['out']} (okf-visualize v{VERSION})")
        print(f"  {counts['concepts']} concept(s), {counts['edges']} link(s), "
              f"{counts['types']} type(s), {counts['homes']} home(s) — {kb} KB, offline")
    return 0


def main() -> int:
    return run_cli(sys.argv[1:])


if __name__ == "__main__":
    sys.exit(main())
