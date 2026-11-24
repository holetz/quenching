---
type: standard
title: Spec claims contract
description: A build reserves its spec with a lease on the `origin` (`refs/quenching/claims/<id>`, compare-and-swap by push), so two machines never build the same spec — only execute acquires, it renews per task, conclude, a blocked or failed runner and the autopilot's round end release, the reconcile deletes terminal leases, an expired lease frees itself, and taking a live one is the human's call
resource: quenching/assets/bin/quenching/specs/claims.py, quenching/assets/bin/quenching/specs/commands/claim.py, quenching/assets/bin/quenching/specs/commands/reconcile.py, quenching/skills/quenching-specs/references/execute.md, quenching/skills/quenching-specs/references/conclude.md, quenching/skills/quenching-specs/references/autopilot.md, quenching/agents/spec-runner.md, quenching/agents/spec-orchestrator.md
tags: [workflows, specs, claims, lease, autonomy]
timestamp: 2026-11-24
audience: both
authority: current
source: epic 404 (specs 405, 406, 407), reservation of specs across machines
maintainer: quenching
---

# Spec claims contract

<!-- rules -->

Two machines running `/quenching-specs autopilot --until-dry` on the same repository would pick the
same spec: nothing one machine does is visible to the other until a push. A **claim** is the build's
reservation of a spec, written where every machine reads — the `origin` — and it must never hold a
spec hostage: a claim nobody releases frees itself, and nothing but a build takes one.

## The lease

The claim is the ref `refs/quenching/claims/<id>` on the `origin`: a parentless commit whose tree
holds one `lease.json` (`spec`, `holder`, `stage`, `acquired`, `renewed`, `expires`, optional
`label`). Creating, replacing and deleting it are pushes with `--force-with-lease`, so the server
compares and swaps and two writers never both win; the same ref lives locally (`git update-ref`
with the expected old value) when there is no remote. It is the same for the git, GitHub and Azure
backends, it never enters the store's history, and it never conflicts with a document write.

- **Holder.** `<machine>:<session>`: the machine is a random id generated once into
  `git config --local quenching.machineId`, the session is `OPENCODE_SESSION_ID` or
  `CLAUDE_SESSION_ID`. Never a hostname or an email: the ref goes to the remote. A `label` is
  declared by the user, never inferred.
- **Mine.** A lease is *mine* when its machine is this one, whatever the session, so a re-spawn
  is never locked out by its own lease.
- **Validity, not vigilance.** A lease expires `shared.autonomy.claimMinutes` (45) after its last
  renewal, with a 2-minute clock tolerance; a dead holder frees the spec when it expires.
- **Terminal.** A lease of an archived spec, or one carrying an `outcome` or `merge` record, is
  ignored by every reader.

The verb is `cq specs claim acquire|renew|release|take|list <id>`: exit 0 ok, 1 held by another
machine or the compare-and-swap lost, 2 git could not answer.

## Who acquires, renews and releases

Only the **build** reserves. `create`, `develop`, `triage` and `status` never do, so a spec
developed by one person and handed to another to build carries no lock.

| Moment | Who | Action |
| --- | --- | --- |
| before the worktree is cut or adopted | `/quenching-specs execute` step 2 | `acquire`; exit 1 stops with `held-by: <holder> until <expires>` |
| after every task tick | `/quenching-specs execute` 5e | `renew`; `not-holder` stops |
| at its opening | `/quenching-specs conclude` step 1 | `renew`; `not-holder` stops |
| before each wave | `spec-orchestrator` | `renew` for every live worker's spec |
| after the handoff (`done`) or the archive (`abandoned`) | `/quenching-specs conclude` step 7 | `release` |
| returning `blocked` or `failed` | `spec-runner` | `release` |
| end of a round | `/quenching-specs autopilot` step 7 | `release` of every `mine` lease on the round's specs |
| any post-merge close | `cq specs reconcile --write` | deletes the lease of every terminal spec, by compare-and-swap with the sha it read |

A git that cannot answer (exit 2) is reported and the build goes on unreserved: the claim protects,
it never blocks a build because the remote is unreachable. A `claims` check in `fail` from
`cq git preflight` means the remote refuses the refs, and the run says another machine could pick
the same spec.

## Choosers

`cq specs next --front` leaves out a spec with a live lease of another machine
(`claimedExcluded`, `--include-claimed` lists it); `list --lean` and `status --json` carry the
`claim`. The `spec-orchestrator` never schedules such a spec (`STATE: blocked`, `NOTE: held-by:`),
and the autopilot keeps it out of the round's queue. An expired, terminal or unreadable lease
(`claim: null`) never keeps a spec out.

## Taking a live lease

`take` replaces a live lease of another machine, and it is **the human's call only**: asked on a
decision sheet in an interactive run, returned as `needs-human: held-by: <holder>` by a sub-agent,
and recorded in the spec's `## Discoveries` with who was taken. The autopilot and the orchestrator
take only an expired lease, which `acquire` already does.

## Grants

`Bash(cq specs claim:*)` is granted in the `tools:` of the `spec-orchestrator` (for `renew`) and
the `spec-runner`, and nowhere else; the commands that call it already hold `Bash(cq:*)`.

<!-- rationale -->

## Why a ref and not a record

A `claim` record in the store would be local until the next sync, only the git backend has a
compare-and-swap, and the sync refuses a same-spec conflict with the whole document. An `assignee`
is a human field with no validity and no compare-and-swap on GitHub. A ref on the `origin` is the
one place every backend shares and the server compares.
