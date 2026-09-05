# First workflow study fixture

This directory contains one deterministic, disposable experiment for the Quenching workflow
study. It uses the bundled stdlib `cq` directly, so it does not require Claude Code, Codex, a
marketplace installation, or a change to the repository checkout.

## What the runner does

`run.sh` performs these checkpoints in a temporary directory:

1. copies `sample/` into a temporary target;
2. appends one term to the canonical glossary, making its generated abbreviation snippet stale;
3. runs `cq knowledge status` and proves the status read leaves the bundle unchanged;
4. runs `cq knowledge project --check` and expects the findings exit code (`1`);
5. runs `cq knowledge project --write` to regenerate the snippet;
6. runs the projection check and bundle validator again, both expecting success (`0`);
7. removes the target on success, or retains it and prints its path on failure.

The temporary target is the only write scope. The runner records this repository's initial Git
status and requires the exact same status at the end, so pre-existing work is preserved while an
accidental checkout mutation remains visible.

## Evidence boundary

The experiment proves a deterministic check/write/check contract and the cleanup behavior of this
runner. It does not prove that an assistant will choose the read-only path, that Claude Code and
Codex behave identically, or that a command with no `Write`/`Edit` grant is a security sandbox while
shell or Python execution remains available.

## Run

From the repository root:

```bash
bash experiments/first-workflow/run.sh
```

The sample target is intentionally tiny: its `docs/` root contains only the OKF listing, the
canonical glossary, and the generated abbreviation snippet. The stale snippet is repaired by the
explicit `project --write` checkpoint rather than by a hidden hook.
