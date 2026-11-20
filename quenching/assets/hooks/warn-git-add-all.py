"""PreToolUse(Bash|PowerShell) warn-level guard for /quenching-git commit: staging is the caller's
decision, so `git add -A`, `--all` and `.` are flagged. Warns (exit 0 + context); never blocks.

The regex is the fast path; a hit is confirmed on the parsed command, so text that only mentions
a blanket `git add` (an echo, a quoted message, a heredoc line that is not `git`) stays silent.
Lines are split on newlines when each parses alone, else the whole command is one stream; input
that is not JSON or does not tokenize keeps the regex's verdict.

Runs under Claude Code and the GitHub Copilot harness, from bash, PowerShell or cmd — the deploy
launches it through one polyglot `python -c` line. Fails open: any crash prints `{}`.
"""
import json
import re
import shlex
import sys

BLANKET = re.compile(r"git[^|;&\n]* add +(-A|--all|\.)([^A-Za-z0-9_./-]|$)")
ASSIGNMENT = re.compile(r"^[A-Za-z_][A-Za-z0-9_]*=")
GLOBAL_OPTIONS = ("-C", "-c")
WARNING = {
    "systemMessage": "/quenching-git commit never stages with git add -A, --all or `.`",
    "hookSpecificOutput": {
        "hookEventName": "PreToolUse",
        "additionalContext": ("Invariant of /quenching-git commit: do not run git add -A, git add --all "
                              "or git add . ; commit only what is already staged."),
    },
}


def _tokens(text: str) -> list[str]:
    lexer = shlex.shlex(text, posix=True, punctuation_chars=True)
    lexer.whitespace_split = True
    return list(lexer) + [";"]


def _streams(command: str) -> list[list[str]]:
    try:
        return [_tokens(line) for line in command.splitlines()]
    except ValueError:
        return [_tokens(command)]


def _blanket(words: list[str]) -> bool:
    while words and ASSIGNMENT.match(words[0]):
        words = words[1:]
    if not words or words[0] != "git":
        return False
    rest = words[1:]
    while rest and rest[0] in GLOBAL_OPTIONS:
        rest = rest[2:]
    return bool(rest) and rest[0] == "add" and any(arg in ("-A", "--all", ".") for arg in rest[1:])


def stages_everything(raw: str) -> bool:
    if not BLANKET.search(raw):
        return False
    try:
        command = json.loads(raw)["tool_input"]["command"]
        streams = _streams(command)
    except (ValueError, KeyError, TypeError):
        return True
    for tokens in streams:
        words: list[str] = []
        for token in tokens:
            if set(token) <= set(";&|()"):
                if _blanket(words):
                    return True
                words = []
            else:
                words.append(token)
    return False


def main() -> None:
    try:
        out = WARNING if stages_everything(sys.stdin.read()) else {}
    except Exception:
        out = {}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
