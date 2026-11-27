# /quenching-specs execute — step 5 i

Loaded only when this sub-step runs, together with the step 5 loop in [step-5-implement-tasks.md](.agents/skills/quenching-specs/references/specs-execute/step-5-implement-tasks.md); the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

i. **A red that is not this spec's has its own route, never a dismissal** — a failing gate, a broken
   test or drift found on the way, read per `/docs/standards/workflows/task-execution.md`
   §Pre-existing errors. **Diagnose, then prove it on the base**: reproduce it in the base worktree
   (`git worktree add --detach .quenching/red <base>`, removed before returning, per
   [execution.md](.agents/quenching/references/specs-execute/execution.md) §The validation loop); no
   reproduction → it is this spec's own and the validation loop applies. Reproduced, the four criteria
   hold together — cause diagnosed and reproduced on the base, few files and no contract changed, an
   existing verification proves it, no human decision — → **fix it in the spec**: append a task
   `[fix-preexistente] <title>` with its own `files:` (generated mirrors included) and a `verify:` that
   fails before and passes after, through `specs_write(verb="section_write", spec=<id>, heading="Tasks", body=<body>)`
   (the checked boxes and their `subject:` survive) then `specs_read(verb="validate")`, and
   run it through this loop. Any criterion failing → **capture it now**, while the context is warm:
   `specs_write(verb="create")` with `## Problem` and the diagnosis (cause, reproduction, files), and
   one `## Discoveries` line `promoted: <id>` on this spec. Never skip, `xfail`, suppress or delete a test,
   edit a `verify:` or use `--no-verify` as the fix. An uncorrected pre-existing red stays a FAIL of the
   gate, and the PR names the base red and the spec that captures it.
