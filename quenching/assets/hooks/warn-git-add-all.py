"""PreToolUse(Bash|PowerShell) warn-level git hygiene guard for /quenching-git. Two rules, one
process, because every shell call pays one interpreter start per hook entry:

* staging is the caller's decision, so `git add -A`, `--all` and `.` are flagged;
* the leak and identity gates live in git hooks, so a command that skips them — `--no-verify`,
  `git commit -n`, or `git -c core.hooksPath=...` — is flagged too.

The file keeps the name of its first rule: the deploy's settings merge finds its own entry by it.
Warns (exit 0 + context); never blocks. It is not a security boundary: it reads the command text,
so a hook path set through a variable, an alias or `git config` before the call goes unseen.

Runs under Claude Code and the GitHub Copilot harness, from bash, PowerShell or cmd — the deploy
launches it through one polyglot `python -c` line. Fails open: any crash prints `{}`.
"""
import json
import re
import sys

BLANKET = re.compile(r"git +add +(-A|--all|\.)([^A-Za-z0-9_./-]|$)")
BYPASS = re.compile(r"\bgit\b[^\n|;&]*\s--no-verify\b"
                    r"|\bgit\s+commit\b[^\n|;&]*\s-n(\s|$|\\|\")"
                    r"|\bgit\s+-c\s*core\.hookspath=", re.I)
RULES = (
    (BLANKET, "/quenching-git commit never stages with git add -A, --all or `.`",
     "Invariant of /quenching-git commit: do not run git add -A, git add --all or git add . ; "
     "commit only what is already staged."),
    (BYPASS, "this command skips the repository's git hooks (--no-verify, commit -n or "
             "-c core.hooksPath=)",
     "The pre-commit and pre-push hooks run the leak and identity gates. Do not skip them: fix "
     "what the hook reports and run the command again without the bypass."),
)


def decide(raw: str) -> dict:
    hits = [(message, context) for pattern, message, context in RULES if pattern.search(raw)]
    if not hits:
        return {}
    return {
        "systemMessage": "; ".join(message for message, _ in hits),
        "hookSpecificOutput": {
            "hookEventName": "PreToolUse",
            "additionalContext": " ".join(context for _, context in hits),
        },
    }


def main() -> None:
    try:
        out = decide(sys.stdin.read())
    except Exception:
        out = {}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
