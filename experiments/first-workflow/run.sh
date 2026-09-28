#!/usr/bin/env bash
set -euo pipefail

repo_root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/../.." && pwd)"
experiment_root="$repo_root/experiments/first-workflow"
cq_bin="$repo_root/plugins/quenching/assets/bin/cq"
cq_cmd=(python3 "$cq_bin")

initial_repo_status="$(git -C "$repo_root" status --porcelain)"

target_root="$(mktemp -d "${TMPDIR:-/tmp}/quenching-first-workflow.XXXXXX")"
retain_target=1

cleanup() {
  local exit_code=$?
  if [[ "$retain_target" -eq 0 ]]; then
    rm -rf "$target_root"
  else
    echo "first-workflow: retained failed target at $target_root" >&2
  fi
  return "$exit_code"
}
trap cleanup EXIT

echo "first-workflow: temporary target $target_root"
cp -R "$experiment_root/sample/." "$target_root/"
printf '\n- **Study-only stale term** — exists to make the generated projection stale\n' >> "$target_root/docs/glossary.md"

bundle_snapshot() {
  (cd "$target_root" && find docs -type f -print0 | sort -z | xargs -0 sha256sum)
}

before_status="$(bundle_snapshot)"
"${cq_cmd[@]}" knowledge status --root "$target_root" docs | tee "$target_root/status.out"
after_status="$(bundle_snapshot)"
if [[ "$before_status" != "$after_status" ]]; then
  echo "first-workflow: status changed the temporary bundle" >&2
  exit 1
fi
echo "first-workflow: status is read-only for this fixture"

set +e
"${cq_cmd[@]}" knowledge project --root "$target_root" docs --check | tee "$target_root/project-check-before.out"
project_before_rc=${PIPESTATUS[0]}
set -e
if [[ "$project_before_rc" -ne 1 ]]; then
  echo "first-workflow: expected stale projection check to exit 1, got $project_before_rc" >&2
  exit 1
fi
echo "first-workflow: stale projection detected with exit 1"

"${cq_cmd[@]}" knowledge project --root "$target_root" docs --write | tee "$target_root/project-write.out"
"${cq_cmd[@]}" knowledge project --root "$target_root" docs --check | tee "$target_root/project-check-after.out"
"${cq_cmd[@]}" knowledge validate --root "$target_root" docs | tee "$target_root/validate.out"

if [[ "$(git -C "$repo_root" status --porcelain)" != "$initial_repo_status" ]]; then
  echo "first-workflow: repository changed during the experiment" >&2
  exit 1
fi

retain_target=0
echo "first-workflow: PASS — deterministic check/write/check flow completed"
