#!/usr/bin/env python3
"""Portable hook (ConfigChange) — audit trail for the knowledge surface itself.

Payload of the ``quenching-management`` method. Generic and self-contained.
Materializes the **third and final lifecycle hook** (the Stop was
``propose-knowledge-delta.py``; the SessionStart-compact was
``reinject-conventions.py``): when something edits the surface during the session —
a ``settings.json``, a skill file — this hook **records an audit trail**
(who/when/what) in a target log. A new skill or a modified settings file
**does not go unnoticed**.

Distinct from the sibling hooks: the Stop *PROPOSES* a new delta at the end of the turn; the
SessionStart *RE-INJECTS* the stable layer on restart; this one **OBSERVES and
RECORDS** the change in the base itself as soon as it happens. All three together =
continuous audit cycle (what survived, what is missing, what changed).

Official contract (ConfigChange — code.claude.com/docs/en/hooks#configchange):

- **Matchers = the config source that changed.** ``user_settings`` (``~/.claude/
  settings.json``), ``project_settings`` (``.claude/settings.json``),
  ``local_settings`` (``.claude/settings.local.json``), ``policy_settings``
  (managed policy), ``skills`` (skill files). The matcher ``""`` covers all;
  the input JSON carries the field ``source`` indicating which fired and ``file_path``
  with the file. *"The `ConfigChange` event fires when an external process or editor
  modifies a configuration file, so you can log changes for compliance."*
- **Audit trail NEVER blocks — exit 0 always.** ConfigChange **can** block
  (``exit 2``/``decision: block``, except ``policy_settings``), but recording a
  trail is **observing**, not vetoing: we use ``exit 0`` always. Blocking a
  legitimate settings/skill change mid-session would be the opposite of an
  audit trail. (Anyone wanting *enforcement* of unauthorized changes is another hook,
  outside this payload — Simplicity First.)
- **Stdout does NOT become context in this event.** Unlike SessionStart/
  UserPromptSubmit, *"For ConfigChange, stdout is written to the debug log but
  not shown in the transcript"*. That is why the trail **goes to a log file**
  (not to stdout) — and stdout stays silent.
- **PORTABILITY — the log destination derives from the target, never hardcoded.** The trail
  is written to ``auditLog`` (default ``.claude/config-audit.log``, relative to
  ``$CLAUDE_PROJECT_DIR``); switch repos and the trail lives in *that* repo. The log
  is **append-only**, with size-based rotation (``maxLogBytes``) to prevent unbounded growth.
- **Latency ceiling (~500 ms on the critical path).** Only assembles one JSONL line and
  does an append; ``deadlineMs`` as a guard. ConfigChange runs on every config change:
  slow here = slow settings editing.

Pre-trust vector: hook config is **executable code** with shell privileges.
This script **does not modify** settings or skills — it only *reads* the event and
*appends* one line to the audit log (append, never overwrites the
surface). Version and review it like infra; never run destructive logic.
Register the ``command`` in ``settings.json`` under the ``ConfigChange`` event (use
``settings.snippet.json``). Honors ``hooks-config.json``/``hooks-config.local.json``
(block ``auditConfigChange``): ``enabled: false`` exits silently.

CAUTION (secrets in the trail): by default the log records only **metadata**
(timestamp/source/file/session), **not the content** of the changed file — config
audit logs may contain secrets. Do not include the diff/value.
"""
from __future__ import annotations

import datetime
import json
import os
import pathlib
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "knowledge-management"
# Valid config sources (= ConfigChange matchers in the official docs).
KNOWN_SOURCES = (
    "user_settings",
    "project_settings",
    "local_settings",
    "policy_settings",
    "skills",
)
DEFAULTS = {
    "enabled": True,
    "auditLog": ".claude/config-audit.log",  # destination derived from the target (relative)
    "sources": list(KNOWN_SOURCES),           # which sources to record (filter)
    "maxLogBytes": 1_000_000,                  # simple rotation: truncates beyond this
    "deadlineMs": 200,                         # ceiling < ~500 ms on the critical path
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
        cfg.update(data.get("auditConfigChange") or {})
    return cfg


def _read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def _resolve_log(cfg: dict, root: str) -> str:
    log = cfg.get("auditLog") or DEFAULTS["auditLog"]
    return log if os.path.isabs(log) else os.path.join(root, log)


def _rotate_if_needed(log_path: str, max_bytes: int) -> None:
    """Simple rotation: if the trail exceeded the ceiling, move to .1 (one generation)."""
    try:
        if os.path.getsize(log_path) <= max_bytes:
            return
    except OSError:
        return
    try:
        os.replace(log_path, log_path + ".1")
    except OSError:
        pass


def _append(log_path: str, entry: dict, max_bytes: int) -> None:
    """Append-only of ONE JSONL line (metadata only, never the file content)."""
    try:
        pathlib.Path(os.path.dirname(log_path) or ".").mkdir(parents=True, exist_ok=True)
        _rotate_if_needed(log_path, max_bytes)
        with pathlib.Path(log_path).open("a", encoding="utf-8") as fh:
            fh.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError as err:
        # Actionable error (dim 14) — says WHAT failed and WHERE, without a raw stack trace.
        sys.stderr.write(
            f"[{TAG}] audit-config-change: could not write the trail to "
            f"{log_path!r} ({err}); adjust 'auditLog' in hooks-config.json or the "
            "folder permissions.\n"
        )


def main() -> int:
    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0

    data = _read_input()
    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0

    source = (data.get("source") or "").strip().lower()
    wanted = {s.lower() for s in (cfg.get("sources") or DEFAULTS["sources"])}
    if source and source not in wanted:  # filtered source → silence
        return 0
    if time.monotonic() - started > deadline:
        return 0

    entry = {
        # METADATA only (never the content/diff of the file — may contain secrets)
        "ts": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "event": "ConfigChange",
        "source": source or "unknown",
        "file": data.get("file_path") or data.get("file") or "",
        "session": data.get("session_id") or "",
    }
    _append(
        _resolve_log(cfg, _project_dir(data)),
        entry,
        int(cfg.get("maxLogBytes", DEFAULTS["maxLogBytes"])),
    )
    return 0  # ALWAYS exit 0 — audit trail OBSERVES, never blocks the change


if __name__ == "__main__":
    sys.exit(main())
