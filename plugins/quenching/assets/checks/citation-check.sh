#!/usr/bin/env bash
# citation-check.sh — the two halves of a rename, over the whole repository, blind.
#
# A rename has two halves, and the cheap one is the trap. Half 1 measures that the OLD name died.
# Half 2 measures that the NEW name was born. A repository in which every citation points at
# nothing passes half 1 on its own — that is exactly what a half-finished rename produces, and it
# is silent: the command registry is rebuilt at SESSION START, so the session that moves a body
# is structurally incapable of observing the breakage it caused.
#
#   usage:  ./citation-check.sh [--half 1|2] [/path/to/repo]
#   exit :  0 both halves passed
#           1 a half failed — a dead name survives, or a citation resolves to nothing
#           2 nothing could be measured — no verdict, do not read it as a pass
#
# BLIND, WITH NO ALLOWLIST. Historical mentions are rewritten to the new name like every other
# citation: git history holds the past, the docs describe the present, and a check with content
# exceptions is a check people learn to ignore.
#
# THREE SCOPE RULES, WHICH ARE NOT EXCEPTIONS:
#
#   - The instrument does not measure itself. A check that greps for a string necessarily
#     contains that string, so this file is out of scope by construction — and to keep that from
#     becoming a hole, half 1 first proves it can SEE, with a canary that must survive the rename.
#     Note what the canary is not: proving that the dead patterns still match something would be
#     a proof that goes false exactly when the rename finishes. What can go silently wrong is the
#     sweep reading an empty corpus — a `git grep` that fails, a pathspec that excludes
#     everything — and then every pattern reports zero hits and half 1 passes over nothing.
#   - `.specs/` is out of scope. It is the planning workspace — the record of what was decided,
#     not a description of the present — and every task-level `verify:` in this plan excludes it
#     the same way.
#   - `tests/fixtures/golden/`, `tests/capture_golden.py` and `assets/evals/**/runs/` are data, not
#     citations. A golden is STDOUT a pre-refactor script actually printed, frozen the day task 1.1
#     captured it — task 1.1's own constraint is that nothing later may recapture one, so a golden
#     necessarily keeps quoting a script that no longer exists, forever, by design; an eval run log
#     is the same shape, a grading record of one dated invocation that used to route through the
#     old namespace before it was renamed. `tests/test_golden.py` names each script by a paraphrase
#     for exactly this reason (see its own module docstring) and is measured normally: it is prose
#     ABOUT the goldens, not the frozen bytes themselves.
#
# Only tracked files are read (`git ls-files`), which is what makes the sweep blind: no path list
# to maintain, and a file added anywhere is covered the day it is committed.
#
# Established by the `modularizar-specs-knowledge-components` spec, task 1.2.
set -uo pipefail

HALF="1,2"
REPO=""
while [ $# -gt 0 ]; do
  case "$1" in
    --half)   HALF="${2:-}"; shift 2 ;;
    --half=*) HALF="${1#*=}"; shift ;;
    -h|--help) sed -n '2,/^set -uo pipefail/p' "${BASH_SOURCE[0]}" | sed '$d'; exit 0 ;;
    *)        REPO="$1"; shift ;;
  esac
done

# checks -> assets -> quenching -> plugins -> the repo root.
REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
SELF="plugins/quenching/assets/checks/citation-check.sh"
cd "$REPO" || { echo "citation-check: cannot enter $REPO"; exit 2; }

# Half 1's own scope, beyond `.specs/`: frozen golden data, not live citations — see the header's
# third scope rule for why.
SCOPE_EXCLUDE=(':!.specs/' ':!plugins/quenching/tests/fixtures/golden/'
               ':!plugins/quenching/tests/capture_golden.py'
               ':(exclude,glob)plugins/quenching/assets/evals/**/runs/**')

want () { case ",$HALF," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }
FAIL=0

echo "citation-check — repo at $REPO"
echo

# --------------------------------------------------------------------------- #
# Half 1 — the old names are dead.
#
# Each pattern is an extended regex. The four script names are matched with their extension so a
# directory called `specs/` or a front called `skill` does not read as a survivor; the namespaces
# are matched in both citation forms — `/docs:<verb>` for a human to type, `quenching:docs:<verb>`
# for the Skill tool — because rewriting one and not the other is the most common way a namespace
# half-survives. `session\.py` alone carries a leading `\b`: unlike the other three, it is also the
# tail of a real, current, correctly-named file — `tests/test_session.py` — and without the
# boundary the retired script and that live test file's name are the same substring.
#
# THE NAMESPACE PATTERNS NAME VERBS, NOT A BARE PREFIX — because this repository ships its own,
# unrelated local command group that happens to share the retired front's name: `/docs:storyteller`
# (`.claude/commands/docs/storyteller.md`) has nothing to do with the plugin's `docs` front and is
# never renamed by this spec. A bare `/docs:` would call that a survivor forever. The ten `docs`
# verbs and six `skill` verbs below are the CLOSED, historical set this rename actually retired
# (`git log --diff-filter=R -- plugins/quenching/commands/` names them exactly); `\b` after each
# stops `import` from also matching `import-memory` short — it already does, because `-` ends a
# word — so the list needs no separate entry for it.
#
# THE `specs` FRONT IS HERE FOR THE OTHER HALF OF THE SAME RULE, AND IT WAS NEVER RENAMED. Its
# front name did not move, but its citation form did: `naming/command-surface.md` §Three citation
# forms says the bare slash is correct ONLY where the command file lives in the target repo's own
# `.claude/commands/`, and it does not live there — so `/specs:develop` names a form that resolves
# nowhere, exactly as `/docs:add` did. Leaving one front bare while the other two were qualified
# is the asymmetry this pattern closes, and without it the bare form regrows silently.
#
# Its verb list is the NINE LIVE commands, and the boundary is `[^a-z-]` rather than `\b` — the one
# place the two differ in consequence. Seven retired verbs (`isolate`, `capture`, `apply`,
# `refine`, `from-claude`, `archive`, `align-and-update`) are still cited by dated measurements and
# by the release history in `README.md`; a retirement has no new name to rewrite to, so minting a
# `quenching:specs:` spelling for one would falsify a record rather than repair a citation. (That
# sentence cannot carry the example spelled out: half 2 reads this file like any other, and a
# three-segment name in a comment is a citation to a body that does not exist.) Those stay bare
# and must not match — and `\b` would have matched `align` inside `/specs:align-and-update`, which
# is harmless when every verb is dead and wrong here, where one is retired and its prefix is live.
# --------------------------------------------------------------------------- #
DEAD_PATTERNS=(
  'specs\.py'
  'skills\.py'
  '\bsession\.py'
  'okf-validate\.py'
  '/docs:(add|align|define|documentation|glossary-backfill|harness|import|learn|status)\b'
  '/skill:(align|new|eval|retro|agent|hook)\b'
  '/specs:(align|conclude|continue|create|develop|execute|orchestrate|status|triage)([^a-z-]|$)'
  '/specs:\*'
  'quenching:docs:(add|align|define|documentation|glossary-backfill|harness|import|learn|status)\b'
  'quenching:skill:(align|new|eval|retro|agent|hook)\b'
)

if want 1; then
  echo "1. the old names are dead"

  # The canary is the plugin's own name: it is in every corner of this repo and the rename does
  # not touch it, so it reads the same before and after. Zero hits means the sweep is blind, not
  # that the repo is clean.
  canary="$(git grep -I -l -E -- 'quenching' -- ":!$SELF" "${SCOPE_EXCLUDE[@]}" 2>/dev/null | wc -l)"
  if [ "$canary" -lt 2 ]; then
    echo "  the sweep sees $canary file(s) — the corpus is empty or git grep failed"
    echo "  nothing could be measured — this is not a pass"
    exit 2
  fi
  printf '  ok     %-22s sweep sees %s files\n' '(canary)' "$canary"

  for pat in "${DEAD_PATTERNS[@]}"; do
    hits="$(git grep -I -c -E -- "$pat" -- ":!$SELF" "${SCOPE_EXCLUDE[@]}" 2>/dev/null | wc -l)"
    occ="$(git grep -I -o -E -- "$pat" -- ":!$SELF" "${SCOPE_EXCLUDE[@]}" 2>/dev/null | wc -l)"
    if [ "$hits" -gt 0 ]; then
      printf '  FAIL   %-22s %s occurrence(s) in %s file(s)\n' "$pat" "$occ" "$hits"
      FAIL=$((FAIL+1))
    else
      printf '  ok     %-22s gone\n' "$pat"
    fi
  done
  echo
fi

# --------------------------------------------------------------------------- #
# Half 2 — the new names were born.
#
# Two assertions, both over tracked text:
#
#   a. every cited PATH resolves to a file that exists;
#   b. every cited /quenching:<ns>:<cmd> corresponds to a body under commands/**.
#
# Candidate extraction is deliberately conservative: a citation carrying a glob, a placeholder or
# an unresolved variable is not a claim about a file that exists, so it is not measured. What IS
# measured is measured with no exceptions.
#
# SOME OF THIS REPO DESCRIBES A DIFFERENT REPO, and a path there is not a claim about a file here.
# The plugin SHIPS content meant to land in a target checkout — the OKF skeleton under
# `assets/knowledge/`, the moulds under `assets/templates/` — so a `/.knowledge/standards/<subject>/<concept>.md` written there
# is a claim about the repo that installs it, not about this checkout. Reading those as citations
# reports the shipped product as broken. So:
#
#   - a path under a shipped tree is not measured against this checkout;
#   - `tests/fixtures/golden/`, `tests/capture_golden.py` and `assets/evals/**/runs/` are not read
#     at all, for both a cited PATH and a cited COMMAND — the same frozen-data reasoning half 1's
#     header gives, applied here because a golden or a grading record legitimately names a path or
#     a namespace that resolved on the day it was captured and is not asked to resolve today.
#
# THERE USED TO BE A THIRD RULE HERE, AND IT WAS EXCUSING A REAL DEFECT. It read: *a path rooted at
# bare `docs/` is not measured at all — that spelling names the target's bundle, and this repo would
# spell its own `.knowledge/`*. The premise is false. `/.knowledge/standards/architecture/bundle-root.md`
# fixes the bundle at `/.knowledge/` **in the target repository**, not only here, so `docs/` names no
# repo's bundle at all. What the rule actually did was silence 95 links and prose paths the 2026-08-06
# root migration left un-migrated inside the shipped trees — a target that scaffolded from them got
# an `index.md` whose every cross-home link resolved nowhere. `cq knowledge validate` never saw it
# either: measured on both bundles, it reports 0 errors, because it does not resolve absolute
# cross-home links. The skeleton and the moulds now spell `/.knowledge/`, and the rule is gone with
# the thing it was hiding.
#
# None of this is an allowlist: no path is exempted by being on a list, and every exclusion is a
# statement about which repository a tree is describing.
#
# EACH TREE IS MEASURED BY THE INSTRUMENT THAT GOVERNS IT. The bundle's own link integrity is
# `knowledge validate`'s — it runs as the `verify:` of every task in the docs sweep — so a bundle
# doc citing the bundle is not measured twice here. But the bundle CITING THE PLUGIN — a `resource:`
# naming a script, a link into `assets/` — has no other instrument, breaks under exactly this
# rename, and is measured with no exception.
# --------------------------------------------------------------------------- #
if want 2; then
  echo "2. the new names were born"
  git ls-files -z -- ':!.specs/' | python3 -c '
import os, re, sys

plugin = "plugins/quenching"
commands_dir = os.path.join(plugin, "commands")

# `${CLAUDE_PLUGIN_ROOT}/<path>`, and the same path spelled absolute in a command body — both name a
# file under the plugin. The absolute form appears because ${CLAUDE_PLUGIN_ROOT} is expanded when
# a body is loaded, and the expansion is what gets copied into prose.
PLUGIN_ROOT_RE    = re.compile(r"\$\{CLAUDE_PLUGIN_ROOT\}/([A-Za-z0-9_./-]+)")
MD_LINK_RE        = re.compile(r"\]\(([^)\s]+)\)")
REPO_PATH_RE      = re.compile(r"(?<![A-Za-z0-9_./-])(plugins/quenching/[A-Za-z0-9_./-]+)")
KNOWLEDGE_PATH_RE = re.compile(r"(?<![A-Za-z0-9_./-])/?(\.knowledge/[A-Za-z0-9_./-]+)")
# Both citation forms. The Skill tool takes the bare `quenching:<ns>:<cmd>`; a human types the slash.
CMD_RE            = re.compile(r"/?(quenching(?::[a-z][a-z0-9-]*){2,})")

# Content the plugin ships for a target checkout to hold, plus the fixture data that names files
# on purpose absent. See the header: these say which repo a tree describes, they exempt no path.
SHIPPED = (plugin + "/assets/knowledge/", plugin + "/assets/templates/", plugin + "/tests/fixtures/")

def unmeasurable(p):
    return (not p) or any(c in p for c in "*?<>${}|") or "..." in p \
        or p.startswith(("http:", "https:", "mailto:", "#"))

# A `describes_target(target)` guard used to sit here, keeping any path that contained `/.knowledge/`
# out of the measurement. `in_bundle` below already carries that rule and carries it the right way
# round — as a statement about the citing FILE, not a substring test on the cited path — so the
# guard is gone. A substring rule over paths is exactly how a spelling nobody had migrated stayed
# invisible for two months.

def trim(p):
    # A path ending a sentence carries the final period, and a path in prose carries the comma
    # after it. Neither is part of the claim. (No apostrophes in this block: the whole script
    # below is a single-quoted shell argument, and one would end it mid-parser.)
    return p.rstrip(".,;:)")

path_findings, cmd_findings = [], []
paths_checked = cmds_checked = 0
commands = set()

for root, _, names in os.walk(commands_dir):
    for n in names:
        if n.endswith(".md"):
            rel = os.path.relpath(os.path.join(root, n), commands_dir)
            commands.add("quenching:" + rel[:-3].replace(os.sep, ":"))

FROZEN_DATA = (plugin + "/tests/fixtures/golden/", plugin + "/tests/capture_golden.py",
               # A `files:` case table reproducing a real, historical bug report verbatim — a
               # disposable probe command, reverted at the end of that repro, whose own comment
               # says so. Not a citation, a fixed
               # historical fact the parser is tested against; the file carries no other path this
               # half would otherwise need to measure.
               plugin + "/tests/test_specs_parse.py")

def is_frozen_eval_run(rel):
    parts = rel.split("/")
    return len(parts) > 2 and rel.startswith(plugin + "/assets/evals/") and "runs" in parts

for rel in sys.stdin.buffer.read().split(b"\x00"):
    rel = rel.decode("utf-8", "replace")
    if not rel or rel.endswith((".png", ".jpg", ".gif", ".ico")):
        continue
    if rel.startswith(FROZEN_DATA) or is_frozen_eval_run(rel):
        continue
    try:
        text = open(rel, encoding="utf-8", errors="replace").read()
    except FileNotFoundError:
        continue

    here = os.path.dirname(rel)
    # Two bundles live in this repo: the real one at .knowledge/, and the skeleton the plugin SHIPS
    # at assets/knowledge/, whose `/.knowledge/` links name the bundle of the repo that installs it
    # and therefore never resolve from here. `knowledge validate` governs both, and the repo gate
    # already runs it over each. Same test, both trees — which is only possible now that they
    # spell the root the same way.
    in_bundle = rel.startswith(".knowledge/") or rel.startswith(SHIPPED)
    in_plugin = rel.startswith(plugin + "/")
    candidates = []
    candidates += [(m, [os.path.join(plugin, trim(m))]) for m in PLUGIN_ROOT_RE.findall(text)]
    candidates += [(m, [trim(m)]) for m in REPO_PATH_RE.findall(text)]
    if not in_bundle:
        candidates += [(m, [trim(m)]) for m in KNOWLEDGE_PATH_RE.findall(text)]
    # A citation is a claim that a file exists, not a claim about which base it is written from:
    # this repo writes links relative to the citing file AND relative to the repo root, and spells
    # the repo root with a leading slash as often as without. Trying every base and failing only
    # when NONE resolves is what keeps the finding list to real breakage — a check that reported
    # the other conventions as broken would be discarded long before the rename finished.
    # Markdown link syntax only means a citation inside markdown. In a .py or a .sh the same
    # `](…)` shape is a regex or a printf, and reading it as a path invents findings.
    if in_plugin and rel.endswith(".md") and not in_bundle:
        for m in MD_LINK_RE.findall(text):
            target = m.split("#", 1)[0]
            if unmeasurable(target):
                continue
            bare = target.lstrip("/")
            candidates.append((m, [os.path.normpath(os.path.join(here, target)), bare]))

    for cited, targets in candidates:
        if unmeasurable(cited):
            continue
        paths_checked += 1
        if not any(os.path.exists(t) for t in targets):
            path_findings.append((rel, cited, targets[-1]))

    for cited in CMD_RE.findall(text):
        cmds_checked += 1
        if cited not in commands:
            cmd_findings.append((rel, cited))

def report(kind, rows, checked, fmt):
    # Every distinct finding prints, up to a cap that exists only so a mid-rename run cannot bury
    # the terminal. A truncated tail says how much it dropped: a silent cap would read as coverage.
    seen, shown = set(), 0
    for row in rows:
        key = row[1:]
        if key in seen:
            continue
        seen.add(key)
        shown += 1
        if shown <= 200:
            print(fmt(row))
    if shown > 200:
        print("         … and %d more" % (shown - 200))
    if seen:
        print("  FAIL   %s: %d distinct, over %d checked" % (kind, len(seen), checked))
    else:
        print("  ok     %s: %d checked, all resolve" % (kind, checked))
    return len(seen)

bad = report("cited paths", path_findings, paths_checked,
             lambda r: "         %s: %s -> %s" % (r[0], r[1], r[2]))
bad += report("cited commands", cmd_findings, cmds_checked,
              lambda r: "         %s: %s has no body under commands/" % (r[0], r[1]))

# A run that extracted no candidates measured nothing. Half 2 passes vacuously over an empty
# corpus, which is the same failure mode the arming proof covers for half 1.
if paths_checked == 0 or cmds_checked == 0:
    print("  nothing could be measured — this is not a pass")
    sys.exit(2)
sys.exit(1 if bad else 0)
'
  case $? in
    0) ;;
    2) echo; echo "  half 2 could not be measured"; exit 2 ;;
    *) FAIL=$((FAIL+1)) ;;
  esac
  echo
fi

if [ "$FAIL" -gt 0 ]; then
  echo "  $FAIL failing assertion(s)"
  exit 1
fi
echo "  both halves clean"
exit 0
