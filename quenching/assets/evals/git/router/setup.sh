#!/usr/bin/env bash
# Seed the repo the git router cases inspect.
set -euo pipefail
printf "base\n" > base.txt
git add base.txt
git commit -q -m "Seed the repository"
