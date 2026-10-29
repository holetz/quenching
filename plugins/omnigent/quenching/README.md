# quenching for Omnigent (generated)

This Omnigent operator agent is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_omnigent_plugin.py --write` to refresh it; never edit it by hand.

One bundle, no payload: 61 skills (`skills/`), 7 sub-agents (`agents/`), and the
`quenching` MCP server launched by `uvx` from the tag `6.12.0`. Built against Omnigent
`v0.19.1` (server image `omnigent-server:v0.19.1`). The bundle pins no model:
the server's policy chooses it. `skills: none` binds the Claude SDK harness only: under OpenCode the
`skill` tool still lists the host skills in `~/.claude/skills/` and `~/.agents/skills/` (only
`~/.config/opencode/skills/` is hidden), so a host that serves this agent must not carry quenching
skills in those two directories.

## Install

Register this directory as an agent on the Omnigent server, or run it locally:

```bash
omnigent run --agent plugins/omnigent/quenching -p "/quenching-specs-status"
```

Do not install the OpenCode distribution on the same machine: it carries the same commands.

## Permissions

The operator runs with the session's tools. Each sub-agent carries one deny-only policy derived from
its source `tools:`; see `docs/standards/architecture/surface-translation.md`. The model table is
`docs/project/model-compat.md`.
