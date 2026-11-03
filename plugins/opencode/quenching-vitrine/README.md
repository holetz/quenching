# quenching-vitrine

The **Specs** panel for OpenCode Desktop. It shows the specs the current session touched — what
the conversation cited, what a `cq specs …` command ran, and the commit or worktree the session is
in — without a general catalog when the session cited nothing.

The session is the unit: one session can touch many specs, and the ledger is hers, not the
plugin's. Opening the panel re-reads the conversation, so a plugin reloaded mid-session keeps the
list. The detail shows the whole spec document in tabs (Overview, Problem, Proposal, …), and its
header repeats the board signals: stage, priority (P1–P4), complexity, age, task progress, runner
state, block reason and assignee. Tasks are clickable and attach to the composer.

## Requirements

- OpenCode Desktop with GUI parts. The panel is a `Panel` in the `side` region plus the `/specs`
  command; a terminal-only OpenCode session has no place to render it.
- `cq` on `PATH` for the version check and the deploy; the spec reads prefer the target's
  `.agents/quenching/bin/cq` when it exists.
- A target where quenching is installed or installable. The **Board** button runs
  `cq portal serve` (no `--read-only`) and opens the system browser with a fresh `nonce` per
  click.

When the target's quenching is older than the `cq` on `PATH`, or absent, the panel offers
**Atualizar** / **Instalar** and runs `cq deploy --target <root> --write` after confirmation.
When it is current, the same place shows a green **OK 6.14.2** chip with the installed version.
A target already installed reuses its manifest; a new target receives `--harness opencode`.

## Install

Add the package directory to the `plugins` array of the OpenCode configuration — the global
`~/.config/opencode/opencode.jsonc` for every project, or `<repo>/opencode.json` for one project:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": ["/absolute/path/to/plugins/opencode/quenching-vitrine"]
}
```

The path may be this checkout's `plugins/opencode/quenching-vitrine/`. Restart the session after
adding or removing the entry. Removing the entry is the uninstall.

## Build

`src/index.ts` is loaded by the host; the GUI entry is the committed bundle
`dist/gui-experimental.cjs`. After changing `src/gui.tsx`, rebuild it:

```bash
npm ci
npm run build
```

`npm run build` runs `tsc` and Vite. `dist/` is committed so a fresh checkout works without a
build; keep it in step with `src/` in the same commit. `node_modules/` is never committed.

## Layout

| Path | What it is |
| --- | --- |
| `src/index.ts` | plugin server: RPC methods, session/commit evidence, the update flow |
| `src/rpc.ts` | the RPC contract the server and the GUI share |
| `src/specs.ts` | spec ledger, conversation harvest, `cq specs` reads, cache |
| `src/quenching.ts` | installed/available version check and `cq deploy` |
| `src/cq.ts` | process and path helpers |
| `src/gui.tsx` | the Specs panel and its `/specs` command |
| `dist/gui-experimental.cjs` | built GUI entry, loaded by OpenCode Desktop |

## Limits

This package is installed by configuration, not by `cq deploy`: a deployed target receives the
command surface and agents, not this desktop panel. It also does not upgrade the `cq` on
`PATH`; the button only writes the target's surface.
