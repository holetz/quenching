#!/usr/bin/env bash
# Print the spec store as the grader sees it: every spec the arm created, or none.
python3 "$CQ" specs list --json 2>&1 || true
