#!/usr/bin/env python3
"""Deterministic structural checks for a built Zensical site."""

from __future__ import annotations

import argparse
import tempfile
from dataclasses import dataclass
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
from xml.etree import ElementTree


REMOTE_SCHEMES = {"http", "https"}
SKIPPED_SCHEMES = {"", "data", "mailto", "tel", "javascript"}


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
            else:
                self.assets.append(value)


def pages(site: Path) -> dict[Path, Page]:
    result: dict[Path, Page] = {}
    for path in site.rglob("*.html"):
        page = Page()
        page.feed(path.read_text(encoding="utf-8"))
        result[path.relative_to(site)] = page
    return result


def local_target(base: Path, raw: str) -> tuple[Path | None, str]:
    parsed = urlsplit(raw)
    if parsed.scheme in REMOTE_SCHEMES:
        return None, "remote"
    if parsed.scheme in SKIPPED_SCHEMES and not parsed.path and not parsed.fragment:
        return None, "skip"
    if parsed.scheme:
        return None, "skip"
    path = Path(parsed.path)
    return ((base / path if not parsed.path.startswith("/") else path), parsed.fragment)


def check(site: Path) -> list[Finding]:
    found: list[Finding] = []
    parsed_pages = pages(site)
    linked_pages: set[Path] = {Path("index.html")}
    for relative, page in parsed_pages.items():
        base = (site / relative).parent
        for asset in page.assets:
            target, kind = local_target(base, asset)
            if kind == "remote":
                found.append(Finding("site-remote-resource", relative, asset))
            elif target and not target.exists():
                found.append(Finding("site-asset-missing", relative, asset))
        for link in page.links:
            target, kind = local_target(base, link)
            if kind == "remote":
                continue
            if not target:
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
    sitemap = site / "sitemap.xml"
    if not sitemap.exists():
        found.append(Finding("site-sitemap-empty", sitemap.relative_to(site), "missing sitemap.xml"))
    else:
        try:
            root = ElementTree.parse(sitemap).getroot()
            if not any(node.tag.endswith("loc") and (node.text or "").strip() for node in root.iter()):
                found.append(Finding("site-sitemap-empty", sitemap.relative_to(site), "no URLs"))
        except ElementTree.ParseError as error:
            found.append(Finding("site-sitemap-empty", sitemap.relative_to(site), f"invalid XML: {error}"))
    for relative in parsed_pages:
        if relative.name in {"404.html"} or relative.parts[0] == "assets":
            continue
        if relative not in linked_pages:
            found.append(Finding("site-page-orphan", relative, "not linked by a generated page"))
    return found


def selftest() -> int:
    with tempfile.TemporaryDirectory() as temp:
        site = Path(temp)
        (site / "assets").mkdir()
        (site / "assets" / "ok.png").write_bytes(b"ok")
        (site / "index.html").write_text('<img src="assets/ok.png"><a href="#present">ok</a><p id="present">x</p>')
        (site / "sitemap.xml").write_text('<urlset><url><loc>https://example.test/</loc></url></urlset>')
        assert not check(site)
        (site / "index.html").write_text('<img src="missing.png"><a href="#gone">x</a>')
        codes = {finding.code for finding in check(site)}
        assert {"site-asset-missing", "site-anchor-missing"} <= codes, codes
    print("documentation-site-check selftest: OK")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("site", nargs="?", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not args.site or not args.site.is_dir():
        parser.error("site must be an existing directory")
    findings = check(args.site)
    for finding in findings:
        print(f"{finding.code}: {finding.path}: {finding.detail}")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
