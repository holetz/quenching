---
type: standard
title: Delivery front
description: The target repository's delivery surface — bounded pipeline shape, release reachability and ownership boundaries across workflow, proof, ops, toolchain and security
resource: .github/workflows/**, .claude/quenching.json, plugins/quenching/assets/bin/quenching/delivery/**
tags: [architecture, delivery, ci, pipelines, release]
timestamp: 2026-08-31
audience: both
authority: background
source: spec 1069 (task 1.1, 2026-08-31) — the declaration is approved; its route and verifier belong to the later delivery implementation
maintainer: quenching
---

# Delivery front

The delivery front is the shape of a target repository's delivery pipeline. It makes workflow
triggers, jobs, stages, runtime provenance and release reachability visible without choosing the
provider, environment or promotion policy. It is a front, not a pillar: its tree is statically
probeable and its bounded drift is reportable, while target-specific delivery choices remain with
the owner.

<!-- rules -->

## Mold adoption

The delivery front adopts the common minimum from
[`front-mold.md`](front-mold.md). Its applicability signal is a `delivery` namespace in the
target's `.claude/quenching.json`; its read model will be `cq delivery status`, and its verifier
will be `cq delivery doctor`. The future align and status bodies must preserve the common
`doctor`/`status` floor while keeping delivery-specific evidence in the delivery route's own
references.

The front owns pipeline shape and release reachability. It does not own the proof result, the
operational meaning of deployment, the runtime declaration, or the permissions audit. Those
boundaries are explicit below so that a pipeline can consume evidence without claiming the
authority that produced it.

## The bounded pipeline tree

An adopting repository exposes a provider workflow tree or its provider-equivalent delivery
configuration. The tree is bounded to artifacts that describe how a change enters the pipeline,
which work runs, how stages connect, and how a release can be reached:

```text
delivery surface
├── workflow tree       # .github/workflows/** or the provider equivalent
├── triggers            # events and branch/path filters
├── jobs and stages     # setup, checkout, dependencies and reachable execution
├── runtime declarations # language/tool versions consumed by the jobs
└── release configuration # tags, publish steps and promotion reachability
```

The tree is a candidate surface, not a file list that every target must create. A provider may
express it in one manifest or several workflow files. The delivery front follows the provider's
equivalent when it can identify the same trigger, job, stage and release relationships; it does
not invent a `.github/workflows/` directory for a target that uses another provider.

## Admission test

The front is admitted only when its pipeline tree has statically verifiable drift and repairable
artifacts. The admission test is satisfied when all three statements hold:

1. A target declaration identifies delivery as applicable, or an equivalent provider artifact
   supplies an unambiguous delivery tree.
2. The tree exposes triggers, jobs or stages, and any release path as relationships that a
   verifier can inspect without running target code.
3. A finding can name the affected artifact and a bounded repair or an owner decision; a vague
   request to change the deployment process is not delivery evidence.

No delivery signal means not applicable, not drift. A present signal with an unreadable or
contradictory configuration is a refusal that names the problem. A readable tree with no finding
is conformant. The align must not create a workflow merely to make the admission test pass.

## Cross-front ownership

The neighbouring fronts retain their own evidence and decisions:

| Surface or relationship | Owner | Delivery relationship |
| --- | --- | --- |
| Workflow triggers, jobs, stages and release reachability | `delivery` | Owns the pipeline tree and reports its bounded shape. |
| Test output, CI evidence and proof gate | [`proof-front.md`](proof-front.md) | Delivery may invoke the gate and read its result; it does not become proof or rerun the target suite as its own evidence. |
| Deployment entry point and operational lifecycle | [`ops-front.md`](ops-front.md) | Delivery may reach the declared `deploy` entry point; deployment semantics remain operations-owned. |
| Language and tool versions | [`toolchain-front.md`](toolchain-front.md) | Delivery reads runtime declarations as pipeline evidence; the toolchain front owns their coherence. |
| Workflow and job permissions | `security` pillar | Security may audit permissions read-only; delivery reports the pipeline location and does not make the security decision. |
| Shared configuration keys | Shared arbiter-by-key contract | A physical key has one declared writer even when delivery, proof, ops or toolchain reads it. |

Reading another front's artifact does not transfer ownership. In particular, a CI workflow can
contain a test command without owning the test contract, and a release job can invoke deployment
without owning the operational entry point.

## Measured boundary evidence

The current repository makes these boundaries concrete without turning its own plugin workflow
into a target delivery contract:

| Evidence | Boundary it demonstrates |
| --- | --- |
| `.github/workflows/sync-codex-plugin.yml` | A workflow tree exposes triggers, jobs and permissions; delivery owns its shape, while permission meaning remains with the security pillar. |
| `plugins/quenching/assets/bin/quenching/proof/` | The bundled proof front owns test-layer, CI-evidence and gate semantics; delivery may invoke that evidence but does not claim it. |
| `plugins/quenching/assets/bin/quenching/ops/` | The bundled ops front owns router, entry-point and deploy semantics; delivery may name a reachable `deploy` entry point without absorbing its lifecycle. |
| `docs/standards/architecture/toolchain-front.md` | Runtime and tool declarations remain toolchain-owned even when a workflow consumes them. |
| `plugins/quenching/assets/bin/quenching/common/config.py` | The shared loader reads the configuration envelope; each namespace adapter remains the owner of its semantic keys. |
| `security` pillar | Workflow permissions are read-only security evidence; no local delivery tree or automatic permission repair is invented. |

This evidence is an ownership map, not an assertion that the plugin repository already has a
target `delivery` namespace or a delivery route. The implementation must keep that distinction
visible when it probes a target repository.

## Pipeline shape contract

The delivery verifier and align report the following relationships:

- every declared trigger reaches an intended job or stage;
- every job has the checkout, setup and dependency provenance its commands require;
- every declared stage is reachable from the trigger graph and has a valid predecessor where the
  provider requires one;
- runtime declarations agree with the toolchain evidence they consume;
- a release path is reachable from the pipeline when the target declares one; and
- permission observations are handed to the read-only security audit rather than silently repaired
  as delivery policy.

These checks describe pipeline shape. They do not choose which branch publishes, which environment
promotes, whether a release is manual, or what scope a publish operation has.

## Disposition bands

Bands describe who may decide closure, not severity. The delivery finding map records the concrete
codes and one disposition for each code; its three bands are:

| Band | Examples | Disposition |
| --- | --- | --- |
| Mechanical | generated workflow metadata or a deterministic manifest is stale | Regenerate the owned artifact and rerun the verifier. |
| Structural | an unreachable stage, missing setup or checkout, contradictory runtime, or unreachable release path | Apply a bounded shape repair under the run authorization and rerun the verifier. |
| Judgement | provider, environment, promotion policy, publish scope or permission choice | Report evidence and the owning decision; do not choose or apply the policy automatically. |

Every finding remains in exactly one band. A disposition names the closing command or owner; it is
not an instruction for the align or status body to invoke an unbounded deployment action.

## Boundary with delivery implementation

This standard declares the surface and its admission and ownership rules. It does not create the
`cq delivery` route, command bodies, tests or Codex translation. Those consumers may add provider
adapters and a route-specific vocabulary only when they preserve this bounded tree, the common
front mold and the ownership table above.
