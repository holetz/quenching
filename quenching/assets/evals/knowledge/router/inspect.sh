#!/usr/bin/env bash
# Print the fixture state as the grader sees it.
git status --porcelain -- docs 2>&1 || true
ls docs docs/concepts 2>&1 || true
cat docs/glossary.md 2>&1 || true
