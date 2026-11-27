# /quenching-specs execute — step 5 g

Loaded only when this sub-step runs, together with the step 5 loop in [step-5-implement-tasks.md](.agents/skills/quenching-specs/references/execute/step-5-implement-tasks.md); the flow index is [execute.md](.agents/skills/quenching-specs/references/execute.md).

g. **Run and report the declared hook for this event, and move on.** Once the spec task has
   committed and been confirmed, `after_specs_execute_task` has fired. For every hook the config
   read returned, report the event, command, prompt, `optional` flag and any declared `condition`.
   **Never write `refs/remotes/origin/HEAD`** — it lives in the shared `.git`, outside this
   worktree, and nothing here writes it. The hook gets the base by name instead.
   **In a worktree the hook is never invoked.** When `git rev-parse --path-format=absolute --git-dir`
   and `git rev-parse --path-format=absolute --git-common-dir` differ in the checkout this run
   commits in (absolute, so a subdirectory of the main checkout compares equal), the build runs in a
   linked worktree and the session's hook would review the base checkout with an empty diff, then
   end the turn with the review text. Report each declared hook as above, classify it
   `skipped: worktree` — not a failure, no pause, optional or not — and go to step h; the security
   review of an orchestrated build is the epic's own. Outside a worktree, continue:

   Invoke the declared command as a `Skill` with the task and commit context:

   ```text
   after_specs_execute_task — hook: /security-review — optional: true
     condition: none declared
     prompt: none declared
   Skill("<declared hook command>", "<declared prompt plus task and commit context>")
   ```

   **Name the work checkout and the diff in that context.** A hook runs in the session's working
   directory, which the harness may return to the base checkout while this run builds in a worktree,
   so a hook such as `/security-review` diffs the base and finds nothing. Resolve
   `git rev-parse --show-toplevel` from the checkout this run commits in and pass, with the task
   and commit context, `work checkout: <toplevel>` and `review: git -C <toplevel> diff
   origin/<base>...HEAD`, where `<base>` is the base resolved in step 2,
   with the instruction to review that diff rather than the session's own checkout. The hook declaration is still passed untouched; only the target is added.

   **The hook's output is context, never the run's answer.** Whatever the hook returns (a
   `# Security review: …` text, for one) is read and the run goes on to step h; a run that ends
   with the hook's text instead of the fixed report is a defect. An orchestrated run always ends
   with the fixed report.

   `enabled: false` was filtered during the config read and is never announced or invoked;
   absence of `enabled` means enabled. The executor never evaluates `condition`: it reports the
   declaration and passes it as context to the hook. An optional hook failure is reported and the
   run continues; a non-optional hook failure is reported and pauses the run. Neither failure
   undoes the spec tick or rebuilds the already successful commit. **Classify every hook that
   was invoked as `ran`, `failed` (the command resolved and its run failed) or `unresolved` (no such
   command exists), and every hook not invoked in a worktree as `skipped: worktree`; carry the classification to the report** — an orchestrated run returns it
   as the spec-runner's `HOOKS:` line, so an optional hook that never resolved is never lost. A hook
   absent from config is silent.
