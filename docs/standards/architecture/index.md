# `standards/architecture/`

System structure (layers, modules, boundaries) and the current/active **architectural
patterns**. **`patterns` lives here** — there is no `docs/patterns/`; a design pattern is
a doc in this home.

**Boundary:** the shape of the system (the structural *why*). Code conventions (imports,
lint, symbols) live in [../code/](../code/index.md). An agreed-but-unproven architectural
rule sits here as `authority: background` (no separate decisions home). One standard per file
(files, not sub-folders); each carries `type: standard` + a derived `resource:`; add each to
[../index.md](../index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [align-surface.md](align-surface.md) | The 1×4 align column that replaced the 2×4 matrix — one align per front carrying its content stages, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, and the rule that no sweep records itself: an align's account of its own run goes in the report, never into the bundle |
| [plugin-layout.md](plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [read-only-views.md](read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [retiring-a-reserved-artifact.md](retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`layers` · `module-boundaries` · `patterns` · `dependency-direction` · `integration-points`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
