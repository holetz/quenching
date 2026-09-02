"""The components pillar's argument declarations, its subcommand map, and its entry point.

`build_parser` declares every argument, `DISPATCH` maps a subcommand name to the function that
answers it, and `main` is the pillar's whole entry: the UTF-8 reconfiguration, the `--version`
short-circuit, and the surface resolution every verb is handed.

WHY THE TABLE IS LITERAL. The pre-refactor components script kept two empty dicts at the top of
the file and filled them
from a `register()` call sitting after each verb — registration as an import side effect, spread
over five places. Cut into modules that stops working the moment a submodule is imported in a
different order, or not imported at all, and the failure is a subcommand that silently does not
exist rather than an ImportError. The specs pillar answered this with a literal `DISPATCH` beside
a `build_parser` that declares its subparsers inline, and this is the same answer: the order the
subparsers are declared here IS the order `register()` produced, so `--help` reads as it did.

`selftest` is NOT here. Its fixtures and `cmd_selftest` are tests and migrate to `tests/`;
whether the verb survives is task 6.3's to decide, and re-adding it is one subparser and one
`DISPATCH` row.
"""
from __future__ import annotations

import argparse
import sys

from quenching.common.output import CQArgumentParser, refuse
from quenching.common.version import VERSION
from quenching.components.commands.doctor import cmd_doctor
from quenching.components.commands.lint import cmd_lint
from quenching.components.commands.read import cmd_read
from quenching.components.commands.registry import REGISTRY_RELPATH, cmd_registry
from quenching.components.commands.translate import add_arguments as add_translate_arguments
from quenching.components.commands.translate import cmd_translate
from quenching.components.sections import RULES_MARKER
from quenching.components.surface import find_surface_root
from quenching.session.commands.cli import add_subcommands as add_session_subcommands


def build_parser() -> argparse.ArgumentParser:
    p = CQArgumentParser(prog="cq components",
                         description="deterministic trail for the .claude/ front")
    p.add_argument("--root", help="the surface root holding commands/ "
                                  "(default: nearest .claude/ or commands/ upward)")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")

    def add_json(sp):
        sp.add_argument("--json", action="store_true", help="machine-readable output")
        return sp

    sp = sub.add_parser("lint")
    sp.add_argument("path", nargs="?",
                    help="a command file, a commands/ directory, or a surface root")
    add_json(sp)

    add_json(sub.add_parser("doctor"))

    sp = sub.add_parser("registry")
    sp.add_argument("registry_cmd", choices=["reindex"])
    sp.add_argument("--registry", help="path to the registry doc "
                                       "(default: nearest "
                                       f"{'/'.join(REGISTRY_RELPATH)} upward)")
    add_json(sp)

    sp = sub.add_parser("read")
    sp.add_argument("path", help="a markdown file")
    sp.add_argument("--sections", action="append", default=[],
                    help="a section name, or several comma-separated; "
                         "repeatable. A value that resolves whole is "
                         "never split, so a heading carrying a comma is "
                         "cited in full. A unique prefix resolves. Omit "
                         "for the file's heading index")
    sp.add_argument("--rules-only", action="store_true",
                    help=f"only the {RULES_MARKER} half of each section; "
                         f"a section with no marker comes back whole and "
                         f"says so")
    add_json(sp)

    sp = sub.add_parser("translate",
                        help="translate and reconcile the Claude and Codex surfaces")
    add_translate_arguments(sp)

    sp = sub.add_parser("session",
                        help="read a Claude Code session transcript as evidence")
    add_session_subcommands(sp.add_subparsers(dest="session_cmd", required=True))

    return p


def cmd_session(args, root: str) -> int:
    """The session pillar, mounted here rather than at the root of `cq`.

    The spec's `## Open Decisions` asked whether `session` survives as a first-level
    pillar and answered it by count: one command body invokes the tool, and it is a
    components command. So the tool follows its caller into this front.

    `root` is this front's surface root and the session verbs have no use for it — their
    input is `~/.claude/projects/**`, the operator's machine, not a repo. It is accepted
    and dropped so the row keeps `DISPATCH`'s one signature."""
    return args.func(args)


DISPATCH: dict = {
    "lint": cmd_lint,
    "doctor": cmd_doctor,
    "registry": cmd_registry,
    "read": cmd_read,
    "translate": cmd_translate,
    "session": cmd_session,
}


def _force_utf8_output() -> None:
    """Skill descriptions are prose — em-dashes, arrows, accented words — and a Windows
    console defaults to cp1252, where printing one raises UnicodeEncodeError AFTER the
    write already landed. That turns a clean report into a traceback and a nonzero exit,
    which the exit-code contract (0 ok / 1 findings / 2 refusal) reads as a finding.
    Encode output as UTF-8 and never let a glyph decide the exit code."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, OSError, ValueError):
            pass


def main(argv: list[str]) -> int:
    _force_utf8_output()
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(f"cq components {VERSION}")
        return 0
    if not args.cmd:
        return refuse({"code": "ct-no-command", "message":
                       "choose `lint`, `doctor`, `registry`, `read`, `translate`, or `session`"},
                      False)
    if not hasattr(args, "json"):
        args.json = False
    return DISPATCH[args.cmd](args, find_surface_root(args.root))
