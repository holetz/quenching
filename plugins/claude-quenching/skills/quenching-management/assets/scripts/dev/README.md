# scripts/dev — local tooling

**Local development** tools: run diagnostics, converters, REPL/notebook startup
helpers. Developer convenience, not part of the product.

**OUTSIDE lint/CI scope** (`scripts/dev/` in the linter's `exclude`) — that is what
distinguishes `dev/` from the other purposes: local tooling does not pass through
the product quality gate. A product script left here escapes the gate (wrong home).

> Replace/add the real modules and register each one in the map at
> [../README.md](../README.md). Remove this folder if the repo has no local tooling.
