#!/usr/bin/env bash
# functional-checks.sh — the three checks nothing in-process can make.
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

# bin -> assets -> claude-quenching -> plugins -> the repo root, which is where `docs/` and the
# project's own .claude/settings.json live; the checks below cd into it.
REPO="${1:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../../.." && pwd)}"
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0

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
# --------------------------------------------------------------------------- #
echo "1. a collapsed command loads and cites its re-homed reference"
( cd "$REPO" && claude -p "/claude-quenching:specs:status

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
mkdir -p "$WORK/sandbox/.claude"
( cd "$WORK/sandbox" && git init -q . && printf '# scratch\n' > README.md && git add -A && git commit -qm init )
printf '{ "enabledPlugins": { "claude-quenching@claude-quenching": true } }\n' > "$WORK/sandbox/.claude/settings.json"
( cd "$WORK/sandbox" && claude -p "/claude-quenching:align

You have my authorization for the whole run — treat the plan gate as granted and proceed. I only
need you to reach and INVOKE Front 1 via the Skill tool; stop right after that stage is invoked." \
  --max-turns 12 --output-format stream-json --verbose < /dev/null > "$WORK/2.jsonl" 2>&1 )
if grep -q '"claude-quenching:docs:align"' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=yes; else r=no; fi
check "$r" "invoked claude-quenching:docs:align by name"
if grep -qE '"skill": *"[^"]*quenching-docs-align"' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=no; else r=yes; fi
check "$r" "invoked no retired quenching-* skill name"

# --------------------------------------------------------------------------- #
# 3. a spoken trigger still routes by description alone
#
# The collapse deleted the descriptions that carried verbatim trigger phrases, so this is the
# check that decides whether the surviving /-menu labels are model-routable at all.
# Run against REPO: a phrase whose command needs an OKF bundle correctly declines without one.
# --------------------------------------------------------------------------- #
echo "3. a spoken trigger routes with no / typed"
probe () {
  ( cd "$REPO" && claude -p "$2" --max-turns 4 --output-format stream-json --verbose \
      < /dev/null > "$WORK/3$1.jsonl" 2>&1 )
  if grep -q "\"$3\"" <<<"$(tools Skill "$WORK/3$1.jsonl")"; then r=yes; else r=no; fi
  check "$r" "\"$2\" -> $3"
}
probe a "park a spec for later: the export CSV endpoint times out on large accounts" "claude-quenching:specs:capture"
probe b "capture this for the backlog — we should look at retry logic on the webhook sender"  "claude-quenching:specs:capture"
probe c "add a standard: we always use snake_case for database columns"                       "claude-quenching:docs:add"

echo
echo "  $PASS passed, $FAIL failed"
[ "$FAIL" -eq 0 ]
