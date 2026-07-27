# Git conventions — defaults the target repo may override, and never inherits

The owner of **how** `/specs:execute` and `/specs:conclude` name a branch, word a commit, and merge
a spec's work. Both bodies cite it; neither restates it.

Everything here is a **default**, not a rule. A target repo that has written down its own git
conventions has already decided, and a plugin that ignored that would be imposing house style on
somebody else's history.

## The read-if-present rule

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
never asked for it is `/specs:*` reaching into `/docs:align`'s territory, and it converts a default
this file *offers* into a rule the repo now *declares* — which then wins over this file forever,
without anyone having agreed to it. If a human wants their conventions written down, that is
`/docs:add`, on their word.

An `authority: background` git standard in the target still wins over these defaults. It is an
agreed-but-unproven rule someone wrote on purpose; that beats a plugin's opinion either way.

## Branch and worktree names

```
plan/<slug>
```

The spec's slug, unaltered — kebab-case, no date prefix, no id. The slug is the identity every
command names, so a branch that carries it verbatim is greppable against `specs.py list`, and
`git branch --list 'plan/*'` is the list of work in flight.

A worktree goes beside the repo, never inside it:

```bash
git worktree add ../<repo>-<slug> -b plan/<slug>
```

Inside the repo it lands in the tree the spec is about to change, and shows up in every `git
status`, every glob, and every checker this plugin runs.

`base` is whatever was checked out when the branch was cut. It is not assumed to be `main` — that
is precisely why it is captured into `branch: {base, work}` at the moment it is still true
([execution.md](execution.md) §Recording the isolation).

## Commit messages

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

**No trailers, and no machine-readable anchor inside the message.** The task-to-commit link is the
`commit:` field on the task line, written by `specs.py task --check --commit`. Storing it there
rather than in the message is what leaves the message format entirely the target repo's to decide —
a repo with Conventional Commits, a ticket prefix, or a required sign-off keeps all of it, and the
link still resolves.

Bookkeeping commits — the ones that carry only a ticked box, a stamped record, or a regenerated
listing zone — use the same prefix and say what they are:

```
plan/<slug>: record <task-id>'s commit
```

They exist because the spec file is edited *after* the task's commit is made, and folding that edit
into the task's own commit would mean amending it. That is forbidden
([execution.md](execution.md) §The commit), and for good reason: the recorded sha would change
under the record that names it.

## Merge strategies

Offered by `/specs:conclude`, never chosen for the human. State the trade in one line each:

| Strategy | Command | What it buys | What it costs |
| --- | --- | --- | --- |
| **merge commit** *(default)* | `git merge --no-ff plan/<slug>` | every per-task commit stays on the base branch and every `commit:` sha resolves forever | one extra commit, and the base branch's history carries the spec's task-level detail |
| **squash** | `git merge --squash plan/<slug>` then commit | one commit on the base branch; the spec reads as a single change | **every per-task sha lives only on the branch** — deleting it strands every `commit:` record |
| **rebase** | `git rebase <base> plan/<slug>`, then fast-forward | linear history, per-task commits preserved | **every sha is rewritten**, so every `commit:` record is stale the moment it lands |
| **fast-forward** | `git merge --ff-only plan/<slug>` | nothing is rewritten and nothing is added | only possible when the base has not moved |

Whatever is chosen is recorded as `merge: {strategy, commit}` and stated in `## Outcome`, because a
future reader resolving a `commit:` sha needs to know which of these happened.

### The squash caveat

A squash is the common house style and this file does not argue against it. It has one consequence
that must be said out loud rather than discovered later: **the per-task shas survive only on the
branch.** So when squash is chosen, `/specs:conclude` offers **not** to delete the branch, and says
why. Keeping it costs a ref; deleting it silently turns every `commit:` field in the archived spec
into a dead reference.

### Rebase and the recorded sha

Rebasing rewrites every commit it moves, so the shas recorded during execution no longer exist.
Offer it only when the human asks for it by name, and say plainly that the archived spec's
`commit:` fields will point at commits that are gone. It is the one strategy that makes the record
worse rather than merely narrower.

## What is never done, on any repo

This file owns two prohibitions, and both are about **whose** conventions win:

- **Never install `docs/standards/git/**` into a target.** See §The read-if-present rule. A default
  written into the repo stops being a default.
- **Never apply a convention the target did not declare and this file does not name.** A commit
  style inferred from reading `git log` is a guess, and a guess about house style is worse than the
  stated default — it looks deliberate.

Commit hygiene is not this file's to state: `--no-verify`, `--no-gpg-sign`, amending a recorded
commit, force-pushing, `git init` on the human's behalf, and `git add -A` over a task's declared
files are all forbidden by [execution.md](execution.md) §The commit and §The precondition, which
own them. They bind every command that touches git here, including the ones in this file.
