---
type: standard
title: The bundle root is the fixed `/.docs/` convention
description: The OKF bundle of a target repo lives at the fixed `/.docs/` root and a files-backend specs workspace at the fixed `/.specs/` root — no configuration file names either, because an LLM executor runs command bodies literally and a root it must resolve from configuration is a root it can resolve wrong
resource: /.docs/**, /.specs/**
tags: [architecture, bundle, okf, convention, config]
timestamp: 2026-08-06
audience: both
authority: current
source: docs-em-diretorio-customizado spec (task 1.4, 2026-08-06) — proved by the migration itself: the bundle and the workspace moved to the fixed roots and every shipped reader updated in the same branch
maintainer: quenching
---

# The bundle root is the fixed `/.docs/` convention

The one layout fact every quenching-managed repo shares, and the one that stopped being
configurable.

## Two fixed roots, and no config that names them

- **The OKF bundle** lives at `/.docs/` — at the root of the target repository, beside
  `.claude/`.
- **A files-backend specs workspace** lives at `/.specs/` — the plans and archive folders the
  `files` backend manages.

Both are **conventions, not settings**. Neither is named by `.claude/quenching.json`, which
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

Configuration bought nothing here. The bundle is the plugin's own installable front, not a
target's choice, so no target ever needs to point the plugin at it.

## What the fixed root makes possible

- **The bundle-aggregate `resource:`.** `resource: /.docs/**, /.specs/**` covers the whole
  bundle and the whole workspace in one glob — a string that only exists because the root is
  fixed ([bundle-verification.md](../quality/bundle-verification.md) §The `resource` glob-set
  format).
- **A checker with no root to load.** The hook validates the fixed root by construction; the
  key that used to say where the bundle lives is gone rather than relocated
  ([plugin-configuration.md](../workflows/plugin-configuration.md)).
- **The harness line cites it.** The root harness's one-line language declaration points at
  `/.docs/standards/agents/communication.md` — a citation that is the same string in every repo
  only because the root is fixed ([communication.md](../agents/communication.md)).

## Nothing else contradicts it

Three contracts were checked against this rule, and all three hold after the change:

- [plugin-configuration.md](../workflows/plugin-configuration.md) recognises **six** keys; the
  key that named the bundle root and the section that explained why a second tool read the file
  were removed together.
- [plugin-layout.md](plugin-layout.md) rests the checker's `hooks/` placement on the invocation
  rule alone — `_load_config` reads one file, and the root is not a value it loads.
- [bundle-verification.md](../quality/bundle-verification.md) §The `resource` glob-set format
  keeps its rules; only the aggregate example moves to the fixed root (`resource: /.docs/**`).
