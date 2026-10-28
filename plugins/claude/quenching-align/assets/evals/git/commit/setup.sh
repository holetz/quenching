#!/usr/bin/env bash
# Declare the subject convention, then leave the index the case "$1" needs.
set -euo pipefail
mkdir -p .claude
cat > .claude/quenching.json <<'JSON'
{
  "shared": {
    "gitConventions": {
      "commitSubject": "A short imperative sentence, no trailing period and no type prefix."
    }
  }
}
JSON
printf 'def page_size():\n    return 20\n' > pager.py
git add .claude/quenching.json pager.py
git commit -q -m "Declare the commit convention"
case "$1" in
  staged-change-committed)
    printf 'def page_size():\n    return 25\n' > pager.py
    git add pager.py
    printf '\nDraft note, not ready.\n' >> README.md
    ;;
  nothing-staged-no-commit)
    printf 'def page_size():\n    return 25\n' > pager.py
    ;;
  push-request-declines)
    printf 'def page_size():\n    return 25\n' > pager.py
    git add pager.py
    ;;
esac
