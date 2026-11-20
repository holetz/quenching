"""PreToolUse(Bash|PowerShell) warn-level guard for /quenching-git commit: staging is the caller's
decision, so `git add -A`, `--all` and `.` are flagged. Warns (exit 0 + context); never blocks.

Runs under Claude Code and the GitHub Copilot harness, from bash, PowerShell or cmd — the deploy
launches it through one polyglot `python -c` line. Fails open: any crash prints `{}`.
"""
import json
import re
import sys

BLANKET = re.compile(r"git +add +(-A|--all|\.)([^A-Za-z0-9_./-]|$)")
WARNING = {
    "systemMessage": "/quenching-git commit never stages with git add -A, --all or `.`",
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": ("Invariant of /quenching-git commit: do not run git add -A, git add --all "
                              "or git add . ; commit only what is already staged."),
    },
}


def main() -> None:
    try:
        out = WARNING if BLANKET.search(sys.stdin.read()) else {}
    except Exception:
        out = {}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
