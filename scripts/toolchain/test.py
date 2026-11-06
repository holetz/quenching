"""Run the tests a change reaches, or the whole suite when the selector cannot be sure.

This is the task lane's entry point: `/quenching-specs execute` runs a task's `verify:` many times
per spec, in several worktrees at once, and a whole suite each time is the load this spec exists to
remove. Three tiers, one script:

* a task and a session run ``--affected`` — the diff's tests, without the heavy layer;
* the spec's close runs the whole gate with the suite in affected scope (``verify_repo.sh``);
* CI and ``/release`` run everything, and the heavy layer runs there.

``--affected`` falls back to the whole suite whenever :mod:`scripts.toolchain.affected` cannot
answer, and says which reason it hit. The heavy (`integration`) layer is filtered unless
``--with-integration`` is given; the number deferred is printed, never silently dropped. Explicit
paths win over the diff — a caller who named a test meant it.

Usage::

    python -m scripts.toolchain.test --affected
    python -m scripts.toolchain.test --affected --with-integration -q
    python -m scripts.toolchain.test -q quenching/tests/test_git.py
"""

from __future__ import annotations

import argparse
import os
import pathlib
import subprocess
import sys

from scripts.toolchain import affected

TESTS = "quenching/tests"
FALLBACK_BASE = "origin/main"
WORKERS_ENV = "QUENCHING_TEST_WORKERS"


def _asks_for_workers(extra: list[str]) -> bool:
    """Whether the caller already chose xdist's worker count."""
    return any(arg == "--numprocesses" or arg.startswith("--numprocesses=")
               or arg == "-n" or (arg.startswith("-n") and arg[2:].isdigit())
               for arg in extra)


def build(targets: list[str], with_integration: bool, extra: list[str]) -> list[str]:
    """The pytest argv for one run; `targets` is already the scoped set or the whole suite."""
    argv = [sys.executable, "-m", "pytest", "-p", "scripts.toolchain.layers",
            "-p", "scripts.toolchain.slots"]
    workers = os.environ.get(WORKERS_ENV, "auto")
    if workers not in ("", "0") and not _asks_for_workers(extra):
        argv += ["-n", workers]
    if not with_integration:
        argv += ["-m", "not integration"]
    return [*argv, *targets, *extra]


def count_integration(root: pathlib.Path, targets: list[str]) -> int:
    """How many collected tests the run is deferring to the close."""
    proc = subprocess.run(
        [sys.executable, "-m", "pytest", "-p", "scripts.toolchain.layers", "-q", "--collect-only",
         "-m", "integration", *targets],
        cwd=root, capture_output=True, text=True)
    return sum(1 for line in proc.stdout.splitlines() if "::" in line)


def plan(root: pathlib.Path, base: str | None, use_affected: bool,
         explicit: list[str] | None = None) -> tuple[list[str], str | None]:
    """The targets for this run, and the reason when it had to become the whole suite."""
    if explicit:
        return list(explicit), None
    if not use_affected:
        return [TESTS], None
    selection = affected.select(root, base)
    if selection.complete:
        return [TESTS], selection.reasons[0]
    if not selection.tests:
        return [TESTS], "the selector found no test to run"
    return list(selection.tests), None


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--affected", action="store_true", help="scope the run to the diff")
    parser.add_argument("--with-integration", action="store_true", help="keep the heavy layer")
    parser.add_argument("--base", default=FALLBACK_BASE, help=f"merge-base reference (default: {FALLBACK_BASE})")
    parser.add_argument("targets", nargs="*", help="explicit test paths; without them the diff decides")
    args, extra = parser.parse_known_args(argv)
    root = affected.import_root()
    targets, fallback = plan(root, args.base, args.affected, args.targets)
    if fallback:
        print(f"[test] whole suite: {fallback}", file=sys.stderr)
    elif args.targets:
        print(f"[test] {len(targets)} target(s) given", file=sys.stderr)
    else:
        print(f"[test] {len(targets)} target(s) from the diff against {args.base}", file=sys.stderr)
    if not args.with_integration:
        deferred = count_integration(root, targets)
        print(f"[test] integration: {deferred} test(s) deferred to the close", file=sys.stderr)
    print("[test] " + " ".join(build(targets, args.with_integration, extra)), file=sys.stderr)
    return subprocess.call(build(targets, args.with_integration, extra), cwd=root)


if __name__ == "__main__":
    sys.exit(main())
