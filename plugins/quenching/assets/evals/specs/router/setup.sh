#!/usr/bin/env bash
# Turn the fixture into a git spec store over a local bare origin, next to the workspace.
set -euo pipefail
origin="$(dirname "$EVAL_WORKSPACE")/origin.git"
git init -q --bare "$origin"
git remote add origin "$origin"
mkdir -p .claude
printf '{\n  "backend": "git"\n}\n' > .claude/quenching.json
git add .claude/quenching.json
git commit -q -m "Declare the git spec store"
git push -q origin main
