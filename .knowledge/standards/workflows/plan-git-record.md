---
type: standard
title: Plan git record contract
description: How a plan's work is recorded in git — the commit sha as the task→commit anchor where the spec no longer shares a branch with the code, the commit subject as the anchor a co-branching spec still needs, one commit per task while its section is open squashed to one commit per section at that section's boundary and what that does to the anchor's granularity, the branch, pr and merge frontmatter records — `pr:` stamped by `/quenching:git:pr:create` and `merge:` by `/quenching:git:merge`, each on its own confirmation, read-on-demand rather than a mandatory stamp once `cq git base` reports the resolved base is the host's own default branch, the write-many `pr` record and the minimal-gear run that stops at the open PR without ever stamping `merge`, where a record lands when there is no merge to carry it — the in-place pair `work == base` and the single case where the record rather than git liveness is the signal because that ref can never die, the git-native `quenching-slugs:` branch mark that lets `conclude` self-discover its spec with no frontmatter involved, the base-inference chain a declared integration branch now wins ahead of origin/HEAD, why every record is written before the thing it describes, the squash-merge caveat, the merge that runs via git -C in the base's own checkout and the worktree removed after it, why a branch is deleted with `-d` and never `-D`, and the read-if-present contract for a target's own /.knowledge/standards/git/
resource: plugins/quenching/assets/references/git/**, plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/references/specs-conclude/auto-discover.md, plugins/quenching/assets/bin/quenching/specs/**, plugins/quenching/assets/bin/quenching/git/**, plugins/quenching/commands/specs/execute.md, plugins/quenching/commands/specs/conclude.md, plugins/quenching/commands/git/merge.md, plugins/quenching/commands/git/pr/create.md
tags: [workflows, specs, git, commits, records]
timestamp: 2026-08-16
audience: both
authority: background
source: specs-flow-consolidation plan (sections 2-3); rewritten around the subject anchor by the move-conclude-merge-last plan (task 5.1); the git -C merge and the post-merge worktree removal added by the prefer-worktree-isolation plan (task 4.1); rewritten around the sha anchor by the configurable-spec-backend plan (task 4.5); the always-stamp rule and the adopted-branch base inference added by the rework-specs-isolate-flow plan (task 2.3) — background pending proof in a live adoption; the pull-request route and `merge.pr` added by that same plan's branch review at conclude, which found the `## Impact` path declared for this file and written only in plan-lifecycle.md; the declared-integration-branch step added ahead of origin/HEAD by the configurable-branch-strategy plan (task 2.3, 2026-08-04), proved in code by `infer_base_branch`'s `selftest` fixture; the section squash and its narrowing of the task→commit anchor to section granularity by the reduzir-commits-por-secao spec (2026-08-11); the `quenching-slugs:` branch mark and the auto-discover fallback added by the conclude-detecta-slug-por-marcacao-de-worktree plan (task 3.1, 2026-08-12); the `pr` record, the in-place `work == base` pair and the liveness exception it forces added by vincular-spec-a-branch-commits-e-pr at its conclude — this file was never named under that spec's `## Impact`, and the branch review is what found it contradicted, after `cq specs next` was measured ranking every in-place spec as permanently in flight on a base branch that cannot die; the place rule (§Every record is written where it needs to survive) and the branch-deletion counterpart to the worktree rule (§A branch is deleted with `-d`, never `-D`) added by the fix-conclude-abandoned-branch-harvest plan (task 4.1, 2026-08-16) — proved, not merely agreed: `conclude-order-check.sh`'s `abandoned` arm (task 3.1 of that same plan) builds the fixture, deletes the branch with `-D`, and asserts the closing survives; `pr:`/`merge:` ownership moved to `/quenching:git:pr:create`/`/quenching:git:merge` and the host-link conditionality (measured in task 1.1) added by pilar-git-e-specs-agnosticas-ao-git (task 6.4)
maintainer: quenching
---

# Plan git record contract

What links a plan's checkboxes to the commits that implemented them, which git facts are recorded
in the spec, and whose conventions govern the commits themselves. The procedures implementing this
live in `assets/references/git/**` and `.../specs-execute/execution.md`; this
standard is the contract they answer to.

## Every record is written before the thing it describes

This is the rule the rest of the file follows from. A record pointing at a commit can only be
written *after* that commit if it names something the commit alone can produce — and a sha is
exactly that. Naming the **subject** instead inverts the dependency, because the subject is chosen
by whoever is about to commit.

Two consequences, and they are why the anchor changed:

- **`/quenching:specs:execute` ticks the box before committing**, so the checkbox travels inside the commit
  that implements it — one task, one commit, while its section is still open; the per-task
  bookkeeping commit is gone, and the section's own commits squash to one at that section's own
  boundary ([execution.md](/plugins/quenching/assets/references/specs-execute/execution.md) §The
  section squash — §The task→commit link below is what the anchor does across that squash).
- **`/quenching:git:merge` stamps `merge:` on the work branch before merging**, so the merge is the
  last action of *that* command and **nothing is ever committed to the base branch after it**. One
  merge carries the code, the emergent docs (written earlier, by `/quenching:specs:conclude`, which
  stops before the merge and hands off to this command) and the archived spec's distillation;
  reverting it reverts the spec's whole footprint.

A record that cannot be written beforehand is a record that forces a write afterwards, and a write
after the merge lands where the spec's own branch cannot account for it.

## Every record is written where it needs to survive

The order rule above answers *when*; this one answers *where*, and the two are independent. A
record lands in whichever checkout will still exist to carry it forward.

**When there is a merge, that checkout is the branch** — the merge carries it, which is the whole
mechanism the order rule above depends on. **When there is no merge, that checkout is the base's
own** — `/quenching:specs:conclude`'s `--outcome abandoned` path never merges, so a record written on the
branch would depend on a branch nobody adopted to still exist. It lands instead in the checkout
already holding `<base>`, located the same way the merge itself locates it below (§The merge runs in
the checkout that already holds the base) — `git worktree list --porcelain`, then `git -C <that
path>`.

This does not contradict "nothing is written after the merge" (§Three frontmatter records carry the
underivable git facts, `merge`). Under `abandoned` there is no merge: "after the merge" is
vacuously satisfied, and there is no reversion property to protect either, because none was ever
earned. A commit into the base checkout under this outcome describes only itself — never something a
merge was supposed to carry.

A spec built **in place** (`branch.work == branch.base`) needs no version of this rule: the checkout
it is already standing in is both the branch and the base, so there is nowhere else a record could
go.

## The task→commit link is the commit's own sha, where the spec no longer shares a branch with it

Each completed task line carries a fact about the commit that implements it, in the metadata
grammar `files:` and `verify:` already use:

```markdown
- [x] 3.2 Validate the token
      files: src/auth.py
      verify: pytest tests/auth
      commit: 4f2a9c1
```

Written mechanically by `cq specs task --check <id> --commit <sha>` — never by string surgery —
and only **after** the task verified, self-reviewed, and the commit exists:

```bash
git add <the task's files> && git commit -m "<subject>"
cq specs task --spec <slug> --check <id> --commit "$(git rev-parse HEAD)"
```

### Why a post-commit write stopped being the thing this contract forbade

§Every record is written before the thing it describes is still the rule, and reads for a reason
that has not changed: a record naming something only the commit can produce, written into a file
that shares the commit's own branch, forces a second commit on that branch to carry the record —
turning "one commit per task" into two.

**What changed is which branch the record lands on.** [The spec backend](../architecture/spec-backend.md)
guarantees no backend lets a spec share a branch with the code being committed: the `files` backend
writes the tick to its own dedicated specs branch (by way of a worktree, not by way of a second
commit on the code branch — see [worktree-setup.md](worktree-setup.md)), and an external backend
writes it outside git entirely. Writing `commit: <sha>` after the code commit no longer touches the
code branch a second time, because the write was never going to land there. The rule that forced
subject-before-commit was never "sha is illegal" — it was "never a second commit on the branch
being committed to", and a sha-carrying write that lands on a different store altogether does not
break it.

### Subject is not deprecated; it is what a co-branching spec still needs

A repository whose specs still live on the code branch — this repository's own `plans/`/`archive/`
at the time of writing, per [spec-backend.md](../architecture/spec-backend.md) §The selected
backend is the source of truth — still pays the cost a second commit would carry, because for that
spec the record and the code genuinely do share a branch. `cq specs task --check <id> --subject
<line>` is unchanged and still the right tool there, ticked **before** the commit so the box travels
inside it:

```markdown
- [x] 3.2 Validate the token
      files: src/auth.py
      verify: pytest tests/auth
      subject: plan/session-tokens: 3.2 Validate the token
```

It resolves by substring match, `git log --grep="<the recorded subject>" --fixed-strings`, and is
still **not a trailer and not a machine-readable anchor bolted into the message** — the subject the
target repo's own convention produced, recorded verbatim. `--subject` and `--commit` are accepted
together or alone by the same `task --check`; neither is a special case of the other.

**Both forms are read, forever, and both are now written.** A spec built before subject was
introduced carries `commit: <sha>` from that era; one built during co-branching carries `subject:`;
one built on a non-co-branching backend carries `commit: <sha>` again, for the opposite reason.
Nothing is backfilled and neither form is an error: rewriting an archived spec to modernise its
anchor would falsify when the record was actually made.

### Where each form can fail

A `commit-msg` hook that **replaces** the subject outright breaks a subject-anchored link; substring
matching survives every hook that merely *adds*, which is nearly all of them. `/quenching:specs:execute`
compares `git log -1 --format=%s` against what it recorded and **reports a mismatch as a finding,
writing nothing** — correcting it after the commit would restore the ordering this contract removed.
A sha-anchored link has no equivalent failure mode — the sha is read back from git itself, not
matched against rewritable prose — but a `--commit` write that fails (a network error against an
external backend, mid-way through recording it) must be **reported, never left implicit**: the
commit exists either way, and a tick that silently did not land would claim proof of nothing.

## Three frontmatter records carry the underivable git facts

All three belong to the record vocabulary in [plan-lifecycle.md](plan-lifecycle.md) and pass the
same admission test — a fact no derivation can reproduce:

- **`branch: {base, work}`** — stamped by `/quenching:specs:execute`'s inline isolation offer, write-once,
  **once the work ref is resolved** — taken or declined. `work` is derivable while the branch is
  checked out; `base` is not — **after the merge, git cannot say what the branch was cut from**,
  which is the whole reason the record exists and why it is captured while still true. A later run
  reads the record; a current branch that disagrees with `work` is a finding to report, never a
  value to correct.

  **Work done in place stamps `work` equal to `base`**, where it once stamped nothing. The pair is
  not the empty statement that silence would be: an absent record and `work == base` are different
  claims — *nobody has decided yet* versus *a human declined isolation* — and only a spec that
  records the second can be told apart from one that was never started.

  **Every branch that is not the repository's base gets this stamped**, including one the plugin
  never cut. A human may check one out by hand before running `execute`; a spec built there with
  nothing stamped leaves `conclude` unable to diff the right range and leaves `git:merge` unable to
  say what it merges into. `base` is then **inferred**
  rather than observed, stopping at the first that answers: the spec's own `branch.base` record,
  when one already exists; `git symbolic-ref refs/remotes/origin/HEAD`;
  `git config init.defaultBranch`; then `main`.

  `infer_base_branch` in `cq specs`, proved by
  `tests/test_specs_parse.py`'s `InferBaseBranch` fixture, decides only the order; the git facts
  `origin/HEAD` and `init.defaultBranch` resolve are
  still read by the orchestrator, exactly as before.

  The inference is shown on the same line as the confirmation,
  before stamping, because the record is write-once and that is the only moment disagreeing with
  it is cheap. **Never `git merge-base` or `--fork-point`** — both answer a commit, not a branch
  name, and a commit ancestral to three branches identifies none of them. The mechanics live in
  [git/isolation.md](/plugins/quenching/assets/references/git/isolation.md) §Recording the
  isolation, cited rather than restated.
- **`pr: {number, url, date}`** — stamped by `/quenching:git:pr:create` the moment `gh pr create`
  returns, and **write-many** where the other two are write-once: a PR may be closed and reopened,
  or force-pushed to a fresh number, and each is a new fact rather than a falsification of the old
  one — which is why it carries its own `date`. `/quenching:specs:conclude` never opens a PR or
  writes this record itself; it stops before either, naming `git:pr:create` as the human's own next
  command.

  It is distinct from `merge.pr` below, and the distinction is the whole reason it exists. `merge`
  is stamped only once the merge is about to happen; under `/quenching:specs:cycle`'s minimal
  gear the PR route deliberately **stops** at the open PR, leaving the merge to human review — the
  one case this run invokes `git:pr:create` itself rather than leaving the name for a human. With
  only `merge.pr` to write into, that run would have had no honest way to record the PR it had just
  opened — stamping the write-once `merge` for a merge that had not been decided would have burned
  the one write it gets.

- **`merge: {strategy, subject, pr}`** — stamped by `/quenching:git:merge`, write-once, **on the
  work branch before the merge**. The strategy is a human choice, offered by that command, and the
  subject names the merge it will produce. Under `rebase` and `fast-forward` no merge commit
  exists, so the subject is an explicit none; `cq specs validate` reports a record that gets this
  backwards either way, as `sp-bad-merge`.

  **`pr` names the pull request, and exists only when one was opened first.** Most merges are local
  and carry no `pr:` at all — its absence is never a finding. Where it is present it records a fact
  the base branch's history cannot reproduce: which pull request the merge went through, and
  therefore where the review and the checks still live once the branch is gone.

**Where the host links the merge back to the branch, both records shed the "mandatory" half of
their name.** `cq git base --json` reports `isDefault` alongside the resolved base — whether that
base is the host's own default branch. **Measured for GitHub (task 1.1):** `Closes #<n>` only
populates `closingIssuesReferences` — the fact a caller can read back — when the PR's base *is*
that default; on any other base (this repo's own `develop`) the same keyword still cross-references
the issue but never closes it, so nothing readable exists to fall back on. The rule this forces:

| `cq git base`'s `isDefault` | `pr:`/`merge:` |
| --- | --- |
| `true` | **read on demand** — `gh pr view`/`git log` already answer the same question the record would, so a caller may skip stamping and read the host directly |
| `false` (this repo's own case, base `develop`) | **mandatory stamp** — unchanged from above; nothing on the host names the link back |

`/quenching:git:pr:create` and `/quenching:git:merge` both consult this fact before deciding
whether to stamp; `/quenching:specs:conclude` consults it only to decide which of the two to name
in its own handoff. **The same rule is assumed, not yet measured, for `azure-boards`** — its
`--work-items` link is a structurally different mechanism (an explicit API link, not keyword
parsing), so the branch restriction may not apply there at all; task 1.2 remains blocked (no
authority to create artifacts in a real corporate org from an autonomous run) and is what would
prove or break the assumption.

**The record is never the signal.** A human may cut `plan/<slug>` by hand and stamp nothing, and a
record outlives the branch it names. Anything asking whether a spec is in flight asks git for a
live ref — which is what `cq specs next --front` does, and why that ranking demotes a spec
whose branch is alive but checked out elsewhere.

**`work == base` is the one exception, and it exists because that ref cannot die.** The rule above
is safe only while a live ref means something happened; the base branch is alive in every
repository, always, so a spec built in place would answer *yes, in flight* forever. The liveness
question has to be skipped for that pair and the record read instead — the single case where the
record IS the signal.

MEASURED, and the reason this is written rather than assumed: when in-place work began stamping
the pair, `cq specs next` still ranked on liveness alone, and every spec built in place rose to the
top of that ranking with the reason *"you are on this branch"* whenever the session
stood on the base. The guard the code already carried — *a record whose ref is gone stops
counting* — could not fire, because nothing was ever going to remove `develop`. The shape
generalizes past this record: **an expiry condition that the sentinel value can never satisfy is
not a guard, and it fails silently in the direction of always-true.**

## The branch also carries a git-native mark, outside any frontmatter record

Beside `branch:`, `pr:` and `merge:` above, `/quenching:specs:execute` writes one more signal that is
**not** a frontmatter record: a recognizable line in the branch's own description —
`quenching-slugs: <slug1>,<slug2>` — rewritten, never duplicated, after every task's commit, and
never written when the spec runs `In place`. The mechanism is
[git/isolation.md](/plugins/quenching/assets/references/git/isolation.md) §Marking the branch with
the specs it built, owned by `execute`.

`/quenching:specs:conclude` reads it to resolve which spec(s) built the branch it is closing when
called with no `--spec`: one valid slug resolves silently, more than one asks, and a slug the
marking names that no longer resolves under `plans/` is dropped as stale rather than trusted. No
valid marking at all falls to measuring the branch's own diff and always asking whether to
materialize a minimal spec before continuing — never a size threshold. The full procedure is
[auto-discover.md](/plugins/quenching/assets/references/specs-conclude/auto-discover.md), owned by
`conclude`.

**Why this is not a fourth frontmatter record.** The three records above answer questions only
the spec itself can honestly hold — a write-once fact this exact spec is the source of. The
branch's mark answers a different question — *which* spec(s), if any, built this ref — asked by a
command that does not yet know the slug, so the answer has to live somewhere reachable **before**
any spec is resolved. Frontmatter lives inside a spec; a slug is the key that opens one. The mark
lives on the ref instead, which is the one place a slug-less `conclude` can look first.

**Local to the `.git` that wrote it — the same limitation as any git config.** A branch pulled onto
another machine, or a fresh clone, carries no description at all, so this mark never crosses one.
`conclude`'s diff-based fallback exists to cover exactly that gap, not as a general substitute for
the mark.

## The route is a second choice, and it moves when `merge:` is stamped

The **route** — pull request, or local — is which of `/quenching:git:pr:create` and
`/quenching:git:merge` the human runs, and in which order; `conclude` chooses neither, it only
proves the branch ready and names both by way of §What conclude hands off, below. The route decides
how the merge reaches the base; `git:merge`'s own strategy offer decides what shape it takes once
it does. Three of the four strategies map one-to-one onto a `gh pr merge` flag (`--merge`,
`--squash`, `--rebase`), so the route borrows the strategy vocabulary rather than inventing one.
**`fast-forward` has no `gh` equivalent**, so the PR route makes no sense under it: `cq specs
record` refuses `pr:` set alongside that strategy (`sp-merge-pr-no-route`) and `validate` warns on
one already written.

The route also decides **when** the record can be stamped, and this is the one place the
write-before-the-thing rule bends without breaking:

| Route | When `merge:` is stamped | Why not earlier or later |
| --- | --- | --- |
| local | on the branch, before the merge | the subject is knowable the moment the strategy is chosen |
| pull request | on the branch, after the PR is opened and before it is merged | `merge.pr` names something that does not exist until `gh pr create` returns, and the record is write-once — stamping without it would burn the single write |
| pull request, minimal gear | **never, this run** | `/quenching:specs:cycle` stops at the open PR by design, leaving the merge to human review; the write-many `pr:` record carries the PR until a later run merges it |

Both stamps still land **before** the merge and **on the work branch**, which is the invariant that
matters: nothing is written to the base after it. A run interrupted between the stamp and the merge
leaves the record written and the branch unmerged, which is recoverable — the next run reads the
recorded subject and merges with it. The reverse can only come from a merge outside these two
commands' own runs, and is reported rather than repaired.

### What `conclude` hands off

`/quenching:specs:conclude` proves the branch reviewed, distilled and gate-green, then **names**
the route rather than choosing it: `/quenching:git:pr:create` where `gh` resolves the repository,
`/quenching:git:merge` either way, in its own next-step block. Neither is invoked from `conclude`
itself — the one exception is `/quenching:specs:cycle`'s minimal gear, which invokes
`git:pr:create` under the same run's own authorization because there is no human mid-flow to hand
the name to ([align/convergence.md](/plugins/quenching/assets/references/align/convergence.md)
§The PR route). Every other run reads the name and runs the
command on its own word.

## The squash caveat, and what rebase no longer costs

The four merge strategies differ in one dimension that matters here — what happens to the commits
the recorded subjects resolve against:

| Strategy | The per-section subjects |
| --- | --- |
| merge commit *(default)* | resolve from the base branch forever |
| fast-forward | unchanged — nothing rewritten, nothing added |
| squash | **resolve only from the branch** — deleting it strands every record |
| rebase | **survive**: the rewrite carries the message, so every record still resolves |

A squash is a common house style and is not argued against — but its consequence is said out loud:
when squash is chosen, `/quenching:git:merge` records it in `merge:` and offers **not** to delete
the branch, the only way the archived spec's `subject:` fields stay resolvable. `## Outcome` no
longer names the strategy — it is decided after `conclude` has already written and archived it — so
the branch's own `merge:` record and `git log` are where a later reader resolves which strategy
ran.

**Rebase is no longer the strategy that destroys the record.** Under the sha anchor it rewrote every
recorded commit and left the archived spec pointing at commits that no longer existed — the one
strategy that made the record strictly worse rather than merely narrower. A subject is carried by
the rewrite, so rebase now sits on the same footing as the others. The old warning applies only to
specs still carrying the sha form.

## The merge runs in the checkout that already holds the base — never `git checkout`

A plan's merge is performed **into** the base's checkout, from wherever the run happens to be
standing:

```bash
git worktree list --porcelain                    # which checkout holds <base>
git -C <that path> merge --no-ff plan/<slug> -m "plan/<slug>: merge (<strategy>)"
```

`git checkout <base>` is **never** how a plan comes home. From inside a worktree it does not merely
misbehave, it fails outright — `fatal: '<base>' is already used by worktree at …`, exit 128 — so
that form is broken for precisely the isolation this repo recommends. `git -C` is one path rather
than two special cases: from a worktree it names the main checkout, and from the main checkout it
names itself.

**When no checkout holds the base, the run stops without merging.** It names the base it wanted,
says nothing has it checked out, and names the fix — check the base out, or add a worktree of it.
It never manufactures a temporary checkout. This costs nothing, because `merge:` is stamped
*before* the merge: the run resumes with no record falsified.

## A worktree is removed after a successful merge, and never forced

Isolation that is not cleaned up accumulates: directories beside the repo, each pointing at a
branch already integrated, none of them obviously safe to delete. So once the merge exits 0,
`/quenching:git:merge` removes the worktree — run from the base's checkout, because nothing removes the
tree it is standing in:

```bash
git -C <the base's checkout> worktree remove <the worktree path>
```

**`--force` is never passed on this command.** `git worktree remove` refuses a tree holding
modified or untracked files by itself (`contains modified or untracked files`, exit 128), which is
exactly the irreversible case worth fearing — the safety is already git's, so no confirmation
prompt would buy anything a human would not answer "yes" to every time. A clean tree leaves the
disk silently; a refusal is reported with the path and git's own output, and the worktree stays.

Three bounds keep this from being destructive: it runs **only** after a merge verified at exit 0,
it **never** runs for an abandoned plan, and it does **not** delete the branch — that stays the
separate, offered decision it already was.

## A branch is deleted with `-d`, never `-D`

The same shape as the worktree rule above: git's own refusal is the safety, not a prompt this
contract adds on top of it. `git branch -d <ref>` refuses a branch not fully merged into the one it
is deleted from — the one case worth fearing, and git already declines it on its own. `-D` is never
passed, by any command in this front, under any outcome: on a refusal, report git's own output
verbatim and keep the branch.

This is proven, not merely agreed. `assets/checks/conclude-order-check.sh`'s `abandoned` arm builds
a spec through create → isolate → execute → conclude(`--outcome abandoned`), deletes the branch with
`git branch -D` from the base checkout, and asserts that everything the closing wrote — the archive
move, the `outcome:` stamp, the distillation's background note — still resolves on the base
afterwards. The assertion that failed before §Every record is written where it needs to survive
existed is exactly this one.

## The target's git conventions win — read if present, never installed

Before the first commit of a run, `/.knowledge/standards/git/` is checked **once**. Anything found there
governs verbatim; partial coverage splits (the target's docs for what they cover, the plugin
defaults for the rest); an `authority: background` git standard still wins over the defaults. The
report states which one governed.

With nothing declared, the plugin's defaults apply — branch `plan/<slug>`, one commit per task with
the subject `plan/<slug>: <id> <title>` while a section is open, squashed to one commit per section
with the subject `plan/<slug>: <N> <section title>` at that section's own boundary
([execution.md](/plugins/quenching/assets/references/specs-execute/execution.md) §The section
squash), `plan/<slug>: merge (<strategy>)` for a merge, and `plan/<slug>: record …` for the
bookkeeping that remains. That bookkeeping is now only what a commit genuinely cannot carry ahead
of itself — `## Handoff`, which describes the tree *after* the last commit — and no longer includes
a ticked box or a stamped `merge:` record.

**Never install `/.knowledge/standards/git/**` into a target.** A default written into the repo stops
being a default: it converts an offer into a rule the repo now declares, which then wins forever
without anyone having agreed to it. A target that wants its conventions written down routes
through `/quenching:knowledge:add`, on its human's word. The same restraint bars inferring house style from
`git log` — a guess that looks deliberate is worse than the stated default.
