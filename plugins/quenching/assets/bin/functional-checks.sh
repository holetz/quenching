#!/usr/bin/env bash
# functional-checks.sh — the four checks nothing in-process can make.
#
# The command registry is built at SESSION START, so no change under commands/** is testable
# in the session that writes it. Each check below therefore runs its own fresh `claude -p`.
#
# Every assertion reads the emitted `tool_use` events from `--output-format stream-json`, so it
# asserts on what the process DID (a Read of a given path, a Skill invoked by a given name) and
# never on what its prose claims. A self-report is not a test.
#
#   usage:  ./functional-checks.sh [/path/to/plugin/repo]
#   exit :  0 all passed · 1 a check failed
#
# Established by the `collapse-skills-into-commands` spec, task 7.1.
set -uo pipefail

# bin -> assets -> quenching -> plugins -> the repo root, which is where `docs/` and the
# project's own .claude/settings.json live; the checks below cd into it.
REPO="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0; INCONC=0

emit () { printf '  %-6s %s\n' "$1" "$2"; }
check () { if [ "$1" = "yes" ]; then emit "PASS" "$2"; PASS=$((PASS+1)); else emit "FAIL" "$2"; FAIL=$((FAIL+1)); fi }

# tool_use inputs for a given tool name, one JSON object per line
tools () {
  python3 -c '
import json,sys
want=sys.argv[1]
for line in open(sys.argv[2]):
    try: ev=json.loads(line)
    except Exception: continue
    for c in (ev.get("message",{}).get("content") or []):
        if isinstance(c,dict) and c.get("type")=="tool_use" and c.get("name")==want:
            print(json.dumps(c.get("input",{})))
' "$1" "$2"
}

echo "functional-checks — plugin at $REPO"
echo

# --------------------------------------------------------------------------- #
# 1. a collapsed command loads and ${CLAUDE_PLUGIN_ROOT} substitutes in its body
#
# The prompt never names a path: the command must report the citations IT was given, so a
# Read landing under assets/references/ proves the placeholder resolved in production.
#
# It also covers re-homed references for free: /specs:status cites a reference directory that
# the specs-flow-consolidation fold renamed, so a stale citation fails here rather than silently
# reading nothing.
# --------------------------------------------------------------------------- #
echo "1. a collapsed command loads and cites its re-homed reference"
( cd "$REPO" && claude -p "/quenching:specs:status

Before the report: list the absolute path of every reference file THIS COMMAND'S OWN BODY tells
you to consult, exactly as the body spells them. Then Read the first one. Do not guess a path —
copy it from the body you were given." \
  --max-turns 10 --output-format stream-json --verbose < /dev/null > "$WORK/1.jsonl" 2>&1 )
if grep -q '/assets/references/' <<<"$(tools Read "$WORK/1.jsonl")"; then r=yes; else r=no; fi
check "$r" "Read a file under assets/references/ (placeholder substituted)"
if grep -q '/skills/' <<<"$(tools Read "$WORK/1.jsonl")"; then r=no; else r=yes; fi
check "$r" "read nothing under a skills/ tree"

# --------------------------------------------------------------------------- #
# 2. a conductor reaches its stage BY NAME
#
# The highest-risk path: a wrong name produces a conductor that runs and does nothing. It runs
# against a throwaway repo — /align is invasive — with the plugin still loaded from REPO.
# --------------------------------------------------------------------------- #
echo "2. a conductor invokes its stage by registry name"

# Every sandbox must enable the plugin exactly the way THIS repo does. The marketplace name is
# whatever `claude plugin marketplace add` registered it under — usually the checkout's directory
# name, NOT the `name` inside marketplace.json — so hardcoding it here pins the script to one
# machine and silently reports `Unknown command` as a routing failure. Copy the repo's own keys.
# Built once, up front: check 3's probes need it too and must not depend on check 2 having run.
python3 -c '
import json,sys
try: fm = json.load(open(sys.argv[1])).get("enabledPlugins") or {}
except Exception: fm = {}
json.dump({"enabledPlugins": fm}, open(sys.argv[2], "w"))
sys.exit(0 if fm else 1)
' "$REPO/.claude/settings.json" "$WORK/enabled.json" \
  || { emit "FAIL" "$REPO/.claude/settings.json declares no enabledPlugins — no check can run"; FAIL=$((FAIL+1)); }

# A throwaway git repo with the plugin enabled. Every check that invokes a command gets its own.
newbox () {
  mkdir -p "$1/.claude"
  cp "$WORK/enabled.json" "$1/.claude/settings.json"
  ( cd "$1" && git init -q . && printf '# scratch\n' > README.md && git add -A && git commit -qm init )
}

newbox "$WORK/sandbox"
( cd "$WORK/sandbox" && claude -p "/quenching:align

You have my authorization for the whole run — treat the plan gate as granted and proceed. I only
need you to reach and INVOKE Front 1 via the Skill tool; stop right after that stage is invoked." \
  --max-turns 12 --output-format stream-json --verbose < /dev/null > "$WORK/2.jsonl" 2>&1 )
if grep -q '"quenching:docs:align"' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=yes; else r=no; fi
check "$r" "invoked quenching:docs:align by name"
if grep -qE '"skill": *"[^"]*quenching-docs-align"' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=no; else r=yes; fi
check "$r" "invoked no retired quenching-* skill name"

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
# --------------------------------------------------------------------------- #
echo "3. a spoken trigger routes with no / typed"

# --max-turns is 14, not 4. A probe whose phrase needs any orientation first (a Glob, a Read)
# spends turns before it routes, and a low cap cuts it off mid-orientation — which reports a
# FALSE miss, and a false miss here argues for deleting a trigger that works. Measured while
# building the /skill:agent:new eval: at 3 turns two working triggers reported as misses. 8 was
# then enough in a rich fixture but not in these boxes, where two probes hit the cap while still
# orienting. A probe that still hits the cap is reported INCONCLUSIVE rather than graded, so
# a cap that is one day too low again can never masquerade as a routing failure.
probe () {
  local id="$1" phrase="$2" want="$3"
  local box="$WORK/probe-$id"
  newbox "$box" >/dev/null 2>&1
  # The box must contain whatever the phrases refer to, or the probe grades the FIXTURE.
  # Two ways that bit, both observed here:
  #   - an intent-shaped phrase names a subject ("our migrations"), and where the subject does
  #     not exist the session correctly challenges the premise instead of routing. Probe d
  #     failed in a bare box with "There are no migrations to audit", while the same phrase
  #     routed in the /skill:agent:new eval, whose fixture carried a migration.
  #   - a phrase whose command wants an OKF bundle ("add a standard") spends its turns looking
  #     for one. That cost used to be hidden because probe c ran against REPO, which has a
  #     bundle; sandboxing removed it and pushed the probe into the turn cap.
  # So the box gets a migration and a minimal bundle: the smallest repo all five phrases can
  # be answered in without exploring to find out the subject is missing.
  mkdir -p "$box/db/migrations" "$box/docs/standards"
  printf 'CREATE TABLE accounts (\n  id BIGSERIAL PRIMARY KEY,\n  email TEXT NOT NULL\n);\n' \
    > "$box/db/migrations/0001_create_accounts.sql"
  printf -- '---\nokf_version: "0.1"\n---\n\n# Documentation\n\n- [standards/](standards/index.md)\n' \
    > "$box/docs/index.md"
  printf '# Standards\n' > "$box/docs/standards/index.md"
  ( cd "$box" && git add -A && git commit -qm seed )
  ( cd "$box" && claude -p "$phrase" --max-turns 14 --output-format stream-json --verbose \
      < /dev/null > "$WORK/3$id.jsonl" 2>&1 )
  if grep -q "\"$want\"" <<<"$(tools Skill "$WORK/3$id.jsonl")"; then
    check yes "\"$phrase\" -> $want"
  elif grep -q '"subtype":"error_max_turns"' "$WORK/3$id.jsonl"; then
    emit "SKIP" "\"$phrase\" -> $want (inconclusive: hit the turn cap before routing)"
    INCONC=$((INCONC+1))
  else
    check no "\"$phrase\" -> $want"
  fi
}
probe a "park a spec for later: the export CSV endpoint times out on large accounts" "quenching:specs:create"
probe b "capture this for the backlog — we should look at retry logic on the webhook sender"  "quenching:specs:create"
probe c "add a standard: we always use snake_case for database columns"                       "quenching:docs:add"

# One probe per mint added by the capability layer. Both phrases are intent-shaped — they name
# no artifact and type no `/` — because that is the routing the descriptions have to earn.
# Probe e also guards the trigger the /skill:hook:new eval added: it is the exact phrase that
# measured as a MISS before that edit, so a regression puts it straight back to failing here.
probe d "set up something that audits our migrations and reports back"                        "quenching:skill:agent:new"
probe e "I want something to catch it automatically whenever a migration lands"               "quenching:skill:hook:new"

# --------------------------------------------------------------------------- #
# 4. the conductor's probe asks about the installed tools, from the plugin's copy
#
# The drift check is only worth having if it actually RUNS, and its whole subject —
# `.claude/hooks/` against the plugin that ships it — is invisible to every in-process
# check: `doctor` and `lint` read the surface, not what a session decides to invoke.
#
# The prompt names the STEP (which the body defines) and never the tool, the subcommand
# or the path, so a matching `Bash` call can only have come from the body being loaded.
# The negative half is the rule that makes the answer trustworthy: run from the plugin's
# own copy, because an installed copy answers from the same stale VERSION it is being
# asked about.
# --------------------------------------------------------------------------- #
#
# It loads the plugin with `--plugin-dir "$REPO/plugins/quenching"` instead of through
# the marketplace, and its box enables NO plugin, so exactly one copy is loaded and it is
# the checkout under test. Checks 1-3 above resolve the plugin from the marketplace
# registration, which serves whatever `~/.claude/plugins/cache/` last installed — on this
# machine a 3.0.0 tree carrying commands 4.2.0 deleted. A check that silently grades a
# cached copy reports on code nobody is editing.
# --------------------------------------------------------------------------- #
echo "4. the conductor's probe asks about the installed tools"
newbox "$WORK/sandbox4"
printf '{}\n' > "$WORK/sandbox4/.claude/settings.json"
( cd "$WORK/sandbox4" && claude -p --plugin-dir "$REPO/plugins/quenching" "/quenching:align

Run ONLY step 1, the read-only probe. Report what every call in it returned, then stop —
write nothing and do not present the plan." \
  --max-turns 10 --output-format stream-json --verbose < /dev/null > "$WORK/4.jsonl" 2>&1 )
# `tools` prints each input as JSON, so a quoted path arrives escaped —
# `python3 \"/…/skills.py\" drift`. Match across the escape rather than assuming a bare
# space, or a correct call reads as a miss (it did, on the first run of this check).
if grep -qE 'skills\.py[\\"[:space:]]+drift' <<<"$(tools Bash "$WORK/4.jsonl")"; then r=yes; else r=no; fi
check "$r" "ran skills.py drift during the probe"
if grep -q 'hooks/skills.py' <<<"$(tools Bash "$WORK/4.jsonl")"; then r=no; else r=yes; fi
check "$r" "ran it from the plugin's copy, never from .claude/hooks/"

echo
if [ "$INCONC" -gt 0 ]; then
  echo "  $PASS passed, $FAIL failed, $INCONC inconclusive"
else
  echo "  $PASS passed, $FAIL failed"
fi
[ "$FAIL" -eq 0 ]
