"""The `git` pillar's own entry point — deterministic subcommands over a repository's git
facts. No `doctor` and no `validate`: there is no artifact here for either to check, only
questions git (and, where declared, a host CLI) already has answers for — `## Design` of the
`pilar-git-e-specs-agnosticas-ao-git` spec says why the column stays 1x5 with this row
undoctored.

`base` is minted first (task 3.1). `specs`, `stale` and `conventions` (tasks 3.2-3.4) each add
one import and one `DISPATCH` row — the same shape `specs.commands.cli` and `knowledge.cli`
already use for their own pillars, kept flat here because four leaf subcommands need no
`commands/` package of their own."""
from __future__ import annotations

import argparse
import sys

from quenching.common.output import REFUSAL
from quenching.common.version import VERSION
from quenching.git.base import cmd_base
from quenching.git.conventions import cmd_conventions
from quenching.git.slugs import cmd_specs
from quenching.git.stale import cmd_stale

DISPATCH = {"base": cmd_base, "specs": cmd_specs, "stale": cmd_stale,
            "conventions": cmd_conventions}


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        prog="cq git", description="a repository's git facts — deterministic, nothing to validate")
    p.add_argument("--version", action="store_true", help="print the version and exit")
    sub = p.add_subparsers(dest="cmd")

    sp = sub.add_parser("base", help="the base branch a spec merges into, and whether it is "
                                      "the host's own default")
    sp.add_argument("--json", action="store_true", help="machine-readable output")

    sp = sub.add_parser("specs", help="read, add or remove native spec IDs in a branch's own "
                                       "`quenching-specs:` marking")
    sp.add_argument("branch")
    change = sp.add_mutually_exclusive_group()
    change.add_argument("--add", metavar="ID", help="merge one native spec ID into the marking")
    change.add_argument("--remove", metavar="ID", help="remove one native spec ID from the marking")
    sp.add_argument("--json", action="store_true", help="machine-readable output")

    sp = sub.add_parser("stale", help="branches merged or gone, and worktrees git still "
                                       "registers with no directory on disk — a report only")
    sp.add_argument("--json", action="store_true", help="machine-readable output")

    sp = sub.add_parser("conventions", help="read-if-present: whether the target declares "
                                             "its own .knowledge/standards/git/**, or the "
                                             "plugin's defaults govern")
    sp.add_argument("--json", action="store_true", help="machine-readable output")

    return p


def main(argv: list[str]) -> int:
    if "--version" in argv:
        print(f"cq git {VERSION}")
        return 0
    parser = build_parser()
    args = parser.parse_args(argv)
    if not args.cmd:
        parser.print_usage(sys.stderr)
        return REFUSAL
    return DISPATCH[args.cmd](args)
