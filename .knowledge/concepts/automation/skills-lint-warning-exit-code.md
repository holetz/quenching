---
type: concept
title: cq components lint exits 0 with warning-severity findings still present
description: cq components lint's exit code alone never proves a warning-severity finding closed, and a single-file invocation re-roots the command path — both need naming so a verify: written against this tool does not pass in silence
resource: plugins/quenching/assets/bin/quenching/components/commands/lint.py
tags: [automation, cq, components, lint, verification, gotcha]
timestamp: 2026-08-10
audience: both
authority: background
source: restore-routing-info-on-docs-commands — encountered writing that spec's per-task `verify:` blocks for eleven command descriptions; re-measured under `cq components lint` by modularizar-specs-knowledge-components task 9.4 — both traps still reproduce identically against the one-package tool
maintainer: quenching
---

Two traps sit under `cq components lint`, and both produce a `verify:` that reports green while
the thing it was meant to catch is still there.

## `lint` exits 0 on warning-severity findings

`lint`'s exit code reflects only `severity: error` findings. A finding of `severity: warn` —
`sk-trigger-position` and `sk-no-boundary` among them — leaves `"ok": true` and exit `0` even
though the finding is present in the JSON. Re-measured: `cq components lint
commands/knowledge/add.md --json` prints an `sk-step-criterion` warn finding and still exits `0`.

**Consequence.** A `verify:` step that checks only the exit code proves nothing about a
warning-severity code. The check has to parse `--json` and filter `findings` by `code` — the exit
code is not the signal for anything below `error`.

## A single-file invocation re-roots the reported path

Given one file, `lint` resolves its root to that file's own directory, so a finding for
`commands/knowledge/add.md` reports back as `"command": "/add", "path": "add.md"` — not
`/quenching:knowledge:add` and not the full repo-relative path. A filter written against the full
command path (`/quenching:knowledge:add`) matches nothing against that output, silently.

**Consequence.** Run `lint` against the **whole surface** (`cq --root . components lint --json`)
and filter the returned `findings` array by `path` (repo-relative) and `code`, rather than
invoking `lint` on one file and trusting its own idea of that file's path. Re-measured: under
`--root .` the same finding reports `"command": "/knowledge:add", "path":
"commands/knowledge/add.md"`.

## The combined check

```bash
cd plugins/quenching && python3 assets/bin/cq --root . components lint --json \
| python3 -c "import json,sys; P='commands/knowledge/add.md'; \
F=json.load(sys.stdin)['findings']; \
B=[f for f in F if f['path']==P and f['code'] in ('sk-trigger-position','sk-no-boundary')]; \
[print(f['code'], f['message']) for f in B]; sys.exit(1 if B else 0)"
```

Whole-surface lint, filtered by repo-relative path and code, exit code driven by the filter's own
result — not by `lint`'s.
