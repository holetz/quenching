---
type: decision
title: Security review of the epic 1192 and 1197 changes
description: The read-only security verdict, per merged PR, for the sensitive changes of epics 1192 and 1197 that merged without an effective per-task security review
resource: docs/decisions/index.md
tags: [decision, security, review]
timestamp: 2026-10-08
audience: both
authority: current
source: spec 1232
maintainer: quenching
---

# Security review of the epic 1192 and 1197 changes

Epics 1192 and 1197 merged 25 PRs (#1193 to #1230) through `--autonomous` orchestration with no human
in the loop. The declared `/security-review` hook reviewed the base checkout, with an empty diff,
in 5 of 8 builds of epic 1192. These verdicts continue decisions
[0008](0008-seguranca-das-mudancas-do-epico-1145.md) and
[0009](0009-seguranca-das-mudancas-do-epico-1163.md). Each one comes from the merge diff against its
first parent (`git diff <merge>^1 <merge>`), with the generated Codex tree left out. Nothing was
changed here. Each real defect became its own spec.

| PR | Spec | Surface | Verdict |
| --- | --- | --- | --- |
| #1206 | 1185 | `pr/create.md`, `conclude.md`, `orchestrator.md`, `spec-runner.md`, `git-steward.md` | Accepted |
| #1215 | 1188 | `develop.md`, `spec-runner.md` | Accepted |
| #1225 | 1205 | `orchestrator.md`, `spec-runner.md`, develop/execute/conclude | Accepted |
| #1229 | 1219 | `orchestrator.md`, `verifier.md` | Accepted |
| #1196 | 1190 | `execute.md` step 5g | Accepted, one defect: spec 1242 |
| #1228 | 1210 | `execute.md` step 5g | Accepted |
| #1214 | 1198 | `translate.py`, `sync_specs_reader_plugin.py` | Accepted |
| #1216 | 1202 | `translate.py` (`write_tree`) | Accepted |
| #1222 | 1203 | `translate.py` `COPY_DIRS`, `validate_codex_plugin.py` | Accepted, one finding |
| #1194 | 1191 | `verifier.md` grants | Accepted |
| #1227 | 1211 | `orchestrator.md` grants | Accepted, one defect: spec 1241 |
| #1230 | 1212 | `git/commit.py`, `execute.md` | Accepted |
| #1208 | 1136 | `knowledge/structure.py`, `cli.py` | Accepted |

The two epics' other PRs touch no approval, publication, credential, hook, grant or file-writing
surface: #1193, #1195, #1207, #1209, #1217, #1220, #1221, #1223, #1224 and #1226. They get no section.

## #1206 — `pr:create` publishes on the word `autonomous`

The input word `autonomous` replaces step 4's confirmation. It covers exactly the remote, the
branch and the spec's title, and never adds `--delete-source-branch`. An absent title or a missing
spec id is still asked. The word passes down a fixed chain (orchestrator → spec-runner → conclude →
`pr:create`, and orchestrator → git-steward), and every hop says "only when the caller's prompt
carries it". The command's `allowed-tools` did not change. A human who types the word is giving
their own pre-answer. Accepted.

## #1215 — a forced `low` leaves `complexity` alone

The change only removes a write: a forced `low` stamps `approved by=orchestrator-forced` and no
longer lowers `priority.complexity`. The forced stamp stays tellable apart from a human's. Accepted.

## #1225 — `needs-human` instead of an improvised answer

A sub-agent without `AskUserQuestion` now returns `STATE: blocked` with `NOTE: needs-human:`. The
orchestrator never re-spawns that worker and asks the human. This removes a path where a worker
answered a human question for itself. Accepted.

## #1229 — the verifier requires the conclusion

Check 8 reads `cq specs status` (already granted) and fails a spec that has no `phase: archive` and
`Outcome`. The orchestrator no longer hands such a PR to `git-steward` for merge. The acceptance
gate only got stricter. Accepted.

## #1196 — `git remote set-head` before the hook

Step 5g runs `git remote set-head origin -a` before it invokes the hook. When the remote cannot be
reached, it runs `git remote set-head origin <base>` instead. Both write
`refs/remotes/origin/HEAD` into the shared `.git`. Decision 0009 kept a worker from making that
write, and the spec-runner contract forbids any write outside its worktree. The fallback can also
pin `origin/HEAD` to a spec's `branch.base` that is not the default branch. That value persists, and
execute step 2 and `/security-review` read it as the base for every later run.

- **Defect:** captured as spec **1242**, not fixed here.

## #1228 — the hook targets the worktree

The hook context now names `work checkout: <toplevel>` and `review: git -C <toplevel> diff
origin/HEAD...HEAD`. That is a read-only diff whose path comes from `git rev-parse
--show-toplevel`, not from spec text. The declared hook command is still passed untouched.
Accepted. Its target depends on `origin/HEAD`, so it inherits the #1196 defect.

## #1214 — the aggregate source digest leaves the manifests

`source_sha256` is removed from `.generated-from.json` and from the specs-reader sync script.
`reconciliation` now compares the per-file hashes already versioned in `.generated-files.json`.
No path, permission or write target changed. Accepted.

## #1216 — path containment of `translate --write`

`previous_files` treats every manifest entry as untrusted. It refuses a non-string, empty or
absolute entry, and any entry whose `resolve()` leaves the destination (symlinks included). It
checks all entries before the first `unlink`. A refusal comes back as `ct-translation-refused`
(exit 2). This closes deletion outside the destination through a tampered or merged manifest.
Accepted.

## #1222 — the agents travel to the Codex tree

`agents` joined `COPY_DIRS`, so the six agent files are copied into `plugins/quenching-codex/agents/`.
`validate_codex_plugin.py` now fails a skill that cites an agent the tree does not carry. Nothing
new is executed or written outside the generated tree. Accepted.

- **Finding:** the copies keep their Claude Code `tools:` grants, such as the verifier's read-only
  list. This review did not prove that Codex enforces them. If it does not, "read-only" is prose
  only on that platform. Parked as a discovery of spec 1232.

## #1194 — the verifier's `git branch` grant

`Bash(git branch:*)` was removed. The verifier keeps only read-only git grants. This closes the
finding decision 0009 parked on #1175. Accepted.

## #1227 — the orchestrator's `git branch` grant

`Bash(git branch:*)` was narrowed to `Bash(git branch --list:*)`. Narrowing it was the right move,
but the prefix still admits a delete. Measured on 2026-10-08 in a throwaway repository:
`git branch --list -D tmp` exits 129, while `git branch --list --no-list -D tmp` exits 0 and
deletes `tmp`.

- **Defect:** captured as spec **1241**, not fixed here.

## #1230 — the deterministic commit verb

`cq git commit --subject` runs `git commit -m <subject>` as an argv list, with no shell. It never
stages, amends or passes `--no-verify`, so repository hooks still run. It refuses a blank subject
or an empty index (exit 2). Accepted.

## #1208 — `cq knowledge listing --write`

The verb rewrites one fixed file, `standards/index.md`, and only inside its existing GENERATED
zone. It refuses (exit 2) when that zone is absent. The rows come from the bundle's own
frontmatter, and nothing extracted is executed. `--check` is the default. Accepted.

## Hook evidence

The 1192 orchestration ran `/security-review` over the base checkout in 5 of 8 builds and found an
empty diff. #1228 addresses that. This review did not rely on the hook: it was written by hand from
the merge diffs listed above. Spec 1232's own task invokes the hook against its worktree diff and
reports the classification on the worker's `HOOKS:` line.
