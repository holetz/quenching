# Git for the `specs/` front — taking isolation, wording a commit, merging

The owner of **how** a spec's work is isolated, how its commits are worded, and how the branch
comes home. `/quenching:specs:execute` performs the isolation, inline on its way into a build;
`/quenching:specs:conclude` cites this file for the conventions its own steps depend on.

Everything here is a **default**, not a rule. A target repo that has written down its own git
conventions has already decided, and a plugin that ignored that would be imposing house style on
somebody else's history.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

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

State in the report which one governed.

**Never install a git standard into a target.** Not as a fixup, not as a suggestion applied, not
"so the next run has something to read". If a human wants their conventions written down, that is
`/quenching:knowledge:add`, on their word.

An `authority: background` git standard in the target still wins over these defaults. It is an
agreed-but-unproven rule someone wrote on purpose; that beats a plugin's opinion either way.

## Isolation happens on the way into a build

<!-- rules -->

Isolation was a command of its own for one release, offered at any stage. It is now a **step inside**
`/quenching:specs:execute`, taken once, before the first task is written — and offered only when the
session is standing on the repository's base branch:

| Where the session stands | What `execute` does |
| --- | --- |
| **on** the spec's work ref | nothing — the spec is isolated, and the loop starts |
| on any other non-base branch | **adopts it** as `work`, stamps `branch:`, and starts the loop |
| on the base, work ref alive and unclaimed | offers to **take** it — worktree over it, or checkout — and stamps nothing |
| on the base, no work ref | offers worktree · branch · in place, and stamps whichever was taken |

Standing anywhere but the base means the human already answered the isolation question at checkout,
so asking again buys nothing and costs the turns it takes. Isolation stays optional, is recommended
before building, and is never imposed.

**Isolated means "this checkout is on the work ref", never "the ref exists".** The two come apart in
one ordinary case — the base checked out, `plan/<slug>` sitting one branch over from an earlier
session, nobody holding it — and treating existence as the answer sends the loop to build and commit
onto the base, which is precisely what the offer is for. The work ref itself is the `branch` record's
`work` when one is stamped, else `plan/<slug>`; a live ref held by another worktree is a **stop**,
not an offer, because two checkouts building one spec fork it.

`/quenching:specs:create` and `/quenching:specs:develop` take no branch at all — they write into
`plans/` and stay wherever they were run. That is a narrowing from the retired command, and the
trade is deliberate: the offer costs a confirmation, and the stage where it reliably pays is the one
about to write code.

**Asking "am I isolated?" writes nothing and is answered elsewhere.** `/quenching:specs:continue`
reads the live ref and reports it, and demotes a spec whose branch is checked out somewhere else.
`/quenching:specs:status` reads the frontmatter records and deliberately never asks git.

**Merging is not here.** It stays inside `/quenching:specs:conclude`, behind that command's review and
archive gates — a merge invocable on its own could run against a spec nobody reviewed and nothing
archived, and would have to duplicate every refusal `conclude` already owns.

<!-- rationale -->

**On `plan/<slug>` as the default name.** A branch named to it is greppable against `cq specs list`,
and `git branch --list 'plan/*'` is the list of work cut by the default. A human who already checked
out `fix/isolate-flow` or `123-my-branch` before running `execute` gets that branch recorded, not a
second one cut beside it.

**On putting the worktree beside the repo.** Inside the repo it lands in the tree the spec is about
to change, and shows up in every `git status`, every glob, and every checker this plugin runs. A
worktree leaves the main checkout untouched, which is what lets several specs be built at once and
what keeps satisfying the clean tree the loop demands of itself. A recommendation that changes from
repo to repo cannot be documented in one sentence, and guessing somebody else's build is how a
recommended path becomes a silent trap. So choosing Branch is a decision the human read rather than
a discovery at the first `verify:` that fails.

**The home moved, and the move is the point.** This used to be `specs/config.json`, at the root of
the specs workspace — which only had a place to live while every repo was guaranteed a `specs/`
folder. A repo that declares an external backend may hold no `specs/` at all, so the plugin's
configuration lives in one neutral home shared by all three fronts, and `worktreeSetup` moved there
with the rest of it. Whether the command resolves can only be judged against the new worktree's
path, which `cq specs` is never told.

**On stamping `branch:` for a branch this plugin never cut.** A human may have checked one out by
hand before running `execute`, and a spec built there with nothing stamped leaves
`/quenching:specs:conclude` unable to say what it merges into.

**On removing the worktree after a merge.** Isolation nobody cleans up accumulates: directories
beside the repo, each pointing at an already integrated branch, none of them obviously safe to
delete.

## Branch and worktree names

<!-- rules -->

```
plan/<slug>
```

The **suggested default** when the inline offer cuts a new branch or worktree — kebab-case, no
date prefix, no id. `cq specs next --front` ranks on whether
`plan/<slug>` is **alive**, so a branch named to the default is what tells `/quenching:specs:continue` this
spec is already under way without a stamped `branch` record.

**The name is a suggestion, never a contract.** When `/quenching:specs:execute` starts on a branch that is not
the repository's base — whatever it is named — that branch is **adopted** as `work` outright: no
rename, no refusal, and no requirement that it match `plan/<slug>`.

A worktree goes beside the repo, never inside it:

```bash
git worktree add ../<repo>-<slug> -b plan/<slug>
```

### The worktree is the preferred form

<!-- rules -->

`/quenching:specs:execute`'s inline isolation offer leads with **Worktree and recommends it**, unconditionally — a
plain branch and working in place stay available, in that order after it.

**Unconditionally** means no heuristic sniffing the target for `package.json` or `.venv/`. What is
offered instead is the **cost, stated in the offer itself**: a fresh checkout carries only what git
tracks — no installed dependencies, no `.env`, no venv, no build output.

### A target may declare a setup command

<!-- rules -->

`.claude/quenching.json`, at the repo root, under the `worktreeSetup` key:

```json
{"backend": "files", "worktreeSetup": "./scripts/wt-setup.sh"}
```

See
[plugin-configuration.md](../../../../../.docs/standards/workflows/plugin-configuration.md).

Read by `cq specs config --json` (exit 0 whether or not anything is declared) and run **once** by
the inline offer, immediately after `git worktree add`, with **cwd inside the new worktree** — the
tree lacking the dependencies is the tree that must install them. `cq specs` reads the value and
never executes it.

No file, no key, or a command that does not resolve all mean **no setup**, and none of them is a
finding — most repos declare nothing, and declaring nothing must cost nothing. `cq specs doctor`
reports only the two ways it can be *wrong*, both `warn`: `sp-config-unknown-key` and
`sp-config-unparseable`. They exist for the one real failure mode of a machine-read config —
`worktree_setup` written where `worktreeSetup` was expected, and silence afterwards.

**Its consent is the isolation offer.** The command is displayed **verbatim** in `/quenching:specs:execute`'s
isolation-offer block, and choosing Worktree is the OK for it: no second prompt, no remembered
authorisation. A failing setup is reported and **never undoes the worktree**.

## Recording the isolation

<!-- rules -->

```bash
cq specs record <slug> branch --set base=main --set work=plan/<slug>
```

`base` is whatever was checked out when the branch was cut. It is **not** assumed to be `main`.
`work` is derivable from `git branch --show-current` while the branch is checked out; `base` is
not — **after the merge, git cannot say what the branch was cut from**, which is the whole reason
the record exists and why it is captured while still true.

**Every branch that is not the repository's base gets `branch:` stamped**, including one this
plugin never cut.
Stamp nothing only in the true in-place case: the human declined isolation and stayed on the base
branch, where a record whose `base` equals its `work` would state no fact.

**For a branch this plugin cuts, `base` is an observed fact** — it was what stood checked out the
moment the branch was created. **For a branch it adopts, `base` is inferred**, in this order,
stopping at the first that answers:

1. the spec's own `branch.base` record, when one already exists;
2. `git symbolic-ref refs/remotes/origin/HEAD` — the default the remote declares;
3. `git config init.defaultBranch`, and then `main`.

**Show the inference on the same line as the confirmation, before stamping** —
`base: main — inferred; this branch was not cut by this command` — because the record is
write-once and that is the only moment disagreeing with it is cheap. Never derive `base` from
`git merge-base` or `--fork-point`: both answer a **commit**, not a branch name, and a commit
ancestral to three branches identifies none of them.

The record is `writeOnce: true`, and `cq specs record` enforces it: a second stamp refuses (exit 2)
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

Wrap the title rather than truncating it, and keep the subject under 72
characters where the title allows.

The other subjects this front writes follow the same grammar:

```
plan/<slug>: merge (<strategy>)
plan/<slug>: record <what>
```

## The subject is the anchor

<!-- rules -->

The task→commit link is the **subject line of the commit**, written onto the task line by
`cq specs task --check --subject`:

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

**Still no trailer and no machine-readable anchor inside the message.**

<!-- rationale -->

The link is the subject the
target's own convention produced — if the repo's standard prefixes a ticket or appends a sign-off,
the recorded subject is whatever that convention actually wrote. The record follows; it never
imposes.

**On the default subject `plan/<slug>: <task-id> <task title>`.** Three properties earn it: `git log
--oneline` reads back as the spec's `## Tasks`; a subject grepped by slug returns exactly that
spec's commits; and the task id makes a `git revert` of one task unambiguous.

Under the sha anchor, rebase rewrote every recorded commit and left the archived spec's `commit:`
fields pointing at commits that no longer existed — it was the one strategy that made the record
strictly worse rather than merely narrower.

**On `fast-forward` and `rebase` recording an explicit none.** Under both, the per-task commits land
on the base directly and their subjects resolve there, so a merge pointer would add nothing.

Stopping at the open PR is simpler and is wrong for two reasons, both contracts this file and
[plan-git-record.md](../../../../../.docs/standards/workflows/plan-git-record.md) already state. `## Outcome` is
written before the merge and says what the run **delivered** — an open, unmerged PR archived as
`done` would assert something that has not happened yet. And `merge:` is stamped before the merge
so that it is the run's last action; a run that ends before the merge leaves the record stamped and
nothing merged, which is recoverable but is not what "the merge is last" promises.

### Where the subject can fail, and what is done about it

<!-- rules -->

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

<!-- rules -->

`fast-forward` and `rebase` create none, so the record carries an explicit none rather than a
fabricated pointer:

```yaml
merge:
  strategy: fast-forward
  subject: none — fast-forward creates no merge commit; the branch's commits ARE the
    base branch's history
```

`cq specs validate` reports the mismatched cases both ways — an
anchorless strategy carrying a real subject, and a merge-producing strategy carrying an explicit
none (`sp-bad-merge`).

### The squash caveat

<!-- rules -->

**The per-task commits survive only on the
branch.** So when squash is chosen, `/quenching:specs:conclude` offers **not** to delete the branch, and says
why. Keeping it costs a ref; deleting it silently turns every `subject:` field in the archived spec
into a reference that resolves to nothing.

### Rebase is no longer the strategy that destroys the record

<!-- rules -->

A subject survives a rebase's rewrite, so a rebased branch's
records still resolve. Rebase now sits on the same footing as the others, and the old warning
applies only to specs still carrying the sha form.

### The worktree is removed after a successful merge

<!-- rules -->

Once the merge exits 0,
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

## The pull-request route

<!-- rules -->

`/quenching:specs:conclude` offers a **route** — pull request, or local — **alongside** the strategy, not instead
of it. The route decides how the merge reaches the base; the strategy decides what shape it takes
once it does. Offered only where `gh` resolves the repository — no route, no offer, on any other
host or with `gh` unauthenticated.

```
gh pr merge --merge      # strategy: merge commit
gh pr merge --squash     # strategy: squash
gh pr merge --rebase     # strategy: rebase
```

Three of the four strategies map one-to-one onto a `gh pr merge` flag, so the PR route invents no
vocabulary of its own — `MERGE_STRATEGIES` is unchanged. **`fast-forward` has no `gh` equivalent**,
so the PR route is never offered under it; choosing that strategy answers the route question by
itself, in one line, rather than offering a form that would fail.

**Pushing the branch and opening the PR carry their own confirmation.** The route chosen at the
offer above is not the OK for either — both publish to a remote host, which the local strategies
never do. The block that runs them shows the remote, the name the branch pushes under, and the
PR's title and body, and asks there:

```bash
git push -u origin plan/<slug>
gh pr create --base <base> --title "<title>" --body "<body>"
```

**`--base <base>` is never omitted.** `gh pr create` without it targets the repository's GitHub
default branch, and in a repo running the develop/main flow
([docs/standards/git/branching.md](/.docs/standards/git/branching.md)) that default deliberately
stays the publication branch — see that standard's own reasoning for why. `<base>` is this spec's
own resolved base, the same value the local route's merge targets.

**The PR route concludes the merge; it does not stop at the PR being opened.** `gh pr merge` runs
in the same block, before the run reports done:

```bash
gh pr merge <number> --merge|--squash|--rebase
```

**The merge is asserted, not assumed.** After `gh pr merge` returns, the run confirms the base
actually advanced before reporting success:

```bash
git -C <the base's checkout> pull --ff-only
gh pr view <number> --json state,mergeCommit
```

`git pull --ff-only` first, because the base's local checkout has no reason to know about a merge
that happened on the remote until it is told; `gh pr view` then reads back `state: MERGED` and the
resulting `mergeCommit`, which is what `merge: {strategy, subject, pr}` records — `pr` alongside
the strategy and subject a local conclusion already carries.

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

<!-- rationale -->

Writing `docs/standards/git/**` into a repository that
never asked for it is `/quenching:specs:*` reaching into `/quenching:knowledge:align`'s territory, and it converts a default
this file *offers* into a rule the repo now *declares* — which then wins over this file forever,
without anyone having agreed to it.

**On reporting which governed.** "Read the repo's `docs/standards/git/commit-messages.md`"
and "used the plugin default" are different facts about the same commit, and only one of them means
the human's convention was honoured.
