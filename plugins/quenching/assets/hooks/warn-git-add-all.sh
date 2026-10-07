#!/usr/bin/env bash
# PreToolUse(Bash) warn-level guard for /quenching:git:commit: staging is the caller's decision,
# so `git add -A`, `--all` and `.` are flagged. Warns (exit 0 + context); never blocks.
input=$(cat)
if printf '%s' "$input" | grep -Eq 'git +add +(-A|--all|\.)([^A-Za-z0-9_./-]|$)'; then
  printf '%s\n' '{"systemMessage":"git:commit never stages with git add -A, --all or `.`","hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Invariant of /quenching:git:commit: do not run git add -A, git add --all or git add . ; commit only what is already staged."}}'
  exit 0
fi
printf '%s\n' '{}'
