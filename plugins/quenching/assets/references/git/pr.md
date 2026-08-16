# The pull-request route

The route `/quenching:specs:conclude` offers alongside the merge strategy — pull request, or local —
and what running it does end to end: pushing the branch, opening the PR, merging it through `gh`,
and asserting the merge actually landed. Read
[conventions.md](${CLAUDE_PLUGIN_ROOT}/assets/references/git/conventions.md) first: the read-if-present
rule and the two prohibitions bind here too.

## Contents

`cq components read <this file>` returns the heading index; `--sections` addresses one.

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
vocabulary of its own —
[merge.md](${CLAUDE_PLUGIN_ROOT}/assets/references/git/merge.md) §Merge strategies is unchanged.
**`fast-forward` has no `gh` equivalent**,
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
default branch, and in a repo running the develop/main flow that default deliberately stays the
publication branch rather than the integration one. `<base>` is this spec's
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
