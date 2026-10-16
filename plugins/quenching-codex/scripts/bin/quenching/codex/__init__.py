"""The ``codex`` pillar: whether the Codex quota allows a call, and nothing that writes code.

    cq codex probe [--json]    exit 0 available · 1 unavailable · 2 unknown (the quota);
                               `sandbox` says whether Codex can run commands on this host
    cq codex review --worktree <dir> --prompt <file> [--base <ref> [--head <ref>]]
                    [--run <name>] [--json]
                               exit 0 reviewed · 1 fall back to Codex · 2 refusal
"""
from __future__ import annotations

import argparse
import json
import os

from quenching.codex.config import load_settings
from quenching.codex.probe import EXIT, probe, sandbox
from quenching.codex.review import run_review
from quenching.common.front import resolve_root
from quenching.common.output import NoAbbrevParser, emit, refuse
from quenching.common.version import VERSION


def build_parser() -> argparse.ArgumentParser:
    common = NoAbbrevParser(add_help=False)
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
    review = sub.add_parser("review", parents=[common],
                            help="run codex exec read-only over a worktree, prompt on stdin")
    review.add_argument("--worktree", required=True, help="the checkout Codex reviews")
    review.add_argument("--prompt", required=True, help="file whose text is sent on stdin")
    review.add_argument("--run", help="run name under .quenching/codex/ (default: UTC stamp)")
    review.add_argument("--base", help="the ref whose diff goes into the prompt when the "
                                       "sandbox is unavailable")
    review.add_argument("--head", default="HEAD", help="the diff's other end (default: HEAD)")
    return parser


def _probe(root: str, as_json: bool) -> int:
    settings, warnings = load_settings(root)
    payload = probe(settings)
    payload = {"ok": payload["state"] == "available", **payload,
               "sandbox": sandbox(settings, root), "warnings": warnings}
    source = payload["source"] or "no source"
    emit(as_json, payload, f"codex probe — {payload['state']} ({source}): {payload['reason']}; "
                           f"sandbox: {payload['sandbox']['state']} ({payload['sandbox']['reason']})")
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
    if args.command == "probe":
        return _probe(root, as_json)
    settings, warnings = load_settings(root)
    payload, code = run_review(root, settings, args.worktree, args.prompt, args.run,
                               base=args.base, head=args.head)
    if code == 2:
        return refuse({k: v for k, v in payload.items() if k != "ok"}, as_json)
    payload["findingsNeedReproduction"] = True  # a Codex finding is work only once reproduced
    payload["warnings"] = warnings
    tokens = payload["tokens"]
    if isinstance(tokens, dict):
        tokens = tokens.get("total_tokens", json.dumps(tokens))
    emit(as_json, payload,
         f"codex review — {payload['reason']}; tokens: {tokens}; mode: {payload['mode']}; "
         f"run: {payload['runDir']}")
    return code
