#!/usr/bin/env python3
"""Portable hook (SessionStart) — compact-survival: RE-INJECTS conventions.

Payload of the ``quenching-management`` method. Generic and self-contained.
Materializes the **compact-survival of Step 8** (the ``SessionStart`` hook matcher
``compact``): when ``/compact`` resumes the conversation, the
stable layer (house conventions, FQNs, guardrails, open boundaries) disappears
from context. This hook **re-injects** that layer — what it writes to stdout
goes back into Claude's context on restart.

Distinct from the sibling Stop hook (``propose-knowledge-delta.py``): that one runs at the
**end** of the turn and *PROPOSES* a new delta; this one runs on **SessionStart** and
*RE-INJECTS* what already exists and that ``/compact`` would erase. One writes the base, the other
keeps it alive.

Official contract (SessionStart — code.claude.com/docs/en/hooks#sessionstart):

- **Matchers.** ``compact`` (auto/manual compaction) is the use case. The wiring
  also covers ``clear`` and ``resume`` (re-injects after ``/clear`` and on resume),
  but **not** ``startup`` — for a new session the docs recommend CLAUDE.md, not a
  hook (*"For static context that does not require a script, use CLAUDE.md"*). The
  ``source`` field of the input JSON tells which fired (startup/resume/clear/
  compact); this script only re-injects for non-startup ones.
- **Output = stdout becomes context.** In SessionStart, *"anything you write to
  stdout is added to Claude's context"* (exit 0). For plain text, the docs say that
  *"a hook that only loads context can print to stdout directly without building
  JSON"* — that is what we do; using ``additionalContext`` would only be necessary to
  combine with other fields. Always read-only (writes nothing).
- **PORTABILITY — derives from the target, never a fixed list from this repo.** The
  re-injected content is **read from a target-derived source**, in order of preference:
  (1) a dedicated conventions file (``conventionsFile`` from config, or a
  default like ``.claude/conventions.md``); (2) failing that, the **head** of the root CLAUDE.md
  (``$CLAUDE_PROJECT_DIR/CLAUDE.md``) — the short map that ``/compact``
  would lose. No convention is hardcoded; switch repos and the hook re-injects the
  conventions of *that* repo.
- **Latency ceiling (~500 ms on the critical path).** Reads only the first
  ``maxBytes`` from the source and has ``deadlineMs``; if exceeded or source absent → silence
  (exit 0). SessionStart runs on every restart: slow here = slow restart.

Pre-trust vector: hook config is **executable code** with shell privileges.
This script is **read-only** — version and review it like infra; never run
destructive logic in SessionStart. Register the ``command`` in ``settings.json`` under the
``SessionStart`` event (use ``settings.snippet.json``). Honors
``hooks-config.json``/``hooks-config.local.json`` (block ``reinjectConventions``):
``enabled: false`` exits silently.
"""
from __future__ import annotations

import json
import os
import pathlib
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "knowledge-management"
DEFAULTS = {
    "enabled": True,
    "conventionsFile": ".claude/conventions.md",  # 1st choice (relative to root)
    "fallbackToClaudeMd": True,                    # 2nd choice: head of CLAUDE.md
    "maxBytes": 8_000,                             # only the stable layer (latency)
    "deadlineMs": 300,                             # ceiling < ~500 ms on the critical path
    "matchers": ["compact", "clear", "resume"],    # not 'startup' (use CLAUDE.md)
}


def _load_config() -> dict:
    cfg = dict(DEFAULTS)
    for name in ("hooks-config.json", "hooks-config.local.json"):
        path = os.path.join(HERE, name)
        if not pathlib.Path(path).exists():
            continue
        try:
            with pathlib.Path(path).open(encoding="utf-8") as fh:
                data = json.load(fh)
        except (OSError, json.JSONDecodeError):
            continue
        cfg.update(data.get("reinjectConventions") or {})
    return cfg


def _read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def _read_head(path: str, max_bytes: int) -> str:
    """Reads only the head (stable layer) of a text source."""
    try:
        with pathlib.Path(path).open("rb") as fh:
            raw = fh.read(max_bytes)
    except OSError:
        return ""
    return raw.decode("utf-8", errors="ignore").strip()


def _resolve_source(cfg: dict, root: str) -> tuple[str, str]:
    """Derives the source from the TARGET (never a fixed list). Returns (text, label)."""
    conv = cfg.get("conventionsFile") or DEFAULTS["conventionsFile"]
    conv_path = conv if os.path.isabs(conv) else os.path.join(root, conv)
    text = _read_head(conv_path, int(cfg.get("maxBytes", DEFAULTS["maxBytes"])))
    if text:
        return text, conv
    if cfg.get("fallbackToClaudeMd", True):
        claude_md = os.path.join(root, "CLAUDE.md")
        text = _read_head(claude_md, int(cfg.get("maxBytes", DEFAULTS["maxBytes"])))
        if text:
            return text, "CLAUDE.md (head)"
    return "", ""


def _emit(source_text: str, label: str, source: str) -> None:
    """Re-injects into context (stdout becomes context in SessionStart)."""
    print(
        f"[{TAG}] post-{source} re-injection: /compact may have erased the stable "
        f"layer; here it is from {label} (current conventions/FQNs/guardrails/boundaries):\n"
        f"{source_text}"
    )


def main() -> int:
    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0

    data = _read_input()
    source = (data.get("source") or "").strip().lower()
    matchers = {m.lower() for m in (cfg.get("matchers") or DEFAULTS["matchers"])}
    if source and source not in matchers:  # 'startup' (or unknown) → silence
        return 0

    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0
    text, label = _resolve_source(cfg, _project_dir(data))
    if not text or time.monotonic() - started > deadline:
        return 0  # source absent / budget exceeded → silence

    _emit(text, label, source or "compact")
    return 0  # ALWAYS exit 0 — stdout becomes context; never blocks the start


if __name__ == "__main__":
    sys.exit(main())
