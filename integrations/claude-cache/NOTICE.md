# Notice

`quenching-cache` derives from **cache-maxxing** by 5m0k3, published under the MIT License:
<https://github.com/5m0k3/cache-maxxing>, first imported at upstream `0.5.0`, commit `6df848d`.
The upstream copyright and permission notice is kept in [LICENSE](LICENSE). The idea of the bar,
its light rules, the cost and saving arithmetic, the TTL learning, the first price table and the
Haiku handoff that never resends an expired chat are upstream's work.

This is a fork, not a mirror: it is not re-synced from upstream. An upstream improvement is
brought over by hand, as a change of this repository, and recorded below.

## What quenching changed

| Change | Why |
| --- | --- |
| Named `quenching-cache`, one command `/quenching-cache [toggle\|handoff [focus]\|stats]` instead of `/cmaxx`, `/cmaxx-handoff`, `/cmaxx-stats`, `/cmaxx-update` | the marketplace's `quenching-*` names and the repository's one-entry-with-flows commands; it can be installed beside upstream |
| The bar speaks the language the root harness declares (`Language:` in `AGENTS.md`) | quenching's conversation-language contract (`docs/standards/agents/communication.md`) |
| Settings come from `shared.cache` through `cq config show --effective`; a long chat is `shared.contextBudgets.main` | values the repository controls, in its layered configuration, instead of each user's plugin options |
| Prices are quenching's table, `quenching/assets/bin/quenching/session/pricing.json`, generated into `hooks/prices.ts` by `scripts/cache_plugin_sync.py` | one table for the bar and `cq components session cost\|cache --usd`; the gate refuses a stale copy |
| No network of its own: `/cmaxx-update`, the downloaded price list and the version check are gone | prices and versions move with quenching's release; the plugin reaches nothing outside the machine but Haiku, on a handoff |
| `/quenching-cache handoff` writes quenching's handoff: facts from `cq specs handoff facts`, Haiku on the shared template (`hooks/handoff-template.md`, generated), stored by `cq specs handoff write` beside its spec | one handoff with two doors: `/quenching-handoff` while the cache is warm, this one once it has expired |
| `/quenching-cache stats` reads `cq components session cache --usd` | the measurement quenching already has, for Claude Code and OpenCode alike, instead of a private counter store |
| Removed: the per-chat stats store and its 90-day retirement, the transcript fill-in, `.claude/handoffs/`, the dev-copy and release scripts, the icon and screenshots | each was replaced by a quenching mechanism above, or belongs to upstream's own distribution |
