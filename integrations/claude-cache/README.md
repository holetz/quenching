# quenching-cache

A band above the Claude Code prompt that says how long Claude's prompt cache stays warm, what the
next message costs and what to do about it, in the language the repository declares:

```
🟢 48 min restantes · próxima mensagem ≈ $0.01 · 50K / 1M · ✅ Pode seguir
🔴 cache expirado · próxima mensagem ≈ $2.32 (40× mais) · 290K / 1M · 🔄 Use /quenching-cache handoff e economize 232K tokens | $2.21
```

Derived from [cache-maxxing](https://github.com/5m0k3/cache-maxxing) by 5m0k3 (MIT); what changed
and why is in [NOTICE.md](NOTICE.md), and both copyrights are in [LICENSE](LICENSE).

## Command

| Command | What it does |
| --- | --- |
| `/quenching-cache` | Hide or show the bar in this chat (the **✕** hides it too). |
| `/quenching-cache handoff [focus]` | Haiku writes quenching's handoff from this chat, read locally; `cq specs handoff write` stores it beside the branch's spec and a fresh chat opens with the line that reads it. The expired chat is never resent to the main model. |
| `/quenching-cache stats` | Requests, cache hit rate, cache writes and list-price dollars, this chat and this project, from `cq components session cache --usd`. |

While the cache is warm, `/quenching-handoff` writes the same handoff with the main model.

## The lights

First rule that fits: no reply yet ⚪️; expired or reset and the rebuild costs more than
`shared.cache.rebuildLimitUsd` 🔴, with what a handoff saves; expired but cheap 🟠; under
`shared.cache.warnMinutes` left on the 1-hour cache 🟡; past `shared.contextBudgets.main` tokens 🟢
with a handoff suggestion; otherwise 🟢. Costs are estimates at list price, and a floor.

## Settings

The repository sets them, through quenching's configuration
(`.agents/quenching/bin/cq config set shared.cache.<key> <value> --layer project|local`):

| Key | Default | What it changes |
| --- | --- | --- |
| `shared.cache.rebuildLimitUsd` | `0.5` | above this rebuild cost an expired chat is 🔴 |
| `shared.cache.warnMinutes` | `15` | how early the 1-hour cache turns 🟡 |
| `shared.cache.ttlMinutes` | `auto` | `auto` follows each reply's cache write; `5` or `60` force it (machine scope) |
| `shared.cache.costStyle` | `dollars` | `times` shows "40× more" instead of dollars |
| `shared.contextBudgets.main` | `200000` | the long-chat line |

Without `cq` the bar runs on these defaults, in English unless the root harness declares
otherwise; `handoff` and `stats` need `cq`.

## What it reaches

It runs, by fixed argv and no shell, only the checkout's `.agents/quenching/bin/cq` (or `cq` on
`PATH`): `config show --effective`, `specs handoff facts|write` and `components session cache`. It
has no network of its own; `handoff` makes one Haiku call with an abbreviated copy of the chat (the
last 120 messages, long ones cut, tool output left out). It stores, per chat for 7 days, the time of
the last reply, the chat's size and model, never its text.

## Installation

```
/plugin install quenching-cache --marketplace holetz/quenching
```

It coexists with `quenching-hud`, which draws the spec band.

## Verification

```bash
python3 scripts/cache_plugin_sync.py --check
claude plugin validate integrations/claude-cache
claude plugin test integrations/claude-cache
```
