"""SessionStart hook: adopt the linked worktree the harness cut before the session started.

VS Code's New Worktree and the Copilot CLI open a chat with cwd already inside their own
`<repo>.worktrees/<branch>` checkout. This body asks `cq git worktree adopt` to prepare that
checkout — the declared `sharedPaths`, the declared regenerable directories linked from the
primary, and the `worktreeSetup` once per worktree — and returns the context that tells the
agent it is already isolated and must not cut a second worktree.

The side effects are the contract; the message is a convenience. A client that discards
SessionStart output (the VS Code agent host runs the event and drops the answer) still gets the
tree prepared, and the spec-runner/orchestrator detect the linked worktree from git. On the
primary checkout, in a slot, with no `cq` on disk or with any failure, it prints `{}` and
nothing is written: absence is a no-op, never a block.

Runs under Claude Code and the GitHub Copilot harness, from bash, PowerShell or cmd — the deploy
launches it through one polyglot `python -c` line. Fails open: any crash prints `{}`.
"""
import json
import os
import subprocess
import sys

CQ = os.path.join(".agents", "quenching", "bin", "cq")
TIMEOUT = 280  # under the 300 s the hook entry declares


def _cwd(event: dict) -> str:
    """The session's directory: both harnesses name it, under one of three spellings."""
    for key in ("cwd", "workingDirectory", "working_directory"):
        value = event.get(key)
        if isinstance(value, str) and os.path.isdir(value):
            return value
    return os.getcwd()


def _cq(cwd: str) -> str | None:
    """The deployed launcher at or above the session, else the one in the primary checkout."""
    walk = os.path.realpath(cwd)
    while True:
        candidate = os.path.join(walk, CQ)
        if os.path.isfile(candidate):
            return candidate
        parent = os.path.dirname(walk)
        if parent == walk:
            break
        walk = parent
    for variable in ("CLAUDE_PROJECT_DIR", "COPILOT_PROJECT_DIR"):
        root = os.environ.get(variable)
        if root:
            candidate = os.path.join(root, CQ)
            if os.path.isfile(candidate):
                return candidate
    try:
        common = subprocess.run(["git", "-C", cwd, "rev-parse", "--path-format=absolute",
                                 "--git-common-dir"], capture_output=True, text=True,
                                encoding="utf-8", errors="replace", timeout=20).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None
    if not common:
        return None
    candidate = os.path.join(os.path.dirname(common), CQ)
    return candidate if os.path.isfile(candidate) else None


def _context(payload: dict) -> str:
    branch = payload.get("branch") or "(detached)"
    base = payload.get("base") or "main"
    return (
        f"quenching: this session already stands in the linked worktree {payload['worktree']} "
        f"on branch {branch}, cut before the session started. Do not cut another worktree and do "
        f"not acquire a slot for it: adopt this checkout. Its declared shared paths and "
        f"regenerable directories are linked, and any declared `worktreeSetup` has run. When a "
        f"spec starts here, stamp `branch: {{base: {base}, work: {branch}}}`."
    )


def decide(raw: str) -> dict:
    try:
        event = json.loads(raw)
        if not isinstance(event, dict):
            return {}
        cwd = _cwd(event)
        cq = _cq(cwd)
        if cq is None:
            return {}
        done = subprocess.run([sys.executable, cq, "git", "worktree", "adopt", "--json",
                               "--path", cwd],
                              capture_output=True, text=True, encoding="utf-8", errors="replace",
                              stdin=subprocess.DEVNULL, timeout=TIMEOUT)
        if done.returncode != 0:
            return {}
        payload = json.loads(done.stdout or "{}")
        if not isinstance(payload, dict) or not payload.get("adopted"):
            return {}
        return {"hookSpecificOutput": {"hookEventName": "SessionStart",
                                       "additionalContext": _context(payload)}}
    except Exception:
        return {}


def main() -> None:
    try:
        out = decide(sys.stdin.read())
    except Exception:
        out = {}
    print(json.dumps(out))
    sys.exit(0)


if __name__ == "__main__":
    main()
