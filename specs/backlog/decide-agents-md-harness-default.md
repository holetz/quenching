---
type: task
title: Decide whether AGENTS.md becomes the default harness target
description: Deferred from the docs-verification-layer plan — AGENTS.md is now a Linux Foundation open spec with wide adoption, while the harness molds ship only claude-root.md and claude-subfolder.md
timestamp: 2026-07-25
tags: [docs, harness, templates]
---

# Decide whether AGENTS.md becomes the default harness target

`quenching-docs-harness` refactors both `CLAUDE.md` and `AGENTS.md`, but
`assets/templates/harness/` ships only `claude-root.md` and `claude-subfolder.md`. The default is
therefore Claude-specific, at a point where `AGENTS.md` has become a Linux Foundation open spec with
broad adoption across agent tools.

The question is whether the plugin should invert that default — shipping an `AGENTS.md` mold and
treating `CLAUDE.md` as the Claude-specific pointer to it — or keep the current shape and document
the reasoning.

**Deferred deliberately.** The `docs-verification-layer` proposal ruled it out of scope as
well-founded but independent: it blocks nothing in a verification plan, and it touches the harness
molds rather than the checker. It needs its own plan because the answer changes what every aligned
repo's harness looks like.
