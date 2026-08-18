#!/usr/bin/env bash
# section-squash-check.sh — the section squash resets to a captured SHA, and refuses a target
# that is not an ancestor of HEAD.
#
# `quenching-specs-execute` step 5h folds a section's per-task commits into one with a
# `git reset --soft`. The prose used to name the target by DESCRIPTION — "the commit immediately
# BEFORE this section's first task" — and on a plan's first section that commit *is* the base's
# tip, so an executor reaches for the cheapest ref satisfying the description: the base's name.
# That is correct only while the base does not move.
#
# MEASURED on 2026-08-16, branch `holetz/fast-status`, spec `listagem-ranqueada-nativa-no-cq-specs`:
# `develop` was fast-forwarded by another checkout mid-run, three section squashes resolved the ref
# to the NEW tip, and the three commits went on to declare the removal of 17 files and the
# reversion of 45 more the branch had never opened. Nothing caught it — the tree was clean, the
# spec validated, and the suite passed, because the deleted files belonged to another front.
#
# That claim is about HISTORY, not about any file's contents, so no linter and no reading of the
# command bodies can observe it: only a history exhibits it. This builds a throwaway repo whose
# base advances mid-section and judges three arms of the resulting history.
#
# WHAT THIS PROVES:
#   (a) resetting to the base's REF reproduces the failure — the folded commit declares the
#       removal of files the section never touched;
#   (b) resetting to the SHA captured when the section opened declares exactly what the section
#       wrote, with the same tree the pre-squash HEAD had and the right parent;
#   (c) `git merge-base --is-ancestor` refuses the base's new tip as a target and accepts the
#       captured sha — the guard catches the class regardless of how the target was spelled.
#
# WHAT THIS DOES NOT PROVE: that a live `quenching-specs-execute` session obeys the prose. Nothing
# automated can — the body gates on AskUserQuestion, which `claude -p` cannot answer, so an
# end-to-end session cannot run unattended. `/.knowledge/standards/quality/surface-verification.md`
# §Nothing under `commands/**` is testable in the session that writes it is the rule, and it is
# exactly why the guard lives on the command's own line rather than in a checker.
#
#   usage:  ./section-squash-check.sh
#   exit :  0 all passed · 1 an assertion failed · 2 the fixture could not be built, so NOTHING
#           was measured — not a pass, and not the same thing as a failed assertion either
#
# THE THIRD RUNG IS NOT DECORATION. This script builds the history it then judges, so it has two
# ways to be red and they call for opposite responses: a failed assertion is a claim about the
# squash to investigate, while a fixture that will not build is a claim about nothing at all.
#
# Established by the `squash-de-secao-deve-resetar-para-um-sha` spec, task 2.1.
set -uo pipefail

WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

emit () { printf '  %-6s %s\n' "$1" "$2"; }
check () { if [ "$1" = "yes" ]; then emit "PASS" "$2"; PASS=$((PASS+1)); else emit "FAIL" "$2"; FAIL=$((FAIL+1)); fi }

# The fixture could not be built. Everything below would assert against a history that was never
# constructed, so the run has no verdict to give — exit 2, never 1.
unmeasurable () { echo; echo "  NOTHING COULD BE MEASURED — $1" >&2; echo "  this is not a pass" >&2; exit 2; }

echo "section-squash-check — fixture at $WORK"
echo

# --------------------------------------------------------------------------- #
# Build a history whose base advances mid-section
# --------------------------------------------------------------------------- #
cd "$WORK" || unmeasurable "cannot enter the fixture directory"
git init -q -b main . 2>/dev/null || unmeasurable "git init refused"
git config user.email check@example.invalid
git config user.name  "section squash check"
git config commit.gpgsign false

echo "seed" > README.md
git add -A && git commit -qm "seed" || unmeasurable "the seed commit could not be made"
SECTION_BASE=$(git rev-parse HEAD^{commit})   # <section-base-sha>: captured when the section opens

# The section's two task commits, on a work branch cut from that captured commit.
build_section () {
  git checkout -q -b "$1" "$SECTION_BASE" || return 1
  echo "one" > task-one.txt
  git add task-one.txt && git commit -qm "plan/x: 1.1 first task" || return 1
  echo "two" > task-two.txt
  git add task-two.txt && git commit -qm "plan/x: 1.2 second task" || return 1
}
build_section plan/by-ref || unmeasurable "the by-ref work branch could not be built"

# The base moves — another checkout fast-forwards it with a whole front the branch never opened.
git checkout -q main || unmeasurable "cannot return to the base"
mkdir -p other-front
for n in 1 2 3 4 5; do echo "front file $n" > "other-front/f$n.txt"; done
git add -A && git commit -qm "another front lands on the base" \
  || unmeasurable "the base could not be advanced"
BASE_NEW_TIP=$(git rev-parse HEAD^{commit})

build_section plan/by-sha || unmeasurable "the by-sha work branch could not be built"

[ "$SECTION_BASE" != "$BASE_NEW_TIP" ] \
  || unmeasurable "the base did not actually move — the fixture cannot exhibit the failure"

# --------------------------------------------------------------------------- #
# (a) resetting to the base's REF — the failure, reproduced
# --------------------------------------------------------------------------- #
echo "a. reset --soft <base ref> reproduces the commit that declares removals"
git checkout -q plan/by-ref || unmeasurable "cannot check out the by-ref branch"
git reset --soft main >/dev/null 2>&1 \
  && git commit -qm "plan/x: 1 the section, folded to the ref" \
  || unmeasurable "the by-ref squash could not be made"
BY_REF=$(git rev-parse HEAD)

DELETED_BY_REF=$(git show --name-status --format='' "$BY_REF" | grep -c '^D')
if [ "$DELETED_BY_REF" -eq 5 ]; then r=yes; else r=no; fi
check "$r" "the folded commit declares 5 deletions the section never made (got $DELETED_BY_REF)"

if [ "$(git rev-parse "$BY_REF^")" = "$BASE_NEW_TIP" ]; then r=yes; else r=no; fi
check "$r" "its parent is the base's NEW tip, not the commit the section opened on"

# --------------------------------------------------------------------------- #
# (b) resetting to the captured SHA — what the section actually wrote
# --------------------------------------------------------------------------- #
echo "b. reset --soft <section-base-sha> declares exactly what the section wrote"
git checkout -q plan/by-sha || unmeasurable "cannot check out the by-sha branch"
TREE_BEFORE=$(git rev-parse HEAD^{tree})
git reset --soft "$SECTION_BASE" >/dev/null 2>&1 \
  && git commit -qm "plan/x: 1 the section, folded to the captured sha" \
  || unmeasurable "the by-sha squash could not be made"
BY_SHA=$(git rev-parse HEAD)

NAMES=$(git show --name-status --format='' "$BY_SHA")
if [ "$(grep -c '^D' <<<"$NAMES")" -eq 0 ]; then r=yes; else r=no; fi
check "$r" "the folded commit declares no deletion at all"

if [ "$(grep -c '^A' <<<"$NAMES")" -eq 2 ] \
   && grep -q 'task-one.txt' <<<"$NAMES" && grep -q 'task-two.txt' <<<"$NAMES"; then r=yes; else r=no; fi
check "$r" "it declares exactly the section's own two files"

if [ "$(git rev-parse "$BY_SHA^")" = "$SECTION_BASE" ]; then r=yes; else r=no; fi
check "$r" "its parent is the commit the section opened on"

if [ "$(git rev-parse "$BY_SHA^{tree}")" = "$TREE_BEFORE" ]; then r=yes; else r=no; fi
check "$r" "its tree is the pre-squash HEAD's tree — the squash moved the parent, not the content"

# --------------------------------------------------------------------------- #
# (c) the ancestry guard — it refuses the base's new tip, whatever named it
# --------------------------------------------------------------------------- #
echo "c. git merge-base --is-ancestor refuses a target outside the branch's history"
if git merge-base --is-ancestor "$BASE_NEW_TIP" HEAD 2>/dev/null; then r=no; else r=yes; fi
check "$r" "the base's new tip is rejected (non-zero), so the && stops before the reset"

if git merge-base --is-ancestor "$SECTION_BASE" HEAD 2>/dev/null; then r=yes; else r=no; fi
check "$r" "the captured sha is accepted (exit 0), so the reset runs"

# The guard is spelling-blind: `main` and its sha are the same commit, and both are refused.
if git merge-base --is-ancestor main HEAD 2>/dev/null; then r=no; else r=yes; fi
check "$r" "naming the same commit by its ref is refused too — the guard reads the commit"

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
