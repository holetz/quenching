---
type: standard
title: Read-only views are their own command
description: A front's read-only view is a separate command holding no write tools, never a dry-run mode on the command that writes — because allowed-tools is granted per command, so a mode flag can only ever be a promise the grant does not enforce
resource: plugins/quenching/commands/knowledge/status.md, plugins/quenching/commands/specs/status.md
tags: [architecture, commands, read-only, status, tool-grants]
timestamp: 2026-08-11
audience: both
authority: current
source: docs-verification-layer spec (§Design)
maintainer: quenching
---

# Read-only views are their own command

Every front has a command that **writes** (its align) and a command that **reads** (its status).
They are two files, and the reason is a tool grant rather than tidiness.

## The rule

A read-only view of a front is **its own command**, whose `allowed-tools` contains no `Write` and
no `Edit`, and whose `Bash` is scoped to the front's own verifier. It is never a flag, a mode, or a
`--dry-run` on the command that writes.

## Why a mode flag cannot carry the guarantee

`allowed-tools` is granted **per command, not per invocation**. An align holds `Write` and `Edit`
because aligning is what it does — so a read-only mode inside it would be enforced only by the
body's own prose, while the grant that could actually stop a write stays open for the whole run.
Read-only that depends on the model honouring an instruction is not read-only; it is an intention.

Splitting the command moves the guarantee out of the prose and into the grant, where the failure
mode is impossible rather than merely discouraged. This is the same argument as
[plugin-layout.md](plugin-layout.md)'s — a structural rule beats a remembered one — applied to
tool grants instead of to the directory tree.

## What the read command therefore owns, and does not

- **It owns no contract.** It reports in the vocabulary of the front's own verifier
  (`cq knowledge`, `cq specs`, `cq components`) and cites the references defining each code,
  restating none. Two read paths that must agree is exactly the duplication this plugin avoids
  everywhere else.
- **It splits findings by what closes them** — what the front's align fixes, what a cycle command
  closes, what neither closes. That split is what makes it an honest dry run before the align's one
  OK, delivered without holding the tools to perform one.
- **It may report figures that carry no finding code** — bundle density, task progress, surface
  cost. A writing command has no natural place for a figure that is not a defect, because
  everything it reports is something it is about to change; a reading one does. That is the second
  reason the split earns its keep, and it is what makes a front's emptiness visible without
  accumulating as a defect list (see
  [bundle-verification.md](../quality/bundle-verification.md) §What stays a skill's prose
  self-check).

## The precedent

`/quenching:specs:status` established the shape and `/quenching:knowledge:status` mirrored it exactly: both carry
`allowed-tools: Read, Grep, Glob, Bash(python3:*), Bash(py:*)`, own no contract, and cite three
references apiece. A future front's read command copies this, and a proposal to add a read-only
mode to an existing align is refused on this standard.
