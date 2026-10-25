# Permissions (generated)

Every bundle carries one deny-only CEL policy (`omnigent.policies.builtins.cel.cel_policy`) derived from the source `allowed-tools:` (commands) or `tools:` (agents). What the source does not grant is denied; Omnigent has no positional allow list and a DENY outranks every ALLOW, so no rule is an allow. A scoped `Bash(cq <verbs>:*)` is the exception inside the one shell denial: a call passes only when it matches, in full, `cq <verbs>` segments joined by `&&`, `||` or `;` with arguments free of ; & | < > $ ` \ and newline. Grants Omnigent cannot express are denied and listed below as not expressed.

| Bundle | Shell | Spawn | Denied tool names | Not expressed | Dropped |
| --- | --- | --- | --- | --- | --- |
| `quenching-align` | cq * | no | 16 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-agent-new` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-align` | cq * | yes | 6 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied); Bash(git grep:*) (non-cq scoped Bash grant; denied); Bash(grep:*) (non-cq scoped Bash grant; denied); Bash(mkdir:*) (non-cq scoped Bash grant; denied); Bash(mv:*) (non-cq scoped Bash grant; denied); Bash(rm:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-command-eval` | cq * | yes | 6 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-command-new` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-command-retro` | cq * | no | 21 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-harness-align` | cq * | yes | 6 | Bash(find:*) (non-cq scoped Bash grant; denied); Bash(git grep:*) (non-cq scoped Bash grant; denied); Bash(git check-ignore:*) (non-cq scoped Bash grant; denied); Bash(grep:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-hook-new` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-components-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-delivery-align` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-delivery-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-design-align` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(npx:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-design-genre-new` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-design-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-branch` | cq git base / git conventions / git specs / git state / git worktree add / specs config / specs status / components read | no | 21 | - | - |
| `quenching-git-cleanup` | cq * | no | 21 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-commit` | cq git commit / git conventions / git specs / git state / specs next / components read | no | 21 | - | hooks |
| `quenching-git-commit-incremental` | cq * | no | 21 | Bash(git status:*) (non-cq scoped Bash grant; denied); Bash(git diff:*) (non-cq scoped Bash grant; denied); Bash(git ls-files:*) (non-cq scoped Bash grant; denied); Bash(git add:*) (non-cq scoped Bash grant; denied); Bash(git commit:*) (non-cq scoped Bash grant; denied); Bash(git log:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-merge` | cq * | no | 21 | Bash(git worktree:*) (non-cq scoped Bash grant; denied); Bash(git merge:*) (non-cq scoped Bash grant; denied); Bash(git rebase:*) (non-cq scoped Bash grant; denied); Bash(git branch:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-pr-create` | cq git base / git conventions / git state / git push / git pr create / git pr probe / git pr record / specs config / specs status / specs show / components read | no | 21 | Bash(gh repo view:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-pr-review` | cq * | no | 16 | Bash(gh pr view:*) (non-cq scoped Bash grant; denied); Bash(gh repo view:*) (non-cq scoped Bash grant; denied); Bash(gh api graphql:*) (non-cq scoped Bash grant; denied); Bash(az repos pr:*) (non-cq scoped Bash grant; denied); Bash(az devops invoke:*) (non-cq scoped Bash grant; denied); Bash(az rest:*) (non-cq scoped Bash grant; denied); Bash(git branch:*) (non-cq scoped Bash grant; denied); Bash(git remote get-url:*) (non-cq scoped Bash grant; denied); Bash(git add:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-pr-status` | cq * | no | 21 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(git remote get-url:*) (non-cq scoped Bash grant; denied); Bash(git branch:*) (non-cq scoped Bash grant; denied); Bash(gh repo view:*) (non-cq scoped Bash grant; denied); Bash(gh pr view:*) (non-cq scoped Bash grant; denied); Bash(gh api graphql:*) (non-cq scoped Bash grant; denied); Bash(az repos pr:*) (non-cq scoped Bash grant; denied); Bash(az devops invoke:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-push` | cq * | no | 21 | Bash(git status:*) (non-cq scoped Bash grant; denied); Bash(git branch --show-current:*) (non-cq scoped Bash grant; denied); Bash(git remote:*) (non-cq scoped Bash grant; denied); Bash(git rev-parse:*) (non-cq scoped Bash grant; denied); Bash(git rev-list:*) (non-cq scoped Bash grant; denied); Bash(git log:*) (non-cq scoped Bash grant; denied); Bash(git reflog:*) (non-cq scoped Bash grant; denied); Bash(git ls-remote:*) (non-cq scoped Bash grant; denied); Bash(git push:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-revert` | cq * | no | 21 | Bash(git status:*) (non-cq scoped Bash grant; denied); Bash(git branch --show-current:*) (non-cq scoped Bash grant; denied); Bash(git rev-parse:*) (non-cq scoped Bash grant; denied); Bash(git rev-list:*) (non-cq scoped Bash grant; denied); Bash(git merge-base:*) (non-cq scoped Bash grant; denied); Bash(git log:*) (non-cq scoped Bash grant; denied); Bash(git show:*) (non-cq scoped Bash grant; denied); Bash(git diff:*) (non-cq scoped Bash grant; denied); Bash(git revert:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-git-steward` | cq git base / git commit / git conventions / git specs / git state / git push / git pr create / git pr probe / git pr merge / git pr record / git worktree add / git worktree retire / specs config / specs status / specs show / specs next / components read | no | 21 | Bash(gh repo view:*) (non-cq scoped Bash grant; denied); Bash(gh pr view:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-git-sync` | cq * | no | 21 | Bash(git status:*) (non-cq scoped Bash grant; denied); Bash(git remote get-url:*) (non-cq scoped Bash grant; denied); Bash(git fetch:*) (non-cq scoped Bash grant; denied); Bash(git rebase:*) (non-cq scoped Bash grant; denied); Bash(git for-each-ref:*) (non-cq scoped Bash grant; denied); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-handoff` | denied | no | 22 | Bash(mktemp:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-add` | cq * | no | 10 | - | - |
| `quenching-knowledge-align` | bare (no rule) | yes | 5 | - | - |
| `quenching-knowledge-define` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-documentation-build` | bare (no rule) | no | 10 | - | - |
| `quenching-knowledge-documentation-plan` | cq * | no | 14 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied); Bash(rg:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-documentation-produce` | cq * | no | 16 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-documentation-review` | cq * | yes | 13 | - | - |
| `quenching-knowledge-documentation-write` | cq * | yes | 6 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-glossary-backfill` | cq * | yes | 6 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-import` | cq * | yes | 2 | WebFetch (granted; Omnigent has no tool to express it); Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-import-memory` | cq * | yes | 6 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied); Bash(rm:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-knowledge-learn` | cq * | no | 10 | - | - |
| `quenching-knowledge-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-opensource-align` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-opensource-readiness` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-opensource-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-ops-align` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-ops-entrypoint-new` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-ops-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-orchestrator` | cq specs status / specs list / specs show / specs parallel / specs next / specs record / components session cost / components session context / git state | no | 17 | Agent(quenching-specs:spec-runner, quenching-specs:verifier, quenching-specs:git-steward, quenching-specs:scout, quenching-specs:spec-architect) (scoped sub-agent allowlist; denied); Bash(git for-each-ref:*) (non-cq scoped Bash grant; denied); Bash(git worktree list:*) (non-cq scoped Bash grant; denied); Bash(gh pr view:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-proof-align` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-proof-layer-new` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(mkdir:*) (non-cq scoped Bash grant; denied); Bash(mv:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-proof-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-reviewer` | cq git history | no | 17 | Bash(bash scripts/verify_repo.sh:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-scout` | cq specs show / components read | no | 17 | Bash(git ls-files:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-security-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-spec-architect` | cq specs new / specs list / specs show / specs next / specs epic add | no | 17 | - | model |
| `quenching-spec-runner` | bare (no rule) | no | 9 | - | model |
| `quenching-specs-autopilot` | bare (no rule) | yes | 13 | - | - |
| `quenching-specs-board` | cq * | no | 24 | - | - |
| `quenching-specs-conclude` | bare (no rule) | no | 9 | - | model |
| `quenching-specs-create` | cq * | no | 16 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-specs-develop` | cq * | yes | 9 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-specs-execute` | bare (no rule) | yes | 5 | - | model |
| `quenching-specs-improve` | cq * | yes | 10 | Bash(git:*) (non-cq scoped Bash grant; denied); Bash(wc:*) (non-cq scoped Bash grant; denied); Bash(mkdir:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-specs-orchestrate` | cq * | yes | 17 | - | - |
| `quenching-specs-status` | cq * | no | 21 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-specs-triage` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied); Bash(py:*) (non-cq scoped Bash grant; denied) | model |
| `quenching-toolchain-align` | cq * | no | 10 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-toolchain-status` | cq * | no | 17 | Bash(python3:*) (non-cq scoped Bash grant; denied) | - |
| `quenching-verifier` | cq specs status / specs show / git audit / git pr view | no | 17 | - | model |

`hooks:` and `model:` frontmatter, scoped `Agent(...)` allowlists and non-`cq` scoped `Bash` grants are never generated or approximated.
