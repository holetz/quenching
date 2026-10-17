"""Run Codex as an independent, read-only reviewer of a worktree.

The argv is fixed here and nowhere else: `-s read-only --ignore-user-config --ignore-rules`
always, so the user's `~/.codex/config.toml` (sandbox, approval policy, plugins, hooks) never
applies, and never `--ephemeral`, which would erase the quota snapshot the probe falls back on.
The prompt arrives on stdin; the events and the last message land in `.quenching/codex/<run>/`.

The sandbox is checked first, without spending quota. Where it fails, every command Codex would
run fails with it, so the review turns `prompt-only`: `cq` puts `git diff <base>..<head>` and the
touched files into `prompt.md`, and Codex only reads. The argv stays the same read-only one —
never `workspace-write`, never `danger-full-access`. Without `--base` there is nothing to put in
the prompt, and Codex is not called at all.

    mode    sandboxed · prompt-only · unavailable
    exit 0  Codex finished and wrote the review
    exit 1  Codex failed, wrote nothing, ran past `timeoutSeconds`, or no mode could run —
            the caller falls back
    exit 2  refusal: a missing worktree, prompt or `codex`, a run name already used, or a diff
            that could not be read
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
import time

from quenching.codex.probe import APP_SERVER_DEADLINE, check_sandbox, stop

RUN_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
NOT_MEASURED = "not measured"
PROMPT_ONLY_RULE = (
    "Modo prompt-only: o sandbox do Codex não funciona neste host. Não execute comandos e não "
    "leia arquivos: revise apenas o diff e os arquivos abaixo. Cite cada achado por path:line; "
    "o lado Claude reproduz cada achado antes de agir sobre ele.")


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


def _add_turn(totals: dict, usage: dict) -> None:
    for key, value in usage.items():
        if isinstance(value, int) and not isinstance(value, bool):
            totals[key] = totals.get(key, 0) + value


def measured_tokens(events_path: str):
    """The usage of every `turn.completed` that `codex exec --json` printed, summed.

    Without one, the last `total_token_usage` of the rollout format; without either,
    `not measured`. `total_tokens` is input plus output, as the event does not carry it.
    """
    turns: dict = {}
    found: list = []
    try:
        with open(events_path, encoding="utf-8", errors="replace") as handle:
            for line in handle:
                try:
                    event = json.loads(line)
                except json.JSONDecodeError:
                    continue
                if isinstance(event, dict) and event.get("type") == "turn.completed" \
                        and isinstance(event.get("usage"), dict):
                    _add_turn(turns, event["usage"])
                else:
                    _last_usage(event, found)
    except OSError:
        return NOT_MEASURED
    if turns:
        turns["total_tokens"] = turns.get("input_tokens", 0) + turns.get("output_tokens", 0)
        return turns
    return found[-1] if found else NOT_MEASURED


def _git(worktree: str, *args: str) -> str:
    return subprocess.run(["git", "-C", worktree, *args], capture_output=True, text=True,
                          errors="replace", check=True).stdout


def prompt_only(worktree: str, prompt: str, base: str, head: str) -> str:
    """The prompt, the rule that Codex only reads, the diff, and every touched file at `head`."""
    diff = _git(worktree, "diff", f"{base}..{head}")
    touched = _git(worktree, "diff", "--name-only", "--diff-filter=ACMR", f"{base}..{head}")
    with open(prompt, encoding="utf-8") as handle:
        parts = [handle.read().rstrip("\n"), PROMPT_ONLY_RULE,
                 f"## git diff {base}..{head}\n\n```diff\n{diff}```"]
    for path in touched.splitlines():
        parts.append(f"## {path} @ {head}\n\n```\n{_git(worktree, 'show', f'{head}:{path}')}```")
    return "\n\n".join(parts) + "\n"


def refusal(code: str, message: str) -> tuple[dict, int]:
    return {"ok": False, "code": code, "message": message}, 2


def run_review(root: str, settings: dict, worktree: str, prompt: str, run: str | None,
               env: dict | None = None, base: str | None = None,
               head: str = "HEAD") -> tuple[dict, int]:
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
    sandbox = check_sandbox(binary, worktree,
                            min(APP_SERVER_DEADLINE, settings["timeoutSeconds"]), env)
    mode = "sandboxed" if sandbox["state"] == "available" else "prompt-only"
    if mode == "prompt-only":
        if base is None:
            return {"ok": False, "fallback": True, "mode": "unavailable", "sandbox": sandbox,
                    "reason": "the sandbox is unavailable and no --base was given",
                    "run": run, "runDir": None, "reviewPath": None, "eventsPath": None,
                    "argv": None, "exitCode": None, "timedOut": False,
                    "model": settings["model"], "timeoutSeconds": settings["timeoutSeconds"],
                    "tokens": NOT_MEASURED}, 1
        try:
            text = prompt_only(worktree, prompt, base, head)
        except subprocess.CalledProcessError as exc:
            return refusal("codex-diff-unreadable",
                           f"git diff {base}..{head} failed: {exc.stderr.strip()}")
    os.makedirs(run_dir)
    if mode == "prompt-only":
        prompt = os.path.join(run_dir, "prompt.md")
        with open(prompt, "w", encoding="utf-8") as handle:
            handle.write(text)
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
    return {"ok": ok, "fallback": not ok, "mode": mode, "sandbox": sandbox, "reason": reason,
            "run": run, "runDir": run_dir,
            "reviewPath": review_path if wrote else None, "eventsPath": events_path,
            "argv": ["codex", *argv], "exitCode": code, "timedOut": timed_out,
            "model": settings["model"], "timeoutSeconds": settings["timeoutSeconds"],
            "tokens": measured_tokens(events_path)}, 0 if ok else 1
