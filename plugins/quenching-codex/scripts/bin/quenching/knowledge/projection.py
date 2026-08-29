"""Deterministic projections from the OKF bundle into the documentation home.

The bundle-root glossary is the only editable vocabulary source.  This module turns it into
the two site inputs that must never drift independently: the published reference page and the
Python-Markdown abbreviation definitions.  It deliberately has no Zensical dependency, so the
projection can be checked before the site toolchain is installed.
"""
from __future__ import annotations

import hashlib
import html
import posixpath
import re
from dataclasses import dataclass
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

from quenching.common.frontmatter import parse_frontmatter


GLOSSARY_REL = "glossary.md"
DEFAULT_ROUTE = "reference/glossary.md"
DEFAULT_SNIPPET = "assets/glossary-abbreviations.md"
HOMES = ("documentation", "standards", "concepts", "external", "catalog", "vision")
NO_PUBLICATION = {"não publicar", "nao publicar", "do not publish", "not publish"}
LINK_LABEL = re.compile(r"^\[(?P<label>.*)\]\((?P<link>[^)]+)\)$")
MARKDOWN_LINK = re.compile(r"\[([^]]+)\]\(([^)]+)\)")


@dataclass(frozen=True)
class GlossaryEntry:
    term: str
    definition: str
    link: str | None = None


@dataclass(frozen=True)
class Publication:
    home: str
    decision: str
    route: str


def _plain_term(label: str) -> str:
    match = LINK_LABEL.match(label.strip())
    if match:
        label = match.group("label")
    elif label.strip().startswith("[") and label.strip().endswith("]"):
        # Some glossary entries use link-label styling without a destination.  Keep the
        # vocabulary term itself, not the Markdown delimiters (which break abbr syntax).
        label = label.strip()[1:-1]
    label = html.unescape(label)
    label = re.sub(r"(``?|\*\*?|__?|~~)", "", label)
    return re.sub(r"\s+", " ", label).strip()


def _flatten(text: str) -> str:
    return re.sub(r"\s+", " ", text).strip()


def _entry_from(label: str, definition: str) -> GlossaryEntry | None:
    link = None
    match = LINK_LABEL.match(label.strip())
    if match:
        label, link = match.group("label"), match.group("link")
    term = _plain_term(label)
    if not term or not definition.strip():
        return None
    if "replace with this repo's first term" in term.lower() or "one-sentence meaning" in definition.lower():
        return None
    return GlossaryEntry(term, _flatten(definition), link)


def parse_glossary(markdown: str) -> list[GlossaryEntry]:
    """Read glossary bullets, including wrapped definition lines, in source order."""
    entries: list[GlossaryEntry] = []
    pending: tuple[str, list[str]] | None = None
    in_terms = False

    def flush() -> None:
        nonlocal pending
        if pending is not None:
            entry = _entry_from(pending[0], " ".join(pending[1]))
            if entry is not None:
                entries.append(entry)
        pending = None

    for line in markdown.splitlines():
        if re.match(r"^##\s+Terms\s*$", line, re.IGNORECASE):
            in_terms = True
            continue
        if in_terms and re.match(r"^##\s+", line):
            flush()
            in_terms = False
            continue
        if not in_terms:
            continue
        candidate = line.strip()
        if candidate.startswith(("- ", "* ")) and " — " in candidate:
            label, definition = candidate[2:].rsplit(" — ", 1)
            flush()
            pending = (label, [definition])
            continue
        if pending is not None and line.strip() and not line.lstrip().startswith(("- ", "* ", "#")):
            pending[1].append(line.strip())
        elif pending is not None and not line.strip():
            # A blank line belongs to the preceding wrapped paragraph only when another
            # continuation follows.  Keeping it out makes the projection canonical.
            continue
    flush()
    return entries


def source_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _abbr_definition(definition: str) -> str:
    definition = MARKDOWN_LINK.sub(r"\1", definition)
    definition = re.sub(r"<[^>]+>", "", definition)
    definition = re.sub(r"[`*_~]", "", definition)
    return html.unescape(_flatten(definition))


def _abbr_supported(term: str) -> bool:
    """Whether Python-Markdown's abbreviation syntax can represent this term."""
    return bool(term) and term[0].isalnum() and term[-1].isalnum() and "\\" not in term and "]" not in term


def _abbr_variants(term: str, taken: frozenset[str]) -> list[str]:
    """The exact term plus, for a Title-cased term, its running-prose lowercase form.

    Abbreviation matching is case-sensitive and glossary terms are Title-cased, so without
    the extra variant a term only ever renders as ``<abbr>`` where prose happens to start a
    sentence with it.  Acronyms (second character uppercase) and terms another glossary entry
    already claims in lowercase keep the exact form only.
    """
    variants = [term]
    if len(term) > 1 and term[0].isupper() and term[1].islower():
        lowered = term[0].lower() + term[1:]
        if lowered not in taken:
            variants.append(lowered)
    return variants


def render_abbreviations(source: Path, entries: list[GlossaryEntry]) -> str:
    """Render the complete abbreviation file, including its provenance header."""
    digest = source_sha256(source)
    lines = [
        "<!-- GENERATED FILE — do not edit; source: /docs/glossary.md -->",
        f"<!-- source_sha256: {digest} -->",
        "",
    ]
    taken = frozenset(entry.term for entry in entries)
    for entry in sorted(entries, key=lambda item: (item.term.casefold(), item.term)):
        if _abbr_supported(entry.term):
            for variant in _abbr_variants(entry.term, taken):
                lines.append(f"*[{variant}]: {_abbr_definition(entry.definition)}")
        else:
            lines.append(f"<!-- explicit glossary abbr fallback: {html.escape(entry.term)} -->")
    return "\n".join(lines) + "\n"


def parse_publication_map(markdown: str) -> dict[str, Publication]:
    """Parse the accepted publication table without interpreting any other plan prose."""
    rows: dict[str, Publication] = {}
    active = False
    for line in markdown.splitlines():
        if line.strip().lower().startswith("### mapa editorial de publicação"):
            active = True
            continue
        if active and line.startswith("### "):
            break
        if not active or not line.lstrip().startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 5 or cells[0].lower() in {"home", "---"}:
            continue
        home = cells[0].strip("`").strip().rstrip("/")
        decision = cells[1].strip().lower()
        route = cells[4].strip().strip("`")
        if home and home not in {"---", "<home>"}:
            rows[home] = Publication(home, decision, route)
    return rows


def publication_routes(plan: str | None, default_route: str = DEFAULT_ROUTE) -> dict[str, str]:
    """Return source-home → published-route prefixes from the accepted map.

    The glossary has a safe default because its route is a fixed part of the documentation
    contract.  Other homes require an explicit map row; silently inventing their exposure would
    violate the publication boundary.
    """
    routes: dict[str, str] = {}
    for home, row in parse_publication_map(plan or "").items():
        if row.decision in NO_PUBLICATION or not row.route or row.route in {"—", "-", "—"}:
            continue
        route = row.route.rstrip("/")
        if route.startswith("<"):
            continue
        routes[home] = route
    if plan is None or not any(key in routes for key in ("glossary.md", "glossary")):
        routes["glossary.md"] = default_route
    elif "glossary" in routes and "glossary.md" not in routes:
        routes["glossary.md"] = routes["glossary"]
    return routes


def _bundle_target(raw: str, source_rel: str) -> str | None:
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc:
        return None
    path = parsed.path
    if path.startswith("/docs/"):
        path = path[len("/docs/"):]
    elif path.startswith("/"):
        path = path.lstrip("/")
    elif source_rel == GLOSSARY_REL and path.startswith("../"):
        # The shipped glossary used to live below `concepts/`; its historical links still
        # carry one `../`.  The canonical file is now at the bundle root, so normalize that
        # single legacy climb before applying the publication map.
        path = path[3:]
    else:
        path = posixpath.normpath(posixpath.join(posixpath.dirname(source_rel), path))
    return path


def _published_target(target: str, routes: dict[str, str]) -> str | None:
    if target == GLOSSARY_REL:
        return routes.get(GLOSSARY_REL)
    for home in HOMES:
        prefix = home + "/"
        if target == home:
            return routes.get(home)
        if target.startswith(prefix) and home in routes:
            route = routes[home]
            suffix = target[len(prefix):]
            if route.endswith(".md"):
                return route if suffix in {"", "index.md"} else None
            return posixpath.join(route, suffix)
    return None


def rewrite_link(raw: str, source_rel: str, output_rel: str, routes: dict[str, str]) -> str | None:
    """Map a bundle link to the published route, or return ``None`` for unpublished homes."""
    parsed = urlsplit(raw)
    if parsed.scheme or parsed.netloc or not parsed.path:
        return raw
    if parsed.path.startswith(("/plugins/", "/.agents/")):
        # These are repository navigation links, not pages in the published documentation
        # site.  Keeping them would make a strict site build claim that source files are pages.
        return None
    target = _bundle_target(raw, source_rel)
    if target is None:
        return raw
    published = _published_target(target, routes)
    if published is None:
        # A relative link outside a known home is not a knowledge leak; preserve it for the
        # documentation author's own tree.  A known home with no route is intentionally hidden.
        if target.split("/", 1)[0] in HOMES:
            return None
        return raw
    relative = posixpath.relpath(published, posixpath.dirname(output_rel))
    return urlunsplit(("", "", relative, parsed.query, parsed.fragment))


def rewrite_markdown_links(text: str, source_rel: str, output_rel: str,
                           routes: dict[str, str]) -> str:
    def replace(match: re.Match[str]) -> str:
        target = rewrite_link(match.group(2), source_rel, output_rel, routes)
        return match.group(1) if target is None else f"[{match.group(1)}]({target})"

    return MARKDOWN_LINK.sub(replace, text)


def _escape_literal_brackets(text: str) -> str:
    """Keep task markers and similar prose from becoming unresolved Markdown references."""
    return text.replace("[ ]", r"\[ \]").replace("[!]", r"\[!\]")


def render_route(source: Path, entries: list[GlossaryEntry], routes: dict[str, str],
                 route_rel: str = DEFAULT_ROUTE) -> str:
    digest = source_sha256(source)
    source_fm = parse_frontmatter(source.read_text(encoding="utf-8"))
    timestamp = str(source_fm.get("timestamp", "")).strip()
    lines = [
        "---",
        "type: documentation",
        "title: Glossary",
        "description: Published vocabulary projected from the canonical bundle glossary.",
        "resource: /docs/glossary.md",
        "source: /docs/glossary.md",
        f"source_sha256: {digest}",
        "generated: true",
    ]
    if timestamp:
        lines.append(f"timestamp: {timestamp}")
    lines += [
        "---",
        "",
        "# Glossary",
        "",
        "This page is generated from the canonical bundle glossary. Edit the source file; the",
        "published route and abbreviation definitions are projections, never second sources.",
        "",
        f"<!-- GENERATED FROM /docs/glossary.md; source_sha256: {digest} -->",
    ]
    for entry in sorted(entries, key=lambda item: (item.term.casefold(), item.term)):
        if _abbr_supported(entry.term):
            label = f"**{entry.term}**"
        else:
            definition = html.escape(_abbr_definition(entry.definition), quote=True)
            term_text = html.escape(entry.term).replace("[", "&#91;").replace("]", "&#93;")
            label = f'<abbr title="{definition}">{term_text}</abbr>'
        if entry.link:
            target = rewrite_link(entry.link, GLOSSARY_REL, route_rel, routes)
            if target:
                if _abbr_supported(entry.term):
                    label = f"[{label}]({target})"
                else:
                    label = f'<a href="{html.escape(target, quote=True)}">{label}</a>'
        definition = rewrite_markdown_links(entry.definition, GLOSSARY_REL, route_rel, routes)
        definition = _escape_literal_brackets(definition)
        lines.append(f"- {label} — {definition}")
    return "\n".join(lines) + "\n"


def _relative_route(index: Path, route_rel: str) -> str:
    return posixpath.relpath(route_rel, "reference") if index.name == "index.md" else route_rel


def ensure_reference_index(index: Path, route_rel: str = DEFAULT_ROUTE) -> str:
    """Add the generated route to the reference listing, preserving existing prose."""
    text = index.read_text(encoding="utf-8") if index.exists() else "# reference/\n"
    link = _relative_route(index, route_rel)
    if re.search(rf"\]\({re.escape(link)}(?:#[^)]+)?\)", text):
        return text
    if not text.endswith("\n"):
        text += "\n"
    text += f"\n- [Glossary]({link}) — generated from the canonical bundle glossary\n"
    return text


def ensure_nav(config: Path, route_rel: str = DEFAULT_ROUTE) -> str:
    """Insert the route into an existing ``nav`` list without reformatting other TOML."""
    text = config.read_text(encoding="utf-8") if config.exists() else ""
    if not text or route_rel in text:
        return text
    lines = text.splitlines(keepends=True)
    start = next((i for i, line in enumerate(lines) if re.match(r"^\s*nav\s*=\s*\[", line)), None)
    if start is None:
        return text
    depth = 0
    for i in range(start, len(lines)):
        depth += lines[i].count("[") - lines[i].count("]")
        if i > start and depth == 0:
            indent = re.match(r"^(\s*)", lines[i]).group(1)
            item_indent = indent + "  "
            lines.insert(i, f'{item_indent}{{ "Glossary" = [ "{route_rel}" ] }},\n')
            return "".join(lines)
    return text


def projection_paths(bundle: Path, route_rel: str = DEFAULT_ROUTE,
                     snippet_rel: str = DEFAULT_SNIPPET) -> tuple[Path, Path, Path]:
    docs = bundle / "documentation"
    return bundle / GLOSSARY_REL, docs / route_rel, docs / snippet_rel


def projection_findings(bundle: Path, plan: str | None = None, config: Path | None = None,
                        route_rel: str = DEFAULT_ROUTE,
                        snippet_rel: str = DEFAULT_SNIPPET) -> tuple[dict, list[dict]]:
    source, route, snippet = projection_paths(bundle, route_rel, snippet_rel)
    plan_rows = parse_publication_map(plan or "")
    glossary_row = plan_rows.get(GLOSSARY_REL) or plan_rows.get("glossary")
    excluded = glossary_row is not None and glossary_row.decision in NO_PUBLICATION
    payload = {"source": str(source), "route": str(route), "snippet": str(snippet),
               "excluded": excluded, "findings": []}
    if not source.is_file() or not source.read_text(encoding="utf-8").strip():
        return payload, []
    if excluded:
        findings: list[dict] = []

        def add_excluded(code: str, message: str, path: Path) -> None:
            findings.append({"severity": "error", "code": code, "message": message,
                             "path": str(path)})

        if route.exists():
            add_excluded("glossary-route-unexpected", "explicitly unpublished glossary route exists", route)
        if snippet.exists():
            add_excluded("glossary-snippet-unexpected", "explicitly unpublished glossary snippet exists", snippet)
        index = route.parent / "index.md"
        if index.is_file() and re.search(rf"\]\({re.escape(route.name)}(?:#[^)]+)?\)",
                                         index.read_text(encoding="utf-8")):
            add_excluded("glossary-index-route-unexpected",
                         "reference index exposes an explicitly unpublished glossary", index)
        if config and config.is_file() and route_rel in config.read_text(encoding="utf-8"):
            add_excluded("glossary-nav-route-unexpected",
                         "site navigation exposes an explicitly unpublished glossary", config)
        return payload, findings
    text = source.read_text(encoding="utf-8")
    entries = parse_glossary(text)
    digest = source_sha256(source)
    expected_route = render_route(source, entries, publication_routes(plan, route_rel), route_rel)
    expected_snippet = render_abbreviations(source, entries)
    findings: list[dict] = []

    def add(code: str, message: str, path: Path) -> None:
        findings.append({"severity": "error", "code": code, "message": message, "path": str(path)})

    if not route.is_file():
        add("glossary-route-missing", "generated glossary route is absent", route)
    else:
        actual = route.read_text(encoding="utf-8")
        fm = parse_frontmatter(actual)
        if fm.get("source") != "/docs/glossary.md":
            add("glossary-source-missing", "route does not record the canonical source", route)
        if str(fm.get("source_sha256", "")).strip() != digest:
            add("glossary-source-hash-stale", "route source hash does not match the canonical glossary", route)
        if actual != expected_route:
            add("glossary-route-stale", "route differs from the deterministic projection", route)
    if not snippet.is_file():
        add("glossary-snippet-missing", "generated abbreviation snippet is absent", snippet)
    elif snippet.read_text(encoding="utf-8") != expected_snippet:
        add("glossary-snippet-stale", "abbreviation snippet differs from the canonical glossary", snippet)
    index = route.parent / "index.md"
    if not index.is_file() or not re.search(rf"\]\({re.escape(route.name)}(?:#[^)]+)?\)", index.read_text(encoding="utf-8")):
        add("glossary-index-route-missing", "reference index does not link the generated glossary route", index)
    if config and config.is_file() and route_rel not in config.read_text(encoding="utf-8"):
        add("glossary-nav-route-missing", "site navigation does not expose the generated glossary route", config)
    payload.update({"source_sha256": digest, "terms": len(entries)})
    return payload, findings


def write_projection(bundle: Path, plan: str | None = None, config: Path | None = None,
                     route_rel: str = DEFAULT_ROUTE,
                     snippet_rel: str = DEFAULT_SNIPPET) -> dict:
    source, route, snippet = projection_paths(bundle, route_rel, snippet_rel)
    if not source.is_file() or not source.read_text(encoding="utf-8").strip():
        return {"source": str(source), "skipped": "canonical glossary is absent or empty"}
    plan_rows = parse_publication_map(plan or "")
    glossary_row = plan_rows.get(GLOSSARY_REL) or plan_rows.get("glossary")
    if glossary_row is not None and glossary_row.decision in NO_PUBLICATION:
        return {"source": str(source), "excluded": True,
                "skipped": "canonical glossary is explicitly unpublished"}
    text = source.read_text(encoding="utf-8")
    entries = parse_glossary(text)
    routes = publication_routes(plan, route_rel)
    route.parent.mkdir(parents=True, exist_ok=True)
    snippet.parent.mkdir(parents=True, exist_ok=True)
    route.write_text(render_route(source, entries, routes, route_rel), encoding="utf-8")
    snippet.write_text(render_abbreviations(source, entries), encoding="utf-8")
    index = route.parent / "index.md"
    index.parent.mkdir(parents=True, exist_ok=True)
    index.write_text(ensure_reference_index(index, route_rel), encoding="utf-8")
    if config and config.is_file():
        config.write_text(ensure_nav(config, route_rel), encoding="utf-8")
    return {"source": str(source), "route": str(route), "snippet": str(snippet),
            "source_sha256": source_sha256(source), "terms": len(entries)}
