# quenching-quota

The Claude subscription's **5-hour and weekly windows** in OpenCode, outside the model: no tool call
and no context spent. One line, coloured by how full the fuller window is:

```text
5h ▓▓░░ 35% ↻ 2h30 · semana ▓░░░ 17% ↻ qui 13h
```

- **Desktop**: a composer pill beside the `quenching-cache` band (the cache keeps the first place),
  with **Detail**, **Refresh** and **Hide** (**Detalhe**, **Atualizar**, **Esconder** in Portuguese).
- **TUI**: the same line in the prompt footer's status slot (`prompt.footer.status`).
- **`/quenching-quota`** shows the detail in a toast: both windows with their reset, the Sonnet and
  Opus weekly windows when the reply carries them, where the token came from and when it was read.
  `/quenching-quota toggle` hides or shows the band in every window.

The band speaks the language the repository's `AGENTS.md` (else `CLAUDE.md`) declares on its
`Language:` line; a tag starting with `pt` is Portuguese, anything else English.

## Where the numbers come from

`GET https://api.anthropic.com/api/oauth/usage` with the subscription's OAuth token and
`anthropic-beta: oauth-2025-04-20`. The endpoint is undocumented, used by the community, and does
not spend quota. It is the plugin's **only** network destination (`src/fetch.ts`):

- one reply is reused for `shared.quota.intervalSeconds` (never under 60 s), and the same request in
  flight is shared by every window and every copy of the plugin in the process;
- the request times out after 5 s and refuses redirects;
- a 429 pauses for its `Retry-After` (at least the interval, at most 15 min);
- a 401/403 stops asking until the token changes, and the band asks the person to sign in again.
  The plugin **never refreshes** the token.

Without a window open, nothing is asked: the server has no timer of its own, and each window asks
at most once a minute.

## The token — read, never written

In order, the first that holds a Claude login wins (`src/token.ts`):

1. OpenCode's `auth.json` — `$XDG_DATA_HOME/opencode/auth.json`, `~/.local/share/opencode/auth.json`,
   `%LOCALAPPDATA%/opencode/auth.json` — key `anthropic` with `type: "oauth"`;
2. Claude Code's `.credentials.json` — `$CLAUDE_CONFIG_DIR/.credentials.json`, else
   `~/.claude/.credentials.json` — `claudeAiOauth.accessToken`. This is the route when OpenCode runs
   Claude through the Agent SDK (`claude-agent`).

An expired token is not sent. No token → "no subscription detected". The token never leaves the
network module: what the windows receive carries only its source, and errors are fixed words, never
the runtime's message or the reply's body. The macOS Keychain and the `claude` CLI are not read,
because the plugin opens no process but `cq`.

## Settings

`shared.quota`, read through `cq config show --effective --json` (every 5 min per directory; the
defaults below without `cq`):

| Key | Default | What it does |
| --- | --- | --- |
| `shared.quota.warnPercent` | `70` | from this usage of either window the band turns yellow |
| `shared.quota.dangerPercent` | `90` | from this usage the band turns red |
| `shared.quota.intervalSeconds` | `300` | how long one reading is reused; never under 60 (a machine key) |
| `shared.quota.showSonnet` | `true` | the detail lists the Sonnet and Opus weekly windows |

The `cq` that answers is the project's `.agents/quenching/bin/cq` (found walking up from the
session's directory), then `QUENCHING_CQ`, then this checkout's `quenching/assets/bin/cq`, then `cq`
on `PATH` — always with the fixed argv above and no shell.

## Install

Add the package directory to the `plugins` array of the OpenCode configuration, beside the other
quenching plugins:

```json
{
  "$schema": "https://opencode.ai/config.json",
  "plugins": ["/absolute/path/to/integrations/opencode-quota"]
}
```

Restart the session after adding or removing the entry; removing it is the uninstall. `cq deploy`
never installs it.

## Build and checks

`src/index.ts` (server) and `src/tui.tsx` load as source; the Desktop entry is the committed bundle
`dist/gui-experimental.cjs`. After changing `src/gui.tsx` or what it imports:

```bash
npm ci
npm run build
npm test
```

`npm test` runs `tests/usage.check.mjs` (parser over upstream's sanitized fixtures, the band in both
languages, the tones, the settings), `tests/fetch.check.mjs` (token sources and order, the single
destination and its headers, the 60 s floor, shared requests, 401 and 429, no token in any reading,
the credentials file untouched) and `tests/surface.check.mjs` (the security contour read in the
code: network only in `src/fetch.ts`, a process only in `src/cq.ts` with its fixed argv, no write,
no log, no host storage, no other URL). The repository gate runs the same checks.

## Layout

| Path | What it is |
| --- | --- |
| `src/core/usage.ts` | the pure half: reply parser, settings read, band and detail words |
| `src/token.ts` | the token's two read-only sources |
| `src/fetch.ts` | the one request, its memory, pause and refusal |
| `src/cq.ts` | `cq config show --effective --json`, and nothing else |
| `src/rpc.ts` | the contract between the server and the windows |
| `src/index.ts` | the server: settings per directory, the view the windows draw |
| `src/gui.tsx` | the Desktop pill and `/quenching-quota` |
| `src/tui.tsx` | the TUI footer band and `/quenching-quota` |

Derived from [slkiser/opencode-quota](https://github.com/slkiser/opencode-quota) (MIT); what was cut
and why is in [NOTICE.md](NOTICE.md).
