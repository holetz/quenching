# Install & run

The first hands-on chapter of the Technical guide: get the plugin loaded, then see
what happens when you point it at a repo. For the full step-by-step, continue to the
[8-step workflow](workflow.md).

## Local (development)

Load the plugin straight from the repository:

```bash
claude --plugin-dir ./plugins/claude-quenching
```

Then trigger the method by describing the task — *"audit this repo's knowledge
base"*, *"prepare this repo for Claude Code"*, *"see what's missing from the
knowledge base"* — or invoke the skill by name:

```
/claude-quenching:quenching-management
```

Run `/help` to confirm that **only** `quenching-management` is listed as an active
skill. The bundled payloads under `assets/` are **not** auto-discovered as live
skills/hooks — they are inert installers. After editing the plugin, reload with
`/reload-plugins`.

## From the marketplace

This repository doubles as its own marketplace. Once you have access to it on
GitHub:

```
/plugin marketplace add israelholetz/claude-quenching
/plugin install claude-quenching@claude-quenching
```

Refresh later with `/plugin marketplace update claude-quenching`.

> While the repository is **private**, only accounts with read access (and an
> authenticated `gh`/git locally) can add the marketplace.

## What happens when it runs

The method **audits first** and **installs second, with confirmation**:

1. it derives your repo's shape and scores the 15 dimensions, then hands back a
   **prioritized gap report**;
2. for each gap with a ready payload, it proposes the package artifact and — only
   after your OK, item by item — installs it into your `.claude/`/`docs/`,
   adapting names/paths to your conventions;
3. where your repo already has an equivalent, it installs the package's single
   source and flags yours as **deprecable** (it never removes anything without an
   explicit OK).

See the [8-step workflow](workflow.md) for the full sequence and
[Bundled artifacts](artifacts.md) for what can be installed.
