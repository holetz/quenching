"""The `cq ops` argument parser and its three read-only subcommands."""
from __future__ import annotations

import argparse
import os
import sys
from collections import Counter

from quenching.common.output import emit, refuse
from quenching.common.version import VERSION
from quenching.ops.doctor import doctor as run_doctor, inspect_ops
from quenching.ops.inventory import build_inventory


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cq ops",
        description="read and verify a repository's declared operations surface",
    )
    parser.add_argument("--root", help="repository root (default: current directory)")
    parser.add_argument("--version", action="store_true", help="print the ops pillar version")
    sub = parser.add_subparsers(dest="cmd")
    for name, help_text in (
        ("inventory", "walk the declared operations tree and print its read model"),
        ("doctor", "run the static operations checks"),
        ("status", "summarize packages, lifecycle, router, and findings"),
    ):
        child = sub.add_parser(name, help=help_text)
        child.add_argument("--json", action="store_true", help="print machine-readable output")
    return parser


def _root(value: str | None) -> str:
    return os.path.abspath(value or os.getcwd())


def _human_inventory(payload: dict) -> str:
    router = payload["router"]
    return (f"ops inventory — {payload['root']}\n"
            f"  entry points: {len(payload['entryPoints'])}\n"
            f"  router: {router['path']} ({router['kind'] or 'unsupported'})")


def _human_doctor(payload: dict) -> str:
    lines = [f"ops doctor — {payload['root']} ({len(payload['findings'])} finding(s))"]
    for finding in payload["findings"]:
        lines.append(f"  [{finding['severity']:<5}] {finding.get('path', '-')} — "
                     f"{finding['message']} ({finding['code']})")
    if not payload["findings"]:
        lines.append("  OK — no findings.")
    return "\n".join(lines)


def _status_payload(payload: dict) -> dict:
    entries = payload["entryPoints"]
    packages = Counter(
        entry["path"].split("/", 1)[0] if "/" in entry["path"] else "."
        for entry in entries
    )
    lifecycle = Counter(entry["lifecycle"] or "undeclared" for entry in entries)
    finding_tally = Counter(finding["code"] for finding in payload["findings"])
    router = payload["router"]
    return {
        "root": payload["root"],
        "scanned": payload["scanned"],
        "packages": dict(sorted(packages.items())),
        "router": {
            "path": router["path"],
            "kind": router["kind"],
            "exists": router["exists"],
            "health": "ok" if router["exists"] and router["kind"] else "missing",
        },
        "lifecycle": dict(sorted(lifecycle.items())),
        "findings": dict(sorted(finding_tally.items())),
        "errors": payload["errors"],
        "warnings": payload["warnings"],
        "ok": payload["ok"],
    }


def _human_status(payload: dict) -> str:
    router = payload["router"]
    return (f"ops status — {payload['root']}\n"
            f"  packages: {', '.join(f'{k}={v}' for k, v in payload['packages'].items()) or '(none)'}\n"
            f"  router: {router['path']} ({router['health']})\n"
            f"  lifecycle: {', '.join(f'{k}={v}' for k, v in payload['lifecycle'].items()) or '(none)'}\n"
            f"  findings: {', '.join(f'{k}={v}' for k, v in payload['findings'].items()) or '(none)'}")


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq ops {VERSION}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    as_json = bool(getattr(args, "json", False))
    if not args.cmd:
        return refuse({"code": "op-no-command", "message": "choose `inventory`, `doctor`, "
                       "or `status`"}, as_json)
    root = _root(args.root)
    if args.cmd == "inventory":
        payload, err = build_inventory(root)
        if err:
            return refuse(err, as_json)
        assert payload is not None
        emit(as_json, payload.as_dict(), _human_inventory(payload.as_dict()))
        return 0
    if args.cmd == "doctor":
        payload, err, code = run_doctor(root)
        if err:
            return refuse(err, as_json)
        assert payload is not None
        emit(as_json, payload, _human_doctor(payload))
        return code
    payload, err = inspect_ops(root)
    if err:
        return refuse(err, as_json)
    assert payload is not None
    summary = _status_payload(payload)
    emit(as_json, summary, _human_status(summary))
    return 0 if summary["ok"] else 1
