#!/usr/bin/env bash
# PreToolUse(Bash) block-level guard, wired plugin-wide by hooks/hooks.json: a commit or PR message
# never carries Claude's co-authorship (`Co-Authored-By: Claude …`, `noreply@anthropic.com`,
# `Generated with Claude Code`). Denies with the reason, so Claude reruns the command without it;
# it never rewrites the command, since `updatedInput` only applies paired with `allow`, which would
# auto-approve whatever the command chains. Opt out with QUENCHING_ALLOW_CLAUDE_COAUTHOR=1.
# Fails open: no python3, unparseable input or any crash prints `{}`.
input=$(cat)
if [ "${QUENCHING_ALLOW_CLAUDE_COAUTHOR:-}" = "1" ] \
  || ! printf '%s' "$input" | grep -Eiq 'co-authored-by|noreply@anthropic|generated with \[?claude'; then
  printf '%s\n' '{}'
  exit 0
fi
command -v python3 >/dev/null 2>&1 || { printf '%s\n' '{}'; exit 0; }
printf '%s' "$input" | python3 -I -c '
import json, re, sys
try:
    command = json.load(sys.stdin)["tool_input"]["command"]
except Exception:
    print("{}"); sys.exit(0)
WRITES_MESSAGE = re.compile(r"\bgit\b[^\n|;&]*\b(commit|merge|tag|notes)\b|\bgh\s+pr\b|\bcq\s+git\b")
ATTRIBUTION = re.compile(r"co-authored-by:[^\n]*(claude|anthropic)|noreply@anthropic\.com"
                         r"|generated with \[?claude code", re.I)
if not (isinstance(command, str) and WRITES_MESSAGE.search(command) and ATTRIBUTION.search(command)):
    print("{}"); sys.exit(0)
print(json.dumps({"hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": (
        "quenching removes Claude co-authorship: drop every `Co-Authored-By: Claude ...` trailer and "
        "the `Generated with Claude Code` line from the message, then run the command again. "
        "Set `\"attribution\": {\"commit\": \"\", \"pr\": \"\"}` in settings to stop adding them.")}}))
' 2>/dev/null || printf '%s\n' '{}'
