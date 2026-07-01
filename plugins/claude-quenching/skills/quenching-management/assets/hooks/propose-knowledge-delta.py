#!/usr/bin/env python3
"""Portable hook (Stop) — automatic freshness: PROPOSES knowledge deltas.

Payload of the ``quenching-management`` method. Generic and self-contained.
Materializes the **automatic freshness of Step 8** (recurring maintenance loop)
and the *automated* version of what the evolutionist does manually: at the end of the turn, reads the
session transcript and, if the conversation exposed a knowledge gap (a command
Claude did not know, a corrected pattern, an environment gotcha), **PROPOSES** —
never imposes — a CLAUDE.md/memory delta «while the gap is fresh».

Official contract (Stop hook — code.claude.com/docs/en/hooks#stop):

- **Only PROPOSES — NEVER blocks.** Returns the suggestion via
  ``hookSpecificOutput.additionalContext`` (which *continues* the conversation for
  Claude to report/act), with **exit 0**. Does not use ``decision: block`` nor
  ``exit 2`` — blocking would force the turn not to end, the opposite of «proposing».
- **Guard ``stop_hook_active``.** Exits early (exit 0) if the input JSON carries
  ``stop_hook_active: true`` — without the guard, the harness cuts only after **8
  consecutive blocks**; since there is never a block here, the guard prevents re-proposing in
  a loop when another Stop hook is active.
- **Latency ceiling (~500 ms on the critical path).** Reads only the **tail** of the
  transcript (``maxTranscriptBytes``), matches by cheap regex and has
  ``deadlineMs``; if budget exceeded → exits silently (exit 0). The Stop hook
  runs at the end of every turn: slow here = slow session.
- **Actionable error (dim 14).** Every ``additionalContext`` output says **what** the
  gap is and **where** to record it (CLAUDE.md root × memory), not a raw dump.

Pre-trust vector: hook config is **executable code** with shell privileges.
This script is **read-only** (reads transcript, writes nothing) — version
and review it like infra. Register the ``command`` in ``settings.json`` under the
``Stop`` event (use ``settings.snippet.json``). Honors ``hooks-config.json``/
``hooks-config.local.json`` (block ``proposeKnowledgeDelta``): ``enabled: false``
exits silently.
"""
from __future__ import annotations

import json
import os
import pathlib
import re
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "knowledge-management"
DEFAULTS = {
    "enabled": True,
    "maxTranscriptBytes": 200_000,  # only the transcript tail (latency)
    "deadlineMs": 400,              # ceiling < ~500 ms on the critical path
    "maxFindings": 3,               # do not flood the context with proposals
}

# Cheap signals of "fresh gap" exposed in the turn. Each pattern matches text from the
# transcript and names the proposed delta + the suggested home (CLAUDE.md × memory).
# Generic and portable: no path/term from this repo.
SIGNALS: tuple[tuple[str, str, str], ...] = (
    (
        r"(?i)\b(?:the\s+)?(?:correct|right)\s+command\s+is\b|"
        r"\bo\s+comando\s+(?:certo|correto)\s+(?:é|e)\b|"
        r"\buse\s+`[^`]+`\s+instead\b",
        "command Claude did not know / got wrong",
        "CLAUDE.md (Common commands) — short directive",
    ),
    (
        r"(?i)\b(?:that['']s|this is)\s+(?:deprecated|outdated|no longer)\b|"
        r"\b(?:isso|esse padrão|isto)\s+(?:está|esta|foi)\s+(?:obsoleto|substitu)",
        "pattern described as obsolete/replaced (fossil)",
        "current standards (and pruning the fossil from CLAUDE.md)",
    ),
    (
        r"(?i)\b(?:gotcha|pitfall|footgun|caveat)\b|"
        r"\b(?:pegadinha|armadilha|cuidado:)\b",
        "non-obvious gotcha discovered",
        "memory (agent learning) or CLAUDE.md if it applies to everyone",
    ),
    (
        r"(?i)\b(?:set|export)\s+[A-Z][A-Z0-9_]{3,}=|"
        r"\benv(?:ironment)?\s+var(?:iable)?\b.*\b(?:required|needed|must)\b",
        "environment quirk / required env var",
        "CLAUDE.md (environment quirks)",
    ),
)


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
        cfg.update(data.get("proposeKnowledgeDelta") or {})
    return cfg


def _read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _tail_text(transcript_path: str, max_bytes: int) -> str:
    """Reads only the tail of the .jsonl transcript and concatenates message texts."""
    try:
        size = os.path.getsize(transcript_path)
        with pathlib.Path(transcript_path).open("rb") as fh:
            if size > max_bytes:
                fh.seek(size - max_bytes)
                fh.readline()  # discard the initial partial line
            raw = fh.read().decode("utf-8", errors="ignore")
    except OSError:
        return ""
    return raw


def _emit(findings: list[tuple[str, str]]) -> None:
    """Returns the PROPOSAL via additionalContext (continues the conversation, does not block)."""
    lines = [
        f"[{TAG}] automatic freshness: this session may have exposed knowledge gap(s). "
        "PROPOSAL (not mandatory) — record while it is fresh:",
    ]
    for what, where in findings:
        lines.append(f"  - {what} → {where}")
    lines.append(
        "If confirmed, open the edit with confirmation (CLAUDE.md = short map + link; "
        "memory only for agent-learning). Ignore if it is noise."
    )
    payload = {
        "hookSpecificOutput": {
            "hookEventName": "Stop",
            "additionalContext": "\n".join(lines),
        }
    }
    print(json.dumps(payload))


def main() -> int:
    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0

    data = _read_input()
    if data.get("stop_hook_active") is True:  # anti-loop guard (cap of 8)
        return 0
    transcript_path = data.get("transcript_path")
    if not transcript_path:
        return 0

    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0
    text = _tail_text(transcript_path, int(cfg.get("maxTranscriptBytes")))
    if not text:
        return 0

    findings: list[tuple[str, str]] = []
    seen: set[str] = set()
    for pattern, what, where in SIGNALS:
        if time.monotonic() - started > deadline:  # latency ceiling
            break
        if what in seen:
            continue
        if re.search(pattern, text):
            findings.append((what, where))
            seen.add(what)
        if len(findings) >= int(cfg.get("maxFindings", DEFAULTS["maxFindings"])):
            break

    if findings:
        _emit(findings)
    return 0  # ALWAYS exit 0 — proposes, never blocks


if __name__ == "__main__":
    sys.exit(main())
