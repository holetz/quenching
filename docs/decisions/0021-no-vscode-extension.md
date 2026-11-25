---
type: decision
title: No VS Code extension or agent plugin — the deployed surface and the editor cover the client
description: Why quenching ships no VS Code extension and no agent plugin, what each candidate adds and duplicates, the measured cost of a second release surface, and the evidence that reopens the decision
resource: docs/standards/architecture/deploy-mode.md, docs/standards/workflows/plugin-configuration.md, docs/standards/ci-cd/versioning-release.md, docs/decisions/0017-install-only-by-deploy.md, scripts/copilot_bench.py
tags: [decision, architecture, vscode, copilot, extension, plugin, deploy]
timestamp: 2026-11-25
audience: both
authority: current
source: spec 466 (epic 453); the measured candidate matrix is the spec artifact `vscode-extension-evaluation.md` (2026-11-25)
maintainer: quenching
---

# 0021 — No VS Code extension or agent plugin

[ADR 0017](0017-install-only-by-deploy.md) made `cq deploy` the only route into a repository and
kept as plugins only what installs into no repository. The VS Code client was then measured by the
452 bench: it reads the deployed skills, agents, hooks and MCP, and the 460 projected the worktree
slots into a `.code-workspace` and the zero-token tasks into `.vscode/tasks.json`. This records why
the client still gets no extension of its own — and no agent plugin — and what would change that.

## Context

- The client measured is VS Code Insiders 1.149.0-insider with `GitHub.copilot-chat`
  0.77.2026112501. It reads `.claude/skills` and `.agents/skills` (H1), `.claude/agents` and
  `.github/agents` (H2), `.claude/settings.json` hooks — H4, confirmed on Linux, its timeout
  fail-open still `unmeasured-live` — and `.mcp.json` natively.
- The only capability in the original problem that the deployed surface does not reach is a
  persistent status bar with the current spec, the slot, the cost and the quota. Everything else —
  skills, agents, MCP, hooks, rules, settings, tasks, slot projection, worktree creation — is
  either a deployed file or a built-in of the editor.
- The candidates were evaluated against the H9 criterion: cover a flow the CLI does not reach
  **and** not become a second surface. The matrix, the sources and the dates are in the spec
  artifact `vscode-extension-evaluation.md` (spec 466).

## Decision

- **quenching publishes no VS Code extension.** The status bar is presentation of data `cq`
  already exposes; a thin extension would add a publisher, a VSIX, an editor test
  harness, a release owner and a version lockstep — a second release surface — without a measured
  demand that pays for it. The gap is accepted, not closed.
- **quenching publishes no agent plugin.** A plugin bundles skills, agents, MCP and hooks that the
  deploy already writes into the directories the client reads; it would be a stale copy competing
  for the same names, installed by a trust prompt, exactly the distribution ADR 0017 retired. The
  `chatSkills` contribution point has the same problem from the other side: its path must resolve
  inside the extension, so it carries a copy instead of pointing at the workspace.
- **The flow recommends GitHub Pull Requests** (`GitHub.vscode-pull-request-github`) for reviewing
  the PRs `cq git pr create` opens. It complements the `gh` CLI; it does not duplicate the
  deployed surface. The recommendation is documentation only — `cq deploy` neither installs nor
  checks an editor extension.
- **The flow recommends the editor's built-in worktree UI** for the pool: Source Control
  Repositories → Worktrees covers create, open, compare, migrate and delete, and
  `cq git worktree workspace --write` opens the active slots in one `.code-workspace`. A
  third-party worktree manager is not recommended for the pool: it duplicates the built-in, and a
  forced `remove` can delete a free or held slot, defeating the lock that protects the slot's
  `.venv`.
- **The VS Code client is documented where the user reads it**: the guide
  `docs/how-to/work-in-vs-code.md` and the client list in `README.md`.

## Consequences

- The release lockstep gains no artifact; `docs/standards/ci-cd/versioning-release.md` is
  unchanged.
- A target that wants the status bar keeps using `cq specs status`, `cq git worktree slots` and
  `cq components session cost` in the terminal, or the tasks the deploy seeds.
- The recommendation of a third-party extension is not a dependency: a target without it loses
  only the PR review UI, and the `gh` route stays.
- The worktree manager warning is a user-facing consequence of the free-slot lock (460): the lock
  protects the normal flow, and a forced remove is an explicit operator action, not a supported
  one.
- A future extension, if it is ever justified, is an optional integration under `integrations/`,
  read-only, installed apart and never by `cq deploy`; it does not change the deployed surface.

## What would reopen the decision

A second request from a target, or repeated use of `cq specs status` / `cq git worktree slots` in
the terminal, is the measured demand a status-bar extension would need. That evidence opens a spec
for `integrations/quenching-vscode` — read-only, installed apart — and the decision is revisited
with the cost of that release surface in front of the same criterion. The existence of the API
alone is not the trigger.

## What this does not decide

- It does not build the status bar; the gap is accepted with the trigger above.
- It does not create a `--harness copilot` or any client-specific deploy mode; the epic 453
  invariant and the 452 H13 refusal stand, and the client reads the existing layer.
- It does not measure a live candidate extension; the evaluation is documentary and dated
  2026-11-25, and a new client version is a new measurement.
