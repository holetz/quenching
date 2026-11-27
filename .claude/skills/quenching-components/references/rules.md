---
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob
---

# /quenching-components rules — the rules for writing one piece, read-only

**Input**: `$ARGUMENTS` — one piece: `skill` (or `command`), `agent` (subagent), `hook`,
`entrypoint`, `layer` (test layer) or `genre`. Omitted → the request's own words pick it; a request
that fits two pieces is asked, never guessed.

This flow hands over the doctrine that already exists for the piece, so an agent reads it before
editing one by hand. It mints, edits and writes nothing, and it never copies the doctrine's text
into its answer: it reads the sections and names where they live.

Resolve `cq` per
[align/tool-resolution.md](.agents/quenching/references/align/tool-resolution.md)
§Resolving the tool.

## Workflow

### 1. Pick the piece
Map `$ARGUMENTS` to one row of the table below; no row fits → stop and ask which piece.

| Piece | Doctrine, read by section with `components_read(verb="read", path=…, sections=[…])` | Minting flow |
| --- | --- | --- |
| `skill` | `.agents/quenching/references/components-command-new/doctrine.md` (all `##` sections), `taxonomy.md` §The single axis, §Naming, §Placement — the path IS the identity | `command-new` |
| `agent` | `taxonomy.md` §Placement — the path IS the identity; `capabilities.md` §Subagents — when delegation pays, §Model and effort — pin only what is mechanical | `agent-new` |
| `hook` | `capabilities.md` §Hooks — the scope ladder and the handler ladder | `hook-new` |
| `entrypoint` | `.agents/quenching/references/ops-align/entrypoint-contract.md` §The seven rules, §The minting mold, §The disabled-gate rule | `entrypoint-new` |
| `layer` | `.agents/quenching/references/proof-align/layer-contract.md` §The four layer rules, §Minting one declared layer | `layer-new` |
| `genre` | the contract the flow fixes: `.agents/skills/quenching-components/references/genre-new.md` §2 (fields, register, destinations, guardrails) | `genre-new` |

**Done when:** exactly one piece is picked.

### 2. Read the doctrine by section
Run `components_read(verb="read", …)` on the row's paths with the named sections, never the whole
file. A path that does not exist in this target (the `ops-align` and `proof-align` contracts ship
with the `quenching-ops` and `quenching-proof` modules) is reported as *the module is not
installed here*, with the remedy `cq deploy --target . --write`; the other rows still answer.
**Done when:** every cited section of the row was read, or each missing one is named with its
module.

### 3. Add the target's delta
Read `docs/standards/automation/skills.md` when the target has it (`Glob` first); absent → say
the target declares no delta, and the doctrine above is the whole rule. Name what that file adds
or overrides for this piece; never restate the doctrine.
**Done when:** the delta is named, or its absence is stated.

### 4. Report
Give the piece, the sections read with their paths, the target's delta, and the minting flow that
creates one (`/quenching-components <flow>`). **Done when:** the report names the piece, its
sources and the next flow, and no file was written.

## Invariants

- Never write or edit a file: this flow only reads.
- Never copy a doctrine's text; cite the path and section.
