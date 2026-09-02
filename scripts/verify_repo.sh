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

run_check "unit tests" \
  python3 -m unittest discover -s plugins/quenching/tests
run_check "components doctor" \
  python3 plugins/quenching/assets/bin/cq --root plugins/quenching components doctor --json
run_check "components lint" \
  python3 plugins/quenching/assets/bin/cq --root plugins/quenching components lint --json
run_check "docs bundle" \
  python3 plugins/quenching/assets/bin/cq knowledge validate docs
run_check "Claude/Codex translation" \
  python3 plugins/quenching/assets/bin/cq --root . components translate --check --json
run_check "Codex artifact lockstep" \
  python3 scripts/validate_codex_plugin.py
run_check "citation checks" \
  bash plugins/quenching/assets/checks/citation-check.sh
run_check "documentation site source" \
  python3 plugins/quenching/assets/bin/cq knowledge site-source docs site-source --write
run_check "Zensical strict build" \
  uv run zensical build --clean --strict
run_check "built-site checks" \
  python3 plugins/quenching/assets/checks/documentation-site-check.py site --local --remote-policy error

printf '\nRepository verification passed.\n'
