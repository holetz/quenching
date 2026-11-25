# Notice

`quenching-quota` derives from the Anthropic provider of **opencode-quota** by Shawn Kiser
(slkiser), published under the MIT License: <https://github.com/slkiser/opencode-quota>, imported
at upstream `6.3.0`, commit `7af4a67`. The upstream copyright and permission notice is kept in
[LICENSE](LICENSE). The idea of showing the subscription quota outside the model, the OAuth usage
endpoint and its `anthropic-beta` header, the window parser (`parseQuotaWindow`, `readWindow`,
`findUsageWindows`), the shared per-process reply and backoff, and the sanitized fixtures under
`tests/fixtures/` are upstream's work.

`nguyenngothuong/opencode-claude-quota` (MIT, Copyright (c) 2025 nguyenngothuong) was read only as a
reference for the reply's shape (`seven_day_sonnet`, `seven_day_opus`) and for the location of
OpenCode's `auth.json`; no code was copied from it.

This is a fork, not a mirror: it is not re-synced from upstream. An upstream improvement is
brought over by hand, as a change of this repository, and recorded below.

## What quenching changed

| Change | Why |
| --- | --- |
| Named `quenching-quota`, one command `/quenching-quota` instead of `/quota` and its tools | the `quenching-*` names; it can be installed beside upstream |
| Cut to Claude: every other provider, the multi-provider settings, the sidebar and the toasts are gone | the request is the Claude 5-hour and weekly windows, beside the `quenching-cache` band |
| No process but `cq`: the Claude CLI probe (`claude auth status`) and the macOS Keychain read (`security`) are gone | the plugin may open no shell; `cq config show --effective` by fixed argv is the only child process |
| The token is read from OpenCode's `auth.json`, then `~/.claude/.credentials.json` (or `$CLAUDE_CONFIG_DIR`), never from OpenCode's SQLite store, and never refreshed or written | read-only access to one credential; a refused or expired token asks the person to sign in again |
| One destination, `https://api.anthropic.com/api/oauth/usage`, with `redirect: "error"`, a 5 s timeout and a reply reused for at least 60 s | the network surface a security review can read in one file (`src/fetch.ts`) |
| Settings come from `shared.quota` through `cq config show --effective`; the band speaks the `Language:` of `AGENTS.md` | values the repository controls, in its layered configuration, and quenching's conversation-language contract |
| The band is `5h ▓▓░░ 35% ↻ 2h30 · semana ▓░░░ 17% ↻ qui 13h`, a `ComposerPill` on Desktop and the `prompt.footer.status` slot on the TUI | one line beside the cache band, coloured by `shared.quota` thresholds |
| Usage Credits and the Fable weekly window are not shown; Sonnet and Opus weeks go to the detail | the band carries the two windows that stop a session |
