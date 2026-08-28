#!/usr/bin/env python3
"""Inspect rendered HTML for explicitly enabled Zensical capability effects."""
from __future__ import annotations

import argparse
from pathlib import Path


EXPECTED = {
    "autorefs": ("href=\"#stable-heading\"",),
    "mkdocstrings": ("api-signature",),
    "preview": ("127.0.0.1",),
    "tags": ("data-tags=\"",),
    "provenance": ("class=\"provenance\"",),
}


def check(path: Path, enabled: list[str]) -> list[str]:
    body = path.read_text(encoding="utf-8")
    return [f"capability-effect-missing: {name}"
            for name in enabled
            if name in EXPECTED and not any(token in body for token in EXPECTED[name])]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("html", type=Path, nargs="?", default=Path(__file__).parent / "fixtures" / "zensical-capabilities" / "healthy" / "index.html")
    parser.add_argument("--enabled", default=",")
    args = parser.parse_args()
    enabled = [name for name in args.enabled.split(",") if name]
    errors = check(args.html, enabled)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"zensical-capability-check: OK ({args.html})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
