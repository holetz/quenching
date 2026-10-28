---
name: quenching-git-commit
description: "Commit what is already staged under the repo's commit convention. Use for \"commit this\", \"make a commit\", \"wrap this up in a commit\". Not for: staging, merging or pushing → quenching-git-merge."
---

<!-- GENERATED FROM plugins/quenching/commands/git/commit.md -->

<!-- CODEX RUNTIME START -->
## Codex runtime

Use Codex host sub-agents only. Never launch Claude CLI, request Claude models, or fall back to Claude during a Codex run. The Claude source may separately delegate development to Codex. Read each named agent protocol and pass its role, prohibitions, model and effort to the host's spawn-agent tool; protocol files are not automatically registered agent types. Use host messaging, completion notifications and interrupt tools for lifecycle management. If delegation is unavailable, report the limitation; do not silently replace required independent verification with self-review.

Tier mapping: opus → `gpt-6-astra`; sonnet → `gpt-6.1-sol`; haiku → `gpt-6-luna`. Preserve declared effort. Pass model explicitly; when the host requires a fresh context for model overrides, use that mode and include the necessary brief and protocol. Use gpt-6-luna for product code only on ONE task whose `cq specs estimate --task` reports `oracleProtected` and `smallTierEligible` (an executable `verify:` whose tests sit outside the task's `files:`, nothing under `/docs/`, projected context at or under 80k); a failed `verify:` returns it to the session model. Never use gpt-6-luna for judgment roles or for import-memory classification/executor roles. Report tokens per model and role only when host telemetry provides them; otherwise `not measured`. Claude session logs and `cq components session cost` do not measure this Codex run.

<!-- CODEX RUNTIME END -->


# quenching-git-commit — commit what is staged, under the target's own convention

This command is the single commit boundary for standalone commits. `quenching-specs-execute` does
not delegate here per task: it commits each task through `cq git commit --subject`. This command
resolves the subject, commits the existing index and reports the subject actually written. It never receives a request to stage an unrelated path.

**Input**: `$ARGUMENTS` — an optional explicit commit subject. When omitted, resolve one from the
current spec/task context; never invent it from the diff and never ask for confirmation.

Commits **only what is already in the index** — never `git add -A` on the human's behalf, and
never a guess at which files belong together.

## Workflow

### 1. Read-if-present, and the staged diff
```bash
cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
cq components read ../../references/git/conventions.md \
  --sections "§The declared-directive layer" --sections "§The read-if-present rule"
cq git conventions --json
cq git state --json   # `staged` is the index, `branch` the current branch
```
One `cq git conventions` call answers both declared layers: `config.commitSubject` is the target's
directive for this artifact, `governs`/`declared` the docs layer. Nothing staged → refuse: name that
the index is empty and say what to stage. **Done when:** which layer governs the subject
(`gitConventions.commitSubject`, the target's docs, or the plugin default below) and the staged file
list are both known.

### 2. Resolve the subject
§The declared-directive layer's table governs, for this one artifact: `config.commitSubject` from
step 1 wins where it is declared; else a target doc naming a subject format wins outright, and a doc
covering only part of it governs that part. With neither declared:
```bash
cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
cq components read ../../references/git/commit.md --sections "§Commit messages"
```
`$ARGUMENTS` given → use it verbatim, wrapped rather than truncated past 72 characters where the
title allows; an explicit subject always wins. When it is omitted, resolve the current branch and
its `quenching-specs:` mark:
```bash
cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
cq git specs <current-branch> --json   # <current-branch>: `branch` from step 1's `cq git state`
cq specs next --spec <spec-id> --json
```
If that produces exactly one spec and one actionable task, derive the subject with the governing
convention from the spec id, task id and task title. If the execution caller already supplies a
unique spec/task pair, use that pair as the equivalent context. More than one candidate, no
candidate, or no actionable task is **ambiguous or missing context**: refuse, name the unresolved
fact, and tell the caller to supply an explicit subject or spec/task pair. Do not choose by
recency, branch order or staged-diff content. **Done when:** the exact subject string is fixed or
the refusal is reported.

### 3. Commit
```bash
cq() {
  local plugin_root="${CODEX_PLUGIN_ROOT:-${PLUGIN_ROOT:-}}"
  if [ -z "$plugin_root" ]; then
    plugin_root="$(set -o pipefail
codex plugin list --json | python3 -c '
import json, os, sys
from pathlib import Path
plugins = [p for p in json.load(sys.stdin)["installed"] if p.get("name") == "quenching-codex" and p.get("enabled")]
if len(plugins) != 1:
    sys.exit("quenching-codex: enable exactly one installation, or provide its plugin root")
p = plugins[0]
home = Path(os.environ.get("CODEX_HOME", str(Path.home() / ".codex")))
print(p.get("installedPath") or home / "plugins/cache" / p["marketplaceName"] / p["name"] / p["version"])
')" || return 2
  fi
  if [ -z "$plugin_root" ] || [ ! -f "$plugin_root/scripts/cq" ]; then
    echo "quenching-codex: installed plugin root not found; enable the plugin first" >&2
    return 2
  fi
  python3 "$plugin_root/scripts/cq" "$@"
}
cq git commit --subject "<subject>" --json
```
The verb reports the `sha`, the `subject` git recorded and `subjectMatches`; exit 1 is git refusing
the commit (a hook, an identity) with HEAD unchanged, exit 2 a blank subject or an empty index.
Execute immediately after the staged-diff and hygiene checks; a resolvable omitted subject does
not add a confirmation question. The command commits the existing index only — it never stages
files, amends history, or bypasses hooks.
The `commit-msg` hook only *adds* (a ticket prefix, a sign-off) still matches by substring and needs
nothing; one that **replaces** the subject outright is a mismatch, reported as a finding rather than silently accepted. **Done when:**
the commit exists and its logged subject either matches or the mismatch is reported.

### 4. Report
State the sha, the subject, the committed files, and **which layer governed the subject** —
`gitConventions.commitSubject`, the target's docs, or the plugin default. **Done when:** all four
are named.

## Invariants

- **Never `git add -A`, or any equivalent of it.** Staging is the caller's decision; this command
  commits the index exactly as it finds it.
- **Never `--no-verify` or `--no-gpg-sign`.** A rejecting hook is a finding to report, not an
  obstacle to route around.
- **Never amend or rewrite an existing commit, and never force-push.**
- **Never install `docs/standards/git/**` into the target, and never write `gitConventions` into
  its `.claude/quenching.json`.** A convention read here is followed, never written back.
