#!/usr/bin/env bash
# Print the fixture state as the grader sees it.
git log --oneline 2>&1 || true
git status --porcelain 2>&1 || true
