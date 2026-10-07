# AGENTS.md — claude-quenching

Language: pt-BR — the contract is /docs/standards/agents/communication.md.
Ephemeral writes: .quenching/ — the contract is /docs/standards/agents/ephemeral-writes.md

This repository publishes the `quenching` Claude Code plugin marketplace (and its Codex
translation). It has no application build: command bodies and references are executable prose,
while a few Python tools provide the local checks. Treat command-body edits like code.

## Operating

After changing the repository, run the single repository gate from its root:

```bash
bash scripts/verify_repo.sh
```

The gate is zero errors. Surface-load checks live at
`plugins/quenching/assets/checks/functional-checks.sh`; exit 2 is inconclusive, not green. The spec
backend is GitHub, so there is no local `/.specs/` workspace.

## Safety that must stay visible

- Do not add `context: fork` beside a command's mid-flow gate; the minimal building cycle is the
  only documented exception, and its review lives in the PR.
- Never downgrade classification or executor sub-agents to `haiku` in
  `/quenching:knowledge:import-memory`.

Both rules are also scoped in `.claude/rules/` so they load when those files are touched.

## Navigation

Durable knowledge lives in [/docs/index.md](/docs/index.md); resolve unfamiliar terms in
[/docs/glossary.md](/docs/glossary.md). The product manual, command catalog, cost model and install
path live in [plugins/quenching/README.md](plugins/quenching/README.md). The registered sources are
`plugins/quenching/commands/**` and `plugins/quenching/assets/references/**`. Do not replicate
durable knowledge in this file.
