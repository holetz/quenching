#!/usr/bin/env bash
# conclude-order-check.sh — the one claim no in-process check can see.
#
# Every other check in this repo reads a file and judges its contents. The central claim of the
# `move-conclude-merge-last` spec is not about any file's contents — it is about ORDER:
#
#     nothing is written after the thing it describes,
#     and therefore nothing is committed to the base branch after the merge.
#
# Only a history exhibits that. So this builds a throwaway git repo, walks one spec through
# create -> isolate -> execute -> conclude -> merge using the SAME `cq specs` calls the command
# bodies specify, and then asserts three properties of the resulting history. A SECOND spec then
# walks the same create -> isolate -> execute path into conclude(--outcome abandoned), where the
# claim inverts: nothing is EVER committed to the branch, and everything conclude writes reaches
# the base directly — proved even against `git branch -D`, which the command itself never runs but
# a human might.
#
# WHAT THIS PROVES: that the tool supports the ordering, and that a history built to it has the
# claimed shape — the merge is last, a task's box rides inside that task's own commit, every
# recorded subject resolves to exactly one commit, and — for `abandoned` — the archive move, the
# `outcome:` stamp and the distillation's background note all land on the base with no merge
# involved, and survive the branch being destroyed.
#
# WHAT THIS DOES NOT PROVE: that a live `quenching-specs-execute` or `quenching-specs-conclude` session follows the
# ordering. Nothing automated can: both bodies gate on AskUserQuestion, which `claude -p` cannot
# answer, so an end-to-end session cannot run unattended. That gap is real and is why the command
# bodies state the ordering as an invariant rather than relying on this script.
#
#   usage:  ./conclude-order-check.sh
#   exit :  0 all passed · 1 a check failed · 2 the fixture could not be built, so NOTHING was
#           measured — not a pass, and not the same thing as a failed assertion either
#
# THE THIRD RUNG IS NOT DECORATION. This script builds the history it then judges, so it has two
# ways to be red, and they call for opposite responses: an assertion that fails is a claim about
# `cq specs` to investigate, while a fixture that will not build is a claim about nothing at all.
# It carried only `0 pass · 1 fail` until the fixture broke on two design changes it predates — the
# undated spec filename and the `files` backend's persistent worktree — and reported that as a
# failed check, sending a reader to look for a defect in the tool that the tool did not have. The
# repo's own `/.knowledge/standards/quality/surface-verification.md` §The five preconditions a check must
# satisfy is the rule; `citation-check.sh` already spells the same three rungs.
#
# Established by the `move-conclude-merge-last` spec, task 6.1. The `abandoned` arm — the fixture
# from "conclude --outcome abandoned" onward, and its seven assertions — was added by the
# `fix-conclude-abandoned-branch-harvest` spec, task 3.1.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CQ="$HERE/../bin/cq"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

emit () { printf '  %-6s %s\n' "$1" "$2"; }
check () { if [ "$1" = "yes" ]; then emit "PASS" "$2"; PASS=$((PASS+1)); else emit "FAIL" "$2"; FAIL=$((FAIL+1)); fi }

# The fixture could not be built. Everything below would assert against a history that was never
# constructed, so the run has no verdict to give — exit 2, never 1.
unmeasurable () { echo; echo "  NOTHING COULD BE MEASURED — $1" >&2; echo "  this is not a pass" >&2; exit 2; }

# python3 on POSIX, the `py` launcher on Windows — the same fallback the commands use.
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v py >/dev/null 2>&1; then PY=py
else echo "no python3 or py on PATH" >&2; exit 1; fi

SLUG=order-check
SUBJ_TASK="plan/$SLUG: 1.1 Add the widget"
SUBJ_MERGE="plan/$SLUG: merge (merge-commit)"

echo "conclude-order-check — cq at $CQ"
echo

# --------------------------------------------------------------------------- #
# Build the history, exactly as the command bodies specify it
# --------------------------------------------------------------------------- #
cd "$WORK"
git init -q -b main .
git config user.email check@example.invalid
git config user.name  "order check"
git config commit.gpgsign false

# `.specs/`, not `specs/`, and PRE-CREATED rather than left to `new` — both halves load-bearing,
# and neither was true when this fixture was written. `find_specs_root` walks up for an existing
# `.specs/` and uses it; only when none exists does the `files` backend put the workspace in its
# persistent worktree under `.agents/worktrees/`, on a dedicated branch, in another checkout. This
# fixture needs the in-tree form, because assertion 2 is that a task's box and its code ride the
# SAME commit — which they cannot when the spec file lives on a different branch entirely.
#
# Pre-creating it also keeps the run off the backend's `.gitignore` guard: `cq specs new` refuses
# (exit 2) when `.agents/worktrees/` is not ignored, and that refusal is only reachable on the
# worktree path this fixture never takes. Measured both ways — see the `unmeasurable` call below,
# which is exactly what a fixture that drops this line now gets.
mkdir -p .specs/plans .specs/archive docs
echo "# seed" > README.md
git add -A && git commit -qm "seed"

# create — the refusal is NOT swallowed. `>/dev/null` here hid a hard exit 2 for as long as the
# guard above existed, and every later step failed on its consequences instead of its cause.
if ! "$PY" "$CQ" specs new "$SLUG" --title "Order check" >/dev/null; then
  unmeasurable "cq specs new refused — the fixture has no spec to walk through the cycle"
fi
FILE=$(ls .specs/plans/"$SLUG".md 2>/dev/null) \
  || unmeasurable "no spec file at .specs/plans/$SLUG.md after cq specs new"

# fill the ready gate, plus one task carrying declared files
for h in Proposal "Out of Scope" Impact Validation Design "Alternatives Considered" \
         "Open Decisions" Risks Handoff Tasks; do
  "$PY" "$CQ" specs section "$SLUG" "$h" --write >/dev/null
done
"$PY" - "$FILE" <<'PY'
import io, re, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
# Every gate section gets a body. `## Tasks` is replaced wholesale with one real task — split on
# the HEADING, anchored at line start: the template's leading comment mentions "## Tasks" in
# prose, and splitting on the bare phrase truncates the file mid-comment, leaving an unterminated
# `<!--` that masks every task from the parser.
s = re.sub(r'(?m)^(## (?!Tasks)[A-Z][^\n]*)\n\n(?=(?:<!--|## |\Z))', r'\1\n\n- none — fixture\n\n', s)
head = re.split(r'(?m)^## Tasks[ \t]*$', s)[0]
io.open(p, 'w', encoding='utf-8', newline='').write(
    head + "## Tasks\n\n### 1. The work\n\n- [ ] 1.1 Add the widget\n      files: src/widget.txt\n")
PY
git add -A && git commit -qm "plan/$SLUG: record the spec"

# The fixture is only useful if the tool can see its task. Fail loudly rather than quietly
# asserting against a spec whose `## Tasks` never parsed.
if ! "$PY" "$CQ" specs next --spec "$SLUG" --json 2>/dev/null | grep -q '"task": "1.1"'; then
  unmeasurable "cq specs cannot see task 1.1 — the assertions below would be vacuous"
fi

BASE_BEFORE=$(git rev-parse HEAD)

# isolate — the branch, then the record
git checkout -q -b "plan/$SLUG"
"$PY" - "$FILE" <<'PY'
import io, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
s = s.replace("verification:", "branch: {base: main, work: plan/order-check}\nverification:", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
PY
git add -A && git commit -qm "plan/$SLUG: record the isolation"

# execute — write the code, TICK THE BOX, then commit both together
mkdir -p src && echo "widget" > src/widget.txt
"$PY" "$CQ" specs task --spec "$SLUG" --check 1.1 --subject "$SUBJ_TASK" >/dev/null
git add src/widget.txt "$FILE" && git commit -qm "$SUBJ_TASK"
TASK_COMMIT=$(git rev-parse HEAD)

# conclude — archive on the branch, distil on the branch, stamp the merge on the branch
"$PY" "$CQ" specs section "$SLUG" Outcome --write >/dev/null
"$PY" - "$FILE" <<'PY'
import io, re, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
s = re.sub(r'(?m)^## Outcome\n\n(?=(?:<!--|\Z))', '## Outcome\n\nShipped.\n\n', s)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
PY
git add -A && git commit -qm "plan/$SLUG: write the outcome"
"$PY" "$CQ" specs promote "$SLUG" --to archive --outcome done >/dev/null
ARCHIVED=$(ls .specs/archive/"$SLUG".md 2>/dev/null) \
  || unmeasurable "no archived spec at .specs/archive/$SLUG.md after cq specs promote"
git add -A && git commit -qm "plan/$SLUG: archive"

echo "distilled" > docs/distilled.md                       # the distillation, on the BRANCH
"$PY" - "$ARCHIVED" <<'PY'
import io, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
s = s.replace("verification:",
              'merge: {strategy: merge-commit, subject: plan/order-check: merge (merge-commit)}\nverification:', 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
PY
git add -A && git commit -qm "plan/$SLUG: distil and stamp the merge"

# merge — the last action
git checkout -q main
git merge -q --no-ff "plan/$SLUG" -m "$SUBJ_MERGE"

# --------------------------------------------------------------------------- #
# 1. the base's HEAD IS the merge commit — nothing follows it
# --------------------------------------------------------------------------- #
echo "1. nothing is written to the base after the merge"
HEAD_SUBJ=$(git log -1 --format=%s)
PARENTS=$(git rev-list --parents -n 1 HEAD | wc -w)
if [ "$HEAD_SUBJ" = "$SUBJ_MERGE" ]; then r=yes; else r=no; fi
check "$r" "git rev-parse HEAD is the merge commit (subject matches the record)"
if [ "$PARENTS" -eq 3 ]; then r=yes; else r=no; fi
check "$r" "HEAD has two parents — it is a merge, not a commit made after one"
if [ "$(git rev-list --count "$BASE_BEFORE"..HEAD --first-parent)" -eq 1 ]; then r=yes; else r=no; fi
check "$r" "exactly one first-parent commit landed on main — the merge itself"

# --------------------------------------------------------------------------- #
# 2. the task's commit carries the code AND the ticked box
# --------------------------------------------------------------------------- #
echo "2. the box rides inside the task's own commit"
# --name-only, not --stat: `--stat` abbreviates long paths with `...` and the spec's filename is
# exactly the kind it truncates, which reads as a failure when the file is right there.
NAMES=$(git show --name-only --format='' "$TASK_COMMIT")
if grep -q 'src/widget.txt' <<<"$NAMES"; then r=yes; else r=no; fi
check "$r" "the task commit lists the code file"
if grep -q "$(basename "$FILE")" <<<"$NAMES"; then r=yes; else r=no; fi
check "$r" "the task commit lists the spec file"
if git show "$TASK_COMMIT:$FILE" | grep -q '^- \[x\] 1.1'; then r=yes; else r=no; fi
check "$r" "the box is already ticked in that commit's version of the spec"

# --------------------------------------------------------------------------- #
# 3. every recorded subject resolves to exactly one commit
# --------------------------------------------------------------------------- #
echo "3. each recorded subject resolves to exactly one commit"
while IFS= read -r s; do
  [ -n "$s" ] || continue
  n=$(git log --grep="$s" --fixed-strings --format=%H | wc -l)
  if [ "$n" -eq 1 ]; then r=yes; else r=no; fi
  check "$r" "\"$s\" -> $n commit(s)"
done < <("$PY" - "$ARCHIVED" <<'PY' | tr -d '\r'
import io, re, sys
for m in re.finditer(r'^\s+subject:\s*(.+?)\s*$', io.open(sys.argv[1], encoding='utf-8').read(), re.M):
    print(m.group(1))
PY
)
# `tr -d '\r'` above is load-bearing on Windows: python's print writes \r\n to stdout, and a
# subject carrying a trailing CR makes `git log --grep --fixed-strings` match nothing — which
# reads as "the record is unresolvable" when the record is fine and the pipeline is not.
n=$(git log --grep="$SUBJ_MERGE" --fixed-strings --format=%H | wc -l)
if [ "$n" -eq 1 ]; then r=yes; else r=no; fi
check "$r" "the merge record's subject -> $n commit(s)"

# --------------------------------------------------------------------------- #
# Build a SECOND spec through create -> isolate -> execute -> conclude(--outcome abandoned)
# --------------------------------------------------------------------------- #
echo
echo "conclude --outcome abandoned"
SLUG2=order-check-abandoned
SUBJ_TASK2="plan/$SLUG2: 1.1 Add the gadget"

git checkout -q main
if ! "$PY" "$CQ" specs new "$SLUG2" --title "Order check abandoned" >/dev/null </dev/null; then
  unmeasurable "cq specs new refused — the abandoned fixture has no spec to walk through the cycle"
fi
FILE2=$(ls .specs/plans/"$SLUG2".md 2>/dev/null) \
  || unmeasurable "no spec file at .specs/plans/$SLUG2.md after cq specs new"

for h in Proposal "Out of Scope" Impact Validation Design "Alternatives Considered" \
         "Open Decisions" Risks Handoff Tasks; do
  "$PY" "$CQ" specs section "$SLUG2" "$h" --write >/dev/null </dev/null
done
"$PY" - "$FILE2" <<'PY'
import io, re, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
s = re.sub(r'(?m)^(## (?!Tasks)[A-Z][^\n]*)\n\n(?=(?:<!--|## |\Z))', r'\1\n\n- none — fixture\n\n', s)
head = re.split(r'(?m)^## Tasks[ \t]*$', s)[0]
io.open(p, 'w', encoding='utf-8', newline='').write(
    head + "## Tasks\n\n### 1. The work\n\n- [ ] 1.1 Add the gadget\n      files: src2/gadget.txt\n")
PY
git add -A && git commit -qm "plan/$SLUG2: record the spec"

if ! "$PY" "$CQ" specs next --spec "$SLUG2" --json 2>/dev/null | grep -q '"task": "1.1"'; then
  unmeasurable "cq specs cannot see task 1.1 — the abandoned assertions below would be vacuous"
fi

# isolate — the branch, then the record
git checkout -q -b "plan/$SLUG2"
"$PY" - "$FILE2" <<'PY'
import io, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
s = s.replace("verification:", "branch: {base: main, work: plan/order-check-abandoned}\nverification:", 1)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
PY
git add -A && git commit -qm "plan/$SLUG2: record the isolation"

# execute — the one task, one commit, on the branch
mkdir -p src2 && echo "gadget" > src2/gadget.txt
"$PY" "$CQ" specs task --spec "$SLUG2" --check 1.1 --subject "$SUBJ_TASK2" >/dev/null
git add src2/gadget.txt "$FILE2" && git commit -qm "$SUBJ_TASK2"

# conclude --outcome abandoned — THE FIX UNDER TEST. Everything below is computed HERE, on the
# branch, where the spec's data lives — and none of it is committed here. It carries across to
# the checkout that already holds <base> the same way any uncommitted change does when the
# branch under it is switched: nothing this outcome writes from here on lands on plan/$SLUG2.
echo "background: learned by not building it" > docs/distilled-abandoned.md
"$PY" "$CQ" specs section "$SLUG2" Outcome --write >/dev/null <<'OUT'
## Outcome

Abandoned for the order check.
OUT
"$PY" "$CQ" specs promote "$SLUG2" --to archive --outcome abandoned >/dev/null
[ -f ".specs/archive/$SLUG2.md" ] \
  || unmeasurable "no archived spec at .specs/archive/$SLUG2.md after cq specs promote (abandoned)"

MAIN_BEFORE2=$(git rev-parse main)
git checkout -q main
git add docs/distilled-abandoned.md
git commit -qm "plan/$SLUG2: distil (background)"
git add .specs/archive/"$SLUG2".md
git rm -q .specs/plans/"$SLUG2".md
git commit -qm "plan/$SLUG2: archive (abandoned)"

# --------------------------------------------------------------------------- #
# 4. the archive move reached the base
# --------------------------------------------------------------------------- #
echo "4. the archive move reached the base"
if git cat-file -e "main:.specs/archive/$SLUG2.md" 2>/dev/null; then r=yes; else r=no; fi
check "$r" "main:.specs/archive/$SLUG2.md resolves"

# --------------------------------------------------------------------------- #
# 5. the spec left plans/ on the base
# --------------------------------------------------------------------------- #
echo "5. the spec left plans/ on the base"
if git cat-file -e "main:.specs/plans/$SLUG2.md" 2>/dev/null; then r=no; else r=yes; fi
check "$r" "main:.specs/plans/$SLUG2.md does not resolve"

# --------------------------------------------------------------------------- #
# 6. outcome: abandoned is on the base's own copy, not only the branch's
# --------------------------------------------------------------------------- #
echo "6. outcome: abandoned is on the base's own copy"
if git show "main:.specs/archive/$SLUG2.md" | grep -q '^outcome: abandoned'; then r=yes; else r=no; fi
check "$r" "the base's archived copy carries outcome: abandoned"

# --------------------------------------------------------------------------- #
# 7. the distillation's background note resolves on the base
# --------------------------------------------------------------------------- #
echo "7. the distillation's background note resolves on the base"
if git cat-file -e "main:docs/distilled-abandoned.md" 2>/dev/null; then r=yes; else r=no; fi
check "$r" "main:docs/distilled-abandoned.md resolves"

# --------------------------------------------------------------------------- #
# 8. the base's own branch --merged does not list the branch — nothing was merged
# --------------------------------------------------------------------------- #
echo "8. the branch was never merged"
if git branch --merged main | grep -q "plan/$SLUG2"; then r=no; else r=yes; fi
check "$r" "git branch --merged does not list plan/$SLUG2"

# --------------------------------------------------------------------------- #
# 9. no commit this outcome made on the base is a merge in disguise — one parent each
# --------------------------------------------------------------------------- #
echo "9. nothing landed by way of a merge commit"
ALLONE=yes
for c in $(git rev-list "$MAIN_BEFORE2"..main); do
  p=$(git rev-list --parents -n 1 "$c" | wc -w)
  [ "$p" -eq 2 ] || { ALLONE=no; break; }
done
check "$ALLONE" "every commit made on the base while closing has exactly one parent"

# --------------------------------------------------------------------------- #
# 10. THE assertion that fails today — it survives deleting the branch, even with -D
# --------------------------------------------------------------------------- #
echo "10. it survives deleting the branch, even with -D"
git branch -D "plan/$SLUG2" >/dev/null
if git cat-file -e "main:.specs/archive/$SLUG2.md" 2>/dev/null \
   && ! git cat-file -e "main:.specs/plans/$SLUG2.md" 2>/dev/null \
   && git show "main:.specs/archive/$SLUG2.md" | grep -q '^outcome: abandoned' \
   && git cat-file -e "main:docs/distilled-abandoned.md" 2>/dev/null; then
  r=yes
else
  r=no
fi
check "$r" "assertions 4, 5, 6 and 7 above all still hold after git branch -D"

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
