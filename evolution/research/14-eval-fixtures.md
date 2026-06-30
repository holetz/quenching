# Eval fixtures — curator evaluation harness (detection + prescription)

> Input for **skill development** (not application). The fixtures and measurement records live here, alongside the research, as the «Eval of the audit itself» doctrine of [SKILL.md](../../plugins/claude-quenching/skills/quenching-management/SKILL.md) mandates. Application to a real repo (Steps 1-7) does **not** run this harness.

The method **is an agent tool**, and agent tools are evaluated against **realistic tasks** with a verifiable answer, not by inspection:
*«Each evaluation prompt should be paired with a verifiable response or
outcome»* and *«Your verifier can be as simple as an exact string comparison
between ground truth and sampled responses»*
([Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents),
accessed 2026-06-29). There are **two types** of output to evaluate, with the same fixture form (planted gap/profile → expected result as ground truth):

1. **DETECTION fixtures** (R12 doctrine) — a sample repo with a **known gap planted** in a dimension; the method is expected to **signal it in the right dimension** with `file:line`. Measures: accuracy by dimension · **false-negative** (gap slipped through — the one that matters most) · cost/tokens.
2. **PRESCRIPTION fixtures** (R34, below) — a sample repo of **marked form** with a **planted profile**; the expected **emphasis/roadmap** that the profile calls for is the ground truth in the «For THIS repo, invest first in…» block (Step 4). Measures: **prescription-accuracy** · **prescription-false-negative** (flat emphasis on a marked-form repo).

> **Status: DESIGN. Measurement PENDING Bash** — consistent with R22/R23/R25/R26/ R27/R28/R29 (greps without a run harness). This file **defines** the fixtures and expected results; running them and reading the numbers is work for when Bash is available.

---

## DETECTION fixtures (R12 — record of what was already doctrine)

Small sample repos, one planted gap each, plus a **clean pair** (without the gap in that dimension) to catch false-positives. The five from R12:

| Fixture | Plants (gap) | Expected signal in |
| --- | --- | --- |
| `det-no-claudemd` | repo with no CLAUDE.md at all | dim 1 (Absent) |
| `det-skill-no-frontmatter` | skill without `name`/`description` | dim 6 (Drifted/Partial) |
| `det-adr-implemented` | ADR already implemented, still in tree | dim 5/2 (Drifted) |
| `det-skills-overlapping` | two skills with overlapping scope | dim 6 (bloat R10) |
| `det-boundary-two-homes` | same boundary defined in 2 canonical homes | dim 12 (semantic DRY) |

Test of a new detection rule: **catches the planted gap without triggering on the clean pair**. A rule that moves no measurement is a candidate for exclusion.

---

## PRESCRIPTION fixtures (R34 — planted profile → expected emphasis)

Each fixture is a sample repo whose **FORM** triggers a profile from
[../references/repo-profiles.md](../../plugins/claude-quenching/skills/quenching-management/references/repo-profiles.md). The **ground truth** is the
emphasis/order that the profile calls for — **only the METHOD recommendation** (which dimension/
payload/trigger to invest in), **never content** (there is no ground truth for VISION/memory). The verifier checks that the «For THIS repo, invest first in…» block **contains** the expected dimensions, each one **anchored to an observed trigger** (`file:line`).

| Fixture | Planted signals (Step 1) | Profile | EXPECTED emphasis (ground truth) |
| --- | --- | --- | --- |
| `pre-mlops-marked` | training/inference folder; `mlflow`/`sklearn` pinned; samples/slices; cadence-based release | MLOps/model-heavy | dim 8 (Stop hook + cadence trigger (2)) + dim 14 (pin guardrail). dim 3/10 **only «propose the canonical home»** (Step 6), **not** prescribed |
| `pre-greenfield-empty` | no `.claude/`; few docs; score almost all Absent | greenfield | the **ORDER** (not «which»): triggers the base-Order from `quenching-roadmap` (foundation dim 1/12/2 **before** hooks/MCP) |
| `pre-lib-pure` | `src-layout`/`lib/`; public API; `pyproject` with `version`; no runtime entrypoint | library/SDK | dim 1 **lean** («20-80 lines») + dim 2 (`standards/` for the API) + dim 6 (skill = style-guide) |
| `pre-monorepo` | multiple packages (`packages/*`); many CLAUDE.md; generated/vendored versioned | monorepo/large codebase | dim 1 (per-directory + excludes + Read deny) + **fan-out** to auditor + rollout plugin |
| `pre-form-ambiguous` | small repo, 1 package, **neutral form** (no marked signal for any profile) | **none** | **weak/flat emphasis** — short or absent block is **CORRECT**; strong emphasis = false-positive |

### The two measures (mirror detection)

- **Prescription-accuracy** — for the four marked-form fixtures: the recommended emphasis **matches** the ground truth (contains the expected dimensions) and each item is **anchored to an observed trigger** (`file:line`), not to the profile name? Verifier: the intersection {recommended emphasis} ∩ {expected emphasis} covers the expected items, and no expected item was left out.
- **Prescription-false-negative** (the one that matters most) — did any **marked-form** repo come out with **flat emphasis** (no block, or items with no cited trigger)? That is worse than a false-positive: the recommendation **looks** made and isn't. This is exactly the R29 smell («report with flat emphasis on a marked-form repo»), turned into a metric here.

### Poka-yoke — two guards against over-prescription

1. **Tests METHOD, never CONTENT** (Step 6 / Rev5 / R29 limit). The ground truth is only *which dimension/payload/trigger* the profile calls for — never *what* the VISION/memory/boundary should say. There is no fixture whose expected output is a content text; if one appeared, it would be outside what the method decides. That is why `pre-mlops-marked` expects dim 8/14 (method), and dim 3/10 enter only as «propose the canonical home» (Step 6) — consistent with Rev5.
2. **Ambiguous form → flat emphasis is CORRECT, not a failure** (`pre-form-ambiguous`). In a neutral-form repo, flat emphasis is the **correct** recommendation (repo-profiles.md §«How to use» item 4: «no profile → flat emphasis is correct; do not invent a profile just to have something to prioritize»). Here **strong emphasis** is the **prescription-false-positive** — the curator over-prescribes. This mirrors the Rev7 care (not turning into a skill-spam generator) and the doc: *«watch for unexpected trajectories or overreliance on certain contexts»* ([Equipping agents with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills), accessed 2026-06-29). Without this fixture, the harness would reward always-prescribing.

### Boundary (what the prescription fixture does NOT test)

- Does **not** test whether specific content was written (Rev5 limit) — only whether the **method recommendation** matches the profile. There is no ground truth for direction/memory.
- Does **not** turn profile into a **rigid evaluable gate**: the expected emphasis is a **target set** (covers the items), not an exact match/fixed order — the report can sum emphases from matching profiles (repo-profiles.md: «emphases sum»). The verifier checks **contains the expected**, not **equals the expected** (avoids rejecting a correct recommendation that cites one extra item).
- Does **not** run on application to a real repo (Steps 1-7) — development only.

## Sources

- [Writing effective tools for AI agents — Anthropic Engineering](https://www.anthropic.com/engineering/writing-tools-for-agents)
  (accessed 2026-06-29) — *«Each evaluation prompt should be paired with a
  verifiable response or outcome»*; *«Your verifier can be as simple as an exact
  string comparison between ground truth and sampled responses»*; *«Prompts should
  be inspired by real-world uses and be based on realistic data sources and
  services»*. Anchor: fixture = realistic input **paired with verifiable expected result** — holds for prescription same as detection.
- [Equipping agents for the real world with Agent Skills — Anthropic Engineering](https://www.anthropic.com/engineering/equipping-agents-for-the-real-world-with-agent-skills)
  (accessed 2026-06-29) — *«Identify specific gaps in your agents' capabilities by
  running them on representative tasks»*; *«iterate based on observations: watch for
  unexpected trajectories or overreliance on certain contexts»*. Anchors the poka-yoke against over-prescription (ambiguous form → flat emphasis).
