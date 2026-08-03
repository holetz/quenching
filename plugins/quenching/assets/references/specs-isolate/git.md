# Git for the `specs/` front — taking isolation, wording a commit, merging

The owner of **how** a spec's work is isolated, how its commits are worded, and how the branch
comes home. `/quenching:specs:isolate` performs the isolation; `/quenching:specs:execute` and `/quenching:specs:conclude` cite
this file for the conventions their own steps depend on. None of the three restates it.

Everything here is a **default**, not a rule. A target repo that has written down its own git
conventions has already decided, and a plugin that ignored that would be imposing house style on
somebody else's history.

## Contents

- [The read-if-present rule](#the-read-if-present-rule)
- [Isolation is available at any stage](#isolation-is-available-at-any-stage)
- [Branch and worktree names](#branch-and-worktree-names)
  - [The worktree is the preferred form](#the-worktree-is-the-preferred-form)
  - [A target may declare a setup command](#a-target-may-declare-a-setup-command)
- [Recording the isolation](#recording-the-isolation)
- [Commit messages](#commit-messages)
- [The subject is the anchor](#the-subject-is-the-anchor)
- [Merge strategies](#merge-strategies)
  - [The worktree is removed after a successful merge](#the-worktree-is-removed-after-a-successful-merge)
- [What is never done, on any repo](#what-is-never-done-on-any-repo)

## The read-if-present rule

<!-- rules -->

Before the first commit of a run, look for the target's own conventions — **once**, and cheaply:

```bash
ls docs/standards/git/ 2>/dev/null
```

| What is found | What governs |
| --- | --- |
| one or more `docs/standards/git/**.md` | **the target's docs**, read and followed verbatim |
| nothing | the defaults below |
| a doc that covers only part (e.g. commit subjects but not merges) | the target's for what it covers, the defaults for the rest |

State in the report which one governed. "Read the repo's `docs/standards/git/commit-messages.md`"
and "used the plugin default" are different facts about the same commit, and only one of them means
the human's convention was honoured.

**Never install a git standard into a target.** Not as a fixup, not as a suggestion applied, not
"so the next run has something to read". Writing `docs/standards/git/**` into a repository that
never asked for it is `/specs:*` reaching into `/quenching:docs:align`'s territory, and it converts a default
this file *offers* into a rule the repo now *declares* — which then wins over this file forever,
without anyone having agreed to it. If a human wants their conventions written down, that is
`/quenching:docs:add`, on their word.

An `authority: background` git standard in the target still wins over these defaults. It is an
agreed-but-unproven rule someone wrote on purpose; that beats a plugin's opinion either way.

## Isolation is available at any stage

<!-- rules -->

Isolation used to exist only inside `/quenching:specs:execute`, which made it a privilege of building. It is
not: creating and developing a spec both write into `specs/plans/` and dirty the tree, and a spec
sometimes ought to be born on the branch that will carry its work.

`/quenching:specs:isolate` takes or reports isolation for ONE spec at **any** stage:

| Stage | What isolating buys |
| --- | --- |
| just created | the spec file itself lands on the branch, so the base keeps no trace of work that may be abandoned |
| being developed | an interrogation that rewrites half the spec does not sit in the base branch's tree |
| about to be built | the original case: code, docs and the ticked boxes are all on one branch |

`/quenching:specs:execute` **delegates** here rather than reimplementing; `/quenching:specs:create` and
`/quenching:specs:develop` forward on request and never offer unprompted. Isolation stays optional, is
recommended before building, and is never imposed.

**Merging is not here.** It stays inside `/quenching:specs:conclude`, behind that command's review and
archive gates — a merge invocable on its own could run against a spec nobody reviewed and nothing
archived, and would have to duplicate every refusal `conclude` already owns.

## Branch and worktree names

<!-- rules -->

```
plan/<slug>
```

The spec's slug, unaltered — kebab-case, no date prefix, no id. The slug is the identity every
command names, so a branch that carries it verbatim is greppable against `specs.py list`, and
`git branch --list 'plan/*'` is the list of work in flight. That is not only a convenience:
`specs.py next --front` ranks on whether `plan/<slug>` is **alive**, so a branch named to the
default is what tells `/quenching:specs:continue` this spec is already under way.

A worktree goes beside the repo, never inside it:

```bash
git worktree add ../<repo>-<slug> -b plan/<slug>
```

Inside the repo it lands in the tree the spec is about to change, and shows up in every `git
status`, every glob, and every checker this plugin runs.

### The worktree is the preferred form

`/quenching:specs:isolate` offers **Worktree first and recommends it**, unconditionally — a plain branch and
working in place stay available, in that order after it. A worktree leaves the main checkout
untouched, which is what lets several specs be built at once and what keeps satisfying the clean
tree `/quenching:specs:execute` demands.

**Unconditionally** means no heuristic sniffing the target for `package.json` or `.venv/`. A
recommendation that changes from repo to repo cannot be documented in one sentence, and guessing
somebody else's build is how a recommended path becomes a silent trap. What is offered instead is
the **cost, stated in the offer itself**: a fresh checkout carries only what git tracks — no
installed dependencies, no `.env`, no venv, no build output — so choosing Branch is a decision the
human read rather than a discovery at the first `verify:` that fails.

### A target may declare a setup command

`.claude/quenching.json`, at the repo root, under the `worktreeSetup` key:

```json
{"backend": "files", "worktreeSetup": "./scripts/wt-setup.sh"}
```

**The home moved, and the move is the point.** This used to be `specs/config.json`, at the root of
the specs workspace — which only had a place to live while every repo was guaranteed a `specs/`
folder. A repo that declares an external backend may hold no `specs/` at all, so the plugin's
configuration lives in one neutral home shared by all three fronts, and `worktreeSetup` moved there
with the rest of it. See
[plugin-configuration.md](../../../../docs/standards/workflows/plugin-configuration.md).

Read by `specs.py config --json` (exit 0 whether or not anything is declared) and run **once** by
`/quenching:specs:isolate`, immediately after `git worktree add`, with **cwd inside the new worktree** — the
tree lacking the dependencies is the tree that must install them. `specs.py` reads the value and
never executes it: whether the command resolves can only be judged against the new worktree's path,
which `specs.py` is never told.

No file, no key, or a command that does not resolve all mean **no setup**, and none of them is a
finding — most repos declare nothing, and declaring nothing must cost nothing. `specs.py doctor`
reports only the two ways it can be *wrong*, both `warn`: `sp-config-unknown-key` and
`sp-config-unparseable`. They exist for the one real failure mode of a machine-read config —
`worktree_setup` written where `worktreeSetup` was expected, and silence afterwards.

**Its consent is the isolation offer.** The command is displayed **verbatim** in `/quenching:specs:isolate`'s
plan block, and choosing Worktree is the OK for it: no second prompt, no remembered authorisation.
A failing setup is reported and **never undoes the worktree**.

## Recording the isolation

<!-- rules -->

```bash
specs.py record <slug> branch --set base=main --set work=plan/<slug>
```

`base` is whatever was checked out when the branch was cut. It is **not** assumed to be `main`.
`work` is derivable from `git branch --show-current` while the branch is checked out; `base` is
not — **after the merge, git cannot say what the branch was cut from**, which is the whole reason
the record exists and why it is captured while still true.

Stamp nothing when the human declines isolation and works in place: a record whose `base` equals
its `work` states no fact. Say in the report that the spec carries no `branch` record and why.

The record is `writeOnce: true`, and `specs.py record` enforces it: a second stamp refuses (exit 2)
naming the value already held. A later run **reads** it rather than rewriting it, and a current
branch that disagrees with `work` is a finding to report, never a value to correct. Never edit the
frontmatter to get past that refusal — the refusal is the rule, working.

**The record is not the signal.** A human may cut `plan/<slug>` by hand and stamp nothing, and a
record outlives the branch it names. Anything asking "is this spec in flight?" asks git for a live
ref — the record only supplies the ref's name when it is not the default.

## Commit messages

<!-- rules -->

The default subject, one per task:

```
plan/<slug>: <task-id> <task title>
```

```
plan/session-tokens: 3.2 Add rate limiting to the auth middleware
```

Three properties earn it: `git log --oneline` reads back as the spec's `## Tasks`; a subject
grepped by slug returns exactly that spec's commits; and the task id makes a `git revert` of one
task unambiguous. Wrap the title rather than truncating it, and keep the subject under 72
characters where the title allows.

The other subjects this front writes follow the same grammar:

```
plan/<slug>: merge (<strategy>)
plan/<slug>: record <what>
```

## The subject is the anchor

<!-- rules -->

The task→commit link is the **subject line of the commit**, written onto the task line by
`specs.py task --check --subject`:

```markdown
- [x] 3.2 Validate the token
      files: src/auth.py
      subject: plan/session-tokens: 3.2 Validate the token
```

It resolves by substring match:

```bash
git log --grep="<the recorded subject>" --fixed-strings
```

**The subject is known before the commit exists.** That is the whole reason it is the anchor, and
it has one consequence everywhere: every record is written *before* the thing it describes, so
nothing is left to write afterwards.

- `/quenching:specs:execute` ticks the box **first**, then commits the code and the ticked box together. One
  task is exactly one commit. The per-task bookkeeping commit is gone — it existed only because a
  sha cannot be known before the commit that carries it.
- `/quenching:specs:conclude` stamps `merge: {strategy, subject}` on the work branch, so the **merge is the
  last action of the run** and nothing is ever committed to the base branch after it.

**Two forms are read, forever.** A spec built before this change carries `commit: <sha>` and
resolves by sha. Neither form is backfilled: a recorded sha describes a commit that exists, and
rewriting an archived spec to "modernise" it would falsify when the record was made.

<!-- rationale -->

**Still no trailer and no machine-readable anchor inside the message.** The link is the subject the
target's own convention produced — if the repo's standard prefixes a ticket or appends a sign-off,
the recorded subject is whatever that convention actually wrote. The record follows; it never
imposes.

### Where the subject can fail, and what is done about it

A `commit-msg` hook that **replaces** the subject outright breaks the link. Substring matching
survives every hook that merely *adds* — a ticket prefix, a `Change-Id` trailer, a sign-off — which
is nearly all of them. After committing, `/quenching:specs:execute` compares `git log -1 --format=%s` against
what it recorded and **reports a mismatch as a finding, writing nothing**: a correction made after
the commit would reintroduce the very ordering this design removed.

## Merge strategies

<!-- rules -->

Offered by `/quenching:specs:conclude`, never chosen for the human. State the trade in one line each.

**Every one of them runs in the checkout that already holds the base**, located first and merged
into in place:

```bash
git worktree list --porcelain                 # which checkout holds <base>
git -C <that path> <the chosen command>
```

**Never `git checkout <base>`.** From inside a worktree it fails outright —
`fatal: '<base>' is already used by worktree at …`, exit 128 — so it is broken for exactly the
isolation recommended above. `git -C` is one path, not two special cases: from a worktree it names
the main checkout, from the main checkout it names itself. When no checkout holds the base,
`/quenching:specs:conclude` says so and stops without merging rather than manufacturing one.

| Strategy | Command | What it buys | What it costs |
| --- | --- | --- | --- |
| **merge commit** *(default)* | `git merge --no-ff plan/<slug>` | every per-task commit stays on the base branch and every recorded subject resolves from it | one extra commit, and the base branch's history carries the spec's task-level detail |
| **squash** | `git merge --squash plan/<slug>` then commit | one commit on the base branch; the spec reads as a single change | **the per-task commits live only on the branch** — deleting it leaves every recorded subject resolving to nothing |
| **rebase** | `git rebase <base> plan/<slug>`, then fast-forward | linear history, per-task commits preserved | rewrites every commit it moves — but a subject is carried along by the rewrite, so the records survive it |
| **fast-forward** | `git merge --ff-only plan/<slug>` | nothing is rewritten and nothing is added | only possible when the base has not moved |

Whatever is chosen is recorded as `merge: {strategy, subject}` and stated in `## Outcome`, because
a future reader resolving a task's subject needs to know which of these happened.

### When there is no merge commit to name

`fast-forward` and `rebase` create none, so the record carries an explicit none rather than a
fabricated pointer:

```yaml
merge:
  strategy: fast-forward
  subject: none — fast-forward creates no merge commit; the branch's commits ARE the
    base branch's history
```

Under both, the per-task commits land on the base directly and their subjects resolve there, so a
merge pointer would add nothing. `specs.py validate` reports the mismatched cases both ways — an
anchorless strategy carrying a real subject, and a merge-producing strategy carrying an explicit
none (`sp-bad-merge`).

### The squash caveat

A squash is the common house style and this file does not argue against it. It has one consequence
that must be said out loud rather than discovered later: **the per-task commits survive only on the
branch.** So when squash is chosen, `/quenching:specs:conclude` offers **not** to delete the branch, and says
why. Keeping it costs a ref; deleting it silently turns every `subject:` field in the archived spec
into a reference that resolves to nothing.

### Rebase is no longer the strategy that destroys the record

Under the sha anchor, rebase rewrote every recorded commit and left the archived spec's `commit:`
fields pointing at commits that no longer existed — it was the one strategy that made the record
strictly worse rather than merely narrower. A subject survives the rewrite, so a rebased branch's
records still resolve. Rebase now sits on the same footing as the others, and the old warning
applies only to specs still carrying the sha form.

### The worktree is removed after a successful merge

Isolation nobody cleans up accumulates: directories beside the repo, each pointing at an already
integrated branch, none of them obviously safe to delete. So once the merge exits 0,
`/quenching:specs:conclude` removes the worktree — from the base's checkout, because nothing removes the tree
it is standing in:

```bash
git -C <the base's checkout> worktree remove <the worktree path>
```

**Never `--force`.** `git worktree remove` refuses a tree holding modified or untracked files on
its own (`contains modified or untracked files`, exit 128), so the irreversible case is one git
already declines — no prompt buys safety here, and one always answered "yes" is only friction. A
clean tree leaves the disk silently; a refusal is reported with the path and git's own output, and
the worktree stays.

Three bounds: only after a merge verified at exit 0, never for an abandoned spec, and it does
**not** delete the branch — that stays the separate offer it already was.

## What is never done, on any repo

<!-- rules -->

This file owns two prohibitions, and both are about **whose** conventions win:

- **Never install `docs/standards/git/**` into a target.** See §The read-if-present rule. A default
  written into the repo stops being a default.
- **Never apply a convention the target did not declare and this file does not name.** A commit
  style inferred from reading `git log` is a guess, and a guess about house style is worse than the
  stated default — it looks deliberate.

Commit hygiene is not this file's to state: `--no-verify`, `--no-gpg-sign`, amending a commit,
force-pushing, `git init` on the human's behalf, and `git add -A` over a task's declared files are
all forbidden by
[specs-execute/execution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/specs-execute/execution.md) §The commit and
§The precondition, which own them. They bind every command that touches git here, including the
ones in this file.
