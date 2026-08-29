---
type: standard
title: The bundle root is the fixed `/docs/` convention
description: The OKF bundle of a target repo lives at the fixed `/docs/` root and the design source at `/.design/` — neither root is configurable, because an LLM executor runs command bodies literally and a root it must resolve from configuration is a root it can resolve wrong
resource: /docs/**, /.design/**
tags: [architecture, bundle, okf, convention, config]
timestamp: 2026-08-29
audience: both
authority: current
source: docs-em-diretorio-customizado spec (task 1.4, 2026-08-06) — proved by the migration itself: the bundle moved to the fixed root and every shipped reader updated in the same branch; provider-owned specs have no repository root
maintainer: quenching
---

# The bundle root is the fixed `/docs/` convention

The one layout fact every quenching-managed repo shares, and the one that stopped being
configurable.

## One fixed root, and no config that names it

- **The OKF bundle** lives at `/docs/` — at the root of the target repository, beside
  `.claude/`.
- **The design source** lives at `/.design/` — at the same repository root, beside the OKF bundle;
  `/.design/tokens.json` is the only primitive source the design front writes.

The bundle root is a **convention, not a setting**. It is not named by `.claude/quenching.json`, which
recognises six keys and none of them is a path
([plugin-configuration.md](../workflows/plugin-configuration.md)); nor by the target's
`.claude/hooks/hooks-config.json`, which carries only the checker's behaviour knobs. The
validator's `_load_config` reads just that one file — the bundle root is a constant of the
checker, not a value it loads ([plugin-layout.md](plugin-layout.md)).

## Why a fixed root, and why it is never a config key

An LLM executor runs command bodies **literally**: a body that needs the bundle's location either
cites it as one fixed string or resolves it at runtime from a configuration file. The second path
costs a read, a parse and a propagation on every command that touches the bundle — and each of
those steps is a place to resolve the wrong value. A fixed root is one string everywhere: written
into every body that references it, greppable, and impossible to mis-resolve. This is the same
reason the command surface treats a path as an identity rather than a variable
([command-surface.md](../naming/command-surface.md)) — the path is the identity.

Configuration bought nothing here. The bundle and design roots are the plugin's own installable
fronts, not a target's choice, so no target ever needs to point the plugin at either one.

## What the fixed root makes possible

- **The bundle-aggregate `resource:`.** `resource: /docs/**` covers the whole bundle in one
  glob — a string that only exists because the root is fixed
  ([bundle-verification.md](../quality/bundle-verification.md) §The `resource` glob-set format).
- **A checker with no root to load.** The checker validates the fixed root by construction; the
  key that used to say where the bundle lives is gone rather than relocated
  ([plugin-configuration.md](../workflows/plugin-configuration.md)).
- **The harness line cites it.** The root harness's one-line language declaration points at
  `/docs/standards/agents/communication.md` — a citation that is the same string in every repo
  only because the root is fixed ([communication.md](../agents/communication.md)).

## The name is fixed, but the name is not the identity

`/docs/` is the commonest documentation folder name there is, so — unlike every earlier root —
a repository can hold one by accident. What identifies an OKF bundle is therefore its
**signature**, a root `index.md` declaring `okf_version`, never the folder's name. `cq knowledge
validate` answers a directory without that signature with a single `not-an-okf-bundle` ERROR and
withholds every per-file OKF verdict, so pointing the validator at an ordinary `docs/` reports one
finding about the tree rather than one per document.

This does not loosen the root: the location stays fixed and unconfigurable. It separates two
questions the dotted roots could conflate — *where does the bundle live* (fixed convention) and
*is there a bundle here at all* (the signature).

## Changing a fixed root — one route only

A fixed root is not immutable — it has changed **twice**: it was `/.docs/` until
`renomear-docs-para-knowledge` (2026-08-13) moved it to `/.knowledge/`, and it lost its dot on
2026-08-29 to become `/docs/`. The second move was not a naming preference: a dot-prefixed
directory cannot be a Zensical `docs_dir` — it builds zero pages and exits `0`, measured — so a
dotted root could never be the documentation site's own source
(`docs/external/tools/zensical-measured-behaviour.md`). **The only way this fixed root changes
between plugin releases** is the procedure in
[root-migration.md](root-migration.md) — detected structurally, site by site, never gated on
`okf_version`. Nothing else moves the root: not a config key (there is none to add), not a
convention drifting in prose, not a target improvising its own path.

## Nothing else contradicts it

Three contracts were checked against this rule, and all three hold after the change:

- [plugin-configuration.md](../workflows/plugin-configuration.md) recognises **six** keys; the
  key that named the bundle root and the section that explained why a second tool read the file
  were removed together.
- [plugin-layout.md](plugin-layout.md) rests `cq`'s placement in `bin/` on the invocation rule
  alone — `_load_config` reads one file, and the root is not a value it loads.
- [bundle-verification.md](../quality/bundle-verification.md) §The `resource` glob-set format
  keeps its rules; only the aggregate example moves to the fixed root (`resource: /docs/**`).
