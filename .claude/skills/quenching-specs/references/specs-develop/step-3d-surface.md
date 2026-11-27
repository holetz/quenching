### 3d. Enumerate the surface refinement
Runs only on the ask step 3 identified; skip whole otherwise. Follow
[questions.md](.agents/quenching/references/specs-develop/questions.md) §Surface refinement.

**Plan; do not edit.** Write no workflow, skill, reference, structure or code file during
definition. This boundary lets the pass obey the doctrine it is changing: the surface becomes a
task group, never a prose edit to its targets. `/quenching-specs execute` writes it.

Enumerate every opportunity found while forming the objective — a workflow, a skill, a reference,
the structure that holds them, an automation. Fold each into the group or park it as one
`## Discoveries` line, per §Surface refinement's enumeration. Drop nothing.

Draft `### 1. Process surface` as the first group of `## Tasks`, ahead of the objective's tasks
that rely on the new behaviour. Give every item `files:` and `verify:`. Name in `files:` the
paths in the `Process surface this spec expects to touch` list under `## Impact`, plus the generated
mirrors each source edit rewrites — the deployed `.agents/**` and `.claude/**` mirrors and
`.agents/.quenching-deploy.json` — in the same task as that source edit. Name every declared path
in a task; let no `[P]` cross the group.
Declare the paths per [specs-develop/artifacts.md](.agents/quenching/references/specs-develop/artifacts.md) §`## Impact` — the parsed sub-heading.

Where the plan needs current practice, delegate to the read-only research sub-agent of
[specs-develop/questions.md](.agents/quenching/references/specs-develop/questions.md) §Surface
refinement. Keep one table — source, publication date, retrieval date, claim, what it would
change — in `## Alternatives Considered` or `## Design`. A web source may support an alternative or a rationale;
it never grounds a binding rule alone —
[align/evidence-doctrine.md](.agents/quenching/references/align/evidence-doctrine.md) §3.

This is a subject the pass plans, not an execution question like `[P]`/`files:`/`pattern:`.
Ask the human only what the surface plan cannot answer from evidence, under the pass's track.
**Done when:** every declared surface path is named by a task carrying `files:` and `verify:`,
`specs_read(verb="parallel", spec=<id>)` exits 0 in step 7, and nothing outside the
spec was written.
