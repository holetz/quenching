---
type: decision
title: Security review of the epic 1145 changes
description: The read-only security verdict, per merged PR, for the sensitive changes that landed while the security hook did not resolve
resource: docs/decisions/index.md
tags: [decision, security, review]
timestamp: 2026-10-07
audience: both
authority: current
source: spec 1171
maintainer: quenching
---

# Security review of the epic 1145 changes

While the declared security hook did not resolve (fixed in spec 1167), no spec of epic 1145 had a
security review. This is the manual one, read from each merge's `^1..^2` diff. It changed nothing:
what it found outside its scope is a spec discovery.

| PR | Surface | Verdict |
| --- | --- | --- |
| #1162 | `ci.yml`, `release.md`, `verify_repo.sh`, `functional-checks.sh` | Accepted, one finding |
| #1160 | `schema.py`, orchestrator and spec-runner agents, develop/improve/orchestrate | Accepted |
| #1161 | `cq_calls.py`, `lint.py`, `knowledge/cli.py` | Accepted |
| #1159 | orchestration agents, `orchestrate.md` | Accepted |

## #1162 — workflow, shell, release

- `ci.yml` keeps the top-level `permissions: contents: read` and only loses the surface-load step;
  no permission, secret or trigger was added. The `delivery-permission-policy` finding ("workflow
  permissions require the read-only security audit") is the Judgement band asking for this review:
  the declaration is the least-privilege minimum, so it is accepted.
- `verify_repo.sh` spawns billed `claude -p` sessions only with `QUENCHING_FUNCTIONAL=1`; nothing
  else changed in its execution.
- **Finding:** `release.md` gained `allowed-tools: Bash(bash:*)`, wider than the one script it
  needs (`bash scripts/verify_repo.sh`). Not fixed here; parked as a discovery of spec 1171.

## #1160 — the human approval gate

`approved.by` accepts `orchestrator-forced` beside `human` and `low-gear`; `writeOnce` and
`writtenBy: develop` are untouched. The value can be self-declared by any `cq specs record` caller,
exactly as `low-gear` already could: the stamp is an audit trail, not an authorization, and the
gate that matters (a human answering) was not weakened. Accepted.

## #1161 — parsing of text

`cq_calls.py` loads the plugin's own `cq` entry and pillar parsers (from its own `_BIN_DIR`) and
only compares calls found in command and agent bodies against them. No extracted text is executed,
evaluated or passed to a shell; `lint.py` is read-only. Accepted.

## #1159 — what each agent may run

The only grant added is `Bash(cq specs epic add:*)` for `spec-architect`. No agent gained `git`,
`gh` or unrestricted Bash. Accepted.
