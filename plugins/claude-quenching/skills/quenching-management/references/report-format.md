# Audit report format

> **Way back:** [../SKILL.md](../SKILL.md) (agent roadmap) ·
> human overview & architecture: the project docs site ·
> [README.md](README.md) (`references/` index).

The method **always** delivers this report first (before any installation). It
is scannable: scorecard at the top, prioritized gaps in the middle, deprecables
and installation plan at the end. Cite **`file:line`** in every piece of evidence.

```markdown
# Knowledge audit — <repo> · <date>

**Derived shape:** <1-2 lines with the conventions detected in Step 1
(language, prefix taxonomy, where each layer lives, current boundary doctrine).>

## Scorecard per dimension

| # | Dimension | State | Evidence (file:line) | Payload to fill |
| --- | --- | --- | --- | --- |
| 1 | Map (CLAUDE.md) | Drifted | CLAUDE.md:22 → link to absent file | quenching-map + hook |
| 2 | Normative reference | Present | <index>:1 | quenching-docs |
| 3 | Direction (VISION) | Partial | <vision>:40 (milestone crept in) | — (propose) |
| … | … | … | … | … |
| 12 | Boundaries | Drifted | rule X in CLAUDE.md:30 **and** <index>:12 | — (propose) |

States: **Present · Partial · Drifted · Absent**.

## For THIS repo, invest first in… (emphasis by profile)

> 2-4 items of highest leverage given the derived shape (fit-to-repo). Each
> anchored in an observed trigger. Covers the full scorecard — this reorders,
> it does not hide.

- **<dimension/trigger/payload>** — because the repo exhibits **<profile signal>**
  (`<file:line | Step 1 fact>`). Highest leverage: <what it unlocks>.
- *(repo from scratch: this block becomes the **sequence** of installation —
  map and boundaries first, what unlocks the rest.)*

## Prioritized gaps

> Priority = severity (drifted/broken > absent > partial) × cost ×
> existing ready payload in the package (installable moves up the queue)
> **× profile-weight** (the emphasis above promotes items of highest leverage
> for THIS repo).

### P1 — <short title>  ·  [dimension N · state]
- **Symptom:** <what is wrong>
- **Evidence:** <file:line>
- **Remediation:** <concrete action>
- **Install:** <payload from assets/… → destination in target | "no payload: propose to user">

### P2 — <title>  ·  [dimension N · state]
- …

## Deprecables (repo already had these; package becomes the single source)

> For each installed payload that covers something pre-existing. **Recommendation**,
> not removal: nothing leaves without explicit OK. See doctrine in installation.md.

- **<pre-existing repo artifact>** — did <X>; replaced by <package payload>;
  gain of removing: a single source instead of two diverging.
  - *Alternative:* if the repo's one is better adapted to local conventions,
    keep the repo's and discard the payload (goal = single source, not
    imposing the package).

## Items without payload (human decision)

Dimensions 3 (VISION), 10 (memory), 12 (boundaries): the method **proposes**,
does not install.

- **<dimension>:** <suggested diff/text, ready for the user to apply (or for
  the artifact's owner template to execute the writing).>

## Installation plan

- [ ] Install P1: copy <payload> → <destination>, adapt to derived shape (after OK)
- [ ] Install P2: … (after OK)
- [ ] Deprecables: review and, with OK, remove the listed old artifacts
- [ ] Items without payload: review the proposed diffs
```

## Usage notes

- **Emphasis by profile (fit-to-repo), not a filter:** the "For THIS repo,
  invest first in…" section **modulates** prioritization by the shape+need
  derived in Step 1 — where the method **yields more** for **this** repo
  (monorepo → dim 1 + fan-out; populated `.claude/` surface → dims 6/7/8;
  many external services → dim 15; repo from scratch → the **installation
  sequence**). It is **PROPOSING/PRIORITIZING** about the METHOD itself (which
  dimension/trigger/payload to invest in), **not** imposing content or deciding
  the repo's direction (that's only Step 6). Every dimension stays in the
  scorecard (full coverage); the block only **reorders** and recommends, always
  anchored in an **observed** trigger (`file:line` / Step 1 fact), never in the
  curator's preference. The named profile catalog (signals → emphasis, **free
  examples, not enum**) is in [repo-profiles.md](repo-profiles.md); detail and
  rationale: Step 4 of [../SKILL.md](../SKILL.md).
- **Don't flood:** the scorecard is the 10-second view; detail goes in the gaps.
  Condensed return, not raw dump.
- **Repo from scratch:** if almost everything is **Absent**, the report becomes
  an **installation roadmap** — P1/P2 gaps become "install X from assets/", in
  the order that unlocks the rest (map and boundaries first). The "Deprecables"
  section is empty (there was nothing before).
- **Installation:** each P-N item is only executed **with the user's OK** and by
  **copying the package payload** ([../assets/](../assets/)), adapted to the
  derived shape (see [installation.md](installation.md)). The method never installs
  without confirmation, never removes the old artifact without OK, never touches
  generated artifacts.
