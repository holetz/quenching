"""The record `scripts/verify_repo.sh` leaves behind, and `cq git pr merge` reads.

With `shared.ci.enforce` relaxed, the merge stands the local gate in for CI. A flag the caller
declares proves nothing, so the gate itself writes `.quenching/gate/record.json` when it ends:
the HEAD sha it ran on, its own exit, the scope it ran and whether the tree was clean. The merge
accepts it only for the PR's head, with exit 0 and a clean tree
(`quenching.config.ci.proven_exit` reads it; the keys below are that contract).

    python -m scripts.toolchain.gate_record clear
    python -m scripts.toolchain.gate_record write --exit N [--scope full|affected]

`clear` runs when the gate starts, so a run that never finishes leaves no record; `write` runs from
the gate's EXIT trap with the real exit status. Stdlib only.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
import pathlib
import subprocess
import sys

RECORD = pathlib.Path(".quenching") / "gate" / "record.json"
SCHEMA = 1


def _git(root: pathlib.Path, *args: str) -> str | None:
    try:
        done = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True,
                              encoding="utf-8", check=False)
    except OSError:
        return None
    return done.stdout if done.returncode == 0 else None


def clear(root: pathlib.Path) -> None:
    (root / RECORD).unlink(missing_ok=True)


def write(root: pathlib.Path, exit_code: int, scope: str = "unknown") -> dict | None:
    """Record the gate's end. `None` when git cannot name HEAD: no record beats a guessed one."""
    head = _git(root, "rev-parse", "HEAD")
    status = _git(root, "status", "--porcelain")
    if head is None or status is None:
        return None
    record = {
        "schema": SCHEMA,
        "head": head.strip(),
        "exit": exit_code,
        "scope": scope,
        "dirty": bool(status.strip()),
        "date": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    target = root / RECORD
    target.parent.mkdir(parents=True, exist_ok=True)
    scratch = target.with_suffix(".tmp")
    scratch.write_text(json.dumps(record, indent=2) + "\n", encoding="utf-8")
    os.replace(scratch, target)
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="gate_record", description=__doc__.split("\n\n")[0])
    parser.add_argument("--root", default=".", type=pathlib.Path)
    sub = parser.add_subparsers(dest="action", required=True)
    sub.add_parser("clear")
    writer = sub.add_parser("write")
    writer.add_argument("--exit", dest="exit_code", type=int, required=True)
    writer.add_argument("--scope", default="unknown")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    if args.action == "clear":
        clear(root)
        return 0
    if write(root, args.exit_code, args.scope) is None:
        print("gate record not written: git could not name HEAD", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
