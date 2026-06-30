# The 8-step workflow

The skill's operational spine is a single line of **8 steps**, defined in
[`SKILL.md`](https://github.com/israelholetz/claude-quenching/blob/main/plugins/claude-quenching/skills/quenching-management/SKILL.md).
The governing axis is **audit-by-default + install-with-confirmation**: the report
always comes first (Steps 1–4); installation (Steps 5–7) is an explicit second
step, item by item, with the user's OK; Step 8 keeps the base from rotting.

1. **Derive the current shape** of the target repo (read-only, adaptable) — locate the CLAUDE.md(s), discover where each knowledge layer lives, inventory `.claude/`, and note the profile signals that will modulate emphasis.
2. **Inventory each dimension** — run the adaptive globs/greps; for large repos, delegate the scan to the read-only auditor sub-agent (clean context).
3. **Score each dimension** — Present / Partial / Drifted / Absent, always citing `file:line` evidence.
4. **Produce the prioritized gap report** — scorecard → prioritized gaps → deprecables → installation plan. Priority = severity × cost × ready-payload **× profile-weight**; the report gains a "For THIS repo, invest first in…" block anchored to observed triggers.
5. **Propose → install with confirmation** — for each gap, install the package payload (adapted to the repo's conventions), item by item, only after an OK.
6. **Items without payload → only propose** — direction (3), memory (10) and boundary doctrine (12) are human content decisions: propose the text/diff, never apply.
7. **Flag what became deprecable** — list pre-existing artifacts a package payload now covers; never remove without an explicit OK.
8. **Establish the recurring maintenance cycle** — install the operational loop that keeps the surface fresh, with three triggers (PR/event · model release/cadence · on-demand command) and the right home for each, under an orchestration contract (hook observes/proposes · command/skill applies with OK · sub-agent returns a condensed summary).

For the emphasis-modulation detail, see [The 15 dimensions](dimensions.md) and the
[architecture](architecture.md). For the per-step reference detail, see the skill's
[`references/`](https://github.com/israelholetz/claude-quenching/tree/main/plugins/claude-quenching/skills/quenching-management/references).
