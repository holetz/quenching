"""The read-only ``security`` pillar: its live questions, and the leak gate's scanner.

``leak`` reads and answers through its exit code (0 clean, 1 findings, 2 configuration); the hook
that calls it is what refuses the commit or the push. ``identity`` is the same gate narrowed to the
declared email allowlist (`shared.gitIdentity.allowedEmails`): the hooks `cq deploy` ships into a
target call it, so a target gets the identity check without the content patterns.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys

from quenching.common import identity, leak
from quenching.common.front import resolve_root
from quenching.common.output import NoAbbrevParser, emit, refuse
from quenching.common.version import VERSION
from quenching.controls.evaluate import owner_controls, summary_line
from quenching.security.probe import build_report


def build_parser() -> argparse.ArgumentParser:
    parser = NoAbbrevParser(
        prog="cq security",
        description="report live security questions without changing the repository",
    )
    parser.add_argument("--root", help="repository root (default: current directory)")
    parser.add_argument("--version", action="store_true", help="print the security version")
    parser.add_argument("command", nargs="?", choices=("audit", "status", "leak", "identity"),
                        default="audit",
                        help="read-only audit (the default), its status alias, the leak gate, or "
                             "the identity allowlist alone")
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--staged", action="store_true",
                      help="leak: staged content and the configured author email (pre-commit)")
    mode.add_argument("--pre-push", action="store_true",
                      help="leak: the commits named on stdin by the pre-push hook")
    mode.add_argument("--all", action="store_true", help="leak: every tracked file")
    parser.add_argument("--remote", help="leak --pre-push: the destination remote's name (the "
                                         "hook's first argument)")
    parser.add_argument("--generic-only", action="store_true",
                        help="leak: skip the private denylist (CI)")
    parser.add_argument("--json", action="store_true", help="print machine-readable output")
    return parser


def _human(payload: dict) -> str:
    states = ", ".join(f"{item['key']}={item['state']}" for item in payload["questions"])
    return (f"security audit — {payload['root']} (read-only); {states}; "
            f"{summary_line(payload['controls'])}")


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
    if args.command == "leak":
        return _leak(args, root, as_json)
    if args.command == "identity":
        return _identity(args, root, as_json)
    if args.staged or args.pre_push or args.all or args.generic_only or args.remote:
        parser.error("--staged, --pre-push, --all, --remote and --generic-only belong to `leak`")
    payload = build_report(root).as_dict()
    payload["controls"] = owner_controls("security", root)
    emit(as_json, payload, _human(payload))
    return 0 if payload["ok"] else 2


def _leak(args: argparse.Namespace, root: str, as_json: bool) -> int:
    if not (args.staged or args.pre_push or args.all):
        return refuse({"code": "leak-mode-missing",
                       "message": "`leak` needs one of --staged, --pre-push or --all"}, as_json)
    try:
        pats = leak.patterns(generic_only=args.generic_only)
    except leak.DenylistMissing as missing:
        return refuse({"code": "leak-denylist-missing", "path": str(missing.path),
                       "message": f"{missing}; create it (one regex per line), set "
                                  f"{leak.DENYLIST_ENV}, or pass --generic-only"}, as_json)
    allow = _allowlist(root, as_json)
    if isinstance(allow, int):
        return allow
    mode = "staged" if args.staged else "pre-push" if args.pre_push else "all"
    hook_input = sys.stdin.read() if args.pre_push else ""
    try:
        if args.staged:
            found = leak.scan_staged(root, pats)
        elif args.pre_push:
            found = leak.scan_push(root, hook_input, pats, args.remote)
        else:
            found = leak.scan_all(root, pats)
        found += _identity_findings(args, root, allow, hook_input)
    except subprocess.CalledProcessError as failed:
        return _git_failed(failed, as_json)
    payload = {"ok": not found, "mode": mode, "genericOnly": bool(args.generic_only),
               "findings": [f.as_dict() for f in found]}
    return _report("leak gate", mode, found, payload, as_json)


def _allowlist(root: str, as_json: bool) -> list[str] | None | int:
    """The declared allowlist, `None` when undeclared, or the exit code of its refusal."""
    try:
        return identity.load_allowlist(root)
    except identity.AllowlistInvalid as invalid:
        return refuse({"code": "identity-allowlist-invalid", "key": identity.KEY,
                       "message": str(invalid),
                       "remedy": f"declare {identity.KEY} as a list such as "
                                 '["you@example.org", "*@users.noreply.github.com"], or remove it'},
                      as_json)


def _identity_findings(args: argparse.Namespace, root: str, allow: list[str] | None,
                       hook_input: str) -> list[leak.Finding]:
    if not allow:
        return []
    if args.staged:
        return identity.staged_findings(root, allow)
    if args.pre_push:
        return identity.push_findings(root, hook_input, allow, args.remote)
    return []


def _git_failed(failed: subprocess.CalledProcessError, as_json: bool) -> int:
    return refuse({"code": "leak-git-failed",
                   "message": f"git failed while scanning: {(failed.stderr or '').strip()}"}, as_json)


def _report(gate: str, mode: str, found: list[leak.Finding], payload: dict, as_json: bool) -> int:
    lines = [f.render() for f in found]
    labels = {f.label for f in found}
    if identity.LABEL in labels:
        lines.append(identity.STAGED_REMEDY if mode == "staged" else identity.PUSH_REMEDY)
    lines.append(f"{gate} ({mode}): {len(found)} finding(s)" if found else f"{gate} ({mode}): clean")
    emit(as_json, payload, "\n".join(lines))
    return 1 if found else 0


def _identity(args: argparse.Namespace, root: str, as_json: bool) -> int:
    if args.all or args.generic_only:
        return refuse({"code": "identity-mode-invalid",
                       "message": "`identity` takes --staged or --pre-push [--remote], never "
                                  "--all or --generic-only"}, as_json)
    if not (args.staged or args.pre_push):
        return refuse({"code": "identity-mode-missing",
                       "message": "`identity` needs one of --staged or --pre-push"}, as_json)
    allow = _allowlist(root, as_json)
    if isinstance(allow, int):
        return allow
    mode = "staged" if args.staged else "pre-push"
    hook_input = sys.stdin.read() if args.pre_push else ""
    try:
        found = _identity_findings(args, root, allow, hook_input)
    except subprocess.CalledProcessError as failed:
        return _git_failed(failed, as_json)
    payload = {"ok": not found, "mode": mode, "declared": allow is not None,
               "allowedEmails": allow or [], "findings": [f.as_dict() for f in found]}
    if allow is None and not as_json:
        emit(as_json, payload, f"identity gate ({mode}): no {identity.KEY} declared; nothing judged")
        return 0
    return _report("identity gate", mode, found, payload, as_json)
