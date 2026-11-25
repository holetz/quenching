#!/usr/bin/env bash
# verify_repo.sh — the repository's single, deterministic verification gate.
#
# Keep the order here as the contract. Documentation, CI and local contributors all invoke this
# file instead of carrying their own partial copy of the repository checks.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

# A harness that runs the gate exports its own live session selector (OPENCODE_SESSION_ID here).
# A test that resolves a session must never measure the operator's session: the tree decides.
unset OPENCODE_SESSION_ID CLAUDE_CODE_SESSION_ID

# The Copilot client exports its own session selector through its home; a test that resolves a
# session must never measure the operator's store either.
unset COPILOT_HOME QUENCHING_COPILOT_HOME

# Every `python3` below is the project's own environment when one exists: on Windows the PATH's
# `python3` is the Microsoft Store alias, a different interpreter with none of the dev group.
if [ -x "$ROOT/.venv/bin/python" ]; then
  GATE_PYTHON="$ROOT/.venv/bin/python"
elif [ -x "$ROOT/.venv/Scripts/python.exe" ]; then
  GATE_PYTHON="$ROOT/.venv/Scripts/python.exe"
else
  GATE_PYTHON="$(command -v python3 || command -v python || printf python3)"
fi
python3() { "$GATE_PYTHON" "$@"; }
export GATE_PYTHON
export -f python3  # the bash checks this gate starts (citation-check) call `python3` too

# `cq git pr merge` accepts a relaxed-CI merge only on this record: HEAD, the exit this gate ends
# with, its scope and whether the tree was clean. It is cleared now and written by the EXIT trap, so
# a gate that never finishes leaves none, and a caller's claim of a green gate proves nothing.
python3 -m scripts.toolchain.gate_record clear || true
GATE_TMP=""
finish_gate() {
  local rc=$?
  trap - EXIT
  python3 -m scripts.toolchain.gate_record write --exit "$rc" --scope "${TEST_SCOPE:-unknown}" || true
  if [ -n "$GATE_TMP" ]; then rm -rf "$GATE_TMP"; fi
  exit "$rc"
}
trap finish_gate EXIT

run_check() {
  local name="$1"
  shift
  printf '\n==> %s\n' "$name"
  printf '+ '
  printf '%q ' "$@"
  printf '\n'
  if ! "$@"; then
    printf 'FAILED: %s\n' "$name" >&2
    return 1
  fi
}

# The suite runs ONCE per gate. `pytest-randomly` supplies the order evidence the proof contract
# requires, `pytest-xdist` keeps the deploy loop short, and `pytest-cov` combines the worker data
# (`coverage run -m pytest` would measure only the controller once tests move to workers). The JSON
# artifact is the coverage.py schema `cq proof ratchet` already reads. Without the dev group the
# gate falls back to the serial `coverage`/`unittest` path and states the skip loudly: a local gate
# must not demand an install, but CI and `/release` always run the measured, randomized path.
# `PYTEST_RANDOMLY_SEED` pins the order when a run must be reproducible (CI uses the run id);
# `.coverage-floor.json` is the floor, enforced by `cq proof ratchet --check`.
COVERAGE_DIR=".quenching/coverage"
COVERAGE_JSON="$COVERAGE_DIR/coverage.json"
mkdir -p "$COVERAGE_DIR"
# `COVERAGE_FILE` stays here, outside the per-gate temp directory: the EXIT trap removes that
# directory, and it would take the worker data with it before the report is combined.
export COVERAGE_FILE="$ROOT/$COVERAGE_DIR/.coverage"

# One timezone for every tier: a test that renders a date reads the same clock face on a laptop,
# in an agent session and in CI. The locale is left to the host — `C.UTF-8` is not a macOS locale.
export TZ=UTC

# One temp root for the whole run. `scripts.toolchain.tmproot` prefers a RAM-backed candidate and
# falls back to the disk with a NOTICE on stderr; it prints the chosen root on stdout. The
# `quenching-gate-*` directory under it is per run and removed on exit — normal, failed, SIGINT or
# SIGTERM — so a killed gate leaves nothing in RAM. Exporting all three variables is what makes
# every `tempfile` call, every xdist worker and every `git` child share the root with no test
# edited; `QUENCHING_TEST_TMPROOT` marks it as already resolved for `quenching/tests/_paths.py`.
TMPROOT="$(python3 -m scripts.toolchain.tmproot)" || exit 1
GATE_TMP="$(mktemp -d "$TMPROOT/quenching-gate-$$-XXXXXX")"
export TMPDIR="$GATE_TMP" TEMP="$GATE_TMP" TMP="$GATE_TMP"
export QUENCHING_TEST_TMPROOT="$GATE_TMP"
trap 'exit 130' INT
trap 'exit 143' TERM

# `QUENCHING_TEST_WORKERS` bounds the suite's parallelism (`auto` by default). A machine running
# several gates at once sets it lower so the gates share the cores instead of thrashing.
TEST_WORKERS="${QUENCHING_TEST_WORKERS:-auto}"
printf '\ntemp root: %s\nworkers: %s\n' "$GATE_TMP" "$TEST_WORKERS"

# `QUENCHING_TEST_SCOPE` picks how much of the suite this gate runs. `full` is the contract: CI and
# `/release` always run it. `affected` is the close of a spec on a working machine — the tests the
# branch's diff reaches, with the whole suite as the safe answer whenever
# `scripts.toolchain.affected` cannot be sure. A subset cannot prove the coverage floor, so that
# check is skipped here and enforced by the full gate.
TEST_SCOPE="${QUENCHING_TEST_SCOPE:-full}"
# `QUENCHING_FULL_GATE=1` is the release's promise, not a second scope: an exported
# `QUENCHING_TEST_SCOPE=affected` in the shell must not narrow the gate that decides a tag.
if [ -n "${QUENCHING_FULL_GATE:-}" ] && [ "$TEST_SCOPE" != full ]; then
  printf 'scope: QUENCHING_FULL_GATE=1 forces the full suite (QUENCHING_TEST_SCOPE was %s)\n' "$TEST_SCOPE"
  TEST_SCOPE=full
fi
case "$TEST_SCOPE" in
  full|affected) ;;
  *) printf 'FAILED: QUENCHING_TEST_SCOPE must be full or affected, got "%s"\n' "$TEST_SCOPE" >&2; exit 2 ;;
esac
TEST_SCOPE_BASE="${QUENCHING_TEST_BASE:-origin/main}"
TARGETS=(quenching/tests)
WITH_COVERAGE=1
SUITE_SKIP=""
# The site and the plugin steps are fixed cost the diff usually never touches. Only the affected
# scope, with a readable diff, may skip them; every other path (full scope, a selector that failed,
# an unreadable selection) keeps both at 1, so CI and `/release` run them as before.
RUN_SITE=1
RUN_INTEGRATIONS=1
SITE_SKIP_REASON=""
INTEGRATIONS_SKIP_REASON=""
if [ "$TEST_SCOPE" = affected ]; then
  WITH_COVERAGE=0
  SELECTION_JSON="$(python3 -m scripts.toolchain.affected --json --base "$TEST_SCOPE_BASE")" || SELECTION_JSON=""
  if [ -z "$SELECTION_JSON" ]; then
    printf 'scope: affected — the selector failed, so the gate runs the whole suite\n'
  else
    MODE=full
    TARGETS=()
    if CHANGED_LINES="$(printf '%s' "$SELECTION_JSON" | python3 -c '
import json, sys
doc = json.load(sys.stdin)
site = ("docs/", "quenching/skills/", "quenching/references/", "zensical.toml",
        "quenching/assets/zensical/", "quenching/assets/checks/documentation-site-check.py",
        "quenching/assets/bin/quenching/knowledge/", "scripts/verify_repo.sh")
plugins = ("integrations/", "scripts/cache_plugin_sync.py", "scripts/verify_repo.sh")
changed = doc["changed"]
unreadable = doc.get("diffUnreadable", False)
def hit(prefixes):
    return unreadable or any(p == q or p.startswith(q if q.endswith("/") else q + "/") for p in changed for q in prefixes)
print("SITE\t" + ("1" if hit(site) else "0"))
print("PLUGINS\t" + ("1" if hit(plugins) else "0"))
')"; then
      while IFS=$'\t' read -r tag value; do
        case "$tag" in
          SITE) if [ "$value" = 0 ]; then RUN_SITE=0; fi ;;
          PLUGINS) if [ "$value" = 0 ]; then RUN_INTEGRATIONS=0; fi ;;
        esac
      done <<< "$CHANGED_LINES"
    fi
    if SELECTION_LINES="$(printf '%s' "$SELECTION_JSON" | python3 -c '
import json, sys
doc = json.load(sys.stdin)
print("MODE\tfull" if doc["complete"] else ("MODE\tskip" if not doc["tests"] else "MODE\taffected"))
for reason in doc["reasons"]:
    print("REASON\t" + reason)
for test in doc["tests"]:
    print("TARGET\t" + test)
')"; then
      while IFS=$'\t' read -r tag value; do
        case "$tag" in
          MODE) MODE="$value" ;;
          TARGET) TARGETS+=("$value") ;;
          REASON) printf 'scope: %s\n' "$value" ;;
        esac
      done <<< "$SELECTION_LINES"
      case "$MODE" in
        affected)
          if [ "${#TARGETS[@]}" -eq 0 ]; then
            TARGETS=(quenching/tests)
            printf 'scope: affected — the selection parsed no target, running the whole suite\n'
          else
            printf 'scope: affected against %s — %d test file(s)\n' "$TEST_SCOPE_BASE" "${#TARGETS[@]}"
          fi
          ;;
        skip) SUITE_SKIP="the diff reaches no test" ;;
        *) TARGETS=(quenching/tests); printf 'scope: affected — whole suite, see the reason above\n' ;;
      esac
    else
      TARGETS=(quenching/tests)
      printf 'scope: affected — the selection could not be parsed, running the whole suite\n'
    fi
  fi
fi

pytest_args=("${TARGETS[@]}" -q -p randomly -p scripts.toolchain.slots -n "$TEST_WORKERS")
if [ "$WITH_COVERAGE" = 1 ]; then
  # Python >= 3.12 measures through `sys.monitoring` (`COVERAGE_CORE=sysmon`), cheaper than the C
  # tracer older interpreters default to; the totals are identical, so the floor is unchanged. An
  # operator's own `COVERAGE_CORE` wins. Data left by a killed run is dropped so the combine never
  # reads a stale `.coverage.*`.
  if [ -z "${COVERAGE_CORE:-}" ] && uv run python -c "import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)" >/dev/null 2>&1; then
    export COVERAGE_CORE=sysmon
  fi
  rm -f "$COVERAGE_FILE" "$COVERAGE_FILE".*
  pytest_args+=(--cov=quenching/assets/bin/quenching --cov-report="json:$COVERAGE_JSON")
fi
if [ -n "${PYTEST_RANDOMLY_SEED:-}" ]; then
  pytest_args+=("--randomly-seed=$PYTEST_RANDOMLY_SEED")
fi
if [ -n "$SUITE_SKIP" ]; then
  printf '\n==> unit tests\nSKIPPED: %s (QUENCHING_TEST_SCOPE=affected).\n' "$SUITE_SKIP"
  printf '\n==> coverage floor\nSKIPPED: QUENCHING_TEST_SCOPE=affected runs a subset; the full gate checks the floor.\n'
elif [ "$WITH_COVERAGE" = 1 ] && uv run python -c "import pytest, pytest_randomly, xdist, pytest_cov" >/dev/null 2>&1; then
  run_check "unit tests (randomized order, parallel, measured)" \
    uv run python -m pytest "${pytest_args[@]}"
  run_check "coverage floor" \
    python3 quenching/assets/bin/cq proof ratchet --check --artifact "$COVERAGE_JSON"
elif [ "$WITH_COVERAGE" = 0 ] && uv run python -c "import pytest, pytest_randomly, xdist" >/dev/null 2>&1; then
  run_check "unit tests (randomized order, parallel, affected scope)" \
    uv run python -m pytest "${pytest_args[@]}"
  printf '\n==> coverage floor\nSKIPPED: QUENCHING_TEST_SCOPE=affected runs a subset; the full gate (CI and /release) checks the floor.\n'
elif [ "$WITH_COVERAGE" = 1 ] && python3 -c "import coverage" >/dev/null 2>&1; then
  printf '\n==> unit tests\nSKIPPED: pytest-xdist/pytest-cov are not installed (run `uv sync --all-groups`); the suite runs serially under coverage, without the randomized-order evidence.\n'
  run_check "unit tests (measured, serial fallback)" \
    python3 -m coverage run -m unittest discover -s quenching/tests
  run_check "coverage report" \
    python3 -m coverage json -q -o "$COVERAGE_JSON"
  run_check "coverage floor" \
    python3 quenching/assets/bin/cq proof ratchet --check --artifact "$COVERAGE_JSON"
else
  printf '\n==> coverage floor\nSKIPPED: the `coverage` package is not installed (run `uv sync --all-groups`); the floor in .coverage-floor.json was not checked.\n'
  if [ "$WITH_COVERAGE" = 0 ]; then
    printf 'NOTE: pytest-xdist is not installed, so the affected scope is ignored and the whole suite runs serially.\n'
  fi
  run_check "unit tests" \
    python3 -m unittest discover -s quenching/tests
fi
# The CI `lint` job runs this exact command; the local gate must not pass what the CI refuses.
run_check "ruff" \
  uv run ruff check .
# The suite's temp root is one environment decision; a test that pins its own path escapes it
# silently. The guard reads the AST, so it costs milliseconds.
run_check "temp root guard" \
  python3 -m scripts.toolchain.check_tmp
# The leak gate's generic patterns, the same the hooks in scripts/githooks/ run locally (there is no
# private denylist since 2026-10-27).
run_check "leak gate (generic patterns)" \
  python3 quenching/assets/bin/cq security leak --all --generic-only
# A skill or agent body that cites a `cq` verb with no MCP tool fails here, whatever the affected
# scope selected: the body edit that introduces it touches no file this test imports.
run_check "MCP catalog coverage" \
  python3 -m unittest discover -s quenching/tests -p test_quenching_mcp_coverage.py
run_check "open source controls catalog" \
  python3 scripts/check_opensource_controls.py
run_check "proof doctor" \
  python3 quenching/assets/bin/cq proof doctor
# The ops front is not adopted here (no `ops.opsRoot`/`ops.router`): `op-config-missing` is expected
# and exits 2, which is inconclusive and reported, never green. Any other outcome must be clean.
printf '\n==> ops doctor\n'
ops_out="$(python3 quenching/assets/bin/cq ops doctor 2>&1)" && ops_rc=0 || ops_rc=$?
if [ "$ops_rc" -eq 2 ] && [[ "$ops_out" == *"opsRoot"* ]]; then
  printf 'INCONCLUSIVE: ops front not adopted in this repository (op-config-missing is expected).\n'
elif [ "$ops_rc" -ne 0 ]; then
  printf '%s\nFAILED: ops doctor\n' "$ops_out" >&2
  exit 1
else
  printf '%s\n' "$ops_out"
fi
run_check "components doctor" \
  python3 quenching/assets/bin/cq --root quenching components doctor --json
run_check "components lint" \
  python3 quenching/assets/bin/cq --root quenching components lint --json
run_check "harness (AGENTS.md)" \
  python3 scripts/check_claude_harness.py
run_check "docs bundle" \
  python3 quenching/assets/bin/cq knowledge validate docs
run_check "docs doctor" \
  python3 quenching/assets/bin/cq knowledge doctor docs
# A checkout that installed the surface with `cq deploy` keeps it in lockstep with this source;
# `--check` with no flags reuses the manifest's recorded selection. A checkout that never adopted
# deploy mode has nothing to compare, and says so instead of reporting a green it did not measure.
if [ -f .agents/.quenching-deploy.json ]; then
  run_check "deployed surface lockstep" \
    python3 quenching/assets/bin/cq deploy --target . --check --json
else
  printf '\n==> deployed surface lockstep\nSKIPPED: this checkout does not use deploy mode (no .agents/.quenching-deploy.json).\n'
fi
# Pulled out so a step the affected scope skips says so, with the reason, instead of vanishing.
skip_step() {
  printf '\n==> %s\nSKIPPED: %s\n' "$1" "$2"
}
SITE_SKIP_REASON="QUENCHING_TEST_SCOPE=affected and the diff touches no docs/, quenching/skills|references, zensical.toml or site tooling; the full gate (CI and /release) runs it."
INTEGRATIONS_SKIP_REASON="QUENCHING_TEST_SCOPE=affected and the diff touches no integrations/; the full gate (CI and /release) runs it."
# `$BASH` is the shell running this gate: a bare `bash` may be another one (WSL's launcher on Windows).
run_check "citation checks" \
  "$BASH" quenching/assets/checks/citation-check.sh
if [ "$RUN_SITE" = 1 ]; then
  run_check "documentation site source" \
    python3 quenching/assets/bin/cq knowledge site-source docs site-source --write
  run_check "Zensical strict build" \
    uv run zensical build --clean --strict
  run_check "built-site checks" \
    python3 quenching/assets/checks/documentation-site-check.py site --local --remote-policy error
else
  skip_step "documentation site source" "$SITE_SKIP_REASON"
  skip_step "Zensical strict build" "$SITE_SKIP_REASON"
  skip_step "built-site checks" "$SITE_SKIP_REASON"
fi

# The quenching-hud mod is validated by the host's own validator. Without `claude` the skip is
# stated loudly, as with `coverage`: a local gate must not demand an install, but the release has it.
if [ "$RUN_INTEGRATIONS" = 0 ]; then
  skip_step "quenching-hud plugin" "$INTEGRATIONS_SKIP_REASON"
elif command -v claude >/dev/null 2>&1; then
  run_check "quenching-hud plugin" \
    claude plugin validate integrations/claude-hud
else
  printf '\n==> quenching-hud plugin\n'
  printf 'SKIPPED: `claude` is not on PATH; integrations/claude-hud was not validated.\n'
fi

# The quenching-cache bands (Claude Code and OpenCode) carry generated copies of quenching's price
# table and handoff template, and the OpenCode one the shared core too; a stale copy is refused
# here, with or without `claude`.
run_check "quenching-cache generated copies" \
  python3 scripts/cache_plugin_sync.py --check
if [ "$RUN_INTEGRATIONS" = 0 ]; then
  skip_step "quenching-cache plugin and tests" "$INTEGRATIONS_SKIP_REASON"
elif command -v claude >/dev/null 2>&1; then
  run_check "quenching-cache plugin" \
    claude plugin validate integrations/claude-cache
  run_check "quenching-cache tests" \
    claude plugin test integrations/claude-cache
else
  printf '\n==> quenching-cache plugin\n'
  printf 'SKIPPED: `claude` is not on PATH; integrations/claude-cache was not validated or tested.\n'
fi

# The quenching-vitrine mod (the Claude Desktop Specs pane) is validated and tested the same way:
# the engine type-checks its hooks and runs its UI tests on the terminal and the desktop surface.
if [ "$RUN_INTEGRATIONS" = 0 ]; then
  skip_step "quenching-vitrine plugin and tests" "$INTEGRATIONS_SKIP_REASON"
elif command -v claude >/dev/null 2>&1; then
  run_check "quenching-vitrine plugin" \
    claude plugin validate integrations/claude-vitrine
  run_check "quenching-vitrine plugin tests" \
    claude plugin test integrations/claude-vitrine
else
  printf '\n==> quenching-vitrine plugin\n'
  printf 'SKIPPED: `claude` is not on PATH; integrations/claude-vitrine was not validated or tested.\n'
fi

# The OpenCode vitrine is TypeScript against the GUI SDK it pins; a type error there ships a page
# that fails only inside Desktop. Its dependencies are a local `npm install`, so without
# `node_modules` the skip is stated, as with `claude` above.
if [ -d integrations/opencode-vitrine/node_modules ] && command -v npx >/dev/null 2>&1; then
  run_check "opencode-vitrine typecheck" \
    npx --prefix integrations/opencode-vitrine tsc --noEmit -p integrations/opencode-vitrine
else
  printf '\n==> opencode-vitrine typecheck\n'
  printf 'SKIPPED: integrations/opencode-vitrine/node_modules is absent (run `npm ci` there); the vitrine was not typechecked.\n'
fi
# The warnings bench needs only `node` (strip-types), so it still runs when the typecheck above is
# skipped: an undefined name in the plugin's status path fails here instead of only inside OpenCode.
if [ "$RUN_INTEGRATIONS" = 0 ]; then
  skip_step "opencode-vitrine warnings bench" "$INTEGRATIONS_SKIP_REASON"
  skip_step "opencode-vitrine remote deploy bench" "$INTEGRATIONS_SKIP_REASON"
elif command -v node >/dev/null 2>&1 && node --experimental-strip-types -e '' >/dev/null 2>&1; then
  run_check "opencode-vitrine warnings bench" \
    node --experimental-strip-types integrations/opencode-vitrine/bench/warnings.check.mjs
  run_check "opencode-vitrine remote deploy bench" \
    node --experimental-strip-types integrations/opencode-vitrine/bench/remote.check.mjs
else
  skip_step "opencode-vitrine warnings bench" "no \`node\` with --experimental-strip-types (22.6+) on PATH; the vitrine's warnings were not exercised."
  skip_step "opencode-vitrine remote deploy bench" "no \`node\` with --experimental-strip-types (22.6+) on PATH; the vitrine's deploy origin was not exercised."
fi

# The OpenCode quenching-cache port: its tracker, handoff and load checks need only `node`
# (strip-types); the typecheck needs the SDK it pins, so without `node_modules` that skip is stated.
if [ "$RUN_INTEGRATIONS" = 0 ]; then
  skip_step "opencode-cache typecheck, checks and bench" "$INTEGRATIONS_SKIP_REASON"
else
  if [ -d integrations/opencode-cache/node_modules ] && command -v npx >/dev/null 2>&1; then
    run_check "opencode-cache typecheck" \
      npx --prefix integrations/opencode-cache tsc --noEmit -p integrations/opencode-cache
  else
    printf '\n==> opencode-cache typecheck\n'
    printf 'SKIPPED: integrations/opencode-cache/node_modules is absent (run `npm ci` there); the port was not typechecked.\n'
  fi
  if command -v node >/dev/null 2>&1 && node --experimental-strip-types -e '' >/dev/null 2>&1; then
    run_check "opencode-cache tracker and handoff checks" \
      bash -c 'cd integrations/opencode-cache && node --experimental-strip-types tests/track.check.mjs && node --experimental-strip-types tests/handoff.check.mjs'
    if [ -d integrations/opencode-cache/node_modules ]; then
      run_check "opencode-cache load bench" \
        bash -c 'cd integrations/opencode-cache && node --experimental-strip-types bench/load.ts'
    else
      skip_step "opencode-cache load bench" "integrations/opencode-cache/node_modules is absent (run \`npm ci\` there); the bench loads the SDK."
    fi
  else
    skip_step "opencode-cache checks and bench" "no \`node\` with --experimental-strip-types (22.6+) on PATH; the port was not exercised."
  fi
fi

# The OpenCode quota band reads a credential and talks to the network, so its checks also hold the
# security contour (one destination, one process, no write, no log). They need only `node`; the
# typecheck needs the local `npm ci`, and says so when it is absent.
if [ "$RUN_INTEGRATIONS" = 0 ]; then
  skip_step "opencode-quota typecheck" "$INTEGRATIONS_SKIP_REASON"
  skip_step "opencode-quota checks" "$INTEGRATIONS_SKIP_REASON"
else
  if [ -d integrations/opencode-quota/node_modules ] && command -v npx >/dev/null 2>&1; then
    run_check "opencode-quota typecheck" \
      npx --prefix integrations/opencode-quota tsc --noEmit -p integrations/opencode-quota
  else
    skip_step "opencode-quota typecheck" "integrations/opencode-quota/node_modules is absent (run \`npm ci\` there); the quota band was not typechecked."
  fi
  if command -v node >/dev/null 2>&1 && node --experimental-strip-types -e '' >/dev/null 2>&1; then
    run_check "opencode-quota checks" \
      bash -c 'cd integrations/opencode-quota && node --experimental-strip-types tests/usage.check.mjs && node --experimental-strip-types tests/fetch.check.mjs && node tests/surface.check.mjs'
  else
    skip_step "opencode-quota checks" "no \`node\` with --experimental-strip-types (22.6+) on PATH; the quota band was not exercised."
  fi
fi

# Surface-load checks spawn billed `claude -p` sessions, so they are opt-in: without
# QUENCHING_FUNCTIONAL=1 the skip is stated and the gate stays deterministic. When asked for, an
# inconclusive run (exit 2) or a missing `claude` is a measurement that did not happen, so it fails.
printf '\n==> surface-load checks\n'
if [ "${QUENCHING_FUNCTIONAL:-}" != "1" ]; then
  printf 'SKIPPED: set QUENCHING_FUNCTIONAL=1 to measure that the command surface loads (the release runs it).\n'
elif ! command -v claude >/dev/null 2>&1; then
  printf 'FAILED: surface-load checks — QUENCHING_FUNCTIONAL=1 but `claude` is not on PATH.\n' >&2
  exit 1
else
  printf '+ bash quenching/assets/checks/functional-checks.sh\n'
  functional_rc=0
  bash quenching/assets/checks/functional-checks.sh || functional_rc=$?
  if [ "$functional_rc" -ne 0 ]; then
    printf 'FAILED: surface-load checks (exit %s; 2 is inconclusive and does not pass when the measurement was requested)\n' "$functional_rc" >&2
    exit 1
  fi
fi

printf '\nRepository verification passed.\n'
