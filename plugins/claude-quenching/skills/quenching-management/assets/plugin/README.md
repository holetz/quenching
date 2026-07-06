# assets/plugin/ — plugin rollout scaffold (org distribution channel)

The molds the method uses when the **`plugin` distribution channel** applies
(doctrine: [../../references/lifecycle.md](../../references/lifecycle.md) §4):
the profile signal is *several repos/teams need the same setup* (org,
platform team, monorepo family), and per-repo stamping would multiply drift
and manual hook wiring. Instead of stamping copies, the method **proposes
packaging the approved payload set as an internal plugin** distributed by an
org marketplace.

> **These are TEMPLATES, not an active plugin.** They live under `assets/`
> (inert, `*.template.json`) and only become live when the method assembles
> the org plugin **in the org's marketplace repo** — never in this package.

## What changes vs. the `stamp` channel

- **Hooks wire themselves.** A plugin ships `hooks/hooks.json` and the hooks
  register **with the plugin** — no per-repo `settings.json` merge (the
  merge-not-clobber procedure of
  [../../references/installation.md](../../references/installation.md) remains
  only for stamped installs). Script paths use **`${CLAUDE_PLUGIN_ROOT}`**
  (plugins are copied to a local cache when installed); state that must
  survive plugin updates goes in **`${CLAUDE_PLUGIN_DATA}`**.
- **Upgrades flow by version.** The plugin manifest carries `version`;
  consumers only receive updates when it changes — **bump it on every
  release**. Repos refresh with `/plugin marketplace update`.
- **Adoption is pre-configured per repo.** Each target repo commits
  `extraKnownMarketplaces` + `enabledPlugins` in its `.claude/settings.json`
  (snippet below): team members are prompted to install on folder trust.
- **Trade-off (why `stamp` stays the default):** plugin payloads are
  **canonical for every consumer** — no per-target renaming or per-repo
  adaptation. Choose this channel when uniformity across repos is worth more than
  per-repo fit.

## Assembly procedure (with OK, like any install)

1. **Select the approved payload set** — only what the target org confirmed in
   Steps 4-5 (hooks, the re-audit command-skill, worker agents, templates).
2. **Create the plugin** in the org's marketplace repo:
   `<plugin>/.claude-plugin/plugin.json` from
   [plugin.template.json](plugin.template.json); copy the payloads keeping the
   package layout (`skills/`, `agents/`, `hooks/`).
3. **Convert the wiring**: [hooks.template.json](hooks.template.json) is
   `settings.snippet.json` re-expressed for a plugin — commands point to
   `${CLAUDE_PLUGIN_ROOT}/hooks/<script>.py`. Drop it at `<plugin>/hooks/hooks.json`.
4. **List the plugin** in the marketplace's `.claude-plugin/marketplace.json`
   (entry: `name`, `source`, `description`, `version`).
5. **Pre-configure the targets**: merge
   [settings.marketplace.snippet.json](settings.marketplace.snippet.json) into
   each consuming repo's `.claude/settings.json` (with OK, item-by-item).
6. **Record in each target's install manifest** (`channel: "plugin"`, entry
   `version` = plugin version) so the reconcile scope reads both channels the
   same way ([../../references/lifecycle.md](../../references/lifecycle.md) §2).

## Files

| File | Mold for | Lands in |
| --- | --- | --- |
| `plugin.template.json` | the plugin manifest (`version` is the upgrade key) | `<org marketplace repo>/<plugin>/.claude-plugin/plugin.json` |
| `hooks.template.json` | auto-wired hook config (`${CLAUDE_PLUGIN_ROOT}` paths) | `<org marketplace repo>/<plugin>/hooks/hooks.json` |
| `settings.marketplace.snippet.json` | per-repo adoption (marketplace + enabled plugins) | merge into each target's `.claude/settings.json` |
