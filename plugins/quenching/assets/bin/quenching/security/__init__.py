"""The read-only ``security`` pillar and its live questions."""
from __future__ import annotations

import argparse

from quenching.common.front import resolve_root
from quenching.common.output import emit, refuse
from quenching.common.version import VERSION
from quenching.security.probe import build_report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cq security",
        description="report live security questions without changing the repository",
    )
    parser.add_argument("--root", help="repository root (default: current directory)")
    parser.add_argument("--version", action="store_true", help="print the security version")
    parser.add_argument("command", nargs="?", choices=("audit", "status"), default="audit",
                        help="read-only audit (the default) or its status alias")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    return parser


def _human(payload: dict) -> str:
    states = ", ".join(f"{item['key']}={item['state']}" for item in payload["questions"])
    return f"security audit — {payload['root']} (read-only); {states}"


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq security {VERSION}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = bool(args.json)
    root = resolve_root(args.root)
    if not os.path.isdir(root):
        return refuse({
            "code": "security-root-missing",
            "exit": 2,
            "root": root,
            "message": f"repository root does not exist: {root}",
        }, as_json)
    payload = build_report(root).as_dict()
    emit(as_json, payload, _human(payload))
    return 0 if payload["ok"] else 2
