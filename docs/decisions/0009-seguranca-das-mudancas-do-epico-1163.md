---
type: decision
title: Security review of the epic 1163 changes
description: The read-only security verdict, per merged PR, for the sensitive changes of epic 1163 that merged without a per-task security review
resource: docs/decisions/index.md
tags: [decision, security, review]
timestamp: 2026-10-07
audience: both
authority: current
source: spec 1180
maintainer: quenching
---

# Security review of the epic 1163 changes

Decision [0008](0008-seguranca-das-mudancas-do-epico-1145.md) covered #1159, #1160, #1161 and
#1162. The `## Outcome` of specs 1166, 1168 and 1170 never mention the `after_specs_execute_task`
hook, so the later merges of epic 1163 are reviewed here, read from each merge diff against its first
parent. Nothing was changed: what this review found outside its scope is a spec discovery.

| PR | Surface | Verdict |
| --- | --- | --- |
| #1172 | `.claude/quenching.json`, `.agents/quenching.json`, `execute.md`, `spec-runner.md` | Accepted |
| #1175 | `spec-runner.md`, `verifier.md` | Accepted, one finding |
| #1173 | `backends/github.py`, `promote.py`, `create.md` | Accepted |
| #1177 | `backends/github.py`, `backends/azure.py` | Accepted |
| #1174 | `functional-checks.sh` | Accepted |
| #1181 | `knowledge/checks.py`, `schema.py`, `structure.py`, `docs/` | Accepted |
| #1182 | `scripts/verify_repo.sh` | Accepted |
| #1183 | `verifier.md` | Accepted |
| #1184 | `.claude/commands/release.md` | Accepted |

## #1172 — the hook configuration and the runner report

The hook command is now `/security-review`, still `optional`, with a free-text `condition`. The
executor never evaluates the condition: it passes it to the hook as context, so no new decision
logic runs in a script. No command, grant or permission was added; the new `HOOKS:` line only
reports `ran`, `failed` or `unresolved`. Accepted.

## #1175 — what a worker may not run, and how it is detected

The Forbidden list is prose, so the control is detective, not preventive: verifier check 7 reads
ancestry and the reflog. Its stated limit stands (discarding files by path leaves no reflog entry).
The grants added to the verifier (`git reflog show`, `git merge-base`, `git rev-list`) are read-only.
Accepted.

- **Finding:** the verifier, documented as read-only, keeps the older `Bash(git branch:*)`, which
  also admits `git branch -D` and `-m`. Not fixed here; parked as a discovery of spec 1180.

## #1173 — retry of writes in the GitHub backend

Only reads and the whole-value writes (`gh api -X PATCH|PUT|DELETE`, `gh issue edit`) are repeated.
A POST, which could create a second issue or comment after a timeout, is attempted once, and a
failure after the issue was created names its number so no blind `new` follows. `promote` names an
outcome already written. Accepted.

## #1177 — guards on truncated listings

Both guards only refuse with exit 2 when the listing is shorter than the proven count.
`github_cache_forget` removes a file whose name is a sha256 of the normalized remote under the user's
cache directory; no remote text reaches the path. Accepted.

## #1174 — the functional check 2

The check seeds one orphan doc in its own sandbox under `$WORK` and adds an inconclusive branch for the
turn cap. No permission, network or credential change. Accepted.

## #1181 — frontmatter and link checks

`frontmatter-not-yaml` and `doc-broken-link` read the bundle's own files and emit findings; nothing
extracted is executed or written. The `docs/` edits are quoting and link repairs. Accepted.

## #1182 — ruff in the local gate

Adds `uv run ruff check .`, a read-only lint equal to the CI `lint` job, so the local gate no longer
passes what the CI refuses. Accepted.

## #1183 — the verifier and the worktree creation reset

Exactly one `reset: moving to HEAD` before the first commit is accepted as the worktree creation;
any other `reset`, a later `reset: moving to HEAD` included, stays FAIL. The check was relaxed by
one named line, not by a pattern. Accepted.

## #1184 — the permission of `/release`

`Bash(bash:*)` and `Bash(QUENCHING_FUNCTIONAL=1 bash:*)` became the single command
`Bash(QUENCHING_FUNCTIONAL=1 bash scripts/verify_repo.sh:*)`, which closes the finding decision 0008
parked on #1162. `Bash(git:*)` and `Bash(python3:*)` stay wide and predate the epic. Accepted.
