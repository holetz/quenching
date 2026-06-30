#!/usr/bin/env python3
"""Portable hook: validates every touched CLAUDE.md against the line ceiling.

Payload of the `quenching-management` method. Generic and self-contained — does not
depend on any external skill. Install it in ``.claude/hooks/`` of the target repo and
register the ``command`` in ``settings.json`` for ``PostToolUse`` (after ``Edit``/
``Write``) and ``InstructionsLoaded``. Reads the hook payload from stdin, extracts the
referenced path and exits with a non-zero code with feedback on stderr when the
file exists and exceeds the ceiling.

Exit codes (Claude Code hook contract):
- ``0``  passes
- ``2``  shows stderr to Claude as actionable feedback (does not block)

Configuration: reads ``hooks-config.json`` (and optional ``hooks-config.local.json``)
in the same directory, block ``validateClaudeMd`` (maxLines, exemptFilenameSuffix,
exitCodeOnViolation, enabled). Without config, uses the defaults below.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys

DEFAULT_MAX_LINES = 150
DEFAULT_EXEMPT_SUFFIX = ".local.md"
DEFAULT_VIOLATION_RC = 2
TAG = "knowledge-management"


def _load_config() -> dict:
    """Merges ``hooks-config.json`` and ``hooks-config.local.json`` (local wins)."""
    here = os.path.dirname(os.path.abspath(__file__))
    cfg: dict = {}
    for name in ("hooks-config.json", "hooks-config.local.json"):
        path = os.path.join(here, name)
        if not pathlib.Path(path).exists():
            continue
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        cfg.update(data.get("validateClaudeMd") or {})
    return cfg


def _candidate_paths(payload: dict) -> list[str]:
    """Extracts every path the hook payload may reference.

    Accepts several forms so the same script serves both ``PostToolUse``
    (tool_input.file_path) and ``InstructionsLoaded`` (path / file).
    """
    paths: list[str] = []
    tool_input = payload.get("tool_input") or {}
    for key in ("file_path", "path", "target_file"):
        value = tool_input.get(key)
        if isinstance(value, str):
            paths.append(value)
    for key in ("path", "file", "file_path"):
        value = payload.get(key)
        if isinstance(value, str):
            paths.append(value)
    return paths


def _is_claude_md(path: str, exempt_suffix: str) -> bool:
    base = os.path.basename(path)
    # Personal overrides (CLAUDE.local.md / configurable suffix) are exempt from the
    # ceiling — they live outside the shared chained tree used by the team.
    if base.endswith(exempt_suffix):
        return False
    return base == "CLAUDE.md" or "/.claude/rules/" in path


def main() -> int:
    if sys.stdin.isatty():
        return 0
    raw = sys.stdin.read().strip()
    if not raw:
        return 0
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return 0

    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0
    max_lines = int(cfg.get("maxLines", DEFAULT_MAX_LINES))
    exempt_suffix = str(cfg.get("exemptFilenameSuffix", DEFAULT_EXEMPT_SUFFIX))
    violation_rc = int(cfg.get("exitCodeOnViolation", DEFAULT_VIOLATION_RC))

    violations: list[tuple[str, int]] = []
    for path in _candidate_paths(payload):
        if not _is_claude_md(path, exempt_suffix) or not pathlib.Path(path).exists():
            continue
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                line_count = sum(1 for _ in fh)
        except OSError:
            continue
        if line_count > max_lines:
            violations.append((path, line_count))

    if not violations:
        return 0

    for path, line_count in violations:
        print(
            f"[{TAG}] {path} has {line_count} lines (ceiling = {max_lines}). "
            "It is a map, not a contract: trim it to short-directive + link, or break "
            "it into a chained sub-CLAUDE.md.",
            file=sys.stderr,
        )
    return violation_rc


if __name__ == "__main__":
    sys.exit(main())
