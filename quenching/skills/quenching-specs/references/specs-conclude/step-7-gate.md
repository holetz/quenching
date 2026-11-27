# /quenching-specs conclude — step 7: Prove the gate green, then hand off

**Doctrine of this step.** *An abandoned spec's branch is offered for deletion, never handed off
toward a merge*: partial work on a branch nobody adopted is history, not a change; offer to keep it
or delete it, default to keeping. This is the one branch-disposal decision that stays inline here
rather than in `/quenching-git cleanup`; framed per
[specs-conclude/abandoned.md](.agents/quenching/references/specs-conclude/abandoned.md)
§The branch-delete offer, informed rather than defensive.

**Resuming.** The gate has no record — it is a verdict on the tree as it stands *now*: always re-run
it; a green run from before the last commit proves nothing.
**Under `autonomous`.** Branch behind its base: the base merged in (`git merge --no-edit
origin/<base>`, never a rebase), then the gate; a conflict only in the deployed surface or inside a
generated zone is resolved by regenerating; any other conflict → `git merge --abort` and
`needs-human` with the paths. An inconclusive check → `needs-human`, the check named. The abandoned
branch-delete offer → keep, recorded in the report. A red gate is `STATE: failed`, never a question
— unless the red is a pre-existing error (below). For a `done` outcome this step opens the PR
itself; for `abandoned` there is no handoff to make.

Nothing after this point writes anything — the last commit this run makes is step 5's, and step 6
writes only the spec store.

**First the gate: re-run whatever the repo's `## Validation` names — on the WORK BRANCH, before
merging.** Run it from the checkout that carries the work (the worktree or branch this run is
standing on), so what it grades is the change being proposed. **One full gate per spec:** under
`autonomous` the branch takes the base (the merge below) BEFORE this run, so the gate runs once
over the merged tree and never once before and once after; it runs again only after a
`[fix-preexistente]` commit. `/quenching-specs execute` does not run the full gate at its end, so
this is the spec's only full run; the reviewer and the verifier read its `GATE_EXIT` and the CI
run instead of repeating it.

**A failing check stops the handoff.** Report which check failed and what it printed, leave the
branch unmerged, and let the human fix it *on the branch* — then this command is re-run. Never hand
off past a red check, and never repair one with a commit that isn't the fix itself.

**A red that is not this spec's has its own route**, per `/docs/standards/workflows/task-execution.md`
§Pre-existing errors: reproduce it in the base worktree (`.quenching/red`, removed before returning).
No reproduction → it is the branch's own and the paragraph above applies. Reproduced and contained (the
four criteria together: cause diagnosed and reproduced on the base, few files without a contract change,
an existing verification proves it, no human decision) → the fix itself is the one commit allowed
here, declared as a `[fix-preexistente]` task (`files:` and `verify:`) so the verifier reads it as scope,
and the gate runs again. Otherwise capture it now with `specs_write(verb="create")` (`## Problem` plus
cause, reproduction, files), record `promoted: <id>` in `## Discoveries`, and stop `STATE: failed` (under
`autonomous`, `needs-human:` naming that spec): the red stays a FAIL, the PR names it and the merge
waits for the captured spec. Never skip, `xfail`, suppress a test or edit a `verify:`. The sweep of
step 6 keeps its own criteria; this route is for defects of the product, not of the automation.

**The gate grades the branch, so the branch must already carry the base.** If the base moved since
the branch was cut, a green gate says nothing about the merged tree:

```bash
if git remote get-url origin >/dev/null 2>&1; then
  git fetch origin <base> && git rev-list --count plan/<id>-<handle>..origin/<base>
else
  git rev-list --count plan/<id>-<handle>..<base>     # NO-REMOTE: the local base is the only one
fi                                                     # commits on the base the branch does not have
```

Count against `origin/<base>` wherever `origin` exists: the PR is opened against the remote, and a
PR merged through `gh` moves no local ref, so the local `<base>` can read zero over a branch that
lacks a merged dependency. A fetch error is reported and stops the handoff; it is never read as
zero.

Non-zero → **say so and stop before the gate**, naming the count. Bringing the branch up to date is
a write, and it is the human's call which way — merging the base in, or `/quenching-git sync`'s own
rebase, which carries the recorded task subjects through the rewrite. Never do it unasked, and
never run the gate over a branch you know is behind.

**Under `autonomous` the answer is given, and it is the merge, taken before the gate.** A sibling spec merged mid-wave is
the ordinary way to be behind, and a `needs-human` there is never relaunched. Run the count first;
non-zero, run
`git merge --no-edit origin/<base>` — a merge, never a rebase, so the task shas stay ancestors and
the spec-verifier's check 7 accepts them — and only then the gate, once, over the merged tree. A conflict only in
the deployed surface (`.agents/quenching/**`, `.claude/skills/**`, `.agents/.quenching-deploy.json`)
is mechanical: take the base's side (`git checkout-index --stage=3 -f -- <path>`, `git add <path>`), then
**regenerate before concluding the merge** — `cq deploy --target . --write` — `git add` what it
rewrote, and conclude the merge. A manifest taken from the base alone loses the branch's entries.
The base's manifest does not own the generated files the branch created (a new
`.github/agents/*.agent.md`, say), so the `--write` may refuse with `ct-deploy-unowned` and its
`conflicts` list. Delete exactly the listed paths the branch added
(`git diff --name-only --diff-filter=A origin/<base>...HEAD`) — the `--write` recreates them and the
regenerated manifest owns them — then run the `--write` again. A listed path the branch did not add
is authored text: `git merge --abort` and `needs-human` with the paths.
Then `cq deploy --target . --check` exits 0.

A conflict only inside a generated zone is mechanical too. The zones are those of
`docs/standards/architecture/generated-listings.md` §Enumerated generated zones, each with its
owner verb; the list is not repeated here. It holds only where every conflict marker of the file
sits between the zone's delimiters (`…-start` / `…-end`): a marker outside them is a conflict
in authored text. Resolve only the conflicting hunks, never the whole file, so what merged cleanly
outside the zone survives: write the stages to scratch files (`git show :1:<path>`, `:2:`, `:3:`),
run `git merge-file --theirs <ours> <base> <theirs>`, copy the result over `<path>`, then run the
zone's owner verb in the worktree (`proof_write(verb="readme", write=true, root="<worktree>")` for `quenching-proof-readme`,
`ops_write(verb="registry", write=true, root="<worktree>")` for the operations registry) **before** `cq deploy --target . --write`, which mirrors
the README, and `git add` what they rewrote. Then the owner's `--check` and `cq deploy --target .
--check` exit 0. Any marker outside a zone, or a zone with no owner verb → `git merge --abort`
and `needs-human` naming the paths.

**An inconclusive result is not a green one.** A check that cannot tell "this failed" from "this
could not be measured" has returned no verdict — say which it was, and ask (`autonomous`:
`needs-human`), rather than merging on it. Where the repo keeps `/docs/standards/quality/surface-verification.md`, its §The five
preconditions a check must satisfy is where that distinction is defined for the command surface.

**Run the scope the diff justifies.** A check with a `--only`-style selector gets the subset this
branch can actually break, because a harness that spawns fresh agent sessions bills for every one.
When the repo's `## Validation` names
the scope, follow it; when it does not, run what it says and report the cost as a finding worth a
selector.

The gate passed — the branch is reviewed, distilled, its `## Outcome` written, and proven. For a `done` outcome,
read the complexity from the status payload already in hand. **Under `autonomous` the run opens the
PR itself, whatever the complexity**, because publication cannot depend on an orchestrator that
may never exist: the same verb the `low` path chains, with the word `autonomous` as the human's
pre-answer to its confirmation.

```text
Skill("quenching-git", "pr-create <id> autonomous")
```

`/quenching-git pr-create <id> autonomous` owns its own push, confirmation and `pr` record;
report the url it stamps on `PR:`, and never a second handoff — `/quenching-git merge` is not
invoked from here under any outcome. **Outside `autonomous`, `low` chains the provider handoff
now:**

```text
Skill("quenching-git", "pr-create <id>")
```

Invoke it with the spec id; `/quenching-git pr-create` owns its own confirmation, push and PR
record. Do not offer a second handoff or invoke `/quenching-git merge` on the low path.
**For `medium`, `high` and `xhigh`, do not invoke it: name the handoff and stop:**

Use the provider configuration already read in step 1 to name the next command: recommend
`/quenching-git pr-create` when the configured provider supports the PR route, otherwise
`/quenching-git merge`. The human picks, and neither is invoked from here. Name the branch and the
base so the recommendation is copy-pasteable. Add one line: once the merge lands, `/quenching-specs conclude <id>` archives the spec and releases its worktree (step 8). For an `abandoned` outcome, skip this handoff and
follow the branch-disposal path below.

For `abandoned`, there is nothing to hand off toward — do not remove any worktree; frame and make
the branch-delete offer per
[specs-conclude/abandoned.md](.agents/quenching/references/specs-conclude/abandoned.md)
§The branch-delete offer, informed rather than defensive, default **keep** (taken unasked under
`autonomous`), and record the choice and fate in the report.

**Release the reservation once the build is over** — after the handoff above (`done`: the PR
opened or the handoff named) and after the `abandoned` archive of step 4:
`specs_external(verb="claim_release", claim_id=<id>)`. `released: false` with `reason: absent` is fine;
`not-holder` is reported and left to expire, never taken; exit 2 is reported. A red gate keeps
the lease: the build is not over. The reconcile deletes whatever lease a terminal spec still holds.
