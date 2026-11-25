---
type: how-to
title: Work in VS Code with GitHub Copilot
description: Use the deployed quenching surface in VS Code — the workspace seeds, the zero-token tasks, the worktree slots, the built-in worktree flow and the extensions the flow recommends.
resource: docs/decisions/0021-no-vscode-extension.md, docs/standards/architecture/deploy-mode.md, docs/standards/workflows/plugin-configuration.md, .vscode/settings.json, .vscode/tasks.json
tags:
  - how-to
  - vscode
  - copilot
timestamp: 2026-11-25
audience: human
authority: current
source: spec 466 (epic 453); the client measurements are in the 452 artifact `copilot-bench.md` (2026-11-25); VS Code documentation as cited in the spec artifact `vscode-extension-evaluation.md`
maintainer: Israel Holetz
---

# Work in VS Code with GitHub Copilot

*Audience: implementer · Client: VS Code + GitHub Copilot · No quenching extension needed*

VS Code with GitHub Copilot is a client of the surface `cq deploy` already installs: it reads the
skills, agents, hooks, MCP and path rules from the files the deploy writes. This recipe covers the
workspace seeds, the zero-token tasks, the worktree slots, the built-in worktree flow and the
extensions the flow recommends. The decision behind it is
[ADR 0021](../decisions/0021-no-vscode-extension.md).

## What the client reads

| Capability | Where the deploy writes it | What you see |
| --- | --- | --- |
| Skills | `.claude/skills` (the generated bridge) and `.agents/skills` (the generic layer) | the `quenching-*` skills in the chat's `/` list, each once |
| Agents | `.claude/agents`; `.github/agents` when the repository declares `shared.projections: ["github"]` | the `quenching-spec-*` agents in the custom-agent picker |
| Hooks | `.claude/settings.json` | the tool-call hooks the deploy wires, such as the co-author guard |
| MCP | `.mcp.json` | the `quenching` server and its tools |
| Path rules | `.claude/rules`; `.github/instructions` with the `github` projection | the rule loaded only for the paths it matches |
| Workspace | `.vscode/settings.json` and `.vscode/tasks.json`, seeded by `shared.workspace.vscode` | the search exclusions, the request ceiling and the tasks |

There is no `--harness copilot`: the client reads the existing layer, and
`cq deploy --harness copilot` refuses with `ct-deploy-harness`. The `.github/` projections and the
workspace seeds are opt-in; a repository that declares neither carries no extra file.

## Seed the workspace

Declare the workspace seed in `.agents/quenching.json`:

```json
{
  "shared": {
    "workspace": {
      "vscode": true
    }
  }
}
```

`cq deploy --target . --write` seeds `.vscode/settings.json` and `.vscode/tasks.json` only when they
are absent, and never rewrites an existing file: after it lands, the file is the repository's. Run
`cq doctor --workspace` to see the state of the two files and the block to copy.

## Run the zero-token tasks

Command Palette → **Tasks: Run Task**:

- **quenching: gate** — `bash scripts/verify_repo.sh`
- **quenching: deploy check** — `cq deploy --target . --check`
- **quenching: specs status** — asks for a spec id and prints its state
- **quenching: worktree slots** — who holds each slot
- **quenching: slots workspace** — writes the slots workspace
- **quenching: open slots** — writes it and opens the window

Every task runs in the terminal with no model turn. The `windows` override calls `cq.cmd`, so the
same tasks work in PowerShell and cmd.

## Open the slots

The slot pool lives beside the repository. `cq git worktree workspace --write` writes
`.vscode/quenching-slots.code-workspace` with the primary checkout and the held slots, and the
**quenching: open slots** task runs `code -n` on it. The file carries absolute paths, is
machine-local and is never versioned.

## Worktrees

VS Code's **Source Control Repositories → Worktrees** creates, opens, compares, migrates and deletes
a worktree. The `cq` flow adopts the worktree the client created instead of cutting a second one,
and the `branch:` record points at it. The pool slots are locked: a free slot stays locked as
`quenching: available`, and a held slot is refused by a plain `git worktree remove`. Do not force a
removal on a slot; the lock is what keeps its `.venv` for the next spec. When the work is merged,
the flow gives the slot back clean.

## Extensions

- **GitHub Pull Requests** (`GitHub.vscode-pull-request-github`) — recommended, optional. It reviews
  the PRs `cq git pr create` opens, with the checks and the review threads in the editor. The `gh`
  CLI remains the route without it.
- **No quenching extension.** The status bar is the one thing only an extension draws, and it is
  accepted as a presentation gap; [ADR 0021](../decisions/0021-no-vscode-extension.md) names the
  demand that reopens the decision.
- **A third-party worktree manager is not recommended for the pool.** The built-in covers the
  flow, and a forced remove can delete a slot and its `.venv`; the free-slot lock protects the
  normal path.
- The `anthropic.claude-code` extension belongs to the Claude Code harness, not to Copilot.

## What is measured, and what is expected

The client was measured on 2026-11-25 (VS Code Insiders 1.149.0-insider, `GitHub.copilot-chat`
0.77.2026112501): skills, agents and the hook firing are read — the 452 H1, H2 and the Linux half of
H4 are `confirmed`; the hook's fail-open by timeout is `unmeasured-live`. Path rules, the workspace
keys and prompt-free slot access are `unmeasured-live` (H6, H7, H11 and H12): the artifact exists,
the live half is a protocol with the client open. A new client version is a new measurement, and the
bench that repeats it in this repository is `python3 scripts/copilot_bench.py --target . --json`.

## Verify your setup

- `python3 .agents/quenching/bin/cq deploy --target . --check` — the deployed surface and the seeds.
- `python3 .agents/quenching/bin/cq doctor --workspace` — the two seed files and the block to copy.
- In the chat, type `/` and look for the `quenching-*` skills; the client lists each once.
- In the Source Control view, the **Worktrees** entry lists the worktrees the `cq` flow uses.

The contracts behind the seeds are [deploy-mode](../standards/architecture/deploy-mode.md) and
[plugin-configuration](../standards/workflows/plugin-configuration.md).
