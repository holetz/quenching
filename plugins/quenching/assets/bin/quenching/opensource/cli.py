"""The ``cq opensource`` route: read-only ``doctor`` and ``status``."""
from __future__ import annotations

import argparse
import os

from quenching.common.front import build_parser as build_front_parser, resolve_root
from quenching.common.output import emit, refuse
from quenching.common.version import VERSION
from quenching.opensource.aggregate import doctor, status


def build_parser() -> argparse.ArgumentParser:
    parser = build_front_parser(
        "cq opensource", "aggregate the open source catalog by owner and report the baseline level",
        (("doctor", "probe applicability, template integrity and the opensource findings"),
         ("status", "read every owner's catalog answers and the baseline level, read-only")),
    )
    parser.add_argument("--version", action="store_true", help="print the opensource version")
    return parser


def _human(payload: dict) -> str:
    baseline = payload["baseline"]
    codes = ", ".join(sorted({row["code"] for row in payload["findings"]})) or "none"
    return (f"opensource {payload.get('applicability', {}).get('state', 'status')} — {payload['root']}; "
            f"baseline {baseline['version']} level {baseline['level']}; findings: {codes}")


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq opensource {VERSION}")
        return 0
    args = build_parser().parse_args(argv)
    as_json = bool(getattr(args, "json", False))
    if not args.cmd:
        return refuse({"code": "os-no-command", "message": "choose `doctor` or `status`"}, as_json)
    root = resolve_root(args.root)
    if not os.path.isdir(root):
        return refuse({"code": "os-root-missing", "root": root,
                       "message": f"repository root does not exist: {root}"}, as_json)
    payload = doctor(root) if args.cmd == "doctor" else status(root)
    emit(as_json, payload, _human(payload))
    return 0 if payload["ok"] else 1
