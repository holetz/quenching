---
type: standard
title: Codex pillar
description: A pillar that reads the Codex quota and lets the Codex CLI write one eligible spec task inside a worktree — app-server quota first, exit 0/1/2 failing closed, Codex's native sandbox never asked for, the run under the bypass bounded by a git guard that proves its diff inside `files:`, a stop-loss, and argv that never inherits the user's Codex configuration
resource: quenching/assets/bin/quenching/codex/**, quenching/tests/test_codex_probe.py, quenching/tests/test_codex_guard.py, quenching/tests/test_codex_eligible.py, quenching/tests/test_codex_implement.py, quenching/tests/fixtures/codex/**, .agents/quenching.json
tags: [architecture, codex, pillar, git-guard, quota, executor]
timestamp: 2026-11-20
audience: both
authority: current
source: specs 1818, 1879, 1661, 1660, 1817, 1914, 2190, 2199, ADR 0014 — lineage in decision 0004
maintainer: quenching
---

# Codex pillar

<!-- rules -->

`codex` is a pillar of `cq`, not a front: it owns no converged tree. It answers one live question
— may Codex be called now — and runs one bounded action: the code of one eligible spec task
(§The executor). The executor writes only inside the task's `files:`, never runs git, and never
touches the spec's bookkeeping. It grants a tool to no one. There is no Codex review: the cross
review (`cq codex review`, `crossReview`, the per-task review hook) was removed by spec 2199.

**Codex's native sandbox is never asked for.** No argv carries `-s`, `sandbox_mode` or
`codex sandbox`; the run passes `--dangerously-bypass-approvals-and-sandbox`, and its bounds are
the plugin's: `--ignore-user-config`, an environment without forge tokens or cloud credentials, a
prompt rule, and a git guard read before and after (§The git guard).

## The quota probe

`cq codex probe [--json]` exits with the state:

| Exit | State | Means |
| --- | --- | --- |
| `0` | `available` | the quota is under every configured ceiling |
| `1` | `unavailable` | a known fact forbids the call: a window at or over its ceiling, `ordinaryUsageAllowed` false, `rateLimitReachedType` set, or no `codex` on `PATH` |
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

## The git guard

`quenching.codex.guard` reads, before and after each run and without writing anything, the
worktree's `HEAD`, branch, reflog length and the stash ref, and `git status` with untracked files.
The guard is narrowed to the executor's worktree: the `HEAD` of another worktree and the refs of the
shared repository (other branches, tags, `origin/*`) are not read, so the legitimate commit or push
of a parallel worker never stops a run. Two shared things are watched, and only for rewinds: the
`HEAD` of the base checkout (the main worktree of `git worktree list`) and the primary branch ref
(`origin/HEAD`'s target, else the base checkout's branch, else `main`/`master`). A fast-forward
there (the new value descends from the old one, as in a `git pull` or the conductor's merge) is
accepted; a rewind or rewrite (`reset`, `branch -f` to a non-descendant, `update-ref`), a switch of
the base `HEAD`'s branch, a detached base `HEAD` and the removal of the ref are `moved`. A git
command of the base read that fails is `GuardError`, never an empty value, while a detached `HEAD`
and a repository without `refs/stash` are state. The executor also checks that `git status` stays
inside the task's `files:` (§The executor).

## Configuration

The optional `shared.codex` block of `.agents/quenching.json`:

```json
{"maxUsedPercent": {"primary": 80, "secondary": 90}, "timeoutSeconds": 900,
 "executor": {"enabled": false, "modelSmall": "gpt-6.1-sol", "modelVerified": "gpt-6.1-sol",
              "modelSmallTier": "gpt-6-luna", "reasoningEffort": "medium",
              "maxTaskTokens": 20000, "reservePercent": 10, "stopLossPercent": 15}}
```

These are the defaults; an absent block is every default, so **Codex is opt-in**: a repository that
declares nothing never calls it, and `cq config init` seeds the same disabled values.
The executor's switch is `executor.enabled` (`true` opts in), checked by `cq codex eligible`
before the quota, so the probe itself carries no switch. A value of the wrong shape falls back to
its default and is named in the payload's `warnings`; so is a leftover `crossReview` or `model`
of the removed cross review, which is ignored. There is no sandbox key: a leftover
`executor.sandbox` or `executor.windowsSandbox` is ignored.

## The executor

`/quenching-specs execute` step 5b hands one task at a time to Codex when the code admits it.

`cq codex eligible --spec <id> --task <tid> [--json]` decides, exit `0` eligible, `1` not, `2`
refusal (unknown spec or task). A task is eligible when `executor.enabled` holds, it declares
`files:`, none of them under `docs/` or `knowledge/`, and it is `small` (the bytes of its `files:`
over 4 at most `maxTaskTokens`) or `verified` (it carries a `verify:`). The class picks
`modelSmall` or `modelVerified`; a `verified` task whose `verify:` is a protected oracle (tests
outside its `files:`) and whose `cq specs estimate --task` reports `smallTierEligible` runs on
`modelSmallTier` instead ([ADR 0014](../../decisions/0014-tier-pequeno-em-tarefa-testavel.md)). The quota must sit under `maxUsedPercent − reservePercent` in both
windows; an unknown quota is not eligible.

`cq codex implement --spec <id> --task <tid> --worktree <dir> --prompt <file> [--run <name>]`
judges the task again and runs, from `.quenching/codex/<run>/`:

- `codex exec --dangerously-bypass-approvals-and-sandbox`, always, and never `-s`;
- always `--ignore-user-config --ignore-rules -m <model> -c model_reasoning_effort=<effort>
  -C <worktree> --json`, the prompt on stdin, which forbids git and any write outside `files:`;
- an environment without `GH_TOKEN`, `GITHUB_TOKEN` or any `AWS_*`, `AZURE_*`, `GOOGLE_*`.

The **git guard** (§The git guard) is read before and after, with `git status` contained in
`files:`. Any divergence is exit 2
`codex-git-guard` with the offending paths and `discard: <files>`; the caller discards inside
`files:` only — never `reset`, `stash`, `checkout` or `restore` — and writes the task itself. When
`outside` is non-empty (paths `files:` never declared) the caller may not clean them and stops the
task as `needs-human` naming them instead.

Exit 0 is a diff inside `files:`; exit 1 (ineligible, timeout, Codex error) falls back to Claude.
The payload carries `tokens` (from `turn.completed.usage`, or `not measured`), `quotaBefore`,
`quotaAfter`, `quotaDelta` and `stopLoss`: a primary window moved by more than `stopLossPercent`
points keeps the diff and turns the executor off for the rest of the execution. An unmeasured delta
never trips it. Claude keeps the `verify:` (run on every Codex task whatever the declared policy),
the self-review, the commit and the tick.

## Tests

No test reaches the real Codex. Every test of the pillar runs with `PATH` reduced to a fake
`codex` and `CODEX_HOME` pointed at a fixture or a temporary directory.

<!-- rationale -->

## Why the user's configuration is never inherited

A user's `~/.codex/config.toml` can carry `approval_policy = "never"`, plugins and hooks. A Codex
launched by an orchestrated run must not inherit any of that, so `codex exec` always runs with
`--ignore-user-config`. `codex app-server` takes no `--ignore-user-config`; the probe starts no
thread and no turn, so nothing of the user's configuration runs.

## Why Codex's native sandbox is never asked for

Most of the machines this plugin runs on have no admin rights, and the native sandbox needs them:
unprivileged user namespaces for `bwrap` on Linux (`bwrap: loopback: Failed RTM_NEWADDR:
Operation not permitted` under `apparmor_restrict_unprivileged_userns=1`), `codex sandbox setup
--elevated` on Windows. Where it cannot start, every command a sandboxed Codex runs fails and the
review comes back empty — observed on 2026-10-16. The earlier answers (a quota-free sandbox check,
a `prompt-only` review mode, a `workspace-write` opt-in for the executor) kept the sandbox as a
path and kept raising its errors; on 2026-10-18 the human chose to remove every sandbox path.

The bounds are what the plugin controls instead — `-C <worktree>`, a clean environment, a prompt
rule, and a guard that proves by code that nothing moved outside `files:`. The risk that remains
is a command run outside the worktree, or a network call, that git cannot see.

## Why the cross review was removed

The Codex cross review (`cq codex review`, run beside the Claude review in conclude and autopilot
and offered as a per-task hook) was removed at the human's request on 2026-11-20 (spec 2199). With
it went `crossReview`, the review's `model`, and the half of the git guard only the review used
(the whole-tree snapshot of index, flags, bytes and ignored local configuration). The executor
never depended on any of it.

## Why the app-server comes first

The session snapshot on disk exists only after a Codex session ran, and may be weeks old; the
app-server reports the account's current quota. The field names are the ones the installed
codex-cli's own `codex app-server generate-json-schema` emits (`GetAccountRateLimitsResponse`:
`ordinaryUsageAllowed`, `rateLimits.primary/secondary.usedPercent`, `windowDurationMins`,
`resetsAt`, `rateLimitReachedType`). The method is experimental; a rename degrades to the
fallback and then to `unknown`, never to an unguarded call.
