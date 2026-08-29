---
type: external
title: GitHub CLI measured behaviour
description: Measured facts about `gh` and the GitHub REST API's issue endpoints — the REST create's silent handling of an invalid Issue Type versus the porcelain commands' loud refusal for the same name, where Issue Types are actually defined, why `closingIssuesReferences` stays empty for a PR that targets an integration branch, and the three shapes a `--paginate --slurp` listing can take (`[[]]` for a genuinely empty one, `[]` for zero pages, and no output at all) plus the free `issues.totalCount` that corroborates them
resource: plugins/quenching/assets/bin/quenching/specs/**
tags: [github, gh-cli, rest-api, issue-types, closing-keywords, pagination, tooling]
timestamp: 2026-08-17
audience: both
authority: background
source: 'suportar-tipo-workitem-azure-por-tags spec (tasks 3.3, 3.4) — measured against holetz/claude-quenching#898, a personal-account repository, with `gh` as installed on 2026-08-07; pilar-git-e-specs-agnosticas-ao-git spec (task 1.1) — measured against holetz/claude-quenching PRs #925 and #926 and issue #816, on 2026-08-16; falha-de-leitura-do-backend-vira-front-vazio spec (task 4.2) — measured against holetz/claude-quenching and holetz/nixos with `gh 2.97.0 (2026-07-31)`, on 2026-08-17'
maintainer: quenching
---

# GitHub CLI measured behaviour

Facts about **how `gh` and the GitHub REST issue endpoints actually behave**, measured live rather
than read from documentation. External tool behaviour, not our contract — how this plugin's
`github` backend uses `gh` is
[standards/architecture/spec-backend.md](../../standards/architecture/spec-backend.md).

## Issue Type: the REST create silently drops an invalid name, the porcelain commands refuse

**`gh api -X POST repos/<owner>/<repo>/issues` with a `type` field in the JSON payload neither
applies nor refuses an unknown Issue Type name.** A create posted with `"type": "Nonexistent"`
against a repository that has no such type came back `ok: true`, a real issue number, and
`issueType: null` on the created issue — no error, no field in the response naming what went
wrong. The call looks identical, at the transport layer, to a create that named no type at all.

**`gh issue create --type <name>` and `gh issue edit --type <name>` — the porcelain commands —
both validate the name against the repository's own declared Issue Types and refuse loudly for
the same input:** `type "<name>" not found; available types: `. The REST endpoint the porcelain
commands call underneath is the same one `gh api` reaches directly; the validation lives in the
porcelain layer, not in the endpoint itself.

**The practical consequence: a `type` key on a hand-built REST payload is not a substitute for the
porcelain flag, even though both reach the same API.** A caller that wants a refusal for a bad
name — rather than a silently untyped issue — has to call `gh issue create --type` or
`gh issue edit --type`, never assemble the field into a `gh api` body by hand.

## Issue Types are declared at the ORGANIZATION, not the repository

Issue Types are a GitHub feature configured per-organization; a personal-account repository (the
one this was measured against) has none available, which is itself why the invalid-name refusal
above was the only branch reachable in that account — there was no valid name to test the
accepting path against. An organization repository with Issue Types configured is expected to
accept a declared name and refuse an undeclared one identically through either porcelain command;
that branch was not independently measured here.

## `closingIssuesReferences` stays empty when the PR's base is not the repository's default branch

**A `Closes #<n>` line in a PR body only populates `closingIssuesReferences` — and only auto-closes
the issue on merge — when the pull request's base branch is the repository's default branch.**
Against a PR opened with any other base (an integration branch, say), the same keyword still
creates a plain cross-reference (visible on the issue's timeline as a `cross-referenced` event) but
never a closing link: `gh pr view --json closingIssuesReferences` and the equivalent GraphQL field
both come back an empty list, `gh api .../issues/<n>/timeline` shows the issue's `closed` event with
no `source` and no `commit_id` attached, and the issue itself has to be closed some other way.

Measured against two merged PRs in `holetz/claude-quenching` — a repository whose default branch is
`main` but whose PRs are opened against `develop`
([standards/git/branching.md](../../standards/git/branching.md)): PR #926's body reads
`Closes #816`, PR #925's reads `Closes #902`, both target `develop`, and both report
`"closingIssuesReferences": []`. Issue #816's timeline carries a `cross-referenced` event sourced
from #926 and a `closed` event with `"source": null` — the mention linked, the close did not.

**The practical consequence: a plugin that reads `closingIssuesReferences` back to learn whether a
PR closes a spec's issue gets a structurally empty answer for any repository whose specs merge into
an integration branch rather than the default branch** — which is exactly the shape
[standards/git/branching.md](../../standards/git/branching.md) prescribes (`develop` integrates,
`main` publishes) and this repository's own history already follows. The keyword still documents
intent in the PR body and still cross-references the issue; it does not, by itself, give a caller
anything to read back on that class of repository.

## `--paginate --slurp` distinguishes "no pages" from "one empty page", and `gh` can exit 0 printing nothing

**A listing that legitimately holds nothing comes back as `[[]]` — one page, empty — and never as
`[]`.** `--slurp` wraps each page in an outer array, so the outer array's length is the number of
HTTP responses that arrived, not the number of items found. Zero pages therefore means zero
responses: not an empty front, but a response that did not happen.

Measured on `gh 2.97.0 (2026-07-31)`, against `holetz/claude-quenching`:

| Command | Output |
| --- | --- |
| `gh api --paginate --slurp "repos/holetz/claude-quenching/issues?state=all&per_page=100&labels=zzz-nao-existe"` | `[[]]` — one page, empty |
| `gh api --paginate --slurp "repos/holetz/claude-quenching/issues?state=all&per_page=100"` | two pages, 100 and 95 items |

Re-confirmed on a second repository the same day: `holetz/nixos`, which has no issues at all,
answers `[[]]` for the unfiltered listing too.

**The third shape is the one no output can carry: `gh` exiting 0 having printed nothing at all.**
Any caller that parses with the `json.loads(out or "null")` idiom turns that into a valid `null`,
and a `null` iterated as a listing yields zero items — a failed read laundered into the statement
that there is nothing there. The exit code says success, so nothing downstream has any reason to
doubt it.

Together the three shapes are what make the emptiness *decidable* on this transport: `None` and
`[]` prove a fault, `[[]]` does not. The rule built on them is
[standards/quality/empty-response-honesty.md](../../standards/quality/empty-response-honesty.md);
the measurement is here because it is a fact about `gh`, and it holds only for the version it was
taken against.

**`gh repo view --json issues` answers `issues.totalCount` on the call that already resolves the
repository name**, and it counts issues only — GitHub's `issues` connection excludes pull requests.
Measured the same day: `gh repo view --json nameWithOwner,issues` on `holetz/claude-quenching`
returns `{"issues":{"totalCount":38},"nameWithOwner":"holetz/claude-quenching"}`, and 38 is exactly
what `gh issue list --state open` reports. A caller that already makes that call can corroborate an
empty listing at no extra round trip.
