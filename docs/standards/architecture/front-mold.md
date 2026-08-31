---
type: standard
title: Front mold
description: The one binding minimum for a local front declaration, route, align/status surface, disposition bands and Codex projection, with measured domain-specific deltas
resource: docs/standards/architecture/{design-front.md,ops-front.md,proof-front.md}, plugins/quenching/commands/{design,ops,proof}/**
tags: [architecture, front, mold, design, ops, proof]
timestamp: 2026-08-31
audience: both
authority: current
source: spec 1066 (tasks 1.1 and 4.3) — the common front contract, its pre-adoption baseline and the final post-adoption footprint were measured against the tracked design, ops, proof and conductor surfaces
maintainer: quenching
---

# Front mold

A local front is a repository surface that this plugin can probe, report and converge toward. The
front's domain remains authoritative for its values and decisions; this mold owns only the outer
shape that every aligned front must expose. It prevents a new front from repeating the same route,
applicability, verifier, report and translation contract while keeping domain-specific fields
explicit.

<!-- rules -->

## One binding host

This file is the canonical host for the mold. The architecture standards for design, ops and proof
cite it for the shared minimum, while the executor-facing
`plugins/quenching/assets/references/front-align/mold.md` is a projection for command readers and
must not introduce a competing binding rule. Its Codex copy mirrors the source projection after
the source and projection are generated.

The host is an architecture standard because the rule governs how a front is shaped across target
repositories, not how one command prints a report. A front-specific reference may explain the
commands' local evidence and bands, but the common contract has one address and one owner.

## The common minimum

Every local front declares and preserves these fields. The front owner supplies the value; the mold
does not invent a default when the value is absent.

| Surface | Common minimum | What remains front-owned |
| --- | --- | --- |
| Declaration | owned tree, boundary, configuration home, applicability signal, read model, verifier, align, status and finding ownership | tree, namespace keys, payload and domain boundaries |
| `cq` route | one normalized front entry point, `--help`, `--json`, typed exits `0`/`1`/`2`, explicit refusal, and stable `doctor` and `status` verbs | inventory, registry, build, render, readme, ratchet and other extra verbs |
| Align body | probe before inventory, applicability classification, one plan/authorization, bounded ownership-safe writes, the same closing verifier and a residual report | source arbitration, registry repair, layer/floor treatment and other domain decisions |
| Status body | read-only payload, explicit missing/refused/not-applicable states, stable finding codes and bands, and the owner/command that closes actionable residue | authoritative evidence rows and front-specific findings |
| Disposition bands | mechanical, structural and judgement mapping; evidence; closure command; and the person or mechanism allowed to decide | codes, severity, structural repairs and judgement owner |
| Translation | canonical source command/reference and a Codex surface that mirrors its contract | language, harness spelling and generated path |

The mold is a minimum, not a cloned template. A front-specific field belongs in the front's own
contract when another citer may not legitimately write it. Optionality alone does not make a field
common: the question is whether every citer may own and close it.

## Route floor

The normalized `cq <front>` route is the front's machine-facing boundary. At the floor it provides:

1. `--help` with the route's usage example;
2. `--json` whose stdout contains data only, with diagnostics on stderr;
3. exit `0` for a conformant result, `1` for findings, and `2` for misuse or refusal;
4. an explicit refusal for missing or invalid configuration, never an invented root, router or
   namespace; and
5. stable `doctor` and `status` verbs, where `doctor` verifies the declared surface and `status`
   reads it without writing.

The plugin's `/quenching:<front>:align` and `/quenching:<front>:status` bodies are the human-facing
surface around that route. A front may own extra verbs, but an extra verb is a declared delta and
never a reason to weaken the floor.

## Applicability and ownership

Applicability is a named stage before inventory. A front with no signal is not applicable; an
explicitly scoped front is skipped; a present front with no findings is conformant. None of these
states is converted into drift. A front that is present but refuses configuration reports the
refusal and does not receive a guessed declaration.

The align may close only bounded mechanical or structural findings under its one authorization. It
reports judgement findings with evidence and the exact owner command, and never chooses a
target-specific policy. The status command is read-only and preserves the same distinction.

## Disposition bands

Every front's `bands.md` maps every finding exactly once. Bands describe who may decide closure,
not severity:

| Band | Decider | Permitted action |
| --- | --- | --- |
| Mechanical | generated artifact and deterministic source | regenerate the owned artifact and re-run the verifier |
| Structural | contract plus the one run authorization | apply a bounded shape or gate repair and re-run the verifier |
| Judgement | human who owns the target risk | report evidence and the closing command; make no automatic edit |

A front may have no mechanical code, but its bands reference must say so explicitly. Every mapping
keeps the finding code, path/evidence, severity, disposition and closure command visible. A
judgement command in a report is a hand-off, not an invocation by the align or status body.

## Measured baseline and footprint

Both measurements below were taken on 2026-08-31 from tracked UTF-8 files. A front footprint means
its architecture declaration, `align` and `status` command bodies, all front-specific source
references, the two Codex align/status skills, all Codex front references, and its test module plus
golden fixtures. The three creation commands are deliberate front deltas, so they are excluded
from the common footprint: `design/genre/new.md`, `ops/entrypoint/new.md`, and `proof/layer/new.md`.

### Pre-adoption baseline (task 1.1)

This is the preserved measurement from before the front-specific adoption in tasks 2.1–3.3 and
the generated index registration in task 4.1.

| Front | Declaration | Command bodies | Source refs | Codex skills | Codex refs | Proof files | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| design | 1 | 2 | 0 | 2 | 0 | 1 | **6 files / 55,860 bytes** |
| ops | 1 | 2 | 4 | 2 | 4 | 5 | **18 files / 96,529 bytes** |
| proof | 1 | 2 | 4 | 2 | 4 | 5 | **18 files / 101,461 bytes** |
| **three fronts** | **3** | **6** | **8** | **6** | **8** | **11** | **42 files / 253,850 bytes** |

At that point the shared conductor added `plugins/quenching/commands/align.md` and
`plugins/quenching/tests/test_align_contract.py`: **2 files / 17,813 bytes**, making the
pre-adoption common baseline **44 files / 271,663 bytes**.

### Post-adoption final footprint (task 4.3)

This is the final measurement after front-specific adoption and conductor re-derivation. It uses
the same footprint definition, so the change remains attributable rather than replacing the
baseline evidence.

| Front | Declaration | Command bodies | Source refs | Codex skills | Codex refs | Proof files | Total |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| design | 1 | 2 | 1 | 2 | 1 | 1 | **8 files / 67,806 bytes** |
| ops | 1 | 2 | 4 | 2 | 4 | 5 | **18 files / 98,911 bytes** |
| proof | 1 | 2 | 4 | 2 | 4 | 5 | **18 files / 103,875 bytes** |
| **three fronts** | **3** | **6** | **9** | **6** | **9** | **11** | **44 files / 270,592 bytes** |

The re-derived shared conductor now adds the same two files at **12,314 bytes**, making the final
common footprint **46 files / 282,906 bytes**. The three creation commands remain measured outside
both snapshots as domain-owned extensions, not silently counted as common mold obligations.

The byte counts are dated evidence for this consumer after extraction. A later front may reuse the
mold without claiming that its domain payload is common; any reduction or increase is reported with
the same footprint definition and date.

## Explicit front deltas

The shared minimum does not erase these proven differences:

| Front | Binding domain delta |
| --- | --- |
| design | `/.design/tokens.json` is the DTCG source; projections cover interoperability, editorial and internal adapters; source arbitration with optional Impeccable input remains human-owned; web and non-web detection stay distinct; genres add render destinations. |
| ops | `.claude/quenching.json` owns `opsRoot`, `router` and optional `registry`; inventory and generated registry are first-class; entry points carry lifecycle, reachability, typed exit, output and write-policy evidence; `op-*` findings retain their existing owners. |
| proof | `.claude/quenching.json` owns `proofRoot`, layers, fixtures, measured roots, exclusions and ratchet; layer markers and fixture reach are derived evidence; floors, CI and order evidence remain explicit; the target suite is not run by align or status; `pf-*` findings retain their bands. |

These deltas are why the mold is a contract and not a shared runtime implementation. No generic
Python dispatcher or second configuration schema belongs here. Each front keeps its own payload,
extra route verbs, references, evidence and decision authority while citing this minimum.
