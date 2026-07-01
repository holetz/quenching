# Using it — the 8-step workflow

You have the *why* (the harness is the work) and the *what* (the 15 dimensions).
This is the *how*: **how you run the method** — what fires when you ask, the eight
steps the agent executes, and the three usual scenarios. It is the prose form of the
[architecture](../method/architecture.md); the steps are defined in
[`SKILL.md`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md).

The governing axis is **audit-by-default + install-with-confirmation**: the report always
comes first (Steps 1–4); installation (Steps 5–7) is an explicit second step, item by item,
with your OK; Step 8 keeps the base from rotting.

## How to trigger

The method fires **by description** when you ask to **organize/audit the repo's knowledge**,
**install the knowledge base for Claude Code**, **prepare a repo from scratch for Claude**,
**review docs/skills/hooks/agents/CLAUDE.md**, **see what's missing from the base**, or
otherwise describe a mess/gap in the knowledge surface. It can also be invoked by name
(`/claude-quenching:quenching-management`).

The flow is always the same; what changes by scenario is **where the roadmap weighs** (see
the three scenarios below).

## The steps

1. **Derive the current shape** of the target repo (read-only, adaptable) — locate the
   CLAUDE.md(s), discover where each knowledge layer lives, inventory `.claude/`, and note
   the profile signals that will modulate emphasis.
2. **Inventory each dimension** — run the adaptive globs/greps; for large repos, delegate the
   scan to the read-only auditor sub-agent (clean context).
3. **Score each dimension** — Present / Partial / Drifted / Absent, always citing `file:line`
   evidence.
4. **Produce the prioritized gap report** — scorecard → prioritized gaps → deprecables →
   installation plan. Priority = severity × cost × ready-payload **× profile-weight**; the
   report gains a "For THIS repo, invest first in…" block anchored to observed triggers.
5. **Propose → install with confirmation** — for each gap, install the package payload
   (adapted to the repo's conventions), item by item, only after an OK.
6. **Items without payload → only propose** — vision (3), memory (10) and boundary
   doctrine (12) are human content decisions: propose the text/diff, never apply.
7. **Flag what became deprecable** — list pre-existing artifacts a package payload now covers;
   never remove without an explicit OK.
8. **Establish the recurring maintenance cycle** — install the operational loop that keeps the
   surface fresh, with three triggers (PR/event · model release/cadence · on-demand command)
   and the right home for each, under an orchestration contract (hook observes/proposes ·
   command/skill applies with OK · sub-agent returns a condensed summary).

What each step measures is the [15 dimensions](../method/dimensions/index.md); the per-step
reference detail lives in the skill's
[`references/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/references).

---

## How it plays out — three scenarios

The 8 steps are constant; the **weighting** shifts with what the repo already has.

### Scenario A — new repo (from scratch)

Almost everything is **Absent**; the method becomes the **roadmap to install the structure**.

1. Ask to **"prepare this repo for Claude Code"** / **"install the knowledge base"**.
2. The method derives the little that exists (language, any initial `CLAUDE.md`) and presents
   the report with almost all dimensions as gaps.
3. Confirm installation **item-by-item**. Typically in this order of value:
   - **CLAUDE.md** as map + ceiling hook
     ([`validate-claude-md.py`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/hooks/validate-claude-md.py));
   - **canonical `docs/` taxonomy**
     ([`assets/docs/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/docs):
     `standards/`, `decisions/`, `vision/`, `backlog/`, `guides/`, `reference/`,
     `catalog/`, `communications/`, `presentations/`) — **only the homes that apply** (a repo
     without data doesn't get `catalog/`);
   - **knowledge template-skills**
     ([`assets/skills/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/skills))
     and **sub-agents**
     ([`assets/agents/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/agents));
   - **lifecycle hooks** and the **re-audit command**
     ([`assets/commands/quenching-reaudit/`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/commands/quenching-reaudit)).
4. Each installed artifact is **adapted** to the repo's language/prefix — the payload is the
   starting point, not a rigid mold.
5. **Human content is not installed:** vision (`docs/vision/`), memory and the boundary
   doctrine the method **only proposes** — you write them.

Result: a coherent `.claude/`/`docs/` with the **recurring cycle** already wired (Scenario C
governs future rounds).

### Scenario B — existing repo (audit, install what's missing, deprecate)

The most common case. The method **measures what's there** and installs **only the gaps**.

1. Ask to **"audit/organize the repo's knowledge"** or **"see what's missing from the base"**.
   For large repos, it can delegate the scan to the read-only sub-agent
   [`quenching-auditor`](https://github.com/holetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/assets/agents/quenching-auditor.md)
   (clean context, cheap model).
2. Read the **scorecard per dimension** + the **prioritized gaps** (P1/P2/…). Priority
   combines severity (`drifted`/broken > absent > partial) × cost × whether there's a ready
   payload.
3. Pay attention to two sections of the report:
   - **Deprecables** — skills/agents/hooks the repo already had that a package payload now
     covers. The method **installs the single source** and lists the old one; removal is
     **your decision** (and if the repo's one is better adapted, it offers **keeping yours**
     and discarding the payload).
   - **`docs/` variant names** (`docs/arquitetura/` → `standards/`, `docs/adr/` →
     `decisions/`, single `VISION.md` → `vision/`, `docs/catalogo_dados/` → `catalog/`): the
     method **proposes migration to the canonical name** — converge, not preserve — always
     with OK.
4. Confirm installation **item-by-item**. **Generated** repo artifacts (`*.job.yml`,
   manifests, AUTO-GENERATED catalog, lockfiles) are **never touched** — the repo's "X
   defines Y" rule is respected.

### Scenario C — repo that already applied (maintenance, structure evolution)

Auditing **once** leaves the base fresh **today** — but it **rots** as the code, models and
team change (*context rot*). So the method **doesn't end with the report**: Step 8 installs
the **recurring operational loop** that keeps the surface alive, with three triggers and the
right home for each. In a repo that already applied the structure, maintenance is **operating
those triggers**, not re-installing:

- **On event, in the PR (drift trigger):** touching `CLAUDE.md`/`docs/` is a doc change like
  any other. A **PR hook** re-runs detection of the touched scope and **PROPOSES** (does not
  block) the gaps.
- **On cadence, at model release (review trigger):** revisit the base when switching models —
  an instruction that existed to work around an older model's limitation may become
  **overhead** (a skill/rule the model now does on its own ⇒ deprecable).
- **On demand, by command (manual trigger):** the
  [`/<prefix>-reaudit`](https://github.com/holetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/assets/commands/quenching-reaudit)
  command fires the re-examination (Steps 1–7, or the scope the argument requests) and, in
  large repos, delegates to the auditor sub-agent in clean context.

**Automatic freshness between audits** comes from the bundled hooks (see
[Bundled artifacts](artifacts.md) for the full table). **Typical maintenance:** run the
re-audit command periodically (or when the PR/Stop hook signals), treat the report as in
Scenario B (install what stayed Absent, fix Drifted, migrate variants, deprecate the rest),
and rely on the hooks for freshness between rounds.
