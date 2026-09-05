# `concepts/automation/` — understanding about this plugin's own tooling

* [cq components lint exits 0 with warning-severity findings still present](skills-lint-warning-exit-code.md) — the exit code alone never proves a warning-severity finding closed, and a single-file invocation re-roots the reported command path.
* [The structure already produced is the record](existing-structure-as-the-record.md) — reading a convention back from the artefacts it produced cannot drift; a parallel registry is a second source of truth that can disagree with the tree it describes.
* [Building with the tool being built](building-with-the-tool-being-built.md) — the `cq` that ticks the box is the one the task is editing: the window in which it cannot run makes two tasks inseparable, and ground that moves forces you to capture before you edit.
* [Normalized script pattern](normalized-script-pattern.md) — a stable outer vocabulary for project operations makes setup, checking, testing, and deployment discoverable without requiring contributors to learn each repository's internal layout.
* [Test layering separates location, reach and execution order](test-layering.md) — a test directory answers which layer owns a test, a derived marker answers how a runner selects it, a coverage ratchet preserves progress over a declared surface, and randomized collection exposes order dependence.
