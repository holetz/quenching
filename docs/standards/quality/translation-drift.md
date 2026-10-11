---
type: standard
title: Translation drift is a finding
description: Translation divergence is a named, repairable finding with exit 1; refusal remains exit 2 and neither result is a silent success
resource: plugins/quenching/assets/bin/quenching/components/commands/translate.py, plugins/quenching/commands/components/align.md
tags: [quality, translation, drift, ci, findings]
timestamp: 2026-10-11
audience: both
authority: background
source: alinhar-plugin-a-agents-md spec, tasks 3.1–3.4 (2026-08-18)
maintainer: quenching
---

# Translation drift is a finding

<!-- rules -->

`cq components translate --check --json` exits 0 when the generated Codex surface matches its
Claude source. Each divergent path is a `ct-translation-drift` finding with severity `error`; the
command exits 1 after producing that complete payload. Exit 1 means the check ran and found a
repairable difference, not that translation was unable to run.

A repository with no generated Codex surface at all — no `.agents/`, or no generated plugin
target — has nothing to drift from: `--check` exits 0 with `reconciliation: "absent"` and no
findings. A Codex surface that exists without its `.generated-files.json` still reports drift; only
total absence is the opt-out, and `--write` creates the surface.

A caller that wants to reconcile the generated copy runs `cq components translate --write` and
then checks again. `/quenching:components:align` reports the same findings; it does not write the
generated surface as a side effect of its taxonomy sweep. This repository retired its own Codex
mirror on 2026-10-11, so its gate no longer runs the check.

Exit 2 remains reserved for refusal, including an invalid translation input. Consumers must branch
on the exit code and JSON `findings`, never treat a nonzero result as one undifferentiated failure.
