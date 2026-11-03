#!/usr/bin/env bash
# functional-checks.sh — the checks nothing in-process can make.
#
# The command registry is built at SESSION START, so no change under commands/** is testable
# in the session that writes it. Each check below therefore runs its own fresh `claude -p`.
#
# Every assertion reads the emitted `tool_use` events from `--output-format stream-json`, so it
# asserts on what the process DID (a Read/Bash read of a given path, a Skill invoked by a given name) and
# never on what its prose claims. A self-report is not a test.
#
# EVERY check runs in a throwaway target repository into which THIS checkout's source was installed
# with `cq deploy` — the only way quenching reaches a repository since the plugin model was retired
# (spec 2160). The session reads project settings only and loads no plugin: the surface is the
# box's own `.claude/skills/` bridge and its `.agents/quenching/` payload, so it proves exactly
# what a deploy installs. A read observed under the source tree `quenching`, or under a
# plugin cache or marketplace, is therefore a failure, and a non-builtin plugin in the startup
# inventory fails the isolation. Deploying from the checkout is also what lets this harness see a
# BRANCH or a WORKTREE, and therefore gate a merge before it happens rather than report on it after.
#
#   usage:  ./functional-checks.sh [--only 1,2] [/path/to/quenching/repo]
#   exit :  0 every measured assertion passed
#           1 an assertion failed
#           2 nothing could be measured — no verdict, do not read it as a pass
#
# WHO RUNS THIS, AND WHEN. It belongs to the **components front**: the commands that change the surface
# are the ones that prove it still loads — `/quenching-components-command-new` after minting or editing a command here,
# and `/quenching-components-command-eval` when it tunes a description. It is NOT a repo-wide post-change mandate and it
# does NOT belong in a spec's `## Validation` or a task's `verify:`. Measured 2026-07-29 over the
# whole archive: every red run this harness ever produced traced to a defect in THIS SCRIPT — a
# cp1252 read, a hardcoded marketplace ref, a turn cap, a flaky probe — and not one to a surface
# regression. A check that has only ever caught itself earns a narrow trigger, not a broad one.
#
# Two further triggers, both opt-in by construction. `QUENCHING_FUNCTIONAL=1 bash scripts/verify_repo.sh`
# runs checks 1, 2, 4 and 5 inside the repository gate, and there exit 1 OR 2 fails the gate: whoever
# asked for the measurement does not accept "inconclusive", and a missing `claude` fails too. Without
# the variable the gate prints SKIPPED and stays deterministic. `/release` runs that gated form before
# the bump and blocks on any exit other than 0. CI runs only `--selfcheck` and `--selftest`: it has no
# `claude` CLI, so it measures no surface load.
#
# COST — each check is a full agent session, so scope the run to what the change can break:
#
#   (no flag)        checks 1, 2, 4, 5 — command bodies, citation paths, both declared fronts,
#                    and the core arrangement
#   --mcp-smoke      uvx packaging smoke only; no agent session
#   --only 3         spoken routing — OPT-IN, see below
#   --only 1,2,3,4,5 all five
#
# TWO ARRANGEMENTS. Checks 1-4 deploy every module (`--modules all`); check 5 deploys `--modules
# core`, the smallest install that must still work.
#
# TWO GUARDS, TWO ZERO-COST MODES. The static guard in --selfcheck reads this file:
# every non-commented `claude -p` must carry the project settings filter, no `--plugin-dir` may
# appear outside a comment, no `enabledPlugins` either, and no observed path may be compared with a
# raw grep instead of `anchored`; the anchored guard checks the paths observed in captured
# tool_use events. The --selfcheck mode runs only the source guard, while --selftest
# exercises the observed-path guard against a synthetic capture, and neither starts
# a session.
# The negative halves of the observed-path guard are mandatory: rejecting cache,
# marketplace and source-tree paths remains correct whatever the host canonicalizes, while the
# positive deployed-payload prefix stays diagnostic.
#
# CHECK 3 IS OPT-IN, AND `/quenching-components-command-eval` IS THE BETTER INSTRUMENT. Check 3 is five of the seven
# sessions, the only NON-DETERMINISTIC one (recorded twice: same tree, opposite verdicts on
# identical runs), and a strictly worse duplicate of `/quenching-components-command-eval` step 7 — which measures the
# same thing with should-trigger AND should-not-trigger prompts, graded, per command, instead of
# five hardcoded phrases with no boundary arm. Reach for `/quenching-components-command-eval` when a description changed;
# reach for `--only 3` only to re-guard the five phrases already tuned here.
#
# Established by the `collapse-skills-into-commands` spec, task 7.1; re-based on `cq deploy` by spec 2160.
set -uo pipefail

ONLY="1,2,4,5"
REPO=""
SELF_CHECK=0
SELF_TEST=0
MCP_SMOKE=0
while [ $# -gt 0 ]; do
  case "$1" in
    --only)   ONLY="${2:-}"; shift 2 ;;
    --only=*) ONLY="${1#*=}"; shift ;;
    --selfcheck) SELF_CHECK=1; shift ;;
    --selftest) SELF_TEST=1; shift ;;
    --mcp-smoke) MCP_SMOKE=1; shift ;;
    # the whole header comment, however long it grows — a fixed range silently truncates it
    -h|--help) sed -n '2,/^set -uo pipefail/p' "${BASH_SOURCE[0]}" | sed '$d'; exit 0 ;;
    *)        REPO="$1"; shift ;;
  esac
done

# checks -> assets -> quenching -> the repo root, which is where `docs/` and the
# project's own .claude/settings.json live.
REPO="${REPO:-$(cd "$(dirname "${BASH_SOURCE[0]}")/../../.." && pwd)}"
REPO="$(cd "$REPO" 2>/dev/null && pwd)" || {
  printf 'functional-checks: repository is not a directory: %s\n' "$REPO" >&2
  exit 2
}
SOURCE="$REPO/quenching"
if [ "$MCP_SMOKE" -eq 1 ]; then
  command -v uvx >/dev/null || { echo 'INCONCLUSIVE: uvx is unavailable'; exit 2; }
  python3 - "$REPO" <<'PYSMOKE'
import json
from pathlib import Path
import subprocess
import sys

repo = Path(sys.argv[1])
sys.path.insert(0, str(repo / "quenching/assets/bin"))
from quenching.mcp.cli import surface

requests = "\n".join(json.dumps(request) for request in [
    {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
    {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
]) + "\n"
# Pin HEAD: the package and the in-process catalog must describe the same commit.
revision = subprocess.check_output(["git", "-C", str(repo), "rev-parse", "HEAD"], text=True).strip()
source = f"git+{repo.as_uri()}@{revision}#subdirectory=quenching"
try:
    result = subprocess.run(["uvx", "--from", source, "quenching-mcp"], input=requests,
                            text=True, capture_output=True, cwd=repo, timeout=180)
except subprocess.TimeoutExpired:
    print("INCONCLUSIVE: uvx packaging timed out")
    sys.exit(2)
if result.returncode:
    print(result.stderr, file=sys.stderr)
    network = ("failed to connect", "network is unreachable", "dns error", "error sending request")
    sys.exit(2 if any(token in result.stderr.lower() for token in network) else 1)
try:
    replies = {item["id"]: item for item in map(json.loads, result.stdout.splitlines())}
    assert replies[1]["result"]["serverInfo"]["name"] == "quenching"
    expected = len(surface().list_tools())
    assert len(replies[2]["result"]["tools"]) == expected
except (ValueError, KeyError, AssertionError) as exc:
    print(f"FAIL: packaged MCP response: {exc}: {result.stdout}")
    sys.exit(1)
print(f"PASS: packaged quenching initializes and lists {expected} tools")
PYSMOKE
  exit $?
fi
CQ="$SOURCE/assets/bin/cq"
if [ ! -f "$CQ" ]; then
  printf 'functional-checks: no quenching source at %s\n' "$SOURCE" >&2
  exit 2
fi
# The deployed payload roots the current check accepts reads under; `anchored` checks against it.
LOADED=()
WORK="$(mktemp -d)"
trap 'rm -rf "$WORK"' EXIT
PASS=0; FAIL=0; INCONC=0; MEASURED=0

want () { case ",$ONLY," in *",$1,"*) return 0 ;; *) return 1 ;; esac; }

emit  () { printf '  %-6s %s\n' "$1" "$2"; }
check () { if [ "$1" = "yes" ]; then emit "PASS" "$2"; PASS=$((PASS+1)); else emit "FAIL" "$2"; FAIL=$((FAIL+1)); fi }
inconc () { emit "SKIP" "$1 (inconclusive: $2)"; INCONC=$((INCONC+1)); }

# Static guard for every session invocation in this harness. Commented examples in the
# header are deliberately excluded so the guard measures executable source, not prose.
selfcheck () {
  local src="${BASH_SOURCE[0]}"
  local active invocations forbidden pattern count isolated_count
  pattern="claude -""p"
  active="$(sed '/^[[:space:]]*#/d' "$src")"
  invocations="$(grep -nF "$pattern" <<<"$active" || true)"
  count="$(grep -cF "$pattern" <<<"$active")"
  isolated_count="$(grep -F "$pattern" <<<"$active" | grep -cF -- "--setting-sources project")"

  if [ "$count" -ne "$isolated_count" ]; then
    printf 'FAIL selfcheck: every non-commented %s must restrict settings to project\n' "$pattern"
    printf '%s\n' "$invocations"
    return 1
  fi

  for forbidden_pattern in "--plugin""-dir" "enabled""Plugins"; do
    forbidden="$(grep -nF -- "$forbidden_pattern" <<<"$active" || true)"
    if [ -n "$forbidden" ]; then
      printf 'FAIL selfcheck: %s appears outside a comment\n' "$forbidden_pattern"
      printf '%s\n' "$forbidden"
      return 1
    fi
  done

  # A raw grep for the reference path passes as long as SOME read landed under
  # `assets/references/` — a cache copy included, which is exactly the false-pass measured on
  # 2026-07-28. `anchored` is the only comparison allowed to decide an observed path.
  raw="$(grep -nE "grep[^\n]*assets/""references/" <<<"$active" || true)"
  if [ -n "$raw" ]; then
    printf 'FAIL selfcheck: an observed path is compared with a raw grep, not anchored\n'
    printf '%s\n' "$raw"
    return 1
  fi

  # A routing probe measures the Skill call only; it must not be able to run the routed command's
  # writes (the 2026-10-13 leak of specs 1641-1650 into the real store).
  joined="$(sed -e ':a' -e '/\\$/N; s/\\\n//; ta' <<<"$active")"
  open_probe="$(grep -F "$pattern" <<<"$joined" | grep -F '"$phrase"' | grep -vF -- '--disallowedTools "Bash Write Edit NotebookEdit"' || true)"
  if [ -n "$open_probe" ]; then
    printf 'FAIL selfcheck: a routing probe does not deny the write tools\n'
    printf '%s\n' "$open_probe"
    return 1
  fi

  printf 'PASS selfcheck: %s %s invocation(s) restrict settings to project\n' "$count" "$pattern"
  printf 'PASS selfcheck: no plugin directory flag and no plugin enablement outside comments\n'
  printf 'PASS selfcheck: every routing probe denies write tools\n'
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
# assertion below fails for lack of evidence rather than by verdict. Read it explicitly.
tools () {
  python3 -c '
import json,sys
want=sys.argv[1]
for line in open(sys.argv[2], encoding="utf-8", errors="replace"):
    try: ev=json.loads(line)
    except Exception: continue
    msg=ev.get("message") if isinstance(ev,dict) else None
    for c in ((msg.get("content") if isinstance(msg,dict) else None) or []):
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

# Assert that observed paths came from the deployed payload of the box under test. The forbidden
# half is the verdict: a cache, a marketplace or the source tree is always wrong. The expected
# half accepts the box's absolute payload path, or the relative `.agents/quenching/` a Bash read
# spells from the box's root.
anchored () {
  local observed="$1"
  local forbidden=""
  local result=yes
  local dir inside=no

  forbidden="$(grep -nE '/plugins/(cache|marketplaces)/' <<<"$observed" || true)"
  if [ -n "$forbidden" ]; then
    printf 'FAIL anchor: observed path came from cache or marketplace\n'
    printf '%s\n' "$forbidden"
    result=no
  fi

  forbidden="$(grep -nF "$SOURCE/" <<<"$observed" || true)"
  if [ -n "$forbidden" ]; then
    printf 'FAIL anchor: observed path came from the source tree, not the deployed payload\n'
    printf '%s\n' "$forbidden"
    result=no
  fi

  for dir in "${LOADED[@]}"; do
    if grep -qF "$dir/" <<<"$observed"; then inside=yes; fi
  done
  if grep -qE '(^|[" =])\.agents/quenching/' <<<"$observed"; then inside=yes; fi
  if [ "$inside" = no ]; then
    printf 'FAIL anchor: observed path is outside the deployed payload\n'
    printf '  observed: %s\n' "$observed"
    printf '  expected under: %s/\n' "${LOADED[@]}"
    result=no
  fi

  [ "$result" = yes ]
}

# Exercise every branch of anchored without starting a session: the box's payload passes; a cache
# copy, the source tree, and another box's payload are rejected.
selftest () {
  local fixture="$WORK/selftest.jsonl"
  local result=0
  local -a inputs=()

  LOADED=("$WORK/box-a/.agents/quenching")
  cat > "$fixture" <<EOF
{"message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"$WORK/box-a/.agents/quenching/assets/references/selftest.md"}}]}}
{"message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"/plugins/cache/quenching/3.0.0/assets/references/selftest.md"}}]}}
{"message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"$SOURCE/assets/references/selftest.md"}}]}}
{"message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"$WORK/box-b/.agents/quenching/assets/references/selftest.md"}}]}}
{"message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"cat .agents/quenching/assets/references/selftest.md"}}]}}
EOF
  mapfile -t inputs < <(tools Read "$fixture"; tools Bash "$fixture")

  if [ "${#inputs[@]}" -ne 5 ]; then
    printf 'FAIL selftest: expected five captured inputs, got %s\n' "${#inputs[@]}"
    return 1
  fi

  if anchored "${inputs[0]}" >/dev/null; then
    printf 'PASS selftest: accepted the deployed payload path\n'
  else
    printf 'FAIL selftest: rejected the deployed payload path\n'
    result=1
  fi

  if anchored "${inputs[4]}" >/dev/null; then
    printf 'PASS selftest: accepted a relative read of the deployed payload\n'
  else
    printf 'FAIL selftest: rejected a relative read of the deployed payload\n'
    result=1
  fi

  if anchored "${inputs[1]}" >/dev/null; then
    printf 'FAIL selftest: accepted the cache path\n'
    result=1
  else
    printf 'PASS selftest: rejected the cache path\n'
  fi

  if anchored "${inputs[2]}" >/dev/null; then
    printf 'FAIL selftest: accepted the source tree path\n'
    result=1
  else
    printf 'PASS selftest: rejected the source tree path\n'
  fi

  if anchored "${inputs[3]}" >/dev/null; then
    printf 'FAIL selftest: accepted another box payload\n'
    result=1
  else
    printf 'PASS selftest: rejected another box payload\n'
  fi
  LOADED=()

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
# The startup inventory is independent of the calls we grade: a correct call must not hide a
# loaded plugin, and the deployed skills must be in the registry. Missing inventory is absence of
# evidence, not contamination.
isolated () {
  python3 -c '
import json,sys
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try: ev=json.loads(line)
    except ValueError: continue
    if not isinstance(ev,dict) or ev.get("type")!="system" or ev.get("subtype")!="init": continue
    plugins=ev.get("plugins") or []
    if not isinstance(plugins,list) or any(not isinstance(p,dict) for p in plugins): sys.exit(2)
    foreign=[p for p in plugins if p.get("path")!="builtin"]
    if foreign:
        print("FAIL isolation: unexpected plugins: " + json.dumps(foreign))
        sys.exit(1)
    names=[n for key in ("slash_commands","skills") for n in (ev.get(key) or []) if isinstance(n,str)]
    sys.exit(0 if any(n.startswith("quenching-") for n in names) else 2)
sys.exit(2)
' "$1"
}

evidence () {
  local isolation_rc=0
  isolated "$1" || isolation_rc=$?
  if [ "$isolation_rc" -ne 0 ]; then
    if [ "$isolation_rc" -eq 1 ]; then
      check no "session plugin registry is isolated"
    fi
    return 1
  fi
  [ "$(python3 -c '
import json,sys
n=0
for line in open(sys.argv[1], encoding="utf-8", errors="replace"):
    try: ev=json.loads(line)
    except Exception: continue
    msg=ev.get("message") if isinstance(ev,dict) else None
    for c in ((msg.get("content") if isinstance(msg,dict) else None) or []):
        if isinstance(c,dict) and c.get("type")=="tool_use": n+=1
print(n)
' "$1")" -gt 0 ] || return 1
  MEASURED=$((MEASURED+1))
}

# Every check gets a throwaway git repo that enables NO plugin, and this checkout's source deployed
# into it with `cq deploy --harness claude` — the `.claude/skills/` bridge and the `.agents/quenching/`
# payload are the whole surface. `newbox <dir> [modules]` leaves LOADED on that box's payload.
#
# The box must contain whatever the prompts refer to, or a check grades the FIXTURE.
# Three ways that bit, all observed here:
#   - an intent-shaped phrase names a subject ("our migrations"), and where the subject does
#     not exist the session correctly challenges the premise instead of routing.
#   - a phrase whose command wants an OKF bundle ("add a standard") spends its turns looking
#     for one.
#   - a command that reports on a workspace (`/quenching-knowledge-status`) wants one to report on.
# So every box gets a migration, a minimal bundle and an empty `specs/plans/`: the smallest repo
# every prompt below can be answered in without exploring to find out its subject is missing.
newbox () {
  local modules="${2:-all}"
  mkdir -p "$1/.claude" "$1/db/migrations" "$1/docs/standards" "$1/specs/plans"
  printf '{}\n' > "$1/.claude/settings.json"
  printf 'CREATE TABLE accounts (\n  id BIGSERIAL PRIMARY KEY,\n  email TEXT NOT NULL\n);\n' \
    > "$1/db/migrations/0001_create_accounts.sql"
  printf -- '---\nokf_version: "0.2"\n---\n\n# Documentation\n\n- [standards/](standards/index.md)\n' \
    > "$1/docs/index.md"
  printf '# Standards\n' > "$1/docs/standards/index.md"
  ( cd "$1" && git init -q . && printf '# scratch\n' > README.md && git add -A && git commit -qm init )
  if ! python3 "$CQ" deploy --target "$1" --modules "$modules" --harness claude --write >"$1.deploy.log" 2>&1; then
    printf 'functional-checks: cq deploy failed for %s:\n' "$1" >&2
    cat "$1.deploy.log" >&2
    exit 2
  fi
  LOADED=("$1/.agents/quenching")
}

echo "functional-checks — $SOURCE deployed into throwaway targets"
echo "  checks: $ONLY"
echo

# --------------------------------------------------------------------------- #
# 1. a deployed command loads and cites a reference of its payload
#
# The prompt never names a path: the command must report the citations IT was given, so a
# Read landing under the box's `.agents/quenching/assets/references/` proves the deployed body
# points at the deployed payload. `/quenching-knowledge-status` cites a reference directory the
# knowledge-flow consolidation owns, so a stale citation fails here rather than reading nothing.
# --------------------------------------------------------------------------- #
if want 1; then
echo "1. a deployed command loads and cites its reference"
newbox "$WORK/sandbox1"
( cd "$WORK/sandbox1" && claude -p --setting-sources project "/quenching-knowledge-status

Before the report: list the path of every reference file THIS COMMAND'S OWN BODY tells
you to consult, exactly as the body spells them. Then Read the first one. Do not guess a path —
copy it from the body you were given." \
  --max-turns 10 --output-format stream-json --verbose < /dev/null > "$WORK/1.jsonl" 2>&1 )
if evidence "$WORK/1.jsonl"; then
  if anchored "$(reference_reads "$WORK/1.jsonl")"; then r=yes; else r=no; fi
  check "$r" "read a file under the deployed assets/references/"
  if grep -q '/skills/' <<<"$(reference_reads "$WORK/1.jsonl")"; then r=no; else r=yes; fi
  check "$r" "read nothing under a skills/ tree"
else
  inconc "read a file under the deployed assets/references/" "missing tool activity or verifiable skill inventory"
  inconc "read nothing under a skills/ tree" "missing tool activity or verifiable skill inventory"
fi
fi

# --------------------------------------------------------------------------- #
# 4. both declared front bodies load and cite their own references
#
# One parameterized check with two sessions: adding a front must add both its direct command
# surface and its reference surface to the functional gate.
# --------------------------------------------------------------------------- #
if want 4; then
echo "4. the ops and proof front bodies load and cite their references"
front_probe () {
  local id="$1" command="$2"
  local box="$WORK/front-$id"
  newbox "$box"
  ( cd "$box" && claude -p --setting-sources project "$command

Before the report: list the path of every reference file THIS COMMAND'S OWN BODY tells
you to consult, exactly as the body spells them. Then Read the first one. Do not guess a path —
copy it from the body you were given." \
    --max-turns 10 --output-format stream-json --verbose < /dev/null > "$WORK/front-$id.jsonl" 2>&1 )
  if evidence "$WORK/front-$id.jsonl"; then
    if anchored "$(reference_reads "$WORK/front-$id.jsonl")"; then r=yes; else r=no; fi
    check "$r" "$command loaded from the deployed payload"
    if grep -q '/skills/' <<<"$(reference_reads "$WORK/front-$id.jsonl")"; then r=no; else r=yes; fi
    check "$r" "$command read nothing under a skills/ tree"
  else
    inconc "$command loaded from the deployed payload" "missing tool activity or verifiable skill inventory"
    inconc "$command read nothing under a skills/ tree" "missing tool activity or verifiable skill inventory"
  fi
}
front_probe ops /quenching-ops-status
front_probe proof /quenching-proof-status
fi

# --------------------------------------------------------------------------- #
# 2. a conductor reaches its stage BY NAME
#
# The highest-risk path: a wrong name produces a conductor that runs and does nothing. It runs
# against a throwaway repo — /quenching-align is invasive.
# --------------------------------------------------------------------------- #
# These assertions grade Skill names, not observed paths, so anchored does not apply here.
if want 2; then
echo "2. a conductor invokes its stage by registry name"
newbox "$WORK/sandbox2"
# A conformant box makes /quenching-align report "nothing to align" and stop BEFORE Front 1. Seed
# one real knowledge finding (a concept doc with no frontmatter) so Front 1 has work.
printf '# Orphan\n' > "$WORK/sandbox2/docs/standards/orphan.md"
( cd "$WORK/sandbox2" && claude -p --setting-sources project "/quenching-align

You have my authorization for the whole run — treat the plan gate as granted and proceed. I only
need you to reach and INVOKE Front 1 via the Skill tool; stop right after that stage is invoked." \
  --max-turns 12 --output-format stream-json --verbose < /dev/null > "$WORK/2.jsonl" 2>&1 )
if evidence "$WORK/2.jsonl"; then
  # The conductor reaches Front 1 through the knowledge router with the `align` flow; the leaf
  # skill by its own name is the same stage.
  if python3 -c '
import json,sys
for line in sys.stdin:
    call=json.loads(line)
    skill,args=call.get("skill",""),str(call.get("args","")).lstrip()
    if skill=="quenching-knowledge-align" or (skill=="quenching-knowledge-knowledge" and args.startswith("align")): sys.exit(0)
sys.exit(1)' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=yes
  elif grep -q '"subtype":"error_max_turns"' "$WORK/2.jsonl"; then r=cap
  else r=no; fi
  if [ "$r" = cap ]; then
    inconc "invoked the knowledge align stage by name" "hit the turn cap before routing"
  else
    check "$r" "invoked the knowledge align stage by name"
  fi
  if grep -qE '"skill": *"quenching-[a-z]+:' <<<"$(tools Skill "$WORK/2.jsonl")"; then r=no; else r=yes; fi
  check "$r" "invoked no retired plugin-namespaced skill name"
else
  inconc "invoked the knowledge align stage by name" "missing tool activity or verifiable skill inventory"
  inconc "invoked no retired plugin-namespaced skill name" "missing tool activity or verifiable skill inventory"
fi
fi

# --------------------------------------------------------------------------- #
# 3. a spoken trigger still routes by description alone
#
# Each probe runs in its OWN throwaway repo, never in REPO: these commands write when they fire.
# The probe measures the Skill call, which happens before the routed body acts, so it denies the
# write tools: a probe that routes to /quenching-specs-create must never be able to land a spec.
# A family router (`quenching-<family>-<family>`) that the phrase reaches first counts as routed.
#
# OPT-IN, AND NOT THE FIRST CHOICE: five sessions, non-deterministic, and duplicating what
# `/quenching-components-command-eval` step 7 measures properly. See the COST note at the top.
# --------------------------------------------------------------------------- #
if want 3; then
echo "3. a spoken trigger routes with no / typed"

# The probes never write, but the proof that no spec leaked is cheap and local: the store branch
# tips of the repository under test must be the same after the probes as before them.
store_tips () {
  local ref
  for ref in refs/heads/quenching refs/remotes/origin/quenching refs/quenching/pending/quenching; do
    echo "$ref $(git -C "$REPO" rev-parse -q --verify "$ref" 2>/dev/null || echo absent)"
  done
}
TIPS_BEFORE="$(store_tips)"

# --max-turns is 14: a probe whose phrase needs orientation first spends turns before it routes,
# and a low cap reports a FALSE miss. A probe that still hits the cap is INCONCLUSIVE, never graded.
probe () {
  local id="$1" phrase="$2" want="$3" router="$4"
  local box="$WORK/probe-$id"
  newbox "$box" >/dev/null 2>&1
  ( cd "$box" && claude -p --setting-sources project "$phrase" \
      --disallowedTools "Bash Write Edit NotebookEdit" --max-turns 14 --output-format stream-json --verbose \
      < /dev/null > "$WORK/3$id.jsonl" 2>&1 )
  if ! evidence "$WORK/3$id.jsonl"; then
    inconc "\"$phrase\" -> $want" "missing tool activity or verifiable skill inventory"
  elif grep -qE "\"($want|$router)\"" <<<"$(tools Skill "$WORK/3$id.jsonl")"; then
    check yes "\"$phrase\" -> $want"
  elif grep -q '"subtype":"error_max_turns"' "$WORK/3$id.jsonl"; then
    inconc "\"$phrase\" -> $want" "hit the turn cap before routing"
  else
    check no "\"$phrase\" -> $want"
  fi
}
probe a "park a spec for later: the export CSV endpoint times out on large accounts" "quenching-specs-create" "quenching-specs-specs"
probe b "capture this for the backlog — we should look at retry logic on the webhook sender"  "quenching-specs-create" "quenching-specs-specs"
probe c "add a standard: we always use snake_case for database columns"                       "quenching-knowledge-add" "quenching-knowledge-knowledge"
probe d "set up something that audits our migrations and reports back"                        "quenching-components-agent-new" "quenching-components-components"
probe e "I want something to catch it automatically whenever a migration lands"               "quenching-components-hook-new" "quenching-components-components"
if [ "$(store_tips)" = "$TIPS_BEFORE" ]; then r=yes; else r=no; fi
check "$r" "the routing probes left the spec store branch untouched"
fi

# --------------------------------------------------------------------------- #
# 5. the core arrangement: a spec body loads from the smallest deploy
#
# `cq deploy --modules core` is the smallest install there is. Its specs commands must load and
# read their own payload, and no skill the box does not carry may be invoked.
# --------------------------------------------------------------------------- #
if want 5; then
echo "5. the core arrangement loads a specs body from the smallest deploy"
newbox "$WORK/sandbox5" core
( cd "$WORK/sandbox5" && claude -p --setting-sources project "/quenching-specs-status

Before the report: list the path of every reference file THIS COMMAND'S OWN BODY tells
you to consult, exactly as the body spells them. Then Read the first one. Do not guess a path —
copy it from the body you were given." \
  --max-turns 10 --output-format stream-json --verbose < /dev/null > "$WORK/5.jsonl" 2>&1 )
if evidence "$WORK/5.jsonl"; then
  if anchored "$(reference_reads "$WORK/5.jsonl")"; then r=yes; else r=no; fi
  check "$r" "/quenching-specs-status read only the core payload"
  r=yes
  while IFS= read -r skill; do
    [ -z "$skill" ] && continue
    [ -d "$WORK/sandbox5/.claude/skills/$skill" ] || r=no
  done < <(tools Skill "$WORK/5.jsonl" | python3 -c 'import json,sys
for line in sys.stdin: print(json.loads(line).get("skill",""))')
  check "$r" "invoked no skill the core deploy does not carry"
else
  inconc "/quenching-specs-status read only the core payload" "missing tool activity or verifiable skill inventory"
  inconc "invoked no skill the core deploy does not carry" "missing tool activity or verifiable skill inventory"
fi
fi

echo
if [ "$INCONC" -gt 0 ]; then
  echo "  $PASS passed, $FAIL failed, $INCONC inconclusive"
else
  echo "  $PASS passed, $FAIL failed"
fi

# An inconclusive assertion is NOT a passing one. A run that measured nothing at all exits 2 so
# it can never be quoted as a green gate.
if [ "$FAIL" -gt 0 ]; then exit 1; fi
if [ "$MEASURED" -eq 0 ]; then
  echo "  nothing could be measured — this is not a pass"
  exit 2
fi
exit 0
