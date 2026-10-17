"""The `config` pillar's own entry point — read-only views over the configuration layers.

`show --effective` prints every key with its effective value and the layer that supplied it
(`default`, `user`, `repository`, `branch`)."""
from __future__ import annotations

import argparse
import json
import os
import shlex
import sys

from quenching.common.front import resolve_root
from quenching.common.output import REFUSAL, NoAbbrevParser, emit
from quenching.common.version import VERSION
from quenching.config.effective import effective
from quenching.config.host import build_plan, load_settings


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
    return "\n".join(lines)


def cmd_show(args) -> int:
    if not args.effective:
        print("cq config show: --effective is required", file=sys.stderr)
        return 3
    payload = {"ok": True, **effective(resolve_root(args.root))}
    emit(args.json, payload, _render(payload))
    return 0


def cmd_host(args) -> int:
    settings, warnings = load_settings(resolve_root(args.root))
    payload = {"ok": True, **settings, "warnings": warnings}
    if args.plan:
        command = [c for c in args.command if c != "--"] if args.command else []
        try:
            steps, notes = build_plan(settings, os.path.basename(resolve_root(args.root)), command)
        except ValueError as exc:
            print(f"cq config host: {exc}", file=sys.stderr)
            return REFUSAL
        payload.update(steps=steps, notes=notes)
        text = "\n".join(f"{s['step']:<5} {shlex.join(s['argv'])}" for s in steps)
        text += "".join(f"\nnote: {n}" for n in notes)
    else:
        text = "\n".join(f"{k} = {json.dumps(v, ensure_ascii=False)}"
                         for k, v in settings.items())
    text += "".join(f"\nwarning: {w}" for w in warnings)
    emit(args.json, payload, text)
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
    hp = sub.add_parser("host", help="print the work host (`shared.workHost`) and its dispatch plan")
    hp.add_argument("--plan", action="store_true",
                    help="print the dispatch steps for the command after `--`; runs nothing")
    hp.add_argument("--json", action="store_true", help="machine-readable output")
    hp.add_argument("command", nargs="*", help="the command to dispatch, after `--`")
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
    return cmd_host(args) if args.cmd == "host" else cmd_show(args)
