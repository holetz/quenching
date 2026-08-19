# Provider-owned specs conformance

This reference defines the checks for the specs front after the repository store was retired.
GitHub issues and Azure Boards work items are the source of truth; `cq specs` is the uniform
surface that reads and writes them.

## Provider configuration

The target's `.agents/quenching.json` may refine provider placement and project conventions. The
provider itself is derived from the repository remote and cannot be silently switched by a
command. A legacy repository-store value is refused with an actionable finding.

Provider-specific configuration is validated before any write:

- GitHub requires a resolvable repository and the configured issue transport.
- Azure Boards requires the state mapping and placement needed to create a work item.
- An unknown provider refuses; it never falls back to another transport.

The configuration details and defaults live in
[plugin-configuration.md](plugin-configuration.md).

## Probes

Run the provider checks before reading or changing a spec:

```bash
cq specs doctor --json
cq specs config --json
cq specs validate --json
```

Exit `0` means the provider and fetched front are conformant. Exit `1` reports findings that a
human or the owning lifecycle command must resolve. Exit `2` is a refusal: authentication,
provider selection, or required configuration is missing or invalid.

## Lifecycle ownership

`quenching-specs-create`, `quenching-specs-develop`, `quenching-specs-execute`,
`quenching-specs-status`, `quenching-specs-triage`, and `quenching-specs-conclude` own the provider
lifecycle. There is no installer or migration step for a repository specs tree. A complete spec is
closed by `quenching-specs-conclude`, which records the outcome in the provider and distils durable
knowledge into the OKF bundle.

## Finding policy

Provider findings name the provider, the missing configuration, and the command that owns the
repair. The checks must not invent a path, fabricate a phase, or offer a second repository store.
