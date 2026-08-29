#!/usr/bin/env python3
"""Check a derived catalog index and its detail-page lineage contract."""
from __future__ import annotations

import argparse
import re
from pathlib import Path

LINK = re.compile(r"\]\(([^)#]+)(?:#[^)]+)?\)")
REQUIRED = ("id", "layer", "schema", "lineage")


def check(root: Path) -> list[str]:
    index = root / "reference" / "catalog" / "index.md"
    errors: list[str] = []
    if not index.is_file():
        return [f"site-catalog-index-missing: {index}"]
    links = [match.group(1) for match in LINK.finditer(index.read_text(encoding="utf-8"))]
    if not links:
        errors.append("site-catalog-index-empty: no detail routes")
    for link in links:
        target = (index.parent / link).resolve()
        if not target.is_file():
            errors.append(f"site-catalog-route-missing: {link}")
            continue
        body = target.read_text(encoding="utf-8")
        missing = [key for key in REQUIRED if not re.search(rf"^\s*{re.escape(key)}\s*:", body, re.M)]
        if missing:
            errors.append(f"site-catalog-lineage-missing: {link} ({', '.join(missing)})")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", type=Path, nargs="?", default=Path("docs"))
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        base = Path(__file__).parent / "fixtures" / "catalog-publication" / "healthy"
        errors = check(base)
        if errors:
            print("catalog-publication-check selftest: FAIL")
            print("\n".join(errors))
            return 1
        print("catalog-publication-check selftest: OK")
        return 0
    errors = check(args.root)
    if errors:
        print("\n".join(errors))
        return 1
    print(f"catalog-publication-check: OK ({args.root})")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
