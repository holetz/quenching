---
type: standard
title: Codex pillar
description: A pillar that reads the Codex quota, runs the Codex CLI as an independent reviewer that must change nothing, and lets it write one eligible spec task inside a worktree — app-server quota first, exit 0/1/2 failing closed, Codex's native sandbox never asked for, both runs under the bypass bounded by a git guard (the review's proves the tree unchanged, the executor's proves its diff inside `files:`), a stop-loss, and argv that never inherits the user's Codex configuration
resource: plugins/quenching/assets/bin/quenching/codex/**, plugins/quenching/tests/test_codex_probe.py, plugins/quenching/tests/test_codex_review.py, plugins/quenching/tests/test_codex_eligible.py, plugins/quenching/tests/test_codex_implement.py, plugins/quenching/tests/fixtures/codex/**, .claude/quenching.json
tags: [architecture, codex, pillar, git-guard, quota, review, executor]
timestamp: 2026-10-18
audience: both
authority: current
source: specs 1818, 1879, 1661, 1660 — lineage in decision 0004
maintainer: quenching
---

# Codex pillar

<!-- rules -->

`codex` is a pillar of `cq`, not a front: it owns no converged tree. It answers one live question
— may Codex be called now — and runs two bounded actions: a review of a worktree, and the code of
one eligible spec task (§The executor). The review must change nothing; the executor writes only
inside the task's `files:`, never runs git, and never touches the spec's bookkeeping. Neither
grants a tool to anyone.

**Codex's native sandbox is never asked for.** No argv carries `-s`, `sandbox_mode` or
`codex sandbox`; both runs pass `--dangerously-bypass-approvals-and-sandbox`, and their bounds are
the plugin's: `--ignore-user-config`, an environment without forge tokens or cloud credentials, a
prompt rule, and a git guard read before and after (§The git guard).

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

## The review

`cq codex review --worktree <dir> --prompt <file> [--run <name>] [--json]` runs exactly:

```text
codex exec --dangerously-bypass-approvals-and-sandbox --ignore-user-config --ignore-rules \
  -m <model> -c model_reasoning_effort=high -C <worktree> --json \
  -o .quenching/codex/<run>/review.md - < .quenching/codex/<run>/prompt.md \
  > .quenching/codex/<run>/events.jsonl
```

- The argv is built in one function and asserted literally by the tests. The bypass,
  `--ignore-user-config` and `--ignore-rules` are never optional, and `--ephemeral` is never
  passed (it would erase the quota snapshot the probe falls back on).
- `prompt.md` is the caller's prompt followed by the rule that Codex only reads: no file written,
  created, moved or deleted, no git command that changes anything. It travels on stdin. The run
  lands under `.quenching/codex/<run>/` at the repository root; `<run>` defaults to a UTC stamp,
  and a run name already used is refused.
- The environment loses `GH_TOKEN`, `GITHUB_TOKEN` and every `AWS_*`, `AZURE_*`, `GOOGLE_*`.
- **Exit 0** — Codex finished, wrote the review and the guard saw no change. **Exit 1** — Codex
  exited non-zero, wrote nothing, or ran past `timeoutSeconds` and was killed; the payload carries
  `fallback: true` and the caller falls back to the Claude review, saying so. **Exit 2** —
  refusal: a missing worktree, prompt or `codex`, a worktree outside a git checkout (no guard
  could hold), or a bad or reused run name; or `codex-git-guard` (§The git guard).
- **Tokens only when measured:** the last `total_token_usage` in `events.jsonl`, else the string
  `not measured`.
- The review never calls the probe: whether to run is the caller's decision.
- **Every finding needs reproduction.** The payload carries `findingsNeedReproduction: true`: a
  Codex finding becomes work only once the Claude side reproduces it, with the command and its
  output (decision 3 of epic 1817).

## The git guard

`quenching.codex.guard` reads, before and after each run and without writing anything, the
worktree's `HEAD`, branch, reflog length, the stash ref and every worktree's `HEAD`, and `git
status` with untracked files. The review reads the refs strictly: a git command that fails is
`GuardError`, never an empty value, while a detached `HEAD` and a repository without `refs/stash`
are state.

- **The review** also records every ref (`git for-each-ref`, so a new branch or tag moves it), the
  hash of the index (`git ls-files -s`, so a swapped staged blob moves it), the hash of the index
  flags (`git ls-files -v`, so `assume-unchanged` and `skip-worktree` move it) and, for every path
  `git status` reports and every file those flags hide, its status code and the hash of its bytes
  (a symlink is hashed as its `os.readlink` target plus the bytes it resolves to; every symlink that
  resolves to a file enters this way — tracked, ignored or pointing outside the worktree — while a
  symlink to a directory is not walked, so writes through it stay unseen) — the run's own
  `.quenching/codex/<run>/` excepted. The ignored files that hold local configuration (`.claude/**`
  and `*.local.json`) are recorded too; the other ignored files (caches) are not. A git command of
  the review's snapshot that fails is never an empty tree, and neither is a file-system error
  (an unreadable file, a vanished path): before the run it refuses, after it the guard cannot
  prove anything. Both are exit 2 `codex-git-guard` with no fallback, the refusal before the run
  removes the run's `.quenching/codex/<run>/` folder, and the payload carries the keys
  the CLI prints (`tokens`, `reason`, `runDir`), so the exit 2 is never lost to a missing key. Any moved ref or any path whose
  entry differs is the same exit 2, with `guard.moved` and `changed`. The caller never
  cleans it (no `reset`, `stash`, `checkout` or `restore`): it stops and hands the tree to the
  human, naming the paths.
- **The executor** checks that `git status` stays inside the task's `files:` (§The executor).

## Configuration

The optional `shared.codex` block of `.claude/quenching.json`:

```json
{"crossReview": "auto", "maxUsedPercent": {"primary": 80, "secondary": 90},
 "timeoutSeconds": 900, "model": "gpt-6-astra",
 "executor": {"enabled": true, "modelSmall": "gpt-6.1-sol", "modelVerified": "gpt-6.1-sol",
              "modelSmallTier": "gpt-6-luna", "reasoningEffort": "medium",
              "maxTaskTokens": 20000, "reservePercent": 10, "stopLossPercent": 15}}
```

These are the defaults; an absent block is every default. `crossReview: "off"` is the explicit
opt-out of the review; it never turns off the executor, whose own switch is `executor.enabled`. A value of the wrong shape falls back to its default and is named in the payload's
`warnings`. There is no sandbox key: a leftover `executor.sandbox` or `executor.windowsSandbox` is
ignored.

## The per-task review hook

A repository may ask for a Codex review after each committed spec task by declaring an optional
`after_specs_execute_task` hook ([extension-points.md](../automation/extension-points.md) holds the contract). This
repository does not declare it: switching it on is the human's decision.

```json
{"shared": {"hooks": {"after_specs_execute_task": [{"command": "/<repo>:codex-review", "optional": true}]}}}
```

The command is the declaring repository's own (for example `.claude/commands/codex-review.md`, with
its own `Bash(cq:*)` grant); the plugin ships none, and no `allowed-tools` or `tools:` widens. Its
body runs, in order:

1. `cq codex probe --json`. Exit 0 continues. Exit 1 reports the quota as unavailable and stops:
   the Claude review stands. Exit 2 (`unknown`) tries the review and reports the fallback if it fails.
2. Writes the prompt to a file, naming the diff the execute step hands the hook
   (`review: git -C <toplevel> diff origin/<base>...HEAD`) and asking for an independent review.
3. `cq codex review --worktree <toplevel> --prompt <file> --run <spec>-<task>`.
4. Reports the review path `.quenching/codex/<run>/review.md`, the tokens (or `not measured`)
   and, on exit 1, the `fallback: true` fallback to the Claude review. On exit 2
   `codex-git-guard` it stops the build and names the changed paths for the human.

- **The hook is `optional: true`:** an absent `codex`, a spent quota or a timeout never pauses the build.
- **Worktree limit.** `/quenching-specs:specs:execute` never invokes a hook in a linked worktree
  (it reports `skipped: worktree`), so this review runs only in the main checkout, never in an
  orchestrated build.
- **Findings are reported, never acted on:** `findingsNeedReproduction` holds, so a Codex finding
  becomes work only after the Claude side reproduces it with a command and its output.

## The executor

`/quenching-specs:specs:execute` step 5b hands one task at a time to Codex when the code admits it.

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
rule, and a guard that proves by code what moved: for the review nothing, for the executor nothing
outside `files:`. The risks that remain are a command run outside the worktree, or a network call,
that git cannot see, and a write through a symlink to a directory, which the guard does not walk
(walking it has no bound on cost).

`codex exec review --base` is not used: the plugin's own argv, prompt and guard would not apply.

## Why the app-server comes first

The session snapshot on disk exists only after a Codex session ran, and may be weeks old; the
app-server reports the account's current quota. The field names are the ones the installed
codex-cli's own `codex app-server generate-json-schema` emits (`GetAccountRateLimitsResponse`:
`ordinaryUsageAllowed`, `rateLimits.primary/secondary.usedPercent`, `windowDurationMins`,
`resetsAt`, `rateLimitReachedType`). The method is experimental; a rename degrades to the
fallback and then to `unknown`, never to an unguarded call.
