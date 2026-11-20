# quenching-cache-maxxing

The **cache-maxxing** bar, by [5m0k3](https://github.com/5m0k3/cache-maxxing), shipped from
quenching's marketplace. Above the Claude Code prompt it shows how many minutes are left on Claude's
prompt cache, what the next message costs, and one tip:

```
🟢 48 min left · next message ≈ $0.01 · 50K / 1M · ✅ Keep going
🔴 cache expired · next message ≈ $2.32 (40× more) · 290K / 1M · 🔄 Try /cmaxx-handoff to save 232K tokens | $2.21
```

It is a vendored copy, kept faithful to upstream: what changed and why is in [NOTICE.md](NOTICE.md),
and the upstream [README](https://github.com/5m0k3/cache-maxxing#readme) is the manual for the bar's
rules, settings and limitations. Licensed MIT, © 2026 5m0k3 — see [LICENSE](LICENSE).

## Commands

| Command | What it does |
| --- | --- |
| `/cmaxx` | Hide or show the bar in this chat (the **✕** on the bar hides it too). |
| `/cmaxx-handoff` | Haiku writes a brief of this chat under `.claude/handoffs/` (self-ignored by git) and a fresh chat picks up from it; the expired chat is never resent to the main model. |
| `/cmaxx-stats` | Savings, cache hit rate, rebuilds and replies, for this chat and all chats. |
| `/cmaxx-update` | Checks this marketplace for a newer version and refreshes the price list from upstream. |

## What it reaches

The bar runs locally from numbers Claude Code already tracks and calls no model. Two commands
reach outside, only when you run them: `/cmaxx-handoff` sends Haiku an abbreviated copy of the
chat, and `/cmaxx-update` downloads this plugin's `plugin.json` from `holetz/quenching` and
`prices.json` from `5m0k3/cache-maxxing`, sending nothing. It stores, per chat, the time of the last
reply, its size and model (7 days) and the `/cmaxx-stats` counts — never the chat's text.

## Installation

```
/plugin install quenching-cache-maxxing --marketplace holetz/quenching
```

Do not install it beside upstream `cache-maxxing`: both register the same `/cmaxx*` commands.
It coexists with `quenching-hud`, which draws its own band above the prompt.

## Verification

```bash
claude plugin validate integrations/claude-cache-maxxing
claude plugin test integrations/claude-cache-maxxing
```
