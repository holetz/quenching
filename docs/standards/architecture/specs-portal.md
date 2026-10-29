---
type: standard
title: The specs portal reads one store and widens nothing without a decision
description: The local spec portal (cq specs serve) reads only the specs store open_backend reads, exposes a fixed set of GET and POST routes plus, under --chat, a read-only claude -p chat polled by job, keeps its loopback, token, Host/Origin and CSP guarantees, builds every node with textContent, reuses cockpit UX patterns but never its code, shows the spec-runner's run record on the card, and regenerates the reader copy and the Codex mirror with every change
resource: plugins/quenching/assets/bin/quenching/specs/portal.py, plugins/quenching/assets/bin/quenching/specs/chat.py, plugins/quenching/assets/portal/**, plugins/quenching/assets/bin/quenching/portal/**, plugins/quenching/assets/bin/quenching/common/lent.py, plugins/quenching/assets/bin/quenching/session/portal.py
tags: [architecture, portal, specs, security, ux]
timestamp: 2026-10-29
audience: both
authority: current
source: specs 1769, 1812, 1814, 1815, 1816 and the owner decisions B-O1 to B-O4 of epics 1768 and 1810
maintainer: quenching
---

# The specs portal reads one store and widens nothing without a decision

<!-- rules -->

`cq specs serve` is a local portal over the specs store, and `cq portal serve` serves one such
portal per registered project from a single server (§Central server). This standard is the contract any change
to `portal.py` or `assets/portal/**` is reviewed against. It describes what exists and fixes the
limits; it does not prescribe layout.

## Read scope

The portal reads exactly what `open_backend` reads, through the same layer the CLI uses. Nothing
else is read: no `~/.claude`, no other file tree, no `gh` call on a read (`derive_epic` runs without
`pr_states`). A change that needs data outside the store is not a portal change until a human
decides it.

The one exception is the live Claude Code sessions, and only when the portal was started with
`--sessions` (off by default). Then, and only on `GET /api/sessions`, it reads
`<claude root>/sessions/*.json` (`QUENCHING_CLAUDE_ROOT`, else `~/.claude`) and the tail of each
live session's transcript, through `quenching.session.live.read_live`, keeping only the sessions
whose `cwd` lies inside a worktree of this repository (`quenching.session.worktrees.list_worktrees`).
It never opens a `*.key` file and never returns `messagingSocketPath`, a `pid`, a `tool_result` or
a raw tool `input`. Without the flag, nothing under `~/.claude` is read and the session code is
not even imported. `specs/portal.py` never imports `quenching.session`: the reader is lent to it.
`cq` declares the loan in its `LOANS` table (`specs` borrows `specs.portal.sessions` from
`quenching.session.portal`) and registers it at dispatch, through `quenching.common.lent.lend`,
only when the module carrying the session package is enabled; the portal calls
`borrow(SESSIONS)`, which imports the lender only then. A new cross-pillar capability takes the
same route, never a direct import: the `portal` pillar borrows `portal.specs`
(`quenching.specs.portal`), `portal.worktrees` (`quenching.session.worktrees`) and
`specs.portal.sessions` under `LOANS["portal"]`, and `cq portal serve` refuses
(`portal-serve-unavailable`) when either of the first two is not lent. The `quenching-specs-reader` copy does not carry the session
package, so nothing is lent and it refuses `--sessions` (`sp-portal-sessions-unavailable`) before
a socket opens.

The second exception is the chat, and only when the portal was started with `--chat` (off by
default). Then `POST /api/chat` starts one child process, `claude -p`, whose `cwd` is a worktree of
this project; that process reads files of that worktree with `Read`, `Grep` and `Glob` and nothing
else (§Security guarantees). The portal itself still reads only the store: it reads the child's
stdout, never the files the child opened. `specs/portal.py` imports `quenching.specs.chat`, which
imports only the standard library, so the reader copy keeps carrying only `common` and `specs`.
Without the flag no process is started and both chat routes are a 404.

## Project registry

The projects a portal shows are registered in `~/.config/quenching/projects.json`
(`{"schemaVersion": 1, "projects": [{"name", "path"}]}`, `path` the absolute main root of the
repository, never a worktree). Only `cq portal add`, `cq portal remove` and `cq portal list`
(`quenching/portal/`) write it, atomically; no server and no page writes it. `cq portal serve` reads it once,
at start (a change to the registry needs a restart), and refuses an empty one
(`portal-no-projects`) before a socket opens. The one-time `cq portal add --from-orca` opens
only orca's `profiles/*/orca-data.json` and keeps `repos[].path` and `repos[].displayName`; any other
field there, tokens and credentials included, is never read into the registry or printed, and a
second import is refused. Reading orca live is not part of this standard.

## Central server

`cq portal serve [--host] [--port] [--read-only] [--open] [--sessions] [--chat] [--chat-budget-usd N]` binds one loopback
`ThreadingHTTPServer` and builds one `Portal` per registered project, all sharing that server's
single token, host and port. `quenching/portal/serve.py`'s `Central.handle` checks `Host` and
`Origin` first, then:

- the page, its assets and the `?nonce=` trade go to a door `Portal` over no root, which never
  reaches a backend because every `/api/` path is answered before it;
- `GET /api/projects` (token required) returns, per project, `name`, `path`, `prefix`
  (`/p/<name percent-encoded>`) and `worktrees[{path, branch, main}]`, read from the git directory
  by `list_worktrees`, never through `git`;
- `/p/<name>/api/<route>` (token required) strips the prefix and hands the request, query string
  included, to that project's `Portal`, which applies every gate of its own; an unregistered name
  is a 404 `portal-unknown-project`, and a non-API path under a prefix is a 404.

`--read-only` reaches every project; `--sessions` gives each project's portal the session reader,
which keeps only the sessions inside **that** project's worktrees; `--chat` gives each project's
portal the chat, with `list_worktrees` (borrowed as `portal.worktrees`) as the list a question's
`worktree` must be in. Under `cq specs serve` that list is the root alone. The `Portal.lock` is per
project and `_STDIO_LOCK` is per process, so two projects never capture each other's verb output.
`SpecBackend.read_only` and `transport_read_only()` are process-wide and therefore hold for every
project at once. `cq specs serve` is unchanged: its `Portal` has no `/api/projects`, so the page
sees a 404 there and shows no project menu.

## Routes

GET: `/api/config`, `/api/specs`, `/api/specs/<id>`, `/api/search`, `/api/epics`, `/api/human`, `/api/schedule`; static assets
under `/`. With `--sessions` only, also `GET /api/sessions`; without the flag it is a 404
(`sp-portal-not-found`) like any unknown route, and `/api/config` reports `sessions: false`. POST: `/api/capture`, `/api/section`, `/api/approve`, `/api/reorder`,
`/api/discovery`, each delegating to the CLI's own verb so CAS and refusals are the terminal's.

- `GET /api/schedule` answers `{ok, fetchedAt, cycle, nodes, criticalPath}` as `cq specs schedule`
  derives it over the snapshot, each node carrying the portal's `stage`; the Gantt page (`#/gantt`)
  only draws it, as SVG built with `createElementNS`, and recomputes no date. It is read-only:
  write-back from the Gantt (dates, dependencies) needs new POST routes and awaits a human decision.
- With `--chat` only: `POST /api/chat` (`{question, worktree?}`) answers `202 {job, worktree}`,
  and `GET /api/chat/<job>?after=<n>` answers `{status, events[n:], next, costUsd, error}`, where
  `status` is `running`, `done`, `failed` or `timeout`. Without the flag both are a 404 and
  `/api/config` reports `chat: false` (`chatBudgetUsd` carries the ceiling when it is on). The
  POST goes through the token, `Origin`, `application/json` and `MAX_BODY` gates but not through
  `writes_enabled`: it writes nothing to the store, so `--read-only` does not turn it off; `--chat`
  is what turns it on. A `question` is a non-empty string of at most 4000 characters (else `400
  sp-portal-bad-input`); a `worktree`, compared by `realpath`, must be one of the project's
  worktrees, and an absent one means the root (else `400 sp-portal-chat-worktree`); one job at a
  time per project (`409 sp-portal-chat-busy`); an unknown job is `404 sp-portal-chat-unknown-job`.
  The page polls every 1.5 s; there is no streaming and no WebSocket.
- Under `cq portal serve` only: `GET /api/projects`, and every route above under
  `/p/<project>/` (§Central server).
- No new POST route enters without a human decision; `/api/chat` is the one epic 1810 decided. Reading more is a GET over the same store.
- A GET request starts no process beyond the read the store backend already makes (on the git backend, `git` reading the `quenching` branch), and never calls `gh`.
- A POST request writes to the store through the CLI's own verb. On the git backend a write lands in the clone's local pending commit and reaches the remote only at the next sync point; a capture is one, so `/api/capture` pushes, and the other routes stay local until a code push, a PR, `cq specs push` or the next capture. Every write route goes through the backend's write path, and with a card provider configured (`card: {provider: github}`) that path reaches `gh`: it creates the card on capture (`cmd_new` → `resolve_card_client`) and, through `_card_transitions` in the git backend at the sync, updates it when the `lifecycle_key` changed between the remote tip and the pushed commit (title, board state, phase, labels or tags). Which routes trigger it follows from that mechanism, not from a list. This describes what exists; it grants nothing new.
- The portal's reads see the clone's pending writes: the backend's one-second tip memo holds the pending ref beside the remote tip, so a write made by another process of the clone is read once that memo and the portal's own snapshot TTL expire.
- `GET /api/specs` rows carry `run`: the spec's `run` record (`state`, `verifier`, `date`), rebuilt field by field, or null. The `quenching:spec-runner` writes it through `cq specs record` at the end of its step (spec 1774, decision A: the orchestrator holds no write grant); `NOTE` and `TOKENS` never reach the store or the page. The card shows it as a chip and the drawer's records timeline lists it. It is a read of the same store: no route, no process.
- Static assets are read-only: any non-GET/HEAD method on them is a 405.
- `GET /api/sessions` returns `generatedAt`, `windowMinutes` and, per session, exactly
  `sessionId`, `cwd`, `worktree` (`{path, branch, main}` or null), `state`, `status`,
  `statusSince`, `lastEvent`, `pendingQuestion` (the question texts of an unanswered
  `AskUserQuestion`, or `plan` for `ExitPlanMode`), `subagents[{agentType, start, end, active}]`
  and `activity` (60 per-minute counts). Every row is rebuilt field by field, so a field Claude
  Code adds tomorrow never reaches the page. It starts no process: the liveness check is a
  signal 0, and worktrees are read from the git directory, not through `git`.

## Security guarantees

Kept as `portal.py` documents them in its docstring:

- Loopback only; a non-loopback `--host` is refused before a socket opens.
- A random per-run token on every `/api/` call and for the page itself (under `cq portal serve`,
  one token and one cookie for the whole server and every project behind it), carried by the `qtoken`
  cookie (`HttpOnly; SameSite=Strict; Path=/`) or the `X-Quenching-Token` header, and never
  accepted in a URL (`?token=` is refused). The URL the portal prints and `--open` hands to the
  browser holds only a random one-use nonce: `GET /?nonce=` trades it once for the cookie with a
  303 to `/`, and a used or wrong nonce is a 401. The token never reaches the argv, the history
  or `app.js`.
- `Host` must name the bound loopback address; `Origin`, when sent, must be this server, and
  every POST must send it (a POST without `Origin` is refused with `sp-portal-bad-origin`).
- Writes need `application/json`, are bounded by `MAX_BODY`, and are refused server-side under
  `--read-only` or a read-only backend.
- A refusal or conflict is an HTTP error carrying the CLI's `code`, never a success.
- The chat child runs a fixed argv (`quenching.specs.chat.chat_argv`): `claude -p --model sonnet
  --output-format stream-json --verbose --tools Read,Grep,Glob --strict-mcp-config
  --no-session-persistence --disable-slash-commands --permission-mode dontAsk --setting-sources
  project --max-budget-usd <ceiling> --settings <deny file>`. The question enters through stdin,
  never the argv. Any tool beyond `Read`/`Grep`/`Glob` (Bash, writes, web, MCP, sub-agents) is
  outside what epic 1810 authorized.
- The deny file is a temporary `0600` file, deleted when the job ends, carrying `disableAllHooks:
  true` and `permissions.deny` of `Read(~/.ssh/**)`, `Read(~/.config/**)`, `Read(**/*.key)` and
  `Read(**/.env)`; Claude Code applies `Read` rules to `Grep` and `Glob` as well, so no separate
  rule is written for them.
- The ceiling is `--chat-budget-usd` (default `0.50`), passed as `--max-budget-usd`; a value ≤ 0 is
  refused before a socket opens (`sp-portal-chat-budget`), and so is `--chat` without `claude` on
  `PATH` (`sp-portal-chat-unavailable`). A fixed `CHAT_TIMEOUT_SECONDS = 300` kills the process and
  ends the job as `timeout`.
- What a poll exposes is rebuilt field by field from each `stream-json` line: the assistant's text,
  the **name** of each tool used, and from the final `result` its text, `costUsd` and `isError`.
  Never a `tool_result`, never a tool `input`, never the raw line; a line that is not JSON is
  dropped. A job keeps at most 500 events and 200 000 characters, and a portal keeps the 20 most
  recent jobs in memory only; nothing persists across restarts.

Static assets carry this CSP: `default-src 'none'; script-src 'self'; style-src 'self';
connect-src 'self'; img-src 'self' data:; base-uri 'none'; form-action 'none'; frame-ancestors
'none'`, plus `no-store`, `nosniff` and `no-referrer`. No inline script or style, no CDN, no build.

## No innerHTML

`app.js` creates every node with `createElement` and `textContent`; spec text is never parsed as
markup. A change that introduces `innerHTML`, `insertAdjacentHTML` or `document.write` is refused.

## UX patterns

Accepted, taken as patterns from the cockpit of 2026-10-13 and never as code (it has no licence):
a hero counter of what waits for the human, state pills, a detail drawer, the count in the title
and favicon, and a notice when the data changes. Browser notification is opt-in by the human,
off by default, and uses no Claude permission, so it is not a grant.

## Regeneration

Every change to `portal.py` or `assets/portal/**` regenerates the `quenching-specs-reader` copy
(`python3 scripts/generate_plugin_modules.py --write`) and the Codex mirror
(`python3 scripts/sync_codex_plugin.py --source plugins/quenching --target plugins/codex/quenching-codex --write`),
and passes `bash scripts/verify_repo.sh`; see [specs-reader-plugin.md](specs-reader-plugin.md).

<!-- rationale -->
The portal is the one surface that both reads the store and writes it from a browser. Its
protection is the sum of the guarantees above, so a widening of any one (a route, a read source, a
grant, an inline script) is a security decision, not a UI detail. Fixing the limits in a document
gives each later change something to be checked against instead of deciding scope on its own.
