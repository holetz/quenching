"""What the target repo declares about this checker, and the two reads that find it.

Moved verbatim out of the pre-refactor OKF validator script.

Config (target repo's `.claude/hooks/hooks-config.json` + `hooks-config.local.json`, block
`okfValidate`): `warnAsError`, `ignoreGlobs`. An empty/absent config uses the defaults below.
The file and directory keep the `hooks` name for the two keys that survive it — the plugin's
self-installed hook that once read the rest of this block (`enabled`, `blockOnFail`, `hardBlock`,
`deadlineMs`, `stopScan`) was retired, and `warnAsError`/`ignoreGlobs` stayed on the same config
surface rather than move, which would have been a breaking change of its own.

Trust note: this config is executable code with shell privileges. This pillar reads the touched
path/content and prints; it writes nothing. In **CLI mode** it additionally shells out to
`git log`/`git rev-parse` (read-only, timeout-bounded) for `stale-doc`. Version and review it like
infra.
"""
from __future__ import annotations

import json
import os
import pathlib

DEFAULTS: dict = {
    "warnAsError": False,       # CLI: treat warnings as failures (exit 1)
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


def _project_dir() -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or os.getcwd()
