"""The ``codex`` pillar: whether the Codex quota allows a call, and nothing that writes code.

    cq codex probe [--json]    exit 0 available · 1 unavailable · 2 unknown
"""
from __future__ import annotations

import argparse
import os

from quenching.codex.config import load_settings
from quenching.codex.probe import EXIT, probe
from quenching.common.front import resolve_root
from quenching.common.output import NoAbbrevParser, emit, refuse
from quenching.common.version import VERSION


def build_parser() -> argparse.ArgumentParser:
    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--root", default=argparse.SUPPRESS,
                        help="repository root whose .claude/quenching.json is read")
    common.add_argument("--json", action="store_true", default=argparse.SUPPRESS,
                        help="print machine-readable output")
    parser = NoAbbrevParser(prog="cq codex", parents=[common],
                            description="read the Codex quota and run Codex read-only")
    parser.add_argument("--version", action="store_true", help="print the codex version")
    sub = parser.add_subparsers(dest="command", required=True)
    sub.add_parser("probe", parents=[common],
                   help="exit 0 when the quota allows a call, 1 when it does not, 2 when unknown")
    return parser


def _probe(root: str, as_json: bool) -> int:
    settings, warnings = load_settings(root)
    payload = probe(settings)
    payload = {"ok": payload["state"] == "available", **payload, "warnings": warnings}
    source = payload["source"] or "no source"
    emit(as_json, payload, f"codex probe — {payload['state']} ({source}): {payload['reason']}")
    return EXIT[payload["state"]]


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq codex {VERSION}")
        return 0
    args = build_parser().parse_args(argv)
    as_json = bool(getattr(args, "json", False))
    root = resolve_root(getattr(args, "root", None))
    if not os.path.isdir(root):
        return refuse({"code": "codex-root-missing", "root": root,
                       "message": f"repository root does not exist: {root}"}, as_json)
    return _probe(root, as_json)
