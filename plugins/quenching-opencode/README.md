# quenching-opencode (generated)

This OpenCode distribution is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_opencode_plugin.py --write` to refresh it; never edit it by hand.

It carries 61 commands (`commands/`), 7 subagents (`agents/`) and the payload they
cite (`quenching/`, including the bundled `cq`).

## Install

Copy the three parts into the OpenCode configuration directory:

```bash
mkdir -p ~/.config/opencode
cp -R commands agents ~/.config/opencode/
mkdir -p ~/.config/opencode/quenching
cp -R quenching/. ~/.config/opencode/quenching/
```

Commands run as `/quenching-<front>-<verb>` (`opencode run --command quenching-specs-status`).
Prose paths assume `~/.config/opencode/quenching`; `cq` honours `QUENCHING_OPENCODE_ROOT` for another root.
Commands and subagents pin no model: the session's configured model runs every role.
