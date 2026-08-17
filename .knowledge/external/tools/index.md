# `external/tools/`

Factual docs for **tools we use** (CLIs, platforms, services) — background, not our
contract. One tool concept per file (`type: external`); a tool's binary manual (PDF) is
consumed via a sidecar (`type: sidecar`).

**Boundary:** facts about an external tool — *how we use it* as a standard lives in
[standards/](/.knowledge/standards/index.md).

## Current docs

| Doc | Covers |
| --- | --- |
| [claude-code-skill-command-mechanics.md](claude-code-skill-command-mechanics.md) | How Claude Code loads plugin commands vs skills — placeholder substitution, the Skill-tool registry, startup-time discovery, and the unified frontmatter schema |
| [azure-devops-cli-measured-behaviour.md](azure-devops-cli-measured-behaviour.md) | Measured facts about `az boards` / `az devops` and the Azure Boards work item as a store — the WIQL macro that answers indistinguishably empty, the column that rewrites the state, the two ceilings a description travels under, and the one resource with a batch form |
| [github-cli-measured-behaviour.md](github-cli-measured-behaviour.md) | Measured facts about `gh` and the GitHub REST issue endpoints — the REST create's silent handling of an invalid Issue Type versus the porcelain commands' loud refusal for the same name, where Issue Types are actually defined, and why `closingIssuesReferences` stays empty for a PR whose base is not the repository's default branch |
