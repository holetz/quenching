# `standards/git/`

How this repository uses git — long-lived branches, the publication trigger, and the conventions
`/quenching:specs:execute` / `/quenching:specs:conclude` read as read-if-present.

**Boundary:** the branch and publication *flow* lives here; the version lockstep that publication
moves lives in [../ci-cd/](../ci-cd/index.md); one spec's own task→commit record lives in
[../workflows/](../workflows/index.md). One standard per file; each carries `type:
standard` + a derived `resource:`; add each to [../index.md](../index.md).

## Current docs

* [branching.md](branching.md) — One long-lived branch — the primary (main) — where every PR
  merges and review lives, the release as a deliberate local act that bumps, tags and publishes
  what the primary accumulated, the trigger on demand and with no cadence, the question that
  pushes toward grouping when the primary carries a single PR since the last tag, and the
  transition for anyone coming from the two-branch flow

## Candidate sub-standards

Break this subject **one concept per file**. The method evaluates each candidate against
the repo, generates the applicable ones (`file:line`-anchored, full OKF frontmatter), and
records the rest below as deferrals (never a silent skip):
`branching` · `commit-conventions` · `tagging`.

## Coverage / deferred sub-standards

Per-subject ledger the verify gate reads. A subject is "done" only when every candidate is
**present or listed here** with a one-line why.

- `branching` — **present**: [branching.md](branching.md).
- `commit-conventions` — **deferred, not applicable.** With no `/docs/standards/git/**` on commit
  messages, `/quenching:specs:execute` already applies the plugin's default
  (`plugins/quenching/assets/references/git/commit.md` §Commit messages); writing one here would
  turn that default into a contract of this repository without anyone having asked for it.
- `tagging` — **deferred, covered by `versioning-release.md`.** The tag is created by the same
  `cq specs release` verb that moves the lockstep;
  [../ci-cd/versioning-release.md](../ci-cd/versioning-release.md) already documents it as part of
  the lockstep, and a standard of its own would duplicate that section.
