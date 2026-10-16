"""Run Codex as an independent, read-only reviewer of a worktree.

The argv is fixed here and nowhere else: `-s read-only --ignore-user-config --ignore-rules`
always, so the user's `~/.codex/config.toml` (sandbox, approval policy, plugins, hooks) never
applies, and never `--ephemeral`, which would erase the quota snapshot the probe falls back on.
The prompt arrives on stdin; the events and the last message land in `.quenching/codex/<run>/`.

    exit 0  Codex finished and wrote the review
    exit 1  Codex failed, wrote nothing, or ran past `timeoutSeconds` — the caller falls back
    exit 2  refusal: a missing worktree, prompt or `codex`, or a run name already used
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time

from quenching.codex.probe import stop

RUN_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
NOT_MEASURED = "not measured"


def build_argv(model: str, worktree: str, review_path: str) -> list[str]:
    return ["exec", "-s", "read-only", "--ignore-user-config", "--ignore-rules",
            "-m", model, "-c", "model_reasoning_effort=high", "-C", worktree,
            "--json", "-o", review_path, "-"]


def _last_usage(node, found: list) -> None:
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "total_token_usage" and isinstance(value, dict):
                found.append(value)
            else:
                _last_usage(value, found)
    elif isinstance(node, list):
        for item in node:
            _last_usage(item, found)


def measured_tokens(events_path: str):
    """The last `total_token_usage` in the events, or `not measured`."""
    found: list = []
    try:
        with open(events_path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    _last_usage(json.loads(line), found)
                except json.JSONDecodeError:
                    continue
    except OSError:
        return NOT_MEASURED
    return found[-1] if found else NOT_MEASURED


def refusal(code: str, message: str) -> tuple[dict, int]:
    return {"ok": False, "code": code, "message": message}, 2


def run_review(root: str, settings: dict, worktree: str, prompt: str, run: str | None,
               env: dict | None = None) -> tuple[dict, int]:
    env = dict(os.environ if env is None else env)
    worktree, prompt = os.path.abspath(worktree), os.path.abspath(prompt)
    if not os.path.isdir(worktree):
        return refusal("codex-worktree-missing", f"worktree does not exist: {worktree}")
    if not os.path.isfile(prompt):
        return refusal("codex-prompt-missing", f"prompt file does not exist: {prompt}")
    binary = shutil.which("codex", path=env.get("PATH"))
    if binary is None:
        return refusal("codex-missing", "codex is not on PATH")
    run = run or time.strftime("%Y%m%dT%H%M%SZ", time.gmtime())
    if not RUN_NAME.match(run):
        return refusal("codex-run-name", f"run name must match {RUN_NAME.pattern}: {run}")
    run_dir = os.path.join(root, ".quenching", "codex", run)
    if os.path.exists(run_dir):
        return refusal("codex-run-exists", f"run directory already exists: {run_dir}")
    os.makedirs(run_dir)
    review_path = os.path.join(run_dir, "review.md")
    events_path = os.path.join(run_dir, "events.jsonl")
    argv = build_argv(settings["model"], worktree, review_path)
    timed_out = False
    with open(prompt, encoding="utf-8") as stdin, \
            open(events_path, "w", encoding="utf-8") as stdout, \
            open(os.path.join(run_dir, "stderr.log"), "w", encoding="utf-8") as stderr:
        process = subprocess.Popen([binary, *argv], stdin=stdin, stdout=stdout, stderr=stderr,
                                   cwd=worktree, env=env, start_new_session=True)
        try:
            code = process.wait(timeout=settings["timeoutSeconds"])
        except subprocess.TimeoutExpired:
            stop(process)
            code, timed_out = process.returncode, True
    wrote = os.path.isfile(review_path) and os.path.getsize(review_path) > 0
    if timed_out:
        reason = f"codex ran past {settings['timeoutSeconds']}s and was stopped"
    elif code != 0:
        reason = f"codex exited {code}"
    elif not wrote:
        reason = "codex wrote no review"
    else:
        reason = "review written"
    ok = not timed_out and code == 0 and wrote
    return {"ok": ok, "fallback": not ok, "reason": reason, "run": run, "runDir": run_dir,
            "reviewPath": review_path if wrote else None, "eventsPath": events_path,
            "argv": ["codex", *argv], "exitCode": code, "timedOut": timed_out,
            "model": settings["model"], "timeoutSeconds": settings["timeoutSeconds"],
            "tokens": measured_tokens(events_path)}, 0 if ok else 1
