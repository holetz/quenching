# /quenching-specs execute — 7. Report, and hand off

Loaded only when this step runs; the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

**When this run's input carried `autonomous`, skip the read below and the mold with it** — a conductor presents the report, not this run; return the content in the fixed shape the caller specified. Otherwise:

```text
components_read(verb="read", path=".agents/quenching/references/specs-develop/report-mold.md", sections=["§The report mold"], rules_only=true)
```

Emit §The report mold. The single-spec header line carries overall progress; three body blocks:

1. **This session** — fixed. The isolation and its `branch` record, tasks completed, each task's
   commit and the subject recorded for it, any subject that drifted.
2. **Blocked** — optional. Each blocked task with its reason.
3. **Written along the way** — optional. The standards written, and the discoveries recorded,
   **quoted** as `/quenching-specs develop` quotes them: the same artifact is owed the same fidelity
   whichever command wrote it.

Print §The session-size line before the block — `components_read(verb="session_context")`, read once; exit 1 turns the `→` line into a recommendation to run the next stage **in a new session**, exit 0 and 2 leave it an offer.

**Name what git needs.** Add one line stating what the git flow owes the branch next and what to review first: `/quenching-git pr-create <id>` (or `/quenching-git merge`) after `/quenching-specs conclude`, over the diff `origin/<base>...HEAD`. Execute runs none of it: git is the main session's flow, and in an orchestrated run the `spec-orchestrator` publishes after the `spec-verifier` PASS.

Close on §The next-step block, its recommended line carrying **this spec's id**:
`/quenching-specs conclude <id>` at 100%, `/quenching-specs execute <id>` when the run paused
mid-plan.

**At 100%**, after the block, offer once to chain straight into `/quenching-specs conclude` (the `Skill` tool, which takes
the registry name): the branch review,
the emergent `/docs/`, the merge, and the archive-time distillation. Declined → the block already
named the command, so stop. Over budget (the session-size line's exit 1) → the offer's first option
(A, recommended) is to run `/quenching-specs conclude <id>` in a new session, the measured peak in
its own text; chaining here stays an option. Paused → say why and wait.

**Done when:** the summary is shown and the hand-off has been offered or declined.
