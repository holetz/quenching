---
type: standard
title: Codex pillar
description: A pillar that reads the Codex quota and runs the Codex CLI as an independent, read-only reviewer — app-server quota first, session snapshot as fallback, exit 0/1/2 failing closed, and a fixed `-s read-only --ignore-user-config` argv that never inherits the user's Codex configuration
resource: plugins/quenching/assets/bin/quenching/codex/**, plugins/quenching/tests/test_codex_*.py, plugins/quenching/tests/fixtures/codex/**, .claude/quenching.json
tags: [architecture, codex, pillar, read-only, quota, review]
timestamp: 2026-10-16
audience: both
authority: current
source: spec 1818 (task 2.1) — the `cq codex` pillar of epic 1817 (D8 A, Codex as independent reviewer by default when quota allows), absorbing the quota probe proved in spec 1660
maintainer: quenching
---

# Codex pillar

<!-- rules -->

`codex` is a pillar of `cq`, not a front: it owns no converged tree. It answers one live question
— may Codex be called now — and runs one bounded action — a read-only review of a worktree. It
never writes code, never edits the repository it reviews, and never grants a tool to anyone.

## The quota probe

`cq codex probe [--json]` exits with the state:

| Exit | State | Means |
| --- | --- | --- |
| `0` | `available` | the quota is under every configured ceiling |
| `1` | `unavailable` | a known fact forbids the call: a window at or over its ceiling, `ordinaryUsageAllowed` false, `rateLimitReachedType` set, `crossReview: "off"`, or no `codex` on `PATH` |
| `2` | `unknown` | no source could be read, the account's usage permission is reported unavailable, no window is reported, or the only snapshot is stale |

- **Primary source:** the `account/rateLimits/read` JSON-RPC method of `codex app-server` over
  stdio (`initialize` → `initialized` → the read), under a deadline of the smaller of 15 seconds
  and `timeoutSeconds`, with the whole process group killed when it passes.
- **Fallback, only when the app-server does not answer:** the last `token_count` event carrying
  `rate_limits` in the newest `$CODEX_HOME/sessions/AAAA/MM/DD/rollout-*.jsonl` (`CODEX_HOME`
  defaults to `~/.codex`). A snapshot in which any reported window's `resets_at` is not in the
  future is stale and reads `unknown`.
- **Fail closed.** Doubt is `unknown`, never `available`. `ordinaryUsageAllowed: null` from the
  app-server is `unknown`, and the percentages are not used to infer past it.
- **Never read `auth.json`.**

## The read-only review

`cq codex review --worktree <dir> --prompt <file> [--run <name>] [--json]` runs exactly:

```text
codex exec -s read-only --ignore-user-config --ignore-rules -m <model> \
  -c model_reasoning_effort=high -C <worktree> --json \
  -o .quenching/codex/<run>/review.md - < <prompt> > .quenching/codex/<run>/events.jsonl
```

- The argv is built in one function and asserted literally by the tests. `-s read-only`,
  `--ignore-user-config` and `--ignore-rules` are never optional, and `--ephemeral` is never
  passed (it would erase the quota snapshot the probe falls back on).
- The prompt travels on stdin. The run lands under `.quenching/codex/<run>/` at the repository
  root; `<run>` defaults to a UTC stamp, and a run name already used is refused.
- **Exit 0** — Codex finished and wrote the review. **Exit 1** — Codex exited non-zero, wrote
  nothing, or ran past `timeoutSeconds` and was killed; the payload carries `fallback: true` and
  the caller falls back to the Claude review, saying so. **Exit 2** — refusal: a missing worktree,
  prompt or `codex`, or a bad or reused run name.
- **Tokens only when measured:** the last `total_token_usage` in `events.jsonl`, else the string
  `not measured`.
- The review never calls the probe: whether to run is the caller's decision.

## Configuration

The optional `shared.codex` block of `.claude/quenching.json`:

```json
{"crossReview": "auto", "maxUsedPercent": {"primary": 80, "secondary": 90},
 "timeoutSeconds": 900, "model": "gpt-6-astra"}
```

These are the defaults; an absent block is every default. `crossReview: "off"` is the explicit
opt-out. A value of the wrong shape falls back to its default and is named in the payload's
`warnings`.

## Tests

No test reaches the real Codex. Every test of the pillar runs with `PATH` reduced to a fake
`codex` and `CODEX_HOME` pointed at a fixture or a temporary directory.

<!-- rationale -->

## Why the user's configuration is never inherited

A user's `~/.codex/config.toml` can carry `sandbox_mode = "danger-full-access"`,
`approval_policy = "never"`, plugins and hooks. A reviewer launched by an orchestrated run must not
inherit any of that, so `codex exec` always runs with `--ignore-user-config` and a read-only
sandbox. `codex app-server` takes no `--ignore-user-config`; the probe starts no thread and no
turn, and still passes `-c sandbox_mode="read-only"` and `-c approval_policy="untrusted"`.

`codex exec review --base` is not used: its help shows no `-s`, so the read-only sandbox could not
be proved.

## Why the app-server comes first

The session snapshot on disk exists only after a Codex session ran, and may be weeks old; the
app-server reports the account's current quota. The field names are the ones the installed
codex-cli's own `codex app-server generate-json-schema` emits (`GetAccountRateLimitsResponse`:
`ordinaryUsageAllowed`, `rateLimits.primary/secondary.usedPercent`, `windowDurationMins`,
`resetsAt`, `rateLimitReachedType`). The method is experimental; a rename degrades to the
fallback and then to `unknown`, never to an unguarded call.
