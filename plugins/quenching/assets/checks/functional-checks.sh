#!/usr/bin/env bash
# functional-checks.sh — the three checks nothing in-process can make.
#
# The command registry is built at SESSION START, so no change under commands/** is testable
# in the session that writes it. Each check below therefore runs its own fresh `claude -p`.
#
# Every assertion reads the emitted `tool_use` events from `--output-format stream-json`, so it
# asserts on what the process DID (a Read/Bash read of a given path, a Skill invoked by a given name) and
# never on what its prose claims. A self-report is not a test.
#
# EVERY check loads the plugin with `--plugin-dir`, from a sandbox that enables NO plugin, so
# exactly one copy is loaded and it is the checkout THIS SCRIPT LIVES IN. Resolving through the
# marketplace instead — which checks 1-3 used to do — serves whatever `~/.claude/plugins/cache/`
# last installed: measured 2026-07-28, a 3.0.0 tree still carrying a command 4.2.0 had deleted,
# so the repo's only check for a `commands/**` change was grading a copy nobody had edited.
# It is also what lets this harness see a BRANCH or a WORKTREE, and therefore gate a merge
# before it happens rather than report on it afterwards.
#
#   usage:  ./functional-checks.sh [--only 1,2] [/path/to/plugin/repo]
#   exit :  0 every measured assertion passed
#           1 an assertion failed
#           2 nothing could be measured — no verdict, do not read it as a pass
#
# WHO RUNS THIS, AND WHEN. It belongs to the **components front**: the commands that change the surface
# are the ones that prove it still loads — `/quenching:components:command:new` after minting or editing a command here,
# and `/quenching:components:command:eval` when it tunes a description. It is NOT a repo-wide post-change mandate and it
# does NOT belong in a spec's `## Validation` or a task's `verify:`. Measured 2026-07-29 over the
# whole archive: every red run this harness ever produced traced to a defect in THIS SCRIPT — a
# cp1252 read, a hardcoded marketplace ref, a turn cap, a flaky probe — and not one to a surface
# regression. A check that has only ever caught itself earns a narrow trigger, not a broad one.
#
# COST — each check is a full agent session, so scope the run to what the change can break:
#
#   (no flag)      checks 1, 2 — a command BODY, a citation path
#   --only 3       spoken routing — OPT-IN, see below
#   --only 1,2,3   all three
#
# TWO GUARDS, TWO ZERO-COST MODES. The static guard in --selfcheck reads this file:
# every non-commented `claude -p` must carry --plugin-dir, no `enabledPlugins` may
# appear outside a comment, and no observed path may be compared with a raw grep
# instead of `anchored`; the anchored guard checks the paths observed in captured
# tool_use events. The --selfcheck mode runs only the source guard, while --selftest
# exercises the observed-path guard against a synthetic capture, and neither starts
# a session.
# The negative half of the observed-path guard is mandatory: rejecting cache and
# marketplace paths remains correct even if Claude Code canonicalizes or copies
# the plugin directory, while the positive $PLUGIN prefix stays diagnostic.
#
# CHECK 3 IS OPT-IN, AND `/quenching:components:command:eval` IS THE BETTER INSTRUMENT. Check 3 is five of the seven
# sessions, the only NON-DETERMINISTIC one (recorded twice: same tree, opposite verdicts on
# identical runs), and a strictly worse duplicate of `/quenching:components:command:eval` step 7 — which measures the
# same thing with should-trigger AND should-not-trigger prompts, graded, per command, instead of
# five hardcoded phrases with no boundary arm. Reach for `/quenching:components:command:eval` when a description changed;
# reach for `--only 3` only to re-guard the five phrases already tuned here.
#
# Established by the `collapse-skills-into-commands` spec, task 7.1.
set -uo pipefail

ONLY="1,2"
REPO=""
SELF_CHECK=0
SELF_TEST=0
while [ $# -gt 0 ]; do
  case "$1" in
    --only)   ONLY="${2:-}"; shift 2 ;;
    --only=*) ONLY="${1#*=}"; shift ;;
    --selfcheck) SELF_CHECK=1; shift ;;
    --selftest) SELF_TEST=1; shift ;;
    # the whole header comment, however long it grows — a fixed range silently truncates it
    -h|--help) sed -n '2,/^set -uo pipefail/p' "${BASH_SOURCE[0]}" | sed '$d'; exit 0 ;;
    *)        REPO="$1"; shift ;;
  esac
done

# checks -> assets -> quenching -> plugins -> the repo root, which is where `docs/` and the
# project's own .claude/settings.json live.
REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
PLUGIN="$REPO/plugins/quenching"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0; INCONC=0

want () { case ",$ONLY," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }

emit  () { printf '  %-6s %s\n' "$1" "$2"; }
check () { if [ "$1" = "yes" ]; then emit "PASS" "$2"; PASS=$((PASS+1)); else emit "FAIL" "$2"; FAIL=$((FAIL+1)); fi }
inconc () { emit "SKIP" "$1 (inconclusive: $2)"; INCONC=$((INCONC+1)); }

# Static guard for every session invocation in this harness. Commented examples in the
# header are deliberately excluded so the guard measures executable source, not prose.
selfcheck () {
  local src="${BASH_SOURCE[0]}"
  local active invocations forbidden pattern guarded_pattern count guarded_count
  pattern="claude -""p"
  guarded_pattern="$pattern --plugin-dir"
  active="$(sed '/^[[:space:]]*#/d' "$src")"
  invocations="$(grep -nF "$pattern" <<<"$active" || true)"
  count="$(grep -cF "$pattern" <<<"$active")"
  guarded_count="$(grep -cF "$guarded_pattern" <<<"$active")"

  if [ "$count" -ne "$guarded_count" ]; then
    printf 'FAIL selfcheck: every non-commented %s must use --plugin-dir\n' "$pattern"
    printf '%s\n' "$invocations"
    return 1
  fi

  forbidden_pattern="enabled""Plugins"
  forbidden="$(grep -nF "$forbidden_pattern" <<<"$active" || true)"
  if [ -n "$forbidden" ]; then
    printf 'FAIL selfcheck: %s appears outside a comment\n' "$forbidden_pattern"
    printf '%s\n' "$forbidden"
    return 1
  fi

  # The assertion form task 2.3 replaced. A raw grep for the reference path passes as long as
  # SOME read landed under `assets/references/` — a cache copy included, which is exactly the
  # false-pass measured on 2026-07-28. `anchored` is the only comparison allowed to decide an
  # observed path, so the raw form must never come back. Stated as a pattern rather than as a
  # list of the assertions that exist, for the same reason the count above is not an
  # enumeration: a new check would otherwise be born outside the guard.
  raw="$(grep -nE "grep[^\n]*assets/""references/" <<<"$active" || true)"
  if [ -n "$raw" ]; then
    printf 'FAIL selfcheck: an observed path is compared with a raw grep, not anchored\n'
    printf '%s\n' "$raw"
    return 1
  fi

  printf 'PASS selfcheck: %s %s invocation(s) use --plugin-dir\n' "$count" "$pattern"
  printf 'PASS selfcheck: no %s outside comments\n' "$forbidden_pattern"
  printf 'PASS selfcheck: no observed path compared outside anchored\n'
}

if [ "$SELF_CHECK" -eq 1 ]; then
  selfcheck
  exit $?
fi

# tool_use inputs for a given tool name, one JSON object per line.
#
# The capture is UTF-8. A bare open() decodes it in the PLATFORM default — cp1252 on Windows —
# and raises on the first non-ASCII byte, after which this helper yields nothing and every
# assertion below fails for lack of evidence rather than by verdict. Measured three times on
# 2026-07-28, once flipping a check's verdict across identical runs. Read it explicitly.
tools () {
  python3 -c '
import json,sys
want=sys.argv[1]
for line in open(sys.argv[2], encoding="utf-8", errors="replace"):
    try: ev=json.loads(line)
    except Exception: continue
    for c in (ev.get("message",{}).get("content") or []):
        if isinstance(c,dict) and c.get("type")=="tool_use" and c.get("name")==want:
            print(json.dumps(c.get("input",{})))
' "$1" "$2"
}

# Claude may read a cited reference with the dedicated Read tool or with a scoped Bash `cat`.
# Both are observable reads; the path anchor below is the invariant this check actually needs.
reference_reads () {
  tools Read "$1"
  tools Bash "$1"
}

# Assert that observed paths came from the checkout under test. The forbidden half is the
# verdict: a cache or marketplace path is always wrong. The expected-prefix half is diagnostic
# as well as restrictive, because a canonicalized path needs both values beside the failure.
anchored () {
  local observed="$1"
  local forbidden=""
  local result=yes

  forbidden="$(grep -nE '/plugins/(cache|marketplaces)/' <<<"$observed" || true)"
  if [ -n "$forbidden" ]; then
    printf 'FAIL anchor: observed path came from cache or marketplace\n'
    printf '%s\n' "$forbidden"
    result=no
  fi

  if ! grep -qF "$PLUGIN/" <<<"$observed"; then
    printf 'FAIL anchor: observed path is outside the expected plugin checkout\n'
    printf '  observed: %s\n' "$observed"
    printf '  expected: %s/\n' "$PLUGIN"
    result=no
  fi

  [ "$result" = yes ]
}

# Exercise both halves of anchored without starting a session. The first event is a valid
# checkout path; the second is the stale source this guard must reject.
selftest () {
  local fixture="$WORK/selftest.jsonl"
  local result=0
  local -a inputs=()

  cat > "$fixture" <<EOF
{"message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"$PLUGIN/assets/references/selftest.md"}}]}}
{"message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"/plugins/cache/quenching/3.0.0/assets/references/selftest.md"}}]}}
EOF
  mapfile -t inputs < <(tools Read "$fixture")

  if [ "${#inputs[@]}" -ne 2 ]; then
    printf 'FAIL selftest: expected two captured Read inputs, got %s\n' "${#inputs[@]}"
    return 1
  fi

  if anchored "${inputs[0]}" >/dev/null; then
    printf 'PASS selftest: accepted the checkout path\n'
  else
    printf 'FAIL selftest: rejected the checkout path\n'
    result=1
  fi

  if anchored "${inputs[1]}" >/dev/null; then
    printf 'FAIL selftest: accepted the cache path\n'
    result=1
  else
    printf 'PASS selftest: rejected the cache path\n'
  fi

  return "$result"
}

if [ "$SELF_TEST" -eq 1 ]; then
  selftest
  exit $?
fi

# Did the session act at all? Zero tool_use events of ANY name means the capture carries no
# evidence — the process died, the stream was unreadable, or nothing ran. Every assertion here
# must be gated on this, because the NEGATIVE halves ("read nothing under a skills/ tree") pass
# vacuously over an empty stream: an unreadable capture would report a clean surface.
# No evidence is reported as INCONCLUSIVE. It is never a pass and never a failure.
evidence () {
  [ "$(python3 -c '
import json,sys
n=0
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try: ev=json.loads(line)
    except Exception: continue
    for c in (ev.get("message",{}).get("content") or []):
        if isinstance(c,dict) and c.get("type")=="tool_use": n+=1
print(n)
' "$1")" -gt 0 ]
}

# Every check gets a throwaway git repo that enables NO plugin — the plugin arrives by
# --plugin-dir, so exactly one copy is loaded and it is $PLUGIN.
#
# The box must contain whatever the prompts refer to, or a check grades the FIXTURE.
# Three ways that bit, all observed here:
#   - an intent-shaped phrase names a subject ("our migrations"), and where the subject does
#     not exist the session correctly challenges the premise instead of routing. Probe d
#     failed in a bare box with "There are no migrations to audit", while the same phrase
#     routed in the /quenching:components:agent:new eval, whose fixture carried a migration.
#   - a phrase whose command wants an OKF bundle ("add a standard") spends its turns looking
#     for one. That cost used to be hidden because probe c ran against REPO, which has a
#     bundle; sandboxing removed it and pushed the probe into the turn cap.
#   - a command that reports on a workspace ("/quenching:knowledge:status") wants one to report on.
# So every box gets a migration, a minimal bundle and an empty `specs/plans/`: the smallest repo
# every prompt below can be answered in without exploring to find out its subject is missing.
# The folder alone is the workspace — `plans/index.md` is a retired artifact, and `cq specs`
# derives the listing from disk, so seeding one would only re-create what was withdrawn.
newbox () {
  mkdir -p "$1/.claude" "$1/db/migrations" "$1/docs/standards" "$1/specs/plans"
  printf '{}\n' > "$1/.claude/settings.json"
  printf 'CREATE TABLE accounts (\n  id BIGSERIAL PRIMARY KEY,\n  email TEXT NOT NULL\n);\n' \
    > "$1/db/migrations/0001_create_accounts.sql"
  printf -- '---\nokf_version: "0.1"\n---\n\n# Documentation\n\n- [standards/](standards/index.md)\n' \
    > "$1/docs/index.md"
  printf '# Standards\n' > "$1/docs/standards/index.md"
  ( cd "$1" && git init -q . && printf '# scratch\n' > README.md && git add -A && git commit -qm init )
}

echo "functional-checks — plugin at $PLUGIN"
echo "  checks: $ONLY"
echo

# --------------------------------------------------------------------------- #
# 1. a collapsed command loads and ${CLAUDE_PLUGIN_ROOT} substitutes in its body
#
# The prompt never names a path: the command must report the citations IT was given, so a
# Read landing under assets/references/ proves the placeholder resolved in production.
#
# It also covers re-homed references for free: /quenching:knowledge:status cites a reference directory that
# the knowledge-flow consolidation owns, so a stale citation fails here rather than silently
# reading nothing.
#
# It runs in a sandbox rather than in REPO so that --plugin-dir is the ONLY source of the
# plugin. In REPO the checkout's own enabledPlugins would load a second, marketplace copy.
# --------------------------------------------------------------------------- #
if want 1; then
echo "1. a collapsed command loads and cites its re-homed reference"
newbox "$WORK/sandbox1"
( cd "$WORK/sandbox1" && claude -p --plugin-dir "$PLUGIN" "/quenching:knowledge:status

Before the report: list the absolute path of every reference file THIS COMMAND'S OWN BODY tells
you to consult, exactly as the body spells them. Then Read the first one. Do not guess a path —
copy it from the body you were given." \
  --max-turns 10 --output-format stream-json --verbose < /dev/null > "$WORK/1.jsonl" 2>&1 )
if evidence "$WORK/1.jsonl"; then
  if anchored "$(reference_reads "$WORK/1.jsonl")"; then r=yes; else r=no; fi
  check "$r" "read a file under assets/references/ (placeholder substituted)"
  if grep -q '/skills/' <<<"$(reference_reads "$WORK/1.jsonl")"; then r=no; else r=yes; fi
  check "$r" "read nothing under a skills/ tree"
else
  inconc "Read a file under assets/references/ (placeholder substituted)" "no tool_use in the capture"
  inconc "read nothing under a skills/ tree" "no tool_use in the capture"
fi
fi

# --------------------------------------------------------------------------- #
# 2. a conductor reaches its stage BY NAME
#
# The highest-risk path: a wrong name produces a conductor that runs and does nothing. It runs
# against a throwaway repo — /align is invasive — with the plugin loaded from $PLUGIN.
# --------------------------------------------------------------------------- #
# These assertions grade Skill names, not observed paths; the static --plugin-dir guard is the
# only path guard for this check, so anchored does not apply here.
if want 2; then
echo "2. a conductor invokes its stage by registry name"
newbox "$WORK/sandbox2"
( cd "$WORK/sandbox2" && claude -p --plugin-dir "$PLUGIN" "/quenching:align

You have my authorization for the whole run — treat the plan gate as granted and proceed. I only
need you to reach and INVOKE Front 1 via the Skill tool; stop right after that stage is invoked." \
  --max-turns 12 --output-format stream-json --verbose < /dev/null > "$WORK/2.jsonl" 2>&1 )
if evidence "$WORK/2.jsonl"; then
  if grep -q '"quenching:knowledge:align"' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=yes; else r=no; fi
  check "$r" "invoked quenching:knowledge:align by name"
  if grep -qE '"skill": *"[^"]*quenching-knowledge-align"' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=no; else r=yes; fi
  check "$r" "invoked no retired quenching-* skill name"
else
  inconc "invoked quenching:knowledge:align by name" "no tool_use in the capture"
  inconc "invoked no retired quenching-* skill name" "no tool_use in the capture"
fi
fi

# --------------------------------------------------------------------------- #
# 3. a spoken trigger still routes by description alone
#
# The collapse deleted the descriptions that carried verbatim trigger phrases, so this is the
# check that decides whether the surviving /-menu labels are model-routable at all.
#
# Each probe runs in its OWN throwaway repo, never in REPO. A routing probe succeeds by making
# the command fire, and these commands write when they fire — "park a spec" lands a real file in
# specs/plans/, "add a standard" lands one in docs/. A check that mutates the repository it is
# verifying is not a check, and the mess it leaves is indistinguishable from real work.
#
# OPT-IN, AND NOT THE FIRST CHOICE: five sessions, non-deterministic, and duplicating what
# `/quenching:components:command:eval` step 7 measures properly. See the COST note at the top.
# --------------------------------------------------------------------------- #
# These assertions also grade Skill names rather than observed paths; the static --plugin-dir
# guard remains the only path guard for this check, so anchored does not apply here.
if want 3; then
echo "3. a spoken trigger routes with no / typed"

# --max-turns is 14, not 4. A probe whose phrase needs any orientation first (a Glob, a Read)
# spends turns before it routes, and a low cap cuts it off mid-orientation — which reports a
# FALSE miss, and a false miss here argues for deleting a trigger that works. Measured while
# building the /quenching:components:agent:new eval: at 3 turns two working triggers reported as misses. 8 was
# then enough in a rich fixture but not in these boxes, where two probes hit the cap while still
# orienting. A probe that still hits the cap is reported INCONCLUSIVE rather than graded, so
# a cap that is one day too low again can never masquerade as a routing failure.
probe () {
  local id="$1" phrase="$2" want="$3"
  local box="$WORK/probe-$id"
  newbox "$box" >/dev/null 2>&1
  ( cd "$box" && claude -p --plugin-dir "$PLUGIN" "$phrase" \
      --max-turns 14 --output-format stream-json --verbose \
      < /dev/null > "$WORK/3$id.jsonl" 2>&1 )
  if ! evidence "$WORK/3$id.jsonl"; then
    inconc "\"$phrase\" -> $want" "no tool_use in the capture"
  elif grep -q "\"$want\"" <<<"$(tools Skill "$WORK/3$id.jsonl")"; then
    check yes "\"$phrase\" -> $want"
  elif grep -q '"subtype":"error_max_turns"' "$WORK/3$id.jsonl"; then
    inconc "\"$phrase\" -> $want" "hit the turn cap before routing"
  else
    check no "\"$phrase\" -> $want"
  fi
}
probe a "park a spec for later: the export CSV endpoint times out on large accounts" "quenching:specs:create"
probe b "capture this for the backlog — we should look at retry logic on the webhook sender"  "quenching:specs:create"
probe c "add a standard: we always use snake_case for database columns"                       "quenching:knowledge:add"

# One probe per mint added by the capability layer. Both phrases are intent-shaped — they name
# no artifact and type no `/` — because that is the routing the descriptions have to earn.
# Probe e also guards the trigger the /quenching:components:hook:new eval added: it is the exact phrase that
# measured as a MISS before that edit, so a regression puts it straight back to failing here.
probe d "set up something that audits our migrations and reports back"                        "quenching:components:agent:new"
probe e "I want something to catch it automatically whenever a migration lands"               "quenching:components:hook:new"
fi

echo
if [ "$INCONC" -gt 0 ]; then
  echo "  $PASS passed, $FAIL failed, $INCONC inconclusive"
else
  echo "  $PASS passed, $FAIL failed"
fi

# An inconclusive assertion is NOT a passing one. A run that measured nothing at all exits 2 so
# it can never be quoted as a green gate — the failure mode precondition 4 exists to name.
if [ "$FAIL" -gt 0 ]; then exit 1; fi
if [ "$PASS" -eq 0 ]; then
  echo "  nothing could be measured — this is not a pass"
  exit 2
fi
exit 0
