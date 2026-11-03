#!/usr/bin/env bash
# Seed the surface the components router cases inspect.
set -euo pipefail
mkdir -p .agents/skills
printf "# surface\n" > .agents/README.md
git add .agents
git commit -q -m "Seed the surface"
