# quenching-specs-reader

A read-only view of another project's [quenching](../quenching/README.md) specs.
It registers **one** command, `/quenching-specs-reader:read`, for a project that needs to read a
specs front (an Obsidian vault reading its to-do list, for example) without enabling the full
`quenching` plugin and its 54 commands.

## Install in a target project

Add the marketplace once, then enable only this plugin in the target's `.claude/settings.json`,
pointing it at a local checkout of the project whose specs you read:

```json
{
  "extraKnownMarketplaces": {
    "quenching": { "source": { "source": "github", "repo": "holetz/claude-quenching" } }
  },
  "enabledPlugins": { "quenching-specs-reader@quenching": true },
  "env": { "QUENCHING_SPECS_ROOT": "/absolute/path/to/the/project/checkout" },
  "permissions": { "allow": ["Bash(cq-specs-read:*)"] }
}
```

The command pre-grants `Bash(cq-specs-read:*)` itself, and that is enough in the default
permission mode. The `permissions.allow` line is for sessions that never prompt (`dontAsk`, a
scheduled run): measured on Claude Code 2.1.284, a command's `allowed-tools` did not admit the
call there, and the entry point is read-only, so allowing it project-wide grants no write.

The store and its configuration come from that checkout. A git store is read from a bare mirror of its own, with no write to the target; a deprecated tracker backend is read as for `cq specs`: reading
GitHub issues needs an authenticated `gh`, Azure Boards an authenticated `az`.

## Use

- `/quenching-specs-reader:read`: the ranked front of active specs, with task progress.
- `/quenching-specs-reader:read 1139`: one spec's open, blocked and done tasks.
- `/quenching-specs-reader:read --root ~/code/other-project`: overrides `QUENCHING_SPECS_ROOT`.

The executable is `cq-specs-read` (on `PATH` while the plugin is enabled). It admits only `list`,
`status`, `show`, `section` (read form), `next` and `config`. Every write verb, `section --write`
and `--fold` are refused with exit 2, and every backend write path is disabled before dispatch.

## Maintenance

Only `commands/`, `bin/` and this README are edited here. `assets/**`, `VERSION`,
`.claude-plugin/plugin.json` and `.generated-from.json` are generated from `plugins/quenching/`:

```bash
python3 scripts/sync_specs_reader_plugin.py --write   # after changing plugins/quenching
bash scripts/verify_repo.sh                            # runs the --check
```
