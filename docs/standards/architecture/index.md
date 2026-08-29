# `standards/architecture/`

System structure (layers, modules, boundaries) and the current/active **architectural
patterns**. **`patterns` lives here** — there is no `/docs/patterns/`; a design pattern is
a doc in this home.

**Boundary:** the shape of the system (the structural *why*). Code conventions (imports,
lint, symbols) live in [../code/](../code/index.md). An agreed-but-unproven architectural
rule sits here as `authority: background` (no separate decisions home). One standard per file
(files, not sub-folders); each carries `type: standard` + a derived `resource:`; add each to
[../index.md](../index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [align-surface.md](align-surface.md) | The 1×5 align column that replaced the 2×4 matrix — one align per front carrying its content stages, the `git` pillar declared with no align because it ships no verifier a probe could run, the probe-before-inventory rule that makes a no-op align cost a couple of tool calls, the rule that no sweep records itself, and the conductor categories sharing the cycle-authorization contract — `/align` conducts the three local fronts, `/quenching:specs:cycle` the four stages of one spec, and the two fan-out entries N specs each; none reimplements what it conducts |
| [bundle-root.md](bundle-root.md) | The OKF bundle of a target repo lives at the fixed `/docs/` root and the design source at `/.design/` — neither root is configurable, because an LLM executor runs command bodies literally and a root it must resolve from configuration is a root it can resolve wrong |
| [design-front.md](design-front.md) | The single DTCG source, its portable and editorial projections, explicit arbitration with Impeccable, and the boundary between web and non-web drift |
| [generated-listings.md](generated-listings.md) | A listing regenerated from disk is a second source of a fact something else already derives, so it earns its keep only where nothing else derives that fact and a checker can decide freshness; the decision criterion is whether a command already answers the same question on demand, the /docs/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides |
| [install-profiles.md](install-profiles.md) | A profile declares which of the four fronts (plus the `git` pillar) a repository uses, in `.claude/quenching.json` — what it turns on and off is the residency of a front's command descriptions (`disable-model-invocation: true`), never a command or a file; the `/align` conductor runs the installed local fronts in dependency order and names an uninstalled one in its report instead of failing on it, and `git` carries no conductor to skip at all, only its own residency toggle |
| [plugin-layout.md](plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [read-only-views.md](read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [root-migration.md](root-migration.md) | When a plugin release renames a root it itself declares — the bundle root moved from `/.docs/` to `/docs/` once — the migration is detected site by site from what sits on disk, never gated on a version bump, and resolved through exactly one route, `/quenching:knowledge:align` |
| [reference-loading.md](reference-loading.md) | A body that needs a reference section at step N loads that section at step N, with the literal, copy-pasteable cq components read invocation — a preamble citation says where the rule lives and does not make the session open the file, and the opposite was measured happening across the eight /quenching:specs:* bodies |
| [report-mold.md](report-mold.md) | The shape a front's commands print their report in belongs to ONE section every one of them cites — three fixed bands, an ordered set of columns each command takes a subset of, and every column naming a command executable as printed — and a block whose cells come from a payload is rendered by the TOOL, with the body quoting the output, because a format rewritten in eight bodies goes stale in seven, a table rewritten in three renderers diverges in all three, and no checker sees either |
| [retiring-a-reserved-artifact.md](retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc — plus the one departure this house made knowingly, and the three things that made it payable |
| [shared-mold-keys.md](shared-mold-keys.md) | A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may legitimately set stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available |
| [spec-backend.md](spec-backend.md) | Provider-owned GitHub and Azure Boards specs share five document primitives, one native-ID identity and one refusal boundary; external serialisation may use native fields only when it reassembles the canonical document, while locators, lean listings, placement, and the memory fake keep every consumer on the same contract, a direct read by native ID that reuses an in-process listing rather than paying a request per spec |
| [type-follows-home.md](type-follows-home.md) | Every home in the canonical tree owns exactly one `type:` value (`standards/` → `standard`, `concepts/` → `concept`, and so on) — a home that renames without restamping every doc's `type:` recreates the naming complaint one level down, in the most greppable field of the bundle, and nothing today checks for the mismatch |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`layers` · `module-boundaries` · `patterns` · `dependency-direction` · `integration-points`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
