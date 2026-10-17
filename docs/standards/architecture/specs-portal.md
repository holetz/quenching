---
type: standard
title: The specs portal reads one store and widens nothing without a decision
description: The local spec portal (cq specs serve) reads only the specs store open_backend reads, exposes a fixed set of GET and POST routes, keeps its loopback, token, Host/Origin and CSP guarantees, builds every node with textContent, reuses cockpit UX patterns but never its code, and regenerates the reader copy and the Codex mirror with every change
resource: plugins/quenching/assets/bin/quenching/specs/portal.py, plugins/quenching/assets/portal/**, plugins/quenching/assets/bin/quenching/portal/**
tags: [architecture, portal, specs, security, ux]
timestamp: 2026-10-17
audience: both
authority: current
source: spec 1769 and the fixed owner decisions B-O1 to B-O4 of epic 1768; spec 1812 (epic 1810) for the sessions read
maintainer: quenching
---

# The specs portal reads one store and widens nothing without a decision

<!-- rules -->

`cq specs serve` is a local portal over the specs store. This standard is the contract any change
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
not even imported. The `quenching-specs-reader` copy does not carry the session package and
refuses `--sessions` (`sp-portal-sessions-unavailable`) before a socket opens.

## Project registry

The projects a portal shows are registered in `~/.config/quenching/projects.json`
(`{"schemaVersion": 1, "projects": [{"name", "path"}]}`, `path` the absolute main root of the
repository, never a worktree). Only `cq portal add`, `cq portal remove` and `cq portal list`
(`quenching/portal/`) write it, atomically; no server and no page writes it, and a portal reads it
only once a spec that declares that read has landed. The one-time `cq portal add --from-orca` opens
only orca's `profiles/*/orca-data.json` and keeps `repos[].path` and `repos[].displayName`; any other
field there, tokens and credentials included, is never read into the registry or printed, and a
second import is refused. Reading orca live is not part of this standard.

## Routes

GET: `/api/config`, `/api/specs`, `/api/specs/<id>`, `/api/search`, `/api/epics`, `/api/human`; static assets
under `/`. With `--sessions` only, also `GET /api/sessions`; without the flag it is a 404
(`sp-portal-not-found`) like any unknown route, and `/api/config` reports `sessions: false`. POST: `/api/capture`, `/api/section`, `/api/approve`, `/api/reorder`,
`/api/discovery`, each delegating to the CLI's own verb so CAS and refusals are the terminal's.

- No new POST route enters without a human decision. Reading more is a GET over the same store.
- A GET request starts no process beyond the read the store backend already makes (on the git backend, `git` reading the `quenching` branch), and never calls `gh`.
- A POST request writes to the store and pushes to git through the CLI's own verb. Every write route goes through the backend's write path, and with a card provider configured (`card: {provider: github}`) that path reaches `gh`: it creates the card on capture (`cmd_new` → `resolve_card_client`) and, through `_card_transitions` in the git backend, updates it when the `lifecycle_key` changes (title, board state, phase, labels or tags). Which routes trigger it follows from that mechanism, not from a list. This describes what exists; it grants nothing new.
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
- A random per-run token on every `/api/` call and for the page itself, carried by the `qtoken`
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
(`python3 scripts/sync_codex_plugin.py --source plugins/quenching --target plugins/quenching-codex --write`),
and passes `bash scripts/verify_repo.sh`; see [specs-reader-plugin.md](specs-reader-plugin.md).

<!-- rationale -->
The portal is the one surface that both reads the store and writes it from a browser. Its
protection is the sum of the guarantees above, so a widening of any one (a route, a read source, a
grant, an inline script) is a security decision, not a UI detail. Fixing the limits in a document
gives each later change something to be checked against instead of deciding scope on its own.
