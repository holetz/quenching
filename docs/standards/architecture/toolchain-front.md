---
type: standard
title: Toolchain front
description: The target repository's toolchain surface — manifests, locks, language pins and tool configuration, with explicit ownership boundaries and stable tc-* findings
resource: .claude/quenching.json, pyproject.toml, uv.lock, CLAUDE.md, .github/workflows/**, plugins/quenching/assets/zensical/ci-github-pages.yml
tags: [architecture, toolchain, dependencies, build, configuration]
timestamp: 2026-08-31
audience: both
authority: current
source: spec 1067 (task 1.1, 2026-08-31) — the admission evidence, cross-file surface and ownership boundaries were measured in the current repository
maintainer: quenching
---

# Toolchain front

The toolchain front is the repository surface that keeps build manifests, dependency locks,
language versions and the tool configuration carried by those artifacts coherent. It is a front,
not a pillar: its tree can be probed and its static relationships can be reported or repaired,
while target-specific policy remains with the owner of the build.

<!-- rules -->

## Admission evidence

This front was admitted from measured seams in the current repository, not from a promise about a
future implementation:

- `pyproject.toml` declares Python `>=3.11`, while `.github/workflows/sync-codex-plugin.yml` and
  `plugins/quenching/assets/zensical/ci-github-pages.yml` use the open-ended `3.x` runtime and no
  `.python-version` is present.
- The development dependency group declares `pytest>=8.0`, while the repository harness in
  `CLAUDE.md` runs `unittest` discovery.
- `pyproject.toml` is read by the `ops` and `proof` fronts, including `[project.scripts]`,
  `tool.coverage` and `tool.pytest`, but ownership is declared by the shared arbiter rather than
  by the toolchain front.

These are structural seams in repairable artifacts. They establish that the surface is measurable;
they do not select a Python version, a test framework, a formatter, a ruleset, an upgrade cadence,
or whether a target should adopt a lock.

## Mold adoption and name

The toolchain front adopts the common minimum from
[`front-mold.md`](front-mold.md). Its applicability signal is a target's declared `toolchain`
namespace; its future read model and verifier are downstream implementation decisions that must
preserve the common `status`/`doctor` floor. Its domain-specific reference is
`plugins/quenching/assets/references/toolchain-align/bands.md`, with the Codex copy mirroring the
Claude-side source.

The name is `toolchain`, not `config`: `.claude/quenching.json` is the plugin configuration home,
and treating it as a toolchain artifact would recreate competing sources of truth. The `tc-`
prefix is reserved for this front's findings and must not be reused by configuration or a
neighbouring front.

## The virtual canonical tree

The front is a cross-file surface, not a new directory. A target may contain only a subset of the
candidate families; the verifier must establish applicability from artifacts that exist rather
than requiring every ecosystem:

```text
toolchain surface
├── manifests: pyproject.toml, setup.cfg, package.json, Cargo.toml
├── locks: uv.lock, poetry.lock, package-lock.json
├── language pins: .python-version, .nvmrc
└── tool-configuration blocks carried by those manifests
```

The list is a candidate family, not an inventory of files the target must create. A later
implementation may extend it only after measuring a real target corpus and adding the extension to
the verifier's declared contract. `.claude/quenching.json` is never a member of this tree.

## Configuration and ownership boundaries

The toolchain front consumes the shared arbiter-by-key contract. It may read a key to establish
toolchain evidence, but it does not become the owning writer merely because the key is physically
inside a manifest. One semantic key has one declared writer; an ambiguous key is reported rather
than selected by file order.

The neighbouring-front boundaries are fixed as follows:

| Artifact or key | Owner | Toolchain relationship |
| --- | --- | --- |
| `project.scripts` and operations entry points | `ops` | Read as build evidence; never claimed or repaired by this front. |
| `tool.pytest`, `tool.coverage` and CI gate invocation | `proof` | Read as evidence of the verification surface; never turned into toolchain ownership. |
| Workflow triggers, jobs and stages | `delivery` | Read runtime declarations as evidence; workflow control remains delivery-owned. |
| Permission inspection | `security` | Remains a read-only pillar concern, outside the toolchain tree. |
| `.claude/quenching.json` | shared configuration loader | Names front configuration; it is not a toolchain source. |

CI runtime declarations may therefore be evidence for toolchain version agreement while CI gate
invocation is proof evidence. Multiple readers do not create multiple writers.

## Disposition bands

A disposition band answers who may decide closure; it is independent of severity:

| Band | Decider | Allowed closure |
| --- | --- | --- |
| Mechanical | A deterministic source and its generated artifact | Regenerate or normalize without a per-item policy question. |
| Structural | The declared contract under one run authorization | Apply a bounded shape repair and re-run the verifier. |
| Judgement | The human who owns the target's build risk | Report evidence and an executable closing action; never drive the policy change. |

No judgement finding is introduced merely for an unmeasured heuristic. Choices such as formatter,
ruleset, upgrade policy, build-backend selection where the ecosystem does not identify one, or
adopting a lock stay as target-owner decisions until a contract makes them statically decidable.

## Finding vocabulary

The stable `tc-*` vocabulary is closed at seven findings. Severity and disposition remain separate:

| Code | Band | Severity | Meaning | Closure shape |
| --- | --- | --- | --- | --- |
| `tc-lock-stale` | Mechanical | `error` | A lock artifact is desynchronized from the manifest declarations it records. | Regenerate the lock from the declared ecosystem source and re-run the verifier. |
| `tc-config-duplicate` | Mechanical | `error` | The same toolchain key is declared in more than one configuration home. | Apply the declared arbiter and remove the duplicate source; never choose an owner from file order. |
| `tc-generated-stale` | Mechanical | `error` | A generated tool-configuration block no longer matches its deterministic source. | Regenerate the block from its source while preserving authored text outside the generated zone. |
| `tc-runtime-drift` | Structural | `error` | A language version disagrees across the manifest, CI, pin file or container declaration. | Align declarations under the target's chosen version source, or hand the version choice to the target owner when none is declared. |
| `tc-tool-unpinned` | Structural | `error` | A declared development tool has no reproducible version pin. | Add the pin in the declared toolchain home; selecting a version where none is evidenced remains a target-owner decision. |
| `tc-build-backend-missing` | Structural | `error` | A buildable manifest lacks the build-backend declaration required by its ecosystem contract. | Add or repair the backend only when the target's build contract identifies it; otherwise report the missing decision. |
| `tc-key-unarbitered` | Structural | `error` | A manifest or toolchain key is read by multiple fronts without one declared owning writer. | Apply the shared arbiter-by-key contract; report ambiguous ownership rather than selecting it by the front. |

The complete one-band mapping is:

| Band | Codes |
| --- | --- |
| Mechanical | `tc-lock-stale`, `tc-config-duplicate`, `tc-generated-stale` |
| Structural | `tc-runtime-drift`, `tc-tool-unpinned`, `tc-build-backend-missing`, `tc-key-unarbitered` |
| Judgement | none |

The remedy named for a finding is capability-shaped. A future verifier must prove that the
concrete regeneration, bounded repair or handoff exists before presenting the finding; "fix the
lock" without an available action is not a complete closure.

## Mold and implementation boundary

This standard owns what `toolchain` is, the tree it covers, the neighbouring ownership seams and
the meaning of its bands and vocabulary. The runtime reference owns the command-facing disposition
table and report-ready closure shapes. A later C2 implementation may add the route, probe,
inventory, verifier, align and status only as consumers of this contract; this declaration creates
none of them and does not repair the measured seams.
