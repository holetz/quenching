#!/usr/bin/env bash
# Generated Codex adapter: source stream-json checks require the source host.
# No Claude subprocess is permitted during a Codex run.
set -uo pipefail
case "${1:-}" in
  --selfcheck)
    printf '%s\n' 'PASS: generated Codex adapter launches no external model runtime'
    exit 0 ;;
  -h|--help)
    printf '%s\n' 'Codex surface-load measurement unavailable; exit 2 is inconclusive.'
    exit 0 ;;
esac
printf '%s\n' 'INCONCLUSIVE: no Codex surface-load capture harness is implemented; no model was launched.' >&2
exit 2
