---
type: tutorial
title: First workflow study
description: Reproduce one disposable Quenching workflow and inspect what its deterministic evidence does and does not prove.
resource: plugins/quenching/README.md
tags:
  - tutorial
  - experiment
  - reproducibility
timestamp: 2026-09-05
audience: human
authority: current
source: experiments/first-workflow/README.md and experiments/first-workflow/run.sh
maintainer: Israel Holetz
---

# First workflow study

*Audience: implementer · ~5 min · disposable target required*

This is the smallest executable study in the repository. It does not install a host integration
or modify this checkout: the runner copies a tiny knowledge bundle into a temporary directory,
seeds one stale generated projection, and demonstrates the explicit check/write/check loop.

!!! warning "Evidence boundary"
    The run proves deterministic CLI behavior and cleanup. It does not prove that an assistant
    will follow the workflow, that a host integration has identical behavior, or that a command
    declared read-only is a security sandbox.

## Prerequisites

- Bash and Python 3.11 or newer.
- A clean checkout of this repository.
- No Claude Code or Codex session is required for the deterministic run.

## Run it

From the repository root:

```bash
bash experiments/first-workflow/run.sh
```

The runner creates its target under `${TMPDIR:-/tmp}`, prints the path while it runs, and removes
it on success. It exits non-zero if any expected checkpoint differs.

## Expected checkpoints

1. `cq knowledge status` returns successfully and leaves the temporary bundle byte-for-byte
   unchanged.
2. `cq knowledge project --check` finds the deliberately stale glossary abbreviation projection
   and returns the findings exit code.
3. `cq knowledge project --write` regenerates that one projection.
4. A second `project --check` and `cq knowledge validate` both return successfully.

The generated file is the only expected change. The runner removes the temporary target after the
last check; the repository checkout remains untouched.

## What this teaches

The workflow has two separate rails: a read-only observation/check rail and an explicit write rail.
That separation is useful evidence for reproducible documentation workflows. It is not a claim
about every action a model could take in a shell with Python available. For the host-specific
Codex loading model, see the [official skills documentation](https://learn.chatgpt.com/docs/build-skills)
and the generated `plugins/quenching-codex/README.md` in the repository checkout.

For the fixture's exact files, checkpoints, and cleanup contract, read
`experiments/first-workflow/README.md` from the repository checkout.
