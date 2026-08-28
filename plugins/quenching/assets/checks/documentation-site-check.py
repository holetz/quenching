#!/usr/bin/env python3
"""Deterministic structural checks for a built Zensical site."""

from __future__ import annotations

import argparse
import html
import re
import tempfile
from os.path import normpath
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


REMOTE_SCHEMES = {"http", "https"}
SKIPPED_SCHEMES = {"", "data", "mailto", "tel", "javascript"}
ASSET_DIRS = {"assets", "static", "media", "images", "img", "imgs"}


@dataclass(frozen=True)
class Finding:
    code: str
    path: Path
    detail: str


class Page(HTMLParser):
    def __init__(self) -> None:
        super().__init__()
        self.ids: set[str] = set()
        self.links: list[str] = []
        self.assets: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        values = dict(attrs)
        if values.get("id"):
            self.ids.add(values["id"] or "")
        for key in ("href", "src"):
            value = values.get(key)
            if not value:
                continue
            if key == "href" and tag == "a":
                self.links.append(value)
            elif key == "src":
                self.assets.append(value)
            elif key == "href" and tag == "link":
                # Validate fetchable link resources, not canonical/prev/next metadata URLs.
                rel = (values.get("rel") or "").split()
                if set(rel) & {"stylesheet", "icon", "manifest", "preload"}:
                    self.assets.append(value)


def pages(site: Path) -> dict[Path, Page]:
    result: dict[Path, Page] = {}
    for path in site.rglob("*.html"):
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        result[path.relative_to(site)] = page
    return result


def local_target(base: Path, raw: str, site_root: Path) -> tuple[Path | None, str]:
    parsed = urlsplit(raw)
    if parsed.scheme in REMOTE_SCHEMES:
        return None, "remote"
    if parsed.scheme in SKIPPED_SCHEMES and not parsed.path and not parsed.fragment:
        return None, "skip"
    if parsed.scheme:
        return None, "skip"
    path = Path(parsed.path)
    if parsed.path.startswith("/"):
        return (Path(normpath(site_root / parsed.path.lstrip("/"))), parsed.fragment)
    # URL resolution is lexical, so a `../`-relative href must be normalized before it is
    # compared against the normalized page keys; an unnormalized path never matches them.
    return (Path(normpath(base / path)), parsed.fragment)


def _asset_reference(raw: str) -> bool:
    """Whether a URL names an asset or asset directory rather than an HTML page."""
    return any(part in ASSET_DIRS for part in Path(urlsplit(raw).path).parts)


def _sitemap_findings(site: Path, local: bool) -> list[Finding]:
    sitemap = site / "sitemap.xml"
    if not sitemap.exists():
        return [] if local else [Finding("site-sitemap-empty", sitemap.relative_to(site), "missing sitemap.xml")]
    try:
        root = ElementTree.parse(sitemap).getroot()
        has_urls = any(node.tag.endswith("loc") and (node.text or "").strip()
                       for node in root.iter())
        # A local build may omit site_url and therefore have no meaningful absolute sitemap
        # location.  A non-empty relative loc is valid too; only the public/default mode needs
        # one URL to prove that the generator emitted a sitemap.
        if not has_urls and not local:
            return [Finding("site-sitemap-empty", sitemap.relative_to(site), "no URLs")]
    except ElementTree.ParseError as error:
        return [Finding("site-sitemap-empty", sitemap.relative_to(site), f"invalid XML: {error}")]
    return []


def _glossary_route_candidates(site: Path, route: str) -> list[Path]:
    relative = Path(route.lstrip("/"))
    if relative.suffix == ".md":
        return [site / relative.with_suffix("") / "index.html", site / relative.with_suffix(".html")]
    if relative.suffix == ".html":
        return [site / relative]
    return [site / relative / "index.html"]


def _glossary_terms(source: Path) -> list[str]:
    if not source.is_file():
        return []
    terms: list[str] = []
    in_terms = False
    link_label = re.compile(r"^\[(?P<label>.*)\]\([^)]*\)$")
    for line in source.read_text(encoding="utf-8").splitlines():
        if re.match(r"^##\s+Terms\s*$", line, re.IGNORECASE):
            in_terms = True
            continue
        if in_terms and re.match(r"^##\s+", line):
            break
        if not in_terms:
            continue
        candidate = line.strip()
        if not candidate.startswith(("- ", "* ")) or " — " not in candidate:
            continue
        label = candidate[2:].rsplit(" — ", 1)[0].strip()
        match = link_label.match(label)
        if match:
            label = match.group("label")
        elif label.startswith("[") and label.endswith("]"):
            label = label[1:-1]
        terms.append(re.sub(r"[`*_]", "", html.unescape(label)).strip())
    return [term for term in terms if term]


def _glossary_findings(site: Path, source: Path | None, route: str,
                       snippet: Path | None, term: str | None,
                       required: bool) -> list[Finding]:
    if not required:
        return []
    findings: list[Finding] = []
    if source is None or not source.is_file() or not source.read_text(encoding="utf-8").strip():
        path = source or (site.parent / ".knowledge" / "glossary.md")
        return [Finding("site-glossary-source-missing", path, "required canonical glossary is absent")]
    route_path = next((path for path in _glossary_route_candidates(site, route) if path.is_file()), None)
    if route_path is None:
        findings.append(Finding("site-glossary-route-missing", Path(route), "published glossary route is absent"))
    if snippet is None:
        snippet = source.parent / "documentation" / "assets" / "glossary-abbreviations.md"
    if snippet is None or not snippet.is_file():
        findings.append(Finding("site-glossary-snippet-missing", snippet or Path("glossary-abbreviations.md"),
                                "generated abbreviation snippet is absent"))
    terms = [term] if term else _glossary_terms(source)
    if terms:
        rendered = html.unescape("\n".join(path.read_text(encoding="utf-8")
                                             for path in site.rglob("*.html")))
        for known in terms[:1]:
            pattern = rf"<abbr\b[^>]*>\s*{re.escape(known)}\s*</abbr>"
            if not re.search(pattern, rendered, re.IGNORECASE):
                findings.append(Finding("site-glossary-term-unrendered", Path(known),
                                        f"known glossary term is not rendered as <abbr>: {known}"))
    return findings


def check(site: Path, *, local: bool = False,
          glossary_source: Path | None = None,
          glossary_route: str = "reference/glossary.md",
          glossary_snippet: Path | None = None,
          glossary_term: str | None = None,
          require_glossary: bool = False) -> list[Finding]:
    found: list[Finding] = []
    parsed_pages = pages(site)
    linked_pages: set[Path] = {Path("index.html")}
    for relative, page in parsed_pages.items():
        base = (site / relative).parent
        for asset in page.assets:
            target, kind = local_target(base, asset, site)
            if kind == "remote":
                found.append(Finding("site-remote-resource", relative, asset))
            elif target and (not target.exists() or target.is_dir()):
                found.append(Finding("site-asset-missing", relative, asset))
        for link in page.links:
            # Zensical's generated accessibility skip link intentionally points at a virtual
            # anchor that is consumed by the theme, not by the page body.
            if link == "#__skip":
                continue
            target, kind = local_target(base, link, site)
            if kind == "remote":
                continue
            if not target:
                continue
            if _asset_reference(link):
                if not target.exists():
                    found.append(Finding("site-asset-missing", relative, link))
                continue
            if target.is_dir():
                target = target / "index.html"
            if not target.exists():
                found.append(Finding("site-anchor-missing", relative, link))
                continue
            fragment = urlsplit(link).fragment
            if fragment:
                target_relative = target.relative_to(site)
                target_page = parsed_pages.get(target_relative)
                if not target_page or fragment not in target_page.ids:
                    found.append(Finding("site-anchor-missing", relative, link))
            elif target.suffix == ".html":
                linked_pages.add(target.relative_to(site))
    found.extend(_sitemap_findings(site, local))
    for relative in parsed_pages:
        if relative.name in {"404.html"} or any(part in ASSET_DIRS for part in relative.parts[:-1]):
            continue
        if relative not in linked_pages:
            found.append(Finding("site-page-orphan", relative, "not linked by a generated page"))
    found.extend(_glossary_findings(site, glossary_source, glossary_route, glossary_snippet,
                                    glossary_term, require_glossary))
    return found


def selftest() -> int:
    with tempfile.TemporaryDirectory() as temp:
        site = Path(temp)
        (site / "assets").mkdir()
        (site / "assets" / "ok.png").write_bytes(b"ok")
        (site / "index.html").write_text('<link rel="canonical" href="https://example.test/"><img src="assets/ok.png"><img src="/assets/ok.png"><a href="#present">ok</a><p id="present">x</p>')
        (site / "sitemap.xml").write_text('<urlset><url><loc>https://example.test/</loc></url></urlset>')
        assert not check(site)
        (site / "index.html").write_text('<img src="missing.png"><a href="#gone">x</a>')
        codes = {finding.code for finding in check(site)}
        assert {"site-asset-missing", "site-anchor-missing"} <= codes, codes
    with tempfile.TemporaryDirectory() as temp:
        site = Path(temp)
        (site / "index.html").write_text('<a href="assets/">asset directory</a><img src="assets/">')
        (site / "assets").mkdir()
        (site / "sitemap.xml").write_text('<urlset><url><loc>index.html</loc></url></urlset>')
        codes = {finding.code for finding in check(site)}
        assert "site-asset-missing" in codes, codes
        assert "site-anchor-missing" not in codes, codes
    with tempfile.TemporaryDirectory() as temp:
        site = Path(temp)
        (site / "a" / "b").mkdir(parents=True)
        (site / "c").mkdir()
        (site / "index.html").write_text('<a href="a/b/">b</a><a href="c/">c</a>')
        (site / "a" / "b" / "index.html").write_text('<a href="../../c/#real">up</a><a href="../../c/#gone">up</a>')
        (site / "c" / "index.html").write_text('<p id="real">x</p>')
        (site / "sitemap.xml").write_text('<urlset><url><loc>index.html</loc></url></urlset>')
        findings = [finding for finding in check(site) if finding.code == "site-anchor-missing"]
        assert [finding.detail for finding in findings] == ["../../c/#gone"], findings
    with tempfile.TemporaryDirectory() as temp:
        root = Path(temp)
        site = root / "site"
        site.mkdir()
        (site / "reference" / "glossary").mkdir(parents=True)
        (site / "reference" / "glossary" / "index.html").write_text('<abbr title="x">ASRC</abbr>')
        source = root / ".knowledge" / "glossary.md"
        source.parent.mkdir()
        source.write_text("- **ASRC** — expected loss stage\n")
        snippet = root / ".knowledge" / "documentation" / "assets" / "glossary-abbreviations.md"
        snippet.parent.mkdir(parents=True)
        snippet.write_text("generated\n")
        (site / "sitemap.xml").write_text('<urlset><url><loc>index.html</loc></url></urlset>')
        assert not _glossary_findings(site, source, "reference/glossary.md", snippet, None, True)
    fixture_root = Path(__file__).with_name("fixtures") / "documentation-site-check"
    expected = {
        "healthy": set(),
        "asset-missing": {"site-asset-missing", "site-sitemap-empty"},
        "anchor-missing": {"site-anchor-missing", "site-sitemap-empty"},
        "sitemap-empty": {"site-sitemap-empty"},
        "page-orphan": {"site-sitemap-empty", "site-page-orphan"},
        "remote-resource": {"site-remote-resource"},
        "local": set(),
        "glossary/site": set(),
    }
    for fixture, expected_codes in expected.items():
        codes = {finding.code for finding in check(fixture_root / fixture, local=fixture == "local")}
        assert expected_codes <= codes, (fixture, codes)
    assert "site-sitemap-empty" in {finding.code for finding in check(fixture_root / "local")}
    glossary_root = fixture_root / "glossary"
    assert not check(
        glossary_root / "site",
        glossary_source=glossary_root / ".knowledge" / "glossary.md",
        glossary_snippet=glossary_root / ".knowledge" / "documentation" / "assets" / "glossary-abbreviations.md",
        require_glossary=True,
    )
    print("documentation-site-check selftest: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", nargs="?", type=Path)
    parser.add_argument("--selftest", action="store_true")
    parser.add_argument("--remote-policy", choices=("warn", "error"), default="warn")
    parser.add_argument("--local", action="store_true",
                        help="allow a local build without a meaningful sitemap URL")
    parser.add_argument("--require-glossary", action="store_true")
    parser.add_argument("--glossary-source", type=Path)
    parser.add_argument("--glossary-route", default="reference/glossary.md")
    parser.add_argument("--glossary-snippet", type=Path)
    parser.add_argument("--glossary-term")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not args.site or not args.site.is_dir():
        parser.error("site must be an existing directory")
    source = args.glossary_source
    if args.require_glossary and source is None:
        source = args.site.parent / ".knowledge" / "glossary.md"
    findings = check(args.site, local=args.local, glossary_source=source,
                     glossary_route=args.glossary_route, glossary_snippet=args.glossary_snippet,
                     glossary_term=args.glossary_term, require_glossary=args.require_glossary)
    for finding in findings:
        policy = "warning" if finding.code == "site-remote-resource" and args.remote_policy == "warn" else "error"
        print(f"{policy}: {finding.code}: {finding.path}: {finding.detail}")
    blocking = [f for f in findings if f.code != "site-remote-resource" or args.remote_policy == "error"]
    return 1 if blocking else 0


if __name__ == "__main__":
    raise SystemExit(main())
