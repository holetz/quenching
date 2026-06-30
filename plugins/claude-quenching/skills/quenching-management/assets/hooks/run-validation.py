#!/usr/bin/env python3
"""Portable hook (Stop) — runs the "before concluding" VALIDATION by CALLING a script.

Payload of the ``quenching-management`` method. Generic and self-contained.
Materializes the doctrine **thin-hook-calls-script** (``scripts/`` taxonomy): the
**deterministic validation logic** does NOT live here — it lives in a **target script**
in the home ``scripts/checks`` (or ``scripts/ci``). This hook is just the **thin trigger**
(Stop→git-diff→exit-code adapter) that, at the END of the turn, invokes the
configured ``validateScript``/``validateCmd`` and **returns the result in an actionable way**
(what the validator complained about + where) for the agent to fix.

Matches the "Development validation (mandatory)" section that many CLAUDE.md files
have — *«before concluding, changed files go through the checks; the type check is the
most forgotten, never skip it»*. Runs **once at the end of the turn** (batch = "fix ALL"),
less disruptive than validating on every edit.

PORTABILITY — what to run is DERIVED from the target, NEVER hardcoded:
- ``validateScript`` is the path to the target's validation script (e.g.
  ``scripts/checks/validate.py``), invoked by ``runner`` (e.g. ``["python3"]``
  or ``["python","-m"]``); **or** ``validateCmd`` is the raw command (e.g.
  ``["make","check"]``). **Default empty ⇒ hook INERT** (runs nothing) — same as
  ``protectedGlobs`` from ``protect-generated.py``: only acts when the target wires the script.
- **Documented example for a Python repo** (illustrates the FORM only, never embedded as
  a fixed path/binary): the target's ``scripts/checks/<validate>`` runs
  ``ruff check --fix`` (fix all) + ``ruff format`` + ``pyright``. A Go repo would wire
  ``go vet``/``gofmt``; a TS repo, ``tsc``/``eslint --fix``. **The hook does not know the
  language** — it runs whatever the target wired.

Scope by CHANGED files (latency ceiling): passes to the script only the files
touched (``git status --porcelain`` — the **official standard** for "a hook that sees every
file change": *«add a Stop hook that scans the working tree once per turn… list
modified and untracked files with `git status --porcelain`»*), filtered by
``includeGlobs`` (e.g. ``*.py``). No file to validate ⇒ exits silently.

Official contract (Stop hook — code.claude.com/docs/en/hooks#stop):

- **Default: PROPOSES/INFORMS, NEVER blocks** (method doctrine — hook OBSERVES/
  PROPOSES; blocking enforcement is only for GENERATED artifacts, ``protect-generated.py``).
  ``ruff --fix``/``format`` MUTATE code files (not the knowledge base) —
  that is why the result goes via ``hookSpecificOutput.additionalContext`` with **exit 0**:
  says that formatting ran + the remaining errors (e.g. ``pyright``), for the agent
  to act. Does not use ``decision: block`` by default.
- **Configurable BLOCKING mode (``blockOnFail: true``, OFF by default).**
  For the "mandatory/never skip" semantics: if the validator exits with an error, returns
  ``{"decision": "block", "reason": <errors>}`` (or ``exit 2`` legacy via
  ``blockMode: "exit2"``) — the docs: for Stop, *«the `reason` is fed back to Claude so
  it keeps working»*, so the agent fixes before concluding. **Do not mix** the
  two forms (*«Claude Code ignores JSON when you exit 2»*).
- **Guard ``stop_hook_active``.** Exits early (exit 0) if the input carries
  ``stop_hook_active: true`` — without the guard, in blocking mode the harness only cuts after
  **8 consecutive blocks**; the guard prevents re-running/re-blocking in a loop.
- **Latency ceiling.** ``deadlineMs`` covers ``git status`` + the script call;
  if exceeded → exits silently (exit 0). Stop runs at the end of every turn.
- **Actionable error (dim 14).** The output says **what** the validator complained about and **where**
  (the tail of the script output, with the command name), not a raw dump.

Pre-trust vector: hook config is **executable code** with shell privileges.
This script only **reads** git status and **calls** the target's validator (writes
nothing itself — whoever mutates files is the ``ruff --fix``/``format`` that the target wired) —
version and review it like infra. Register the ``command`` in ``settings.json`` under the
``Stop`` event (use ``settings.snippet.json``). Honors ``hooks-config.json``/
``hooks-config.local.json`` (block ``runValidation``): ``enabled: false`` exits silently.
"""
from __future__ import annotations

import fnmatch
import json
import os
import pathlib
import shlex
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = "knowledge-management"

DEFAULTS: dict = {
    "enabled": True,
    # Raw validation command (list of args). Ex. (NOT from this repo): ["make", "check"].
    # Takes precedence over runner+validateScript if set.
    "validateCmd": [],
    # OR: runner + path to the target's validation script (home scripts/checks|ci).
    # Ex. Python (illustrates the FORM only): runner ["python3"], validateScript
    # "scripts/checks/validate.py" (the script runs ruff check --fix + ruff format + pyright).
    "runner": ["python3"],
    "validateScript": "",
    # Pass changed files (filtered) as args to the command/script? (scoped
    # by edit, for latency). false = runs the validator without args (validates everything).
    "passChangedFiles": True,
    "includeGlobs": ["*.py"],   # filter the touched files (derive from repo)
    # Default does NOT block: PROPOSES via additionalContext (exit 0). true = "mandatory":
    # decision:block (or exit 2 via blockMode) for the agent to fix before concluding.
    "blockOnFail": False,
    "blockMode": "decision",    # "decision" (JSON) | "exit2" (legacy/stderr)
    "deadlineMs": 8000,         # covers git status + validator call
    "maxOutputBytes": 4000,     # tail of output returned (do not flood context)
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
        cfg.update(data.get("runValidation") or {})
    return cfg


def _read_input() -> dict:
    try:
        return json.loads(sys.stdin.read() or "{}")
    except (OSError, json.JSONDecodeError):
        return {}


def _project_dir(data: dict) -> str:
    return os.environ.get("CLAUDE_PROJECT_DIR") or data.get("cwd") or os.getcwd()


def _changed_files(root: str, include: list[str], deadline_s: float) -> list[str]:
    """Modified/new files (git status --porcelain), filtered by includeGlobs.

    Official standard for "a hook that sees every file change" in a Stop hook.
    No git / outside repo ⇒ empty list (hook does not fail).
    """
    try:
        out = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=root,
            capture_output=True,
            text=True,
            timeout=max(0.5, deadline_s),
        )
    except (OSError, subprocess.SubprocessError):
        return []
    if out.returncode != 0:
        return []
    files: list[str] = []
    for line in out.stdout.splitlines():
        # porcelain format: 'XY <path>' (or 'XY <orig> -> <path>' for rename)
        path = line[3:].strip()
        if " -> " in path:
            path = path.split(" -> ", 1)[1].strip()
        if not path:
            continue
        if not include or any(fnmatch.fnmatch(path, g) for g in include):
            files.append(path)
    return files


def _build_command(cfg: dict, files: list[str]) -> list[str] | None:
    """Validation command DERIVED from the target. None ⇒ nothing wired (inert hook)."""
    cmd: list[str] = list(cfg.get("validateCmd") or [])
    if not cmd:
        script = (cfg.get("validateScript") or "").strip()
        if not script:
            return None  # nothing wired: hook INERT (default)
        cmd = list(cfg.get("runner") or DEFAULTS["runner"]) + [script]
    if cfg.get("passChangedFiles", True) and files:
        cmd = cmd + files
    return cmd


def _tail(text: str, max_bytes: int) -> str:
    raw = text.encode("utf-8", errors="ignore")
    if len(raw) <= max_bytes:
        return text.strip()
    return "…\n" + raw[-max_bytes:].decode("utf-8", errors="ignore").strip()


def _run(cmd: list[str], root: str, timeout_s: float) -> tuple[int, str]:
    try:
        out = subprocess.run(
            cmd, cwd=root, capture_output=True, text=True, timeout=max(0.5, timeout_s)
        )
    except subprocess.TimeoutExpired:
        return 124, "validation exceeded the latency ceiling (deadlineMs)"
    except (OSError, subprocess.SubprocessError) as exc:
        return 127, f"could not invoke the validator: {exc}"
    return out.returncode, ((out.stdout or "") + (out.stderr or "")).strip()


def _emit_context(cmd_str: str, rc: int, output: str, files: int) -> None:
    """PROPOSES/INFORMS the result via additionalContext (exit 0, does not block)."""
    head = (
        f"[{TAG}] end-of-turn validation ({files} changed file(s)) "
        f"via `{cmd_str}`: "
    )
    if rc == 0:
        msg = head + "PASSED. (formatting/fix applied by the script, if any.)"
    else:
        msg = (
            head + f"FAILED (exit {rc}). Fix before concluding — what it complained about:\n"
            f"{output}"
        )
    payload = {"hookSpecificOutput": {"hookEventName": "Stop", "additionalContext": msg}}
    print(json.dumps(payload))


def main() -> int:
    cfg = _load_config()
    if cfg.get("enabled") is False:
        return 0

    data = _read_input()
    if data.get("stop_hook_active") is True:  # anti-loop guard (cap of 8)
        return 0

    started = time.monotonic()
    deadline = float(cfg.get("deadlineMs", DEFAULTS["deadlineMs"])) / 1000.0
    root = _project_dir(data)

    include = list(cfg.get("includeGlobs") or [])
    files = _changed_files(root, include, deadline)
    if cfg.get("passChangedFiles", True) and not files:
        return 0  # nothing changed in scope ⇒ silence

    cmd = _build_command(cfg, files)
    if cmd is None:  # nothing wired (validateScript/Cmd empty) ⇒ inert hook
        return 0

    remaining = deadline - (time.monotonic() - started)
    if remaining <= 0:
        return 0  # deadline exceeded just assembling the scope: do not delay end of turn
    rc, output = _run(cmd, root, remaining)
    output = _tail(output, int(cfg.get("maxOutputBytes", DEFAULTS["maxOutputBytes"])))
    cmd_str = " ".join(shlex.quote(c) for c in cmd[: 3 if len(cmd) > 3 else len(cmd)])
    if len(cmd) > 3:
        cmd_str += " …"

    # Success: inform lightly (or silence if nothing to say in blocking mode).
    if rc == 0:
        if not cfg.get("blockOnFail", False):
            _emit_context(cmd_str, rc, output, len(files))
        return 0

    # Failure: blocking mode (configurable) × proposal (default).
    if cfg.get("blockOnFail", False):
        reason = (
            f"[{TAG}] mandatory end-of-turn validation FAILED (`{cmd_str}`, "
            f"exit {rc}). Fix and run again before concluding:\n{output}"
        )
        if (cfg.get("blockMode") or "decision") == "exit2":
            print(reason, file=sys.stderr)  # legacy form: stderr + exit 2
            return 2
        # modern form: decision:block + reason (Claude keeps working)
        print(json.dumps({"decision": "block", "reason": reason}))
        return 0

    _emit_context(cmd_str, rc, output, len(files))  # default: PROPOSES, exit 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
