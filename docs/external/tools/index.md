# `external/tools/`

Factual docs for **tools we use** (CLIs, platforms, services) — background, not our
contract. One tool concept per file (`type: external`); a tool's binary manual (PDF) is
consumed via a sidecar (`type: sidecar`).

**Boundary:** facts about an external tool — *how we use it* as a standard lives in
[standards/](../../standards/index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [claude-code-skill-command-mechanics.md](claude-code-skill-command-mechanics.md) | Measured facts about how Claude Code loads plugin commands vs skills — placeholder substitution, the Skill-tool registry, startup-time discovery, the unified frontmatter schema, and what disable-model-invocation actually closes |
| [azure-devops-cli-measured-behaviour.md](azure-devops-cli-measured-behaviour.md) | Measured facts about `az boards` / `az devops` and the Azure Boards work item as a store — the WIQL macro that resolves to an indistinguishable empty answer, the project name the field compares against, the column that rewrites the state, the two ceilings a description travels under, the marker form `System.Description` does not strip, the identity `--assigned-to` accepts, and the one resource with a batch form |
| [github-cli-measured-behaviour.md](github-cli-measured-behaviour.md) | Measured facts about `gh` and the GitHub REST API's issue endpoints — the REST create's silent handling of an invalid Issue Type versus the porcelain commands' loud refusal for the same name, where Issue Types are actually defined, why `closingIssuesReferences` stays empty for a PR that targets an integration branch, and the three shapes a `--paginate --slurp` listing can take (`[[]]` for a genuinely empty one, `[]` for zero pages, and no output at all) plus the free `issues.totalCount` that corroborates them |
| [zensical-measured-behaviour.md](zensical-measured-behaviour.md) | Measured facts about the Zensical static site generator — that it runs no MkDocs plugin at all, that its CLI has three commands and a build with no output flag, that a config resolves every path relative to the config file rather than the working directory, that a dot-prefixed `docs_dir` silently builds an empty site and symlinks are no escape from it, that `site_dir` may not leave the project root, that `.cache/` ignores itself, which Material theme features survived and which one did not, and how publishing changed from a deploy subcommand to a Pages artifact |
