---
type: standard
title: Codex pillar
description: A pillar that reads the Codex quota, runs the Codex CLI as an independent read-only reviewer, and lets it write one eligible spec task inside a worktree — app-server quota first, exit 0/1/2 failing closed, a quota-free sandbox check, a prompt-only review where the sandbox fails, an executor that runs with bypass by default or `workspace-write` on opt-in under a git guard and a stop-loss, and argv that never inherits the user's Codex configuration
resource: plugins/quenching/assets/bin/quenching/codex/**, plugins/quenching/tests/test_codex_probe.py, plugins/quenching/tests/test_codex_review.py, plugins/quenching/tests/test_codex_eligible.py, plugins/quenching/tests/test_codex_implement.py, plugins/quenching/tests/fixtures/codex/**, .claude/quenching.json
tags: [architecture, codex, pillar, read-only, quota, review, executor]
timestamp: 2026-10-17
audience: both
authority: current
source: spec 1818 (tasks 2.1, 3.3) — the `cq codex` pillar of epic 1817 (D8 A), absorbing the quota probe of spec 1660; spec 1879 (task 4.1) — the per-task executor of epic 1914 (E1 A, E2 bypass by default)
maintainer: quenching
---

# Codex pillar

<!-- rules -->

`codex` is a pillar of `cq`, not a front: it owns no converged tree. It answers one live question
— may Codex be called now — and runs two bounded actions: a read-only review of a worktree, and
the code of one eligible spec task (§The executor). The review never writes; the executor writes
only inside the task's `files:`, never runs git, and never touches the spec's bookkeeping. Neither
grants a tool to anyone.

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

### The sandbox check

The probe also answers whether Codex can run commands on this host, without spending quota:
`codex sandbox -c sandbox_mode="read-only" -- true`, under the same deadline. When
`shared.codex.executor.sandbox` is not `off`, it runs the same check under
`sandbox_mode="workspace-write"` and reports it as `sandbox.executor: {state: off | available |
unavailable, reason}`. The payload
carries `sandbox: {state: available | unavailable, reason}`, the reason being the last stderr line
— `bwrap: loopback: Failed RTM_NEWADDR: Operation not permitted` on a host with
`apparmor_restrict_unprivileged_userns=1`. `crossReview: "off"` and a missing `codex` report the
sandbox `unavailable` without spawning anything. **The exit stays the quota's**: a broken
sandbox still leaves the prompt-only review.

## The read-only review

`cq codex review --worktree <dir> --prompt <file> [--base <ref> [--head <ref>]] [--run <name>]
[--json]` runs exactly:

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
- The review never calls the probe: whether to run is the caller's decision. It does run the
  sandbox check first, which spends no quota.

### The three modes

The payload's `mode` names how the review ran, and the human line carries `; mode: <mode>`:

| `mode` | When | What Codex sees |
| --- | --- | --- |
| `sandboxed` | the sandbox check passed | the worktree, through read-only commands |
| `prompt-only` | the sandbox failed and `--base` was given | only `.quenching/codex/<run>/prompt.md`: the prompt, the rule not to run commands, `git diff <base>..<head>` (`--head` defaults to `HEAD`) and every touched file at `<head>` |
| `unavailable` | the sandbox failed and no `--base` was given | nothing — Codex is not called; exit 1 with `fallback: true` |

- The review's argv is the same in every mode. A broken sandbox never widens it: no
  `workspace-write`, no `danger-full-access`, no `--dangerously-bypass-approvals-and-sandbox`. The
  bypass belongs to the executor alone (§The executor).
- A diff `cq` cannot read (an unknown `--base`) is a refusal, exit 2 `codex-diff-unreadable`.
- **Every finding needs reproduction.** The payload carries `findingsNeedReproduction: true`: a
  Codex finding becomes work only once the Claude side reproduces it, with the command and its
  output (decision 3 of epic 1817). A `prompt-only` finding was never run by Codex at all.

## Configuration

The optional `shared.codex` block of `.claude/quenching.json`:

```json
{"crossReview": "auto", "maxUsedPercent": {"primary": 80, "secondary": 90},
 "timeoutSeconds": 900, "model": "gpt-6-astra",
 "executor": {"enabled": true, "modelSmall": "gpt-6.1-sol", "modelVerified": "gpt-6.1-sol",
              "reasoningEffort": "medium", "sandbox": "off", "windowsSandbox": "unelevated",
              "maxTaskTokens": 20000, "reservePercent": 10, "stopLossPercent": 15}}
```

These are the defaults; an absent block is every default. `crossReview: "off"` is the explicit
opt-out of the review; it never turns off the executor, whose own switch is `executor.enabled`. A value of the wrong shape falls back to its default and is named in the payload's
`warnings`.

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
3. `cq codex review --worktree <toplevel> --prompt <file> --base origin/<base> --run <spec>-<task>`.
4. Reports the review path `.quenching/codex/<run>/review.md`, the `mode`, the tokens (or
   `not measured`) and, on exit 1, the `fallback: true` fallback to the Claude review.

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
`modelSmall` or `modelVerified`. The quota must sit under `maxUsedPercent − reservePercent` in both
windows; an unknown quota is not eligible.

`cq codex implement --spec <id> --task <tid> --worktree <dir> --prompt <file> [--run <name>]`
judges the task again and runs, from `.quenching/codex/<run>/`:

- `codex exec` with `--dangerously-bypass-approvals-and-sandbox` when `executor.sandbox` is `off`
  (the default), or `-s workspace-write` (plus `-c windows.sandbox="<windowsSandbox>"` on Windows)
  when it opts in — never both. An opt-in whose `workspace-write` check fails is exit 1, never a
  silent bypass.
- always `--ignore-user-config --ignore-rules -m <model> -c model_reasoning_effort=<effort>
  -C <worktree> --json`, the prompt on stdin, which forbids git and any write outside `files:`;
- an environment without `GH_TOKEN`, `GITHUB_TOKEN` or any `AWS_*`, `AZURE_*`, `GOOGLE_*`.

A **git guard** is read before and after: the worktree's `HEAD`, branch, reflog length, the stash
ref, every worktree's `HEAD`, and `git status` contained in `files:`. Any divergence is exit 2
`codex-git-guard` with the offending paths and `discard: <files>`; the caller discards inside
`files:` only — never `reset`, `stash`, `checkout` or `restore` — and writes the task itself.

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

A user's `~/.codex/config.toml` can carry `sandbox_mode = "danger-full-access"`,
`approval_policy = "never"`, plugins and hooks. A reviewer launched by an orchestrated run must not
inherit any of that, so `codex exec` always runs with `--ignore-user-config`, and the review with
a read-only sandbox. `codex app-server` takes no `--ignore-user-config`; the probe starts no thread
and no turn, and still passes `-c sandbox_mode="read-only"`.

## Why the executor runs with bypass by default

Most of the machines this plugin runs on have no admin rights, and the native sandbox needs them:
unprivileged user namespaces for `bwrap` on Linux, `codex sandbox setup --elevated` on Windows.
Defaulting to `workspace-write` would turn the executor off on exactly those hosts (decision E2 of
epic 1914). The bypass is bounded by what the plugin controls instead — `-C <worktree>`, a clean
environment, a prompt that forbids git, and a guard that proves by code nothing outside `files:`
moved. The risk that remains is a command run outside the worktree that git cannot see; a host
that can afford it opts into `workspace-write`.

`codex exec review --base` is not used: its help shows no `-s`, so the read-only sandbox could not
be proved.

## Why prompt-only and not a wider sandbox

Where the sandbox cannot start, every command a `sandboxed` review runs fails and the review comes
back empty — observed on 2026-10-16 on a host with `apparmor_restrict_unprivileged_userns=1`.
Widening the sandbox to make the commands run would give a reviewer write access to the tree it
reviews. Moving the material into the prompt keeps Codex a reader: `cq`, not Codex, runs `git`.

## Why the app-server comes first

The session snapshot on disk exists only after a Codex session ran, and may be weeks old; the
app-server reports the account's current quota. The field names are the ones the installed
codex-cli's own `codex app-server generate-json-schema` emits (`GetAccountRateLimitsResponse`:
`ordinaryUsageAllowed`, `rateLimits.primary/secondary.usedPercent`, `windowDurationMins`,
`resetsAt`, `rateLimitReachedType`). The method is experimental; a rename degrades to the
fallback and then to `unknown`, never to an unguarded call.
