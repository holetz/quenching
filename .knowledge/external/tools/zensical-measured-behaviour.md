---
type: external
title: Zensical measured behaviour
description: Measured facts about the Zensical static site generator — that it runs no MkDocs plugin at all, that its CLI has three commands and a build with no output flag, that a config resolves every path relative to the config file rather than the working directory, that `.cache/` ignores itself, which Material theme features survived and which one did not, and how publishing changed from a deploy subcommand to a Pages artifact
resource: plugins/quenching/assets/zensical/**, plugins/quenching/commands/knowledge/documentation/**, plugins/quenching/assets/references/knowledge-documentation/**
tags: [zensical, mkdocs, static-site-generator, documentation, tooling]
timestamp: 2026-08-27
audience: both
authority: current
source: 'spec 1003 (2026-08-27) — measured against `zensical 0.0.57` from PyPI, built repeatedly over this plugin''s own `documentation/` payload; the documentation read is the `github.com/zensical/docs` tarball at branch `master` on the same date'
maintainer: quenching
---

# Zensical measured behaviour

Facts about **how Zensical actually behaves**, measured by building this plugin's own
`documentation/` payload with it rather than read from a summary. External tool behaviour, not our
contract — how this plugin stamps and verifies the site layer is
`/quenching:knowledge:documentation:build` and its `knowledge-documentation/` references.

Zensical is written by the Material for MkDocs team and is where that team now ships. It reads
`mkdocs.yml` natively and states it always will, so an existing MkDocs project is not forced to
convert — but the compatibility stops at the file format.

## No MkDocs plugin runs — the whole `plugins:` list is inert

**Zensical runs no MkDocs plugin at all.** A `plugins:` list in a `mkdocs.yml` it reads is not
partially honoured or warned about; nothing in it executes. The project's own FAQ frames plugin
support as a future *module system* with no ETA, and a committed list of third-party plugins to be
covered by it.

The consequence that bites a migrating project is `awesome-pages`: **`.pages` sidecar files stop
shaping anything the moment the generator changes.** With no `nav` in the config, the sidebar falls
back to the folder tree — alphabetical order, titles derived from each page — so curated section
titles silently revert. The replacement is an explicit `nav` list in the config, and its cost is
that **a new page is a new line**: a page missing from the list is still built and still indexed
for search, it is only absent from the sidebar.

## The CLI is three commands, and `build` has no output flag

`zensical new`, `zensical build`, `zensical serve`. `build` accepts exactly `-f/--config-file`,
`--clean` and `--strict` — **there is no `--site-dir`**, so a build cannot be redirected per run
the way `mkdocs build --site-dir <throwaway>` could. The output goes to the configured `site_dir`.

There is also **no deploy subcommand**: `gh-deploy` has no equivalent. Publishing to GitHub Pages
is a workflow that runs `zensical build --clean` and hands `site/` to `upload-pages-artifact` +
`deploy-pages`, which requires the repository's Pages source to be set to "GitHub Actions" — a
setting outside the tree that no command can change on the human's behalf.

`zensical serve` is preview only; the project states plainly that it is not for production.

## A config resolves its paths relative to itself, not to the working directory

**Measured, and it is the trap in any throwaway-config scheme.** Running
`zensical build -f /somewhere/else/probe.toml` from inside the repository does *not* resolve
`docs_dir` against the working directory — it resolves it against the config file's own location,
and the build exits:

```
Error: Docs directory does not exist: /somewhere/else/docs
```

So a throwaway config that must reach the repo's real `docs_dir` has to be written **at the repo
root**, with only its `site_dir` pointing elsewhere.

## `.cache/` ignores itself

The build writes a `.cache/` directory beside the config, and **puts a `.gitignore` containing `*`
inside it**. Nothing needs to be added to the repository's own `.gitignore` for it; only the built
`site/` does.

## Link validation is on by default, and `--strict` turns it into an abort

`invalid_links` and `invalid_link_anchors` are enabled without configuration, reported with the
offending line and a caret, and `--strict` aborts the build on any of them. The project documents
the other validation keys as deprecated in their current form.

Two consequences measured on real content: absolute links to a path outside `docs_dir` are reported
as `page does not exist` — the same payload built clean once six such links became plain prose —
and heading anchors are ASCII-folded, so a link written `#pré-requisitos` does not resolve to the
`id="pre-requisitos"` the heading actually generates.

## The theme carried over almost whole; search is the exception

Of the eleven theme features this plugin stamped for Material, **ten exist unchanged** —
`navigation.indexes`, `navigation.sections`, `navigation.footer`, `navigation.tracking`,
`navigation.top`, `toc.follow`, `content.code.copy`, `content.code.annotate`, `content.tabs.link`,
`search.highlight`. **`search.suggest` has no equivalent**: the search engine is a new
implementation, and its interface is **English-only for now** regardless of `theme.language`, which
localizes the rest of the theme normally.

The HTML structure is unchanged from Material in both theme variants (`modern`, the default, and
`classic`), so CSS written against the `--md-*` variables keeps working.

## Markdown is the same parser, with two spellings changed

Zensical uses the same Python-Markdown, so the extensions carry over. In `zensical.toml` the
`!!python/name:` YAML values become **plain strings**, and the emoji index moves namespace:
`zensical.extensions.emoji.twemoji` / `.to_svg` in place of `material.extensions.emoji.*`.

## Versioning: 0.0.x is deliberate and technical

The project states the 0.0.x line is about its own API churn, not readiness, with a beta announced
and no 1.0 ETA — and commits to not breaking user-facing configuration or the CLI in the meantime.
Support for Material for MkDocs is committed for at least 12 months from Zensical's release on
2025-11-05. A pin here is therefore a floor at the version actually measured, not a ceiling
guessing at a numbering the authors say will change.
