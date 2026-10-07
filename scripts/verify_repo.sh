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

# Coverage is measured around the unit suite when the `coverage` package is importable (the uv dev
# group installs it). Without it the suite still runs, uncovered, and the skip is stated loudly: a
# local gate must not demand an install, but CI always runs with it. `.coverage-floor.json` is the
# floor, enforced by `cq proof ratchet --check`.
COVERAGE_DIR=".quenching/coverage"
COVERAGE_JSON="$COVERAGE_DIR/coverage.json"
if python3 -c "import coverage" >/dev/null 2>&1; then
  mkdir -p "$COVERAGE_DIR"
  export COVERAGE_FILE="$ROOT/$COVERAGE_DIR/.coverage"
  run_check "unit tests (measured)" \
    python3 -m coverage run -m unittest discover -s plugins/quenching/tests
  run_check "coverage report" \
    python3 -m coverage json -q -o "$COVERAGE_JSON"
  run_check "coverage floor" \
    python3 plugins/quenching/assets/bin/cq proof ratchet --check --artifact "$COVERAGE_JSON"
else
  printf '\n==> coverage floor\nSKIPPED: the `coverage` package is not installed (run `uv sync --all-groups`); the floor in .coverage-floor.json was not checked.\n'
  run_check "unit tests" \
    python3 -m unittest discover -s plugins/quenching/tests
fi
run_check "proof doctor" \
  python3 plugins/quenching/assets/bin/cq proof doctor
# The ops front is not adopted here (no `ops.opsRoot`/`ops.router`): `op-config-missing` is expected
# and exits 2, which is inconclusive and reported, never green. Any other outcome must be clean.
printf '\n==> ops doctor\n'
ops_out="$(python3 plugins/quenching/assets/bin/cq ops doctor 2>&1)" && ops_rc=0 || ops_rc=$?
if [ "$ops_rc" -eq 2 ] && [[ "$ops_out" == *"opsRoot"* ]]; then
  printf 'INCONCLUSIVE: ops front not adopted in this repository (op-config-missing is expected).\n'
elif [ "$ops_rc" -ne 0 ]; then
  printf '%s\nFAILED: ops doctor\n' "$ops_out" >&2
  exit 1
else
  printf '%s\n' "$ops_out"
fi
run_check "components doctor" \
  python3 plugins/quenching/assets/bin/cq --root plugins/quenching components doctor --json
run_check "components lint" \
  python3 plugins/quenching/assets/bin/cq --root plugins/quenching components lint --json
run_check "harness (AGENTS.md / CLAUDE.md)" \
  python3 scripts/check_claude_harness.py
run_check "docs bundle" \
  python3 plugins/quenching/assets/bin/cq knowledge validate docs
run_check "Claude/Codex translation" \
  python3 plugins/quenching/assets/bin/cq --root . components translate --check --json
run_check "Codex artifact lockstep" \
  python3 scripts/validate_codex_plugin.py
run_check "specs reader lockstep" \
  python3 scripts/sync_specs_reader_plugin.py --check
run_check "citation checks" \
  bash plugins/quenching/assets/checks/citation-check.sh
run_check "documentation site source" \
  python3 plugins/quenching/assets/bin/cq knowledge site-source docs site-source --write
run_check "Zensical strict build" \
  uv run zensical build --clean --strict
run_check "built-site checks" \
  python3 plugins/quenching/assets/checks/documentation-site-check.py site --local --remote-policy error

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
  printf '+ bash plugins/quenching/assets/checks/functional-checks.sh\n'
  functional_rc=0
  bash plugins/quenching/assets/checks/functional-checks.sh || functional_rc=$?
  if [ "$functional_rc" -ne 0 ]; then
    printf 'FAILED: surface-load checks (exit %s; 2 is inconclusive and does not pass when the measurement was requested)\n' "$functional_rc" >&2
    exit 1
  fi
fi

printf '\nRepository verification passed.\n'
