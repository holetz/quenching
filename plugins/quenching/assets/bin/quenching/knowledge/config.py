"""What the target repo declares about this checker, and the two reads that find it.

Moved verbatim out of the pre-refactor OKF validator script.

Config (target repo's `.claude/hooks/hooks-config.json` + `hooks-config.local.json`, block
  `okfValidate`): enabled, warnAsError, blockOnFail, hardBlock, deadlineMs, stopScan.
An empty/absent config uses the defaults below; `enabled: false` makes the hook inert.

Trust note: hook config is executable code with shell privileges. This pillar reads the
touched path/content and prints; the only thing it ever writes is the dirty-marker stamp
file in the system temp dir (`quenching.knowledge.marker`). In **CLI mode only** it
additionally shells out to `git log`/`git rev-parse` (read-only, timeout-bounded) for
`stale-doc`; the hook paths never spawn a subprocess. Version and review it like infra.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

DEFAULTS: dict = {
    "enabled": True,
    "warnAsError": False,       # CLI: treat warnings as failures (exit 1)
    "blockOnFail": False,       # PostToolUse/Stop: escalate proposal to decision:block
    "hardBlock": False,         # PreToolUse: enable the hard deny gate (off = propose-only)
    "deadlineMs": 4000,
    "stopScan": "dirty",        # Stop: "dirty" = scan only after a docs/** edit; "always" = every turn
    "ignoreGlobs": [],          # bundle-relative dir-prefix/fnmatch globs pruned from every scan
}


def _load_config(project_dir: str) -> dict:
    cfg = dict(DEFAULTS)
    for name in ("hooks-config.json", "hooks-config.local.json"):
        path = os.path.join(project_dir, ".claude", "hooks", name)
        if not pathlib.Path(path).exists():
            continue
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        cfg.update(data.get("okfValidate") or {})
    return cfg


def _read_stdin() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()
