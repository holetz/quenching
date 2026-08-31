---
type: standard
title: Ops front
description: The target repository's current operations surface — one normalized router, its entry-point contract, lifecycle and finding vocabulary, verified by the shipped cq ops route
resource: https://github.com/holetz/claude-quenching/issues/1043
tags: [architecture, ops, automation, scripts, contract]
timestamp: 2026-08-30
audience: both
authority: current
source: declare-the-ops-front spec 1043 (2026-08-30), grounded in GitHub's Scripts To Rule Them All pattern and the measured target repository; the shipped cq ops route and checks implement this contract
maintainer: quenching
---

# Ops front

The ops front is the operations surface a target repository converges toward. It gives routine
work a predictable outer interface while leaving domain logic in the packages that own it. The
front is both the contract for that surface and the shipped implementation boundary that checks
it.

## The canonical tree

An adopting repository declares one operations root, `scripts/` by default. The root holds the
normalized entry points and a generated registry; domain packages are grouped by domain, never by
the lifecycle action that happens to call them:

```text
scripts/
├── bootstrap
├── setup
├── update
├── check
├── test
├── deploy
├── registry.md       # generated entry-point inventory
├── <domain>/         # domain packages, not lifecycle folders
│   └── ...
└── _archive/         # entry points whose lifecycle has ended
    └── ...
```

The root may be declared elsewhere when the repository has a reason to do so, but the declaration
must be unambiguous. The generated registry names every reachable entry point, and `_archive/`
keeps retired entry points visible without presenting them as part of the active interface.

## Configuration home

The operations root and canonical router are declared together in the target repository's
`.claude/quenching.json`:

```json
{
  "opsRoot": "scripts",
  "router": "pyproject.toml"
}
```

`opsRoot` and `router` are paths relative to the repository root. Both declarations are required;
the ops tooling reads them through the shared configuration loader and refuses with
`op-config-missing` when either one is absent. It never guesses `scripts/` or chooses among
multiple router files.

## The generated registry

`registry.md` is the generated record of the operations inventory. The generator owns exactly the
block between these delimiters and preserves all text outside it:

```markdown
<!-- quenching-ops-registry-start -->
<!-- quenching-ops-registry-sha256 <64 lowercase hexadecimal digits> -->
...
<!-- quenching-ops-registry-end -->
```

The hash is SHA-256 over the UTF-8 bytes of the canonical JSON object containing `router` and
`entryPoints` from the inventory payload, serialized with sorted keys, compact separators, and no
trailing newline. Every path in that object is relative to the declared operations root, so the
digest is stable across checkouts. `op-registry-stale` compares this digest and the rows against a
fresh inventory; an absent registry is handled by `op-undocumented`, not by `op-registry-stale`.

Non-Python entry points remain registry rows with their path, invocation, and lifecycle. Their
`module` is `null`, their AST-derived fields are empty or false, and the verifier marks the AST
checks not applicable to them. The inventory does not execute or parse their contents.

## One router

An adopting repository declares **exactly one canonical router** for the normalized interface:

- a Python `[project.scripts]` console script;
- a `justfile`; or
- a `Taskfile.yml`.

The router maps the normalized names to the operations that implement them. A convenience wrapper
may call that router — for example, a `justfile` recipe may invoke an installed console command —
but a wrapper is not a second router and must not duplicate domain logic. The chosen declaration is
the source of truth for contributors, the generated registry, and the verifier.

## The entry-point contract

Every active entry point answers to the same seven rules. The `Kind` column is part of the contract:
it distinguishes what a verifier can decide from what the align can report but cannot prove without
running arbitrary target code.

| # | Rule | Kind |
| --- | --- | --- |
| 1 | Every entry point is reachable from the router and named by the generated registry. | checked |
| 2 | Root resolution, `sys.path`, and shared flags come from one bootstrap module. | checked |
| 3 | Exit codes are typed: `0` for success, `1` for findings, and `2` for misuse. | checked |
| 4 | Data goes to `stdout`, diagnostics to `stderr`, and `--json` puts only data on `stdout`. | checked |
| 5 | An entry point that writes outside the repository is preview-first, armed by an explicit flag, and never armed by editing its source. | checked |
| 6 | `--help` carries a usage example. The static description/epilog proxy is checked; the help text itself is prose for the align to report. | prose, with static proxy |
| 7 | Every entry point declares a lifecycle: `active` or `archived`. | checked |

The router is an outer interface, not a second home for implementation. Entry points may compose
domain packages, and the packages may be tested independently, but the normalized names and their
boundary behaviour remain stable.

## Disabled gates are findings

A verification call commented out inside an entry point is a finding, not a configuration. A
repository that wants a check off declares that state explicitly; it does not hide the call behind
`#`. The disabled call has no owner, date, or searchable declaration, so the verifier reports it as
`op-disabled-check`.

`op-disabled-check` is the only heuristic in this vocabulary and therefore ships at severity
`warn`; the other seven codes are structural checks and ship at `error`. The implementation knows
the measured inventory has 61 tracked modules (28 with a `__main__` block), but its target
false-positive rate is not available while the target's configuration blocks task 4.4. The `warn`
default is consequently provisional and makes no claim about a rate that was not measured. When
that measurement is available, any code firing on more than half the inventory must be re-derived
before it is retained as a contract check.

## Why a front and not a pillar

The distinction is owned by [`align-surface.md`](align-surface.md), §The aligned-front column and
§The seventh pillar has no align: a front is a tree this plugin can converge toward and probe, while
the `git` pillar answers live questions about a target repository. The operations surface qualifies
as a front because its tree, router, registry, lifecycle, and entry-point contract give a verifier a
decidable target. It therefore earns its own alignment stages; it is not merely another `cq` axis
that reports the current state of a repository.

## How `op-disabled-check` is detected

The verifier detects a disabled gate with Python's `tokenize` module alongside its AST pass. It
looks for a `COMMENT` token whose text, after the leading `#` is removed, parses as a Python call
expression, and whose indentation places it inside a function the AST has already identified as
part of the entry point's control flow. This pairing catches a call hidden from the AST without
mistaking an explanatory comment for a disabled check. The mechanism is published because the
finding must be reviewable, and it follows the measured target's existing `tokenize` plus AST
technique rather than relying on an unpublished heuristic.

## The shipped implementation

The bundled `cq ops` route implements this contract and keeps the operations surface measurable:

| Surface | Implementation |
| --- | --- |
| Axis and route | `cq ops` exposes `inventory`, `doctor`, `status`, and `registry` under one operations namespace. |
| Inventory | `cq ops inventory` reads the declared root, router, entry points, lifecycle and write-policy facts. |
| Verification | `cq ops doctor --json` runs the static checks and emits typed findings with the contract's exit codes. |
| Registry | `cq ops registry --check` proves freshness; `cq ops registry --write` regenerates only the owned registry block. |
| Reader view | `cq ops status` reports configuration, packages, lifecycle, findings by band and registry freshness without writing. |

The route, inventory model, registry generator and verifier live in the bundled `quenching.ops`
package. The align and status command bodies consume the same route and keep judgment findings in
the report; they do not create a second operations implementation.

## Finding vocabulary

The verifier and the align use these eight codes. Their names are stable so a target can fix a
finding without translating a private vocabulary invented by one implementation:

| Code | Meaning | Severity |
| --- | --- | --- |
| `op-undocumented` | An active entry point exists but is not named by the generated registry. | `error` |
| `op-registry-stale` | The generated registry does not match the entry points reachable from the router. | `error` |
| `op-adhoc-root` | An entry point resolves the repository root through an undeclared path calculation instead of the shared bootstrap module. | `error` |
| `op-untyped-exit` | An entry point returns an untyped or otherwise non-contractual exit status. | `error` |
| `op-unarmed-write` | An operation writes outside the repository without preview-first behaviour and an explicit arming flag. | `error` |
| `op-disabled-check` | A verification call is commented out inside an entry point's control flow. | `warn` |
| `op-orphan` | An entry point is present in the operations tree but is not reachable from the canonical router. | `error` |
| `op-no-router` | The repository has no single declared router for its normalized operations surface. | `error` |
