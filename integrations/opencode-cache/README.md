# quenching-cache for OpenCode

The prompt-cache band of [`quenching-cache`](../claude-cache/README.md), for OpenCode: how long the
cache stays warm, what the next message costs, and what to do about it, in the language the
repository declares. Derived from [cache-maxxing](https://github.com/5m0k3/cache-maxxing) by 5m0k3
(MIT); what changed is in [NOTICE.md](NOTICE.md) and both copyrights are in [LICENSE](LICENSE).

```
🟢 48 min restantes · próxima mensagem ≈ $0.01 · 50K / 1M · ✅ Pode seguir
🔴 cache expirado · próxima mensagem ≈ $2.32 (40× mais) · 290K / 1M · 🔄 Faça um handoff e economize 232K tokens | $2.21
```

## Surfaces

| Surface | What it shows |
| --- | --- |
| OpenCode Desktop | a `ComposerPill` above the composer: light, text, and menu rows for **handoff**, **stats** and **hide**; sending on a 🔴 chat warns once |
| OpenCode TUI | the same band in the composer's top slot |

Provider with **implicit** caching (OpenAI, Gemini, gateways with no breakpoints): a reduced band,
size and next-message cost only, with no countdown and no expiry light.

## What it reaches

`cq` by fixed argv and no shell, at most two at a time (found as the vitrine does: the project's
`.agents/quenching/bin/cq`, the plugin checkout's, then `PATH`): `config show --effective`,
`specs handoff facts|write` and `components session cache --harness opencode --usd`. The only network
is the one Haiku call a handoff makes, through `ctx.experimental.generate.text`. It stores, per chat,
the time of the last reply, the chat's size and model, never its text.

## The shared core

`src/core/` is generated from `../claude-cache/hooks/` by `scripts/cache_plugin_sync.py --write`;
never edit it by hand. The gate runs `--check`.

## Develop

```
npm ci
npm run build   # tsc + vite build → dist/gui-experimental.cjs (commit it)
npm test        # the tracker and handoff checks, no OpenCode needed
npm run bench   # load against a fake host
```

The bundled GUI is built by `vite` and committed as `dist/`, like the vitrine's.
