---
type: concept
title: Normalized script pattern
description: A stable outer vocabulary for project operations makes setup, checking, testing, and deployment discoverable without requiring contributors to learn each repository's internal layout
resource: https://github.com/github/scripts-to-rule-them-all, https://clig.dev/, docs/standards/architecture/ops-front.md
tags: [automation, scripts, cli, conventions, routing]
timestamp: 2026-08-30
audience: both
authority: background
source: GitHub's Scripts To Rule Them All README and the Command Line Interface Guidelines at clig.dev, consulted 2026-08-30
maintainer: quenching
---

# Normalized script pattern

The [Scripts To Rule Them All](https://github.com/github/scripts-to-rule-them-all) pattern gives
projects a shared vocabulary for routine operations. The implementation can vary with the
language and framework; the useful invariant is that the outer names stay predictable. A
contributor who knows the pattern can enter an unfamiliar repository and try the expected command
without first learning how its packages are arranged.

The pattern is an interface, not a second implementation of the work. Each named entry point owns
one unit of orchestration and may call smaller operations in the project's domain packages. A
repository should have one declared router for that interface, even when it offers convenience
wrappers over the same router.

## The original names

GitHub's reference pattern describes these names and responsibilities:

| Name | Responsibility |
| --- | --- |
| `bootstrap` | Fulfil project dependencies: language packages, system packages, runtimes, or submodules. |
| `setup` | Put a freshly cloned project into its initial usable state; it may call `bootstrap`. |
| `update` | Bring a checked-out project up to date after a pull, including dependencies or migrations when needed. |
| `server` | Start the application and any supporting processes needed to run it locally. |
| `test` | Run the test suite and, where useful, fast linting or other checks before the slower tests. |
| `cibuild` | Prepare the continuous-integration environment and invoke the project's test path. |
| `console` | Open the application's interactive console for the requested environment. |

These names are a convention rather than a requirement to copy the reference scripts verbatim.
The project decides which operations its surface needs and keeps the meaning of each name stable.

## The normalized ops interface

The operations front uses the following six-name vocabulary for the common outer interface:

| Name | Responsibility |
| --- | --- |
| `bootstrap` | Install or otherwise fulfil the dependencies required by the repository's operations. |
| `setup` | Establish the initial local state after a clone or an intentional reset. |
| `update` | Refresh a working checkout after a change of revision, including dependency or data migrations when the project requires them. |
| `check` | Run fast, non-destructive checks that report whether the repository is in an acceptable state. |
| `test` | Run the test suite, normally including the checks that should fail early. |
| `deploy` | Perform the repository's deployment operation, subject to its explicit preview and arming rules. |

`check` and `test` are related but not interchangeable: `check` is the quick preflight, while
`test` is the suite that establishes behavioural confidence. `deploy` is the boundary at which an
operation can affect something outside the repository, so its interface must make preview and
intent explicit. The router can delegate any of these names to domain-specific packages; it must
not become a second home for their business logic.

## A composable command-line boundary

The [Command Line Interface Guidelines](https://clig.dev/) treat standard input, output, errors,
and exit codes as the interface between a command and the programs around it. The normalized
pattern applies the same discipline to repository operations:

- Put the primary result on `stdout`, including structured data intended for a pipe or a
  machine-readable mode.
- Put diagnostics, progress messages, and errors on `stderr`, so a pipeline receives data rather
  than incidental narration.
- Return zero on success and a non-zero code on failure. The operations contract makes that
  distinction typed: `0` means success, `1` means findings, and `2` means misuse of the interface.
  A caller can therefore distinguish a valid run that found work from an invocation it cannot
  interpret.
- In `--json` mode, keep `stdout` data-only; diagnostics remain on `stderr`. This lets a caller
  parse the result without stripping human-oriented text first.

These rules make the six names useful to both humans and automation. A contributor can run the
same entry point interactively, while CI or another script can compose it from its exit code and
its clean data stream.

## Three acceptable routers

The outer interface needs one canonical router. The project can choose the mechanism that fits its
ecosystem:

| Router | What it provides | What it requires |
| --- | --- | --- |
| Python `[project.scripts]` | An installed console command that dispatches into a Python module and can share the package's argument parsing and dependencies. | Packaging metadata, an installable project, and one dispatcher module kept as the canonical entry point. |
| `justfile` | Short, readable recipes with arguments and dependencies, useful for composing the named operations from shell commands or package tools. | The `just` runner and a declaration that the recipes are the repository's canonical router; wrappers must delegate rather than duplicate logic. |
| `Taskfile.yml` | Declarative tasks, dependencies, variables, and cross-platform orchestration for the named operations. | The Task runner and a declaration that this file is canonical; the task definitions still need one source of domain logic. |

The mechanisms are alternatives at the boundary, not three routers that must be installed
together. A convenience layer may call the chosen router, such as a `justfile` recipe invoking a
packaged console command, without creating a second canonical implementation. The repository's
declaration answers which entry point a contributor and an automated verifier should treat as the
source of truth.
