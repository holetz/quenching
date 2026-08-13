# `standards/architecture/`

System structure (layers, modules, boundaries) and the current/active **architectural
patterns**. **`patterns` lives here** — there is no `/.knowledge/patterns/`; a design pattern is
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
| [bundle-root.md](bundle-root.md) | The OKF bundle lives at the fixed `/.knowledge/` root of the target repo and a files-backend specs workspace at the fixed `/.specs/` root — no configuration file names either, because an LLM executor runs command bodies literally and a root it must resolve from config is a root it can resolve wrong |
| [generated-listings.md](generated-listings.md) | A derived listing only pays for itself when a program can prove it is fresh — the decision criterion is whether a command already answers the same question on demand, the /.knowledge/ bundle index.md files are the counterexample that bounds the rule, and a convergence condition may name only what a checker decides |
| [install-profiles.md](install-profiles.md) | A profile declares which of the three fronts a repository uses, in `.claude/quenching.json` — it turns residency on and off (`disable-model-invocation: true`), never a command or a file, and the `/align` conductor runs the installed fronts in dependency order and names an uninstalled one in its report instead of failing on it |
| [plugin-layout.md](plugin-layout.md) | commands/** is the only tree Claude Code registers, so everything that is not an entry point lives under assets/ and is cited by absolute path |
| [read-only-views.md](read-only-views.md) | A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce |
| [root-migration.md](root-migration.md) | How a root the plugin itself declares changes name between releases — detected structurally, site by site, never gated on `okf_version`; resolved through exactly one route, `/quenching:knowledge:align` |
| [reference-loading.md](reference-loading.md) | Um corpo que precisa de uma seção de reference no passo N carrega essa seção no passo N, com a invocação literal e copiável de cq components read — uma citação de preâmbulo diz onde a regra mora e não faz a sessão abrir o arquivo, e o oposto foi medido acontecendo nos oito corpos /quenching:specs:* |
| [report-mold.md](report-mold.md) | A forma em que os comandos de uma frente imprimem seu relatório pertence a UMA seção citada por todos — três bandas fixas, um conjunto ordenado de colunas do qual cada comando toma um subconjunto, e um bloco de próximo passo executável como impresso — porque um formato reescrito em oito corpos envelhece em sete e nenhum checker vê |
| [retiring-a-reserved-artifact.md](retiring-a-reserved-artifact.md) | A reserved filename that is retired keeps its slot in RESERVED and its skip in the hard block; only its checker goes, because unreserving it silently converts every surviving file into a malformed concept doc — plus the one departure this house made knowingly, and the three things that made it payable |
| [shared-mold-keys.md](shared-mold-keys.md) | A frontmatter mold cited by several commands is a fill-in invitation, so a key only one writer may write stays out of it and lives with that writer's own contract — prevention where a deterministic check is not available |
| [spec-backend.md](spec-backend.md) | Where a repo's specs live is configurable, and the interface that makes every backend behave identically — five primitives over the canonical document rather than one method per CLI verb, a single shared derivation, the selected backend as sole source of truth, hybrid serialisation confined to each external implementation, and the in-memory fake that turns "identical" into a checked property |
| [type-follows-home.md](type-follows-home.md) | A home's name and a doc's `type:` are two spellings of the same fact — a home rename restamps every doc's `type:` in the same commit, never as a follow-up sweep, or the naming complaint recreates one level down in the bundle's most greppable field; proved by `renomear-docs-para-knowledge`, unchecked by any validator today |

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`layers` · `module-boundaries` · `patterns` · `dependency-direction` · `integration-points`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- _(none yet — fill on population)_
