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
# create -> isolate -> execute -> conclude -> merge using the SAME `specs.py` calls the command
# bodies specify, and then asserts three properties of the resulting history.
#
# WHAT THIS PROVES: that the tool supports the ordering, and that a history built to it has the
# claimed shape — the merge is last, a task's box rides inside that task's own commit, and every
# recorded subject resolves to exactly one commit.
#
# WHAT THIS DOES NOT PROVE: that a live `/specs:execute` or `/specs:conclude` session follows the
# ordering. Nothing automated can: both bodies gate on AskUserQuestion, which `claude -p` cannot
# answer, so an end-to-end session cannot run unattended. That gap is real and is why the command
# bodies state the ordering as an invariant rather than relying on this script.
#
#   usage:  ./conclude-order-check.sh
#   exit :  0 all passed · 1 a check failed
#
# Established by the `move-conclude-merge-last` spec, task 6.1.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
SPECS="$HERE/specs.py"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

emit () { printf '  %-6s %s\n' "$1" "$2"; }
check () { if [ "$1" = "yes" ]; then emit "PASS" "$2"; PASS=$((PASS+1)); else emit "FAIL" "$2"; FAIL=$((FAIL+1)); fi }

# python3 on POSIX, the `py` launcher on Windows — the same fallback the commands use.
if command -v python3 >/dev/null 2>&1; then PY=python3
elif command -v py >/dev/null 2>&1; then PY=py
else echo "no python3 or py on PATH" >&2; exit 1; fi

SLUG=order-check
SUBJ_TASK="plan/$SLUG: 1.1 Add the widget"
SUBJ_MERGE="plan/$SLUG: merge (merge-commit)"

echo "conclude-order-check — specs.py at $SPECS"
echo

# --------------------------------------------------------------------------- #
# Build the history, exactly as the command bodies specify it
# --------------------------------------------------------------------------- #
cd "$WORK"
git init -q -b main .
git config user.email check@example.invalid
git config user.name  "order check"
git config commit.gpgsign false

mkdir -p specs/plans specs/archive docs
echo "# seed" > README.md
git add -A && git commit -qm "seed"

# create
"$PY" "$SPECS" new "$SLUG" --title "Order check" >/dev/null
FILE=$(ls specs/plans/*-"$SLUG".md)

# fill the ready gate, plus one task carrying declared files
for h in Proposal "Out of Scope" Impact Validation Design "Alternatives Considered" \
         "Open Decisions" Risks Handoff Tasks; do
  "$PY" "$SPECS" section "$SLUG" "$h" --write >/dev/null
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
if ! "$PY" "$SPECS" next --spec "$SLUG" --json 2>/dev/null | grep -q '"task": "1.1"'; then
  echo "  FIXTURE BROKEN: specs.py cannot see task 1.1 — the assertions below would be vacuous" >&2
  exit 1
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
"$PY" "$SPECS" task --spec "$SLUG" --check 1.1 --subject "$SUBJ_TASK" >/dev/null
git add src/widget.txt "$FILE" && git commit -qm "$SUBJ_TASK"
TASK_COMMIT=$(git rev-parse HEAD)

# conclude — archive on the branch, distil on the branch, stamp the merge on the branch
"$PY" "$SPECS" section "$SLUG" Outcome --write >/dev/null
"$PY" - "$FILE" <<'PY'
import io, re, sys
p = sys.argv[1]
s = io.open(p, encoding='utf-8').read()
s = re.sub(r'(?m)^## Outcome\n\n(?=(?:<!--|\Z))', '## Outcome\n\nShipped.\n\n', s)
io.open(p, 'w', encoding='utf-8', newline='').write(s)
PY
git add -A && git commit -qm "plan/$SLUG: write the outcome"
"$PY" "$SPECS" promote "$SLUG" --to archive --outcome done >/dev/null
ARCHIVED=$(ls specs/archive/*-"$SLUG".md)
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

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
