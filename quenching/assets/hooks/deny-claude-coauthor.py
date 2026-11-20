"""PreToolUse(Bash|PowerShell) block-level guard: a commit or PR message never carries Claude's
co-authorship (a `Co-Authored-By:` trailer naming Claude or Anthropic, `noreply@anthropic.com`, the
`Generated with Claude Code` line).

Denies with the reason, so the agent reruns the command without it; it never rewrites the command,
since `updatedInput` only applies paired with `allow`, which would auto-approve whatever the command
chains. Opt out with QUENCHING_ALLOW_CLAUDE_COAUTHOR=1. Fails open: unparseable input or any crash
prints `{}`. Runs under Claude Code and the GitHub Copilot harness, from bash, PowerShell or cmd —
the deploy launches it through one polyglot `python -c` line.
"""
import json
import os
import re
import sys

FAST = re.compile(r"co-authored-by|noreply@anthropic|generated with \[?claude", re.I)
WRITES_MESSAGE = re.compile(r"\bgit\b[^\n|;&]*\b(commit|merge|tag|notes)\b|\bgh\s+pr\b|\bcq\s+git\b")
ATTRIBUTION = re.compile(r"co-authored-by:[^\n]*(claude|anthropic)|noreply@anthropic\.com"
                         r"|generated with \[?claude code", re.I)
REASON = ("quenching removes Claude co-authorship: drop every `Co-Authored-By: Claude ...` trailer and "
          "the `Generated with Claude Code` line from the message, then run the command again. "
          "Set `\"attribution\": {\"commit\": \"\", \"pr\": \"\"}` in settings to stop adding them.")


def command_of(event: dict) -> str | None:
    """The shell command, from Claude's `tool_input` or Copilot's `toolArgs` (an object or JSON text)."""
    args = event.get("tool_input")
    if args is None:
        args = event.get("toolArgs")
        if isinstance(args, str):
            args = json.loads(args)
    command = args.get("command") if isinstance(args, dict) else None
    return command if isinstance(command, str) else None


def decide(raw: str) -> dict:
    if os.environ.get("QUENCHING_ALLOW_CLAUDE_COAUTHOR") == "1" or not FAST.search(raw):
        return {}
    command = command_of(json.loads(raw))
    if not (command and WRITES_MESSAGE.search(command) and ATTRIBUTION.search(command)):
        return {}
    return {"hookSpecificOutput": {"hookEventName": "PreToolUse", "permissionDecision": "deny",
                                   "permissionDecisionReason": REASON}}


def main() -> None:
    try:
        out = decide(sys.stdin.read())
    except Exception:
        out = {}
    print(json.dumps(out))


if __name__ == "__main__":
    main()
