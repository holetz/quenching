# Notice

This plugin is a vendored copy of **cache-maxxing** by 5m0k3, published under the MIT License:
<https://github.com/5m0k3/cache-maxxing>, imported at upstream `0.5.0`, commit `6df848d`. The
upstream copyright and permission notice is kept unchanged in [LICENSE](LICENSE), and every
credit for the bar, its rules, the price table and `/cmaxx-handoff` belongs to the upstream author.

## What quenching changed

Only what installing it from quenching's marketplace requires; the behaviour is upstream's.

| Change | Where | Why |
| --- | --- | --- |
| plugin name `cache-maxxing` → `quenching-cache-maxxing`, and its state keys with it | `.claude-plugin/plugin.json`, `hooks/register.tsx`, `types/index.d.ts`, `tests/bar.test.tsx` | the marketplace names its plugins `quenching-*`, and the atoms' `plugin` must match the plugin's name |
| version moves in quenching's release lockstep, not upstream's | `.claude-plugin/plugin.json` | `cq specs release` bumps every marketplace plugin together ([versioning-release](../../docs/standards/ci-cd/versioning-release.md)) |
| `/cmaxx-update` reads the latest version from this repository and runs `claude plugin update quenching-cache-maxxing@quenching` | `hooks/register.tsx`, `tests/bar.test.tsx` | this copy installs from the `quenching` marketplace; the price list (`prices.json`) is still read from upstream, which maintains it |
| `network.hosts` declares `raw.githubusercontent.com` | `.claude-plugin/plugin.json` | the validator asks for the one host `/cmaxx-update` reads |
| not vendored: `prices.json`, `scripts/`, screenshots, icon, upstream CI and community files | — | the bundled price table lives in `hooks/logic.ts`; release and validation are quenching's gate |

## Syncing a new upstream release

Copy upstream's `hooks/`, `types/` and `tests/` over these, re-apply the table above, and run
`claude plugin validate` and `claude plugin test` on this folder. Update the commit above.
