# Notice

`quenching-cache` for OpenCode derives from **cache-maxxing** by 5m0k3, published under the MIT
License: <https://github.com/5m0k3/cache-maxxing>. It is the same derivative as the Claude Code
plugin in [`../claude-cache`](../claude-cache/NOTICE.md), and everything that notice credits to
upstream (the bar, its light rules, the cost and saving arithmetic, the TTL learning, the Haiku
handoff that never resends an expired chat) is upstream's work here too. The upstream copyright and
permission notice is kept in [LICENSE](LICENSE).

This is a fork, not a mirror; it is not re-synced from upstream.

## What this port changed

| Change | Why |
| --- | --- |
| `src/core/` is a generated copy of the Claude Code plugin's `hooks/` core (`logic`, `handoff`, `i18n`, `message`, `prices`), written by `scripts/cache_plugin_sync.py` with `.ts` import specifiers | one source of logic for two hosts; the gate refuses a stale copy |
| The host is OpenCode (`@opencode/plugin` 2.3.0): usage comes from `session.step.ended`, state lives in `ctx.storage`, the surface is a `ComposerPill` (Desktop) and a TUI slot | the Claude Code API the original used does not exist there |
| Prices can come from the host: a model the quenching table does not know is priced from the host's own cost rows (`hostPrice`) | OpenCode serves providers beyond Anthropic |
| A provider with implicit caching gets a reduced band: size and next-message cost, no countdown and no expiry light | there is no breakpoint whose lifetime could be counted |
| The cache lifetime is read per write from `native` (`ephemeral_5m` / `ephemeral_1h`) and falls back to `shared.cache.ttlMinutes` | the OpenCode route decides the TTL, not this plugin |
| The Haiku call goes through `ctx.experimental.generate.text`; the facts come from `cq specs handoff facts --session <OpenCode id>` | the same handoff, two doors, no model client of its own |
| After a handoff a new session is opened with `ctx.session.create` and sent the line that reads the handoff | OpenCode has no `/clear` plus a filled prompt box |
| The `cq` is found by the vitrine's rules (project, plugin checkout, `PATH`; Windows `.cmd`), run by fixed argv and no shell, two at a time | the OpenCode service must never wait on a hook |
| No network of its own beyond the one Haiku call | same contract as the Claude Code plugin |
