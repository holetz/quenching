#!/usr/bin/env bash
# Print the fixture state as the grader sees it.
git status --porcelain 2>&1 || true
find .agents .claude -type f 2>/dev/null | sort || true
