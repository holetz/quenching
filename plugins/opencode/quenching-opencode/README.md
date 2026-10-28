# quenching-opencode (generated)

This OpenCode distribution is generated from `plugins/quenching/`, the only editable source. Run
`python3 scripts/sync_opencode_plugin.py --write` to refresh it; never edit it by hand.

It carries 61 commands (`commands/`), 7 subagents (`agents/`) and the payload they
cite (`quenching/`, including the bundled `cq`).

## Install

Copy the three parts into `~/.opencode/`, which OpenCode reads beside its configuration directory
and which survives an isolated `XDG_CONFIG_HOME`:

```bash
mkdir -p ~/.opencode
cp -R commands agents ~/.opencode/
mkdir -p ~/.opencode/quenching
cp -R quenching/. ~/.opencode/quenching/
```

This distribution is for OpenCode outside Omnigent. On a machine that runs the hosted Omnigent
operator agent, do not install it: the agent already carries the same commands as skills, and both
copies would load.

### Upgrade from 6.9.0

Before 6.10.0 the distribution lived under `~/.config/opencode/`. Remove that copy first: OpenCode
loads both roots, so a stale `quenching-*` command and the new one would compete under the same
name. Remove only the quenching files, never the user's own commands, agents or configuration:

```bash
rm -f ~/.config/opencode/commands/quenching-*.md
rm -f ~/.config/opencode/agents/quenching-*.md
rm -rf ~/.config/opencode/quenching
```

Then install under `~/.opencode/` as above and start a new OpenCode session.

Commands run as `/quenching-<front>-<verb>` (`opencode run --command quenching-specs-status`).
Prose paths assume `~/.opencode/quenching`; `cq` honours `QUENCHING_OPENCODE_ROOT` for another root.
Commands and subagents pin no model: the session's configured model runs every role.

## Permissions

Subagents that hold scoped `cq` access in the source carry `"*": ask` first, then one
`"cq <verbs> *": allow` pattern per `Bash(cq <verbs>:*)` grant: OpenCode applies the last rule that
matches, so the order is the policy; `edit` and `webfetch` stay `deny` where the source
grants none. Commands take their permissions from
the session, so allow `cq` there the same way in `opencode.json`:

```json
{"permission": {"bash": {"*": "ask", "cq *": "allow"}}}
```

The CI templates under `assets/zensical/` (`ci-github-pages.yml`, `azure-pipelines-docs.yml`) are not
shipped in this distribution.
