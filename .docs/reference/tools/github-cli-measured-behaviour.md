---
type: reference
title: GitHub CLI measured behaviour
description: Measured facts about `gh` and the GitHub REST API's issue endpoints — the REST create's silent handling of an invalid Issue Type versus the porcelain commands' loud refusal for the same name, and where Issue Types are actually defined
resource: plugins/quenching/assets/bin/quenching/specs/**
tags: [github, gh-cli, rest-api, issue-types, tooling]
timestamp: 2026-08-07
audience: both
authority: background
source: suportar-tipo-workitem-azure-por-tags spec (tasks 3.3, 3.4) — measured against holetz/claude-quenching#898, a personal-account repository, with `gh` as installed on 2026-08-07
maintainer: quenching
---

# GitHub CLI measured behaviour

Facts about **how `gh` and the GitHub REST issue endpoints actually behave**, measured live rather
than read from documentation. External tool behaviour, not our contract — how this plugin's
`github` backend uses `gh` is
[standards/architecture/spec-backend.md](/.docs/standards/architecture/spec-backend.md).

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
