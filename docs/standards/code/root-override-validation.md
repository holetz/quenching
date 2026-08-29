---
type: standard
title: Specs commands must not accept a repository-root override
description: Specs are provider-owned, so a root override cannot redirect them to a repository store; provider selection comes from the repository remote, unsupported legacy root settings refuse, and diagnostics report the same configuration fact without inventing a local tree
resource: plugins/quenching/assets/bin/quenching/specs/config.py, plugins/quenching/assets/bin/quenching/specs/backends/__init__.py, plugins/quenching/assets/bin/quenching/specs/commands/doctor.py
tags: [code, cli, validation, provider-selection, findings, refusals]
timestamp: 2026-08-19
audience: both
authority: current
source: remover-backend-local-do-plugin (task 4.3) — the repository-root validation contract was retired with the local specs store; provider configuration now owns selection and locator resolution
maintainer: quenching
---

# Specs commands must not accept a repository-root override

**Provider selection and repository paths are different facts.** Specs live in GitHub issues or
Azure Boards work items. The repository remote selects the provider, while the provider returns the
locator to show a human. No `--root`, `SPECS_ROOT`, or equivalent repository path may redirect a
spec command to a second store.

## The provider-selection predicate

The configuration layer answers one question: which supported provider does the repository remote
name? It must distinguish three cases:

- `github.com` selects GitHub and returns a GitHub issue locator.
- an Azure DevOps host selects Azure Boards and returns a work-item locator.
- an absent, malformed, or unknown host refuses with exit 2 and names the missing or unsupported
  provider.

An explicit legacy repository-store setting is the same refusal. It must never be treated as an
empty front, silently mapped to a provider, or used to create a directory.

## One refusal boundary, one diagnostic shape

Provider selection is resolved once at the backend-opening boundary used by every read and write.
The refusal carries a stable `sp-backend-unavailable`-style shape:

```python
{
    "code": "sp-backend-unavailable",
    "exit": 2,
    "provider": provider,
    "message": "...",
}
```

The message and remedy are built beside the predicate and reused by every caller. A second call
site must not compose its own wording, because the first divergence makes the same configuration
look like two different failures.

`doctor` is the exception to the exit behavior: it always completes its report. It emits the same
condition as a finding with the provider name and remedy, rather than refusing, so a health command
can show all configuration findings in one pass. Commands that read or write a spec refuse before
any provider operation.

## What is forbidden

The shared specs layer must not:

- search upward for a repository specs directory;
- derive a provider locator by joining a configured root to a filename;
- create, migrate, or validate a repository specs tree;
- treat an empty provider response as evidence that a repository path should be created.

The locator returned in JSON is display data. Consumers may show it, but must not compose a new
path from it or use it as a filesystem destination.

## The neighbouring surface rule

The components front has its own root contract (`SKILLS_ROOT`) and its own commands. A future
change to that front may reuse the general shape — one predicate, one refusal at the read/write
boundary, and a finding for a diagnostic — but must not copy the specs provider rule or make the
two fronts share a path resolver.
