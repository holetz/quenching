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
- Python 3.11+ and `git`. The plugin brings its own `cq`: the package is installed from a
  checkout of this repository, and it runs that checkout's `quenching/assets/bin/cq`
  through Python (`python3` on Linux and macOS; `py -3`, else `python`, on Windows). `cq` on
  `PATH` is not required.
- A target where quenching is installed or installable. The **Board** button runs
  `cq portal serve` (no `--read-only`) and opens the system browser with a fresh `nonce` per
  click.

Which `cq` answers:

| Use | Order |
| --- | --- |
| spec reads and the Board | the target's `.agents/quenching/bin/cq`, then the plugin's checkout, then `PATH` |
| available version and the deploy | `QUENCHING_CQ`, then the plugin's checkout, then `PATH` |

`QUENCHING_CQ` is optional: the path of a `cq` file that should win over the checkout. A Python
`cq` runs through the interpreter above; on Windows, a `cq` that is not Python (the `--runtime
uvx` shim) runs through its `cq.cmd` sibling via `cmd.exe`, because Node does not start a `.cmd`
without a shell.

When the target's quenching is older than that `cq`, or absent, the panel offers
**Atualizar** / **Instalar** and runs `cq deploy --target <root> --write` after confirmation.
When it is current, the same place shows a green **OK <version>** chip with the installed version.
A target already installed reuses its manifest; a new target receives `--harness opencode`.

## Install

Add the package directory to the `plugins` array of the OpenCode configuration — the global
`~/.config/opencode/opencode.jsonc` for every project, or `<repo>/opencode.json` for one project:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": ["/absolute/path/to/integrations/opencode-vitrine"]
}
```

The path must be inside a full checkout of this repository (`integrations/opencode-vitrine/`),
because the bundled `cq` lives beside it. On Windows write the path with forward slashes or
escaped backslashes (`"C:/src/quenching/integrations/opencode-vitrine"`). Restart the session
after adding or removing the entry. Removing the entry is the uninstall.

Updating is updating the checkout: `git pull` on its primary branch, or `git checkout <tag>` for
a release, then restart OpenCode. The panel's `cq` and the version it offers to install move with
it.

## Build

`src/index.ts` is loaded by the host; the GUI entry is the committed bundle
`dist/gui-experimental.cjs`. After changing `src/gui.tsx`, rebuild it:

```bash
npm ci
npm run build
```

`npm run build` runs `tsc` and Vite. `dist/` is committed so a fresh checkout works without a
build; keep it in step with `src/` in the same commit. `node_modules/` is never committed.

`npm run bench` loads the server half into a fake host with a ~400k-token session, bursts of
tools and a fake `cq` with latency, and fails when the event loop stays blocked over 50 ms, a hook
returns a promise, more than two `cq` reads run at once, or the in-flight reads are not shared.

## Load budget

The plugin runs inside `opencode-cli serve`, so it must never hold the service:

- the `execute.before`, `execute.after` and `prompt` hooks return immediately; recording, the
  panel notice and any `cq` run detached, with errors swallowed;
- panel notices are coalesced (one `changed` per session per 500 ms, one `updated` per second);
- the conversation scan resumes from a per-session cursor and yields the event loop every 8 ms;
- at most two `cq` reads run at once, the same read in flight is shared, reads time out at 15 s,
  and a process that prints more than 8 MB is killed;
- opening the panel reads at most 12 specs outside `plans` (three `cq` each); the rest enter on
  the next openings.

## Layout

| Path | What it is |
| --- | --- |
| `src/index.ts` | plugin server: RPC methods, session/commit evidence, the update flow |
| `src/rpc.ts` | the RPC contract the server and the GUI share |
| `src/specs.ts` | spec ledger, conversation harvest, `cq specs` reads, cache |
| `src/quenching.ts` | installed/available version check and `cq deploy` |
| `src/cq.ts` | process and path helpers |
| `src/gui.tsx` | the Specs panel and its `/specs` command |
| `bench/load.ts` | the load benchmark behind `npm run bench` |
| `dist/gui-experimental.cjs` | built GUI entry, loaded by OpenCode Desktop |

## Limits

This package is installed by configuration, not by `cq deploy`: a deployed target receives the
command surface and agents, not this desktop panel. It also does not update its own checkout;
the button only writes the target's surface.
