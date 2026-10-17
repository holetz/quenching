"""The `config` pillar's own entry point — read-only views over the configuration layers.

`show --effective` prints every key with its effective value and the layer that supplied it
(`default`, `user`, `repository`, `branch`)."""
from __future__ import annotations

import argparse
import json
import sys

from quenching.common.front import resolve_root
from quenching.common.output import REFUSAL, NoAbbrevParser, emit
from quenching.common.version import VERSION
from quenching.config.effective import effective


def _render(payload: dict) -> str:
    lines = ["layers (low to high precedence):"]
    for layer in payload["layers"]:
        state = ("unparseable: " + layer["unparseable"] if layer["unparseable"]
                 else "present" if layer["present"] else "absent")
        if layer.get("applies") is False:
            state = "not applied (backend is not git)"
        lines.append(f"  {layer['name']:<11} {layer['path'] or '-'}  [{state}]")
    lines.append("")
    width = max((len(row["key"]) for row in payload["values"]), default=0)
    for row in payload["values"]:
        lines.append(f"{row['key']:<{width}} = {json.dumps(row['value'], ensure_ascii=False)}"
                     f"  [{row['source']}]")
    if payload.get("warnings"):
        lines.extend(["", "warnings:", *(f"  {warning}" for warning in payload["warnings"])])
    return "\n".join(lines)


def cmd_show(args) -> int:
    if not args.effective:
        print("cq config show: --effective is required", file=sys.stderr)
        return 3
    payload = {"ok": True, **effective(resolve_root(args.root))}
    emit(args.json, payload, _render(payload))
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = NoAbbrevParser(prog="cq config", description="the configuration layers, read-only")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    p.add_argument("--root", help="repository root (default: current directory)")
    sub = p.add_subparsers(dest="cmd")
    sp = sub.add_parser("show", help="print the effective configuration with each value's layer")
    sp.add_argument("--effective", action="store_true",
                    help="every key with its effective value and source layer")
    sp.add_argument("--json", action="store_true", help="machine-readable output")
    return p


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq config {VERSION}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_usage(sys.stderr)
        return REFUSAL
    return cmd_show(args)
