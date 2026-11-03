---
type: standard
title: Translation drift is a finding
description: Translation divergence is a named, repairable finding with exit 1; refusal remains exit 2 and neither result is a silent success
resource: plugins/quenching/assets/bin/quenching/deploy/cli.py, plugins/quenching/assets/bin/quenching/components/commands/bridge.py, scripts/sync_omnigent_plugin.py, plugins/quenching/commands/components/align.md
tags: [quality, translation, drift, ci, findings]
timestamp: 2026-11-03
audience: both
authority: background
source: alinhar-plugin-a-agents-md spec, tasks 3.1–3.4 (2026-08-18); spec 2160 (install only by deploy)
maintainer: quenching
---

# Translation drift is a finding

<!-- rules -->

Every check of a translated surface answers on the same three exits. `cq deploy --check --json`
exits 0 when a target's deployed surface matches what the source would write, and 1 when it does
not, with each divergent path in `changes`; `cq components bridge --check` exits 1 on an edited
copy, a new source or an orphan; `scripts/sync_omnigent_plugin.py --check` exits 1 when the
Omnigent bundle differs from its source. Exit 1 means the check ran and found a repairable
difference, not that translation was unable to run.

A caller that wants to reconcile the generated copy runs the same command with `--write` and then
checks again. `/quenching-align:components:align` reports the same findings; it does not write the
generated surface as a side effect of its taxonomy sweep. This repository checks its Omnigent
bundle and its own deployed surface in `scripts/verify_repo.sh`.

Exit 2 remains reserved for refusal — files no manifest owns, an invalid source, a legacy layout
deploy will not write over. Consumers must branch on the exit code and the JSON payload, never
treat a nonzero result as one undifferentiated failure.
