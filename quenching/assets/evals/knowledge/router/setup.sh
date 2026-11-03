#!/usr/bin/env bash
# Seed the docs the knowledge router cases inspect.
set -euo pipefail
mkdir -p docs/concepts
printf -- "---\nokf_version: \"0.2\"\n---\n\n# Docs\n" > docs/index.md
printf "# Glossary\n" > docs/glossary.md
git add docs
git commit -q -m "Seed the docs"
