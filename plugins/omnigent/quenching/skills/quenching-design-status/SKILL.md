---
name: quenching-design-status
description: "Report the /.design/ front: source validity, generated identity, genres and drift, read-only. Use for \"design status\", \"is DESIGN.md current\". Not for: fixes → quenching-design-align."
allowed-tools: "Bash(cq:*), Read, Grep, Glob, Bash(python3:*)"
---

<!-- GENERATED FROM plugins/quenching/commands/design/status.md -->

<!-- OMNIGENT RUNTIME START -->
## Omnigent runtime

This runs inside the `quenching` operator agent on whatever model the server's policy selects; it pins none and names no vendor CLI. The bundle carries no payload: read a reference through the `quenching` MCP server's resources (`quenching://references/<path>`), and prefer its tools (`<pillar>_<verb>`) to a shell `cq`, which resolves only where a local install sits under `$QUENCHING_OMNIGENT_ROOT`. Delegate only to the operator's declared sub-agents. Source model tiers and effort are not switches: a declared tier or effort below is a preference to report. Token usage comes from host telemetry when it exists, otherwise it is `not measured`. A tool the permission policy denies stays denied: report it, never route around it. If delegation is unavailable, report the limitation; never replace a required independent verification with self-review.

<!-- OMNIGENT RUNTIME END -->


# quenching-design-status — read the whole design front

**Input**: `$ARGUMENTS` (optional focus; omission reads the whole front).

The common front contract is in
[front-align/mold.md](quenching://references/front-align/mold.md), and the
design-specific disposition map is in
[design-align/bands.md](quenching://references/design-align/bands.md). This
read-only view preserves design's source arbitration, projection and optional-detector deltas.

Resolve `cq` per
[tool-resolution.md](quenching://references/align/tool-resolution.md)
§Resolving the tool, then run:

```bash
cq() { python3 "${QUENCHING_OMNIGENT_ROOT:-$HOME/.omnigent/quenching}/scripts/cq" "$@"; }
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
