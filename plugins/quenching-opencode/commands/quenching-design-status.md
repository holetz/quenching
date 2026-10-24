---
description: "Report the /.design/ front: source validity, generated identity, genres and drift, read-only. Use for \"design status\", \"is DESIGN.md current\". Not for: fixes → quenching-design-align."
---

<!-- GENERATED FROM plugins/quenching/commands/design/status.md -->

<!-- OPENCODE RUNTIME START -->
## OpenCode runtime

Delegate only through OpenCode's task tool, to the registered subagents named `quenching-<agent>` (protocol copies live under `~/.config/opencode/quenching/agents/`). Never launch the Claude CLI and never request a Claude model during an OpenCode run. Source model tiers are not pinned here: every command and subagent runs on the model the OpenCode session configures; a declared tier or effort below is a preference to report, not a switch. Token usage comes from host telemetry when it exists, otherwise it is `not measured`; `cq components session cost` and `context` read no OpenCode log and refuse (exit 2, unmeasured). If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OPENCODE RUNTIME END -->


# quenching-design-status — read the whole design front

**Input**: `$ARGUMENTS` (optional focus; omission reads the whole front).

The common front contract is in
[front-align/mold.md](~/.config/opencode/quenching/references/front-align/mold.md), and the
design-specific disposition map is in
[design-align/bands.md](~/.config/opencode/quenching/references/design-align/bands.md). This
read-only view preserves design's source arbitration, projection and optional-detector deltas.

Resolve `cq` per
[tool-resolution.md](~/.config/opencode/quenching/references/align/tool-resolution.md)
§Resolving the tool, then run:

```bash
cq() { python3 "${QUENCHING_OPENCODE_ROOT:-${XDG_CONFIG_HOME:-$HOME/.config}/opencode/quenching}/scripts/cq" "$@"; }
cq --root . design status --json
cq --root . design build --check --json
```

Read the source and named findings only as needed to explain them. Do not write, import, build,
render, install Impeccable, or reinterpret an external `DESIGN.md` as source.

Report one compact table:

| Band | Evidence |
| --- | --- |
| Source | DTCG schema/version, token count, external schema stamps |
| Product | PRODUCT schema 1 projection and its OKF source homes |
| Portable design | DESIGN.md byte identity and five projected groups |
| Sidecar | schema 2, extensions and canonical/editorial component counts |
| Editorial | genre list, declared media and MEDIUM.md identity |
| Internal adapters | CSS, Typst, Python and brand API identity |
| Residue | orphan assets, non-web literals, missing optional web detector |

Separate errors from warnings and name the exact closing command for each actionable finding.
Impeccable absence is a capability note, not a finding: this front emits a portable format even
when no consumer is installed.

**Done when:** every band has authoritative evidence or an explicit missing state, every finding
keeps its code, and the report states that nothing was written.

## Invariants

- Never repair while reporting status.
- Never call a missing optional detector healthy.
- Never infer round-trip fidelity beyond the five portable groups.
