# Git conventions shared across the `git` pillar

The one home for the two things every command in the `git` pillar shares regardless of which git
operation it performs — whether a target's own conventions win before writing one, and the two
prohibitions that bind every git command on any repo. `isolation.md`, `commit.md`, `merge.md` and
`pr.md` each cite this file instead of restating either.

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
`quenching-knowledge-add`, on their word.

An `authority: background` git standard in the target still wins over these defaults. It is an
agreed-but-unproven rule someone wrote on purpose; that beats a plugin's opinion either way.

An omitted commit subject may use the default grammar only when the caller resolves exactly one
spec and one actionable task. An explicit subject takes precedence; missing or ambiguous context
refuses rather than guessing from the staged diff or recent history.

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
[specs-execute/execution.md](../../references/specs-execute/execution.md) §The commit and
§The precondition, which own them. They bind every command that touches git here, including the
ones in this pillar.

<!-- rationale -->

Writing `docs/standards/git/**` into a repository that
never asked for it is `quenching-specs-*` reaching into `quenching-knowledge-align`'s territory, and it converts a default
this file *offers* into a rule the repo now *declares* — which then wins over this file forever,
without anyone having agreed to it.

**On reporting which governed.** "Read the repo's `docs/standards/git/commit-messages.md`"
and "used the plugin default" are different facts about the same commit, and only one of them means
the human's convention was honoured.
