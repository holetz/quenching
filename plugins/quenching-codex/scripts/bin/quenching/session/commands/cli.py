"""The session pillar's argument declarations, its subcommand map, and its entry point.

`add_subcommands` declares the verbs onto ANY `argparse` subparsers action, `DISPATCH`
maps a subcommand name to the function that answers it, `build_parser` wraps the verbs
in this pillar's own standalone parser, and `main` is the standalone entry point.
Mounting is therefore the CALLER's choice and not this module's: `cq session …` and
`cq components session …` both mount by handing `add_subcommands` their own subparsers
action, and neither path is named anywhere below.

`selftest` is NOT here. `cmd_selftest` and the three fixtures are tests and migrate to
`tests/`; re-adding the verb is one subparser and one `DISPATCH` row.

Moved verbatim out of the pre-refactor session script, whose module docstring carried the two sections
below unchanged. Two adjustments to what they say: `VERSION` is now IMPORTED from
`quenching.common.version` rather than declared "below" — the same constant at the same
value, declared once for the four pillars — and `--json` is now proved by `tests/`
rather than by the `selftest` verb that left with the fixtures.

WHY IT IS NOT INSTALLED
-----------------------
The three shipped tools read the repo being aligned, so each target needs its own copy
and each align upgrades that copy by comparing `--version`. This tool's input is
`~/.codex/projects/**` — the *operator's machine*, not the repo. There is nothing for a
target repo to hold, so nothing installs it.

Two consequences follow, and both are deliberate:

  * It is **outside the six-artifact lockstep** of `/docs/standards/ci-cd/versioning-release.md`.
    That lockstep exists because an align must decide whether an installed copy is stale;
    with no installed copy there is no such decision. `VERSION` below tracks the plugin for
    a legible `--version`, and no align compares it against anything.
  * The pre-refactor components script's stated contract — it reads `commands/**` and nothing
    else — stays intact.
    Folding a transcript reader into it would have broken that sentence.


THE TOOL CONTRACT
-----------------
Same shape as its three siblings, so a command body branches on DATA and never on prose:
every subcommand takes `--json`, and the exit code is the whole decision.

    0   ok            read clean: every record parsed and every stage's attribution closed
    1   findings      read and reported, with an anomaly against it — an unparsable record,
                      or a stage whose counts are an upper bound. The numbers are real; the
                      coverage is not provably complete
    2   refusal       nothing usable: no transcript, an empty one, a non-empty one that
                      yielded no command, or a `--command` that is not in it

Exit 1 exists so a caller can tell "clean read" from "read with holes" without parsing the
anomaly list. It is not a failure — the findings are printed either way.
"""
from __future__ import annotations

import argparse

from quenching.common.output import OK
from quenching.common.version import VERSION
from quenching.session.commands.digest import cmd_digest
from quenching.session.commands.read import cmd_list


def add_subcommands(sub: argparse._SubParsersAction) -> argparse._SubParsersAction:
    """Declare this pillar's verbs onto a subparsers action the caller owns."""
    sp = sub.add_parser("list", help="every command a session ran, with its tool-call span")
    sp.add_argument("transcript", nargs="?",
                    help="path to a .jsonl transcript, or a session id; "
                         "default: the most recent session for this cwd")
    sp.add_argument("--json", action="store_true", help="machine-readable output")
    sp.set_defaults(func=cmd_list)

    dg = sub.add_parser("digest", help="one command's evidence: counts, redundant reads, corrections")
    dg.add_argument("transcript", nargs="?", help="path to a .jsonl transcript, or a session id")
    dg.add_argument("--command", help="digest only this command (default: all of them)")
    dg.add_argument("--json", action="store_true", help="machine-readable output")
    dg.add_argument("--max-quote", type=int, default=200, metavar="N",
                    help="clip every quoted string to N characters (default: 200)")
    dg.add_argument("--cap", type=int, default=20, metavar="N",
                    help="at most N items per evidence list (default: 20)")
    dg.set_defaults(func=cmd_digest)
    return sub


DISPATCH: dict = {
    "list": cmd_list,
    "digest": cmd_digest,
}


def build_parser(prog: str = "cq components session") -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(prog=prog,
                                description="read a Codex session transcript as evidence")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")
    add_subcommands(sub)
    return p


def main(argv: list[str]) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.version:
        print(f"session {VERSION}")
        return OK
    if not getattr(args, "func", None):
        parser.print_help()
        return OK
    return args.func(args)
