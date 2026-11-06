#!/usr/bin/env bash
# verify_repo.sh — the repository's single, deterministic verification gate.
#
# Keep the order here as the contract. Documentation, CI and local contributors all invoke this
# file instead of carrying their own partial copy of the repository checks.
set -Eeuo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT"

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
cleanup_gate_tmp() { rm -rf "$GATE_TMP"; }
trap cleanup_gate_tmp EXIT
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
if [ "$TEST_SCOPE" = affected ]; then
  WITH_COVERAGE=0
  SELECTION_JSON="$(python3 -m scripts.toolchain.affected --json --base "$TEST_SCOPE_BASE")" || SELECTION_JSON=""
  if [ -z "$SELECTION_JSON" ]; then
    printf 'scope: affected — the selector failed, so the gate runs the whole suite\n'
  else
    MODE=full
    TARGETS=()
    while IFS=$'\t' read -r tag value; do
      case "$tag" in
        MODE) MODE="$value" ;;
        TARGET) TARGETS+=("$value") ;;
        REASON) printf 'scope: %s\n' "$value" ;;
      esac
    done < <(printf '%s' "$SELECTION_JSON" | python3 -c '
import json, sys
doc = json.load(sys.stdin)
print("MODE\tfull" if doc["complete"] else ("MODE\tskip" if not doc["tests"] else "MODE\taffected"))
for reason in doc["reasons"]:
    print("REASON\t" + reason)
for test in doc["tests"]:
    print("TARGET\t" + test)
')
    case "$MODE" in
      affected)
        if [ "${#TARGETS[@]}" -eq 0 ]; then
          TARGETS=(quenching/tests)
          printf 'scope: affected — the selection parser returned no target, running the whole suite\n'
        else
          printf 'scope: affected against %s — %d test file(s)\n' "$TEST_SCOPE_BASE" "${#TARGETS[@]}"
        fi
        ;;
      skip) SUITE_SKIP="the diff reaches no test" ;;
      *) TARGETS=(quenching/tests); printf 'scope: affected — whole suite, see the reason above\n' ;;
    esac
  fi
fi

pytest_args=("${TARGETS[@]}" -q -p randomly -p scripts.toolchain.slots -n "$TEST_WORKERS")
if [ "$WITH_COVERAGE" = 1 ]; then
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
run_check "citation checks" \
  bash quenching/assets/checks/citation-check.sh
run_check "documentation site source" \
  python3 quenching/assets/bin/cq knowledge site-source docs site-source --write
run_check "Zensical strict build" \
  uv run zensical build --clean --strict
run_check "built-site checks" \
  python3 quenching/assets/checks/documentation-site-check.py site --local --remote-policy error

# The quenching-hud mod is validated by the host's own validator. Without `claude` the skip is
# stated loudly, as with `coverage`: a local gate must not demand an install, but the release has it.
if command -v claude >/dev/null 2>&1; then
  run_check "quenching-hud plugin" \
    claude plugin validate integrations/claude-hud
else
  printf '\n==> quenching-hud plugin\n'
  printf 'SKIPPED: `claude` is not on PATH; integrations/claude-hud was not validated.\n'
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
