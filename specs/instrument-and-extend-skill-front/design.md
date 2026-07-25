# Design — Ferramenta, escopo e avaliacao no front .claude/

## Context

Binding contracts this design must not contradict:

- `docs/standards/automation/skills.md` (`authority: current`) — the single classification axis,
  the mirrored wrapper for every domain-bound skill, one plan → one OK, MERGE-never-clobber, the
  read-only inventory, and the convergence condition (bijection + registry zone matching disk).
- `docs/standards/naming/command-surface.md` (`authority: current`) — `quenching-<front>-<object>-<verb>`
  mirrored one-to-one at `commands/<front>/[<object>/]<verb>.md`, verb-first names, clean renames,
  canonical English surface. Its stated bijection count is a fact this plan changes.
- `sweep-doctrine.md` — the sweep contract shared by all three aligns; this plan adds a verifier to
  its §6 table but changes none of its behaviour.
- `convergence.md` — the cycle-authorization contract; Stage 2 gaining a tool must not gain a write.

Forces already proven on the other two fronts: a front is only as honest as its verifier, and the
plugin's two existing tools (`okf-validate.py`, `specs.py`) set the mold — stdlib only, `--json`
everywhere, exit 0/1/2, schema and templates loaded from adjacent assets with embedded fallbacks so
an installed copy under a target's `.claude/hooks/` still works, and a `VERSION` constant kept in
lockstep with the plugin.

The measurements this design answers were taken on the current tree: 34,579 characters of skill
metadata plus 2,072 of wrapper descriptions (36,651 total, ~9,200 tokens); two skills over the
1,536 cap; seventeen descriptions over 1,024; eleven skills observed rendered name-only in a live
session listing.

## Decisions

1. **One new tool, `assets/bin/skills.py`, built to the `specs.py` mold — not an extension of an
   existing script.** `okf-validate.py` validates an OKF bundle and installs into a target for the
   `docs/` front; `specs.py` is installed by `quenching-specs-align` for the `specs/` front. Each
   front's align installs its own tool, and `.claude/` is a third front with a third install
   trigger (`quenching-skill-align`). Folding skill linting into either script would make one
   front's align responsible for another front's verifier — the exact coupling the three-front
   split exists to prevent. Cost accepted: a third `VERSION` constant in the release lockstep.

2. **The tool owns the registry's GENERATED zone format.** Today `taxonomy.md` §registry is the
   format's owner and two skills reproduce it by hand. After this plan `skills.py registry reindex`
   is the owner and `taxonomy.md` cites it, mirroring `specs.py backlog reindex` and the rule the
   backlog already carries: never hand-edit inside the markers. This removes the only place in the
   plugin where an LLM is asked to both generate a derived table and verify its own output.

3. **`lint` reports only what is decidable from the file; judgment stays human.** `sk-*` codes
   cover the description caps, trigger position, the `Not for:` boundary, body line count, a
   `**Done when:**` criterion per numbered step, unscoped `Bash` in `allowed-tools`, invocation
   control coherence, name canonicality, and the bijection. The doctrine's remaining tests — the
   no-op test, sediment, sprawl, positive prescription — stay read-by-a-reader in Stage 2, because
   each needs a claim about behaviour that no parser can make. This keeps the plugin's
   anti-fabrication boundary exactly where `sweep-doctrine.md` §5 puts it.

4. **`budget` reports; it never gates.** Exceeding the ceiling exits 1 (findings) and appears in
   the report with the skills sorted by cost. It never refuses a mint: a surface may legitimately
   be large, and the decision to cut is the human's. Exit 2 stays reserved for a genuine refusal,
   as in `specs.py`.

5. **Evaluation is its own on-demand skill, never a sweep or conductor stage.** `/skill:eval`
   spawns subagents and burns real tokens per run; folding it into `quenching-skill-align-and-update`
   would make a converging loop unboundedly expensive and would let a conducted pass rewrite a
   description on evidence the human never saw. It sits beside `/docs:import` in the plugin's
   shape: a per-item tool the human invokes.

6. **The eval artifacts adopt `skill-creator`'s formats verbatim** — `evals/evals.json` beside the
   skill, per-case `grading.json` with evidence strings, `benchmark.json` with a with/without
   delta over pass rate, tokens, and duration. Divergence would buy nothing and would make the
   plugin's evals unreadable by the tool most adopting repos already have installed.

7. **`.claude/agents/` is inventoried by the existing sweep; minting an agent is a new skill.**
   This is the mint/sweep split the front already proved for skills, applied unchanged — and it
   keeps this plan's change to `quenching-skill-align` additive (it reports more; it renames
   nothing new).

8. **The mandatory wrapper stays, and the standard states why.** With commands and skills merged
   in Claude Code, the wrapper's remaining value is the `:`-namespaced `/` tree. That is a real
   discovery story and its measured cost is 2,072 characters. The standard records it as a
   trade-off with a stated revisit trigger (`budget` showing wrappers displacing descriptions)
   rather than as an unexamined structural fact.

9. **The context diet cuts duplication, never triggers.** The trimming pass removes `when_to_use`
   text that restates the description's `Not for:` boundary and prose already implied by the first
   sentence. Trigger phrases are not touched by hand; where a description must still shrink,
   `/skill:eval`'s description tuning decides which triggers earn their place, on measured
   should-trigger / should-not-trigger hit rates.

10. **Phases are independently shippable.** Each `tasks.md` section leaves the plugin releasable:
    the tool lands and is dogfooded before any skill depends on it; the diet lands before the new
    skills add to the budget; the three new skills land one at a time, each with its wrapper and
    its manual entries.

## Alternatives Considered

- **Delegate evaluation entirely to the official `skill-creator` plugin and write no eval skill.**
  It is the better tool for the generic loop and this plan adopts its formats — but it knows
  nothing about the OKF tail, the registry zone, the taxonomy, or the `Not for:` boundary, so its
  output would stop exactly where this plugin's obligations begin. Lost on integration, not on
  quality; `/skill:eval` wraps the loop and lands its conclusions in the repo's own artifacts.
- **Skip the tool and fix the doctrine by hand.** Cheapest path, and it is what produced the
  current state: the caps were already doctrine when both violations were written. A rule with no
  verifier decays; that is the whole finding.
- **Make `lint` a hook (`PostToolUse` on `.claude/skills/**`), like `okf-validate.py`.** Rejected
  for now: a skill body is authored over many turns and a hook firing mid-draft would report
  violations that the next edit fixes. The tool is built so a hook mode can be added later without
  changing its checks.
- **One combined `quenching-skill-audit` skill instead of extending the existing three.** It would
  duplicate the inventory the sweep already performs and give the front a fourth entry point
  outside the 2×4 matrix the plugin's shape is built on.
- **Widen the front to every `.claude/` surface at once** (agents, settings, workflows, output
  styles, MCP). Rejected as a plan shape: the sweep presents one plan for one confirmation, and a
  five-surface inventory makes that plan longer than a human will read — which is how a
  one-OK model degrades into rubber-stamping.

## Open Decisions

- **The numeric always-on ceiling `budget` warns at.** Decided after `budget` has run on this
  plugin plus at least two adopting repos; until then the standard carries the measured baseline
  (36,651 characters) as the ceiling and is born `authority: background`.
- **Whether `quenching-skill-package` also emits a marketplace manifest for a multi-plugin repo, or
  only a single plugin manifest.** Decided at its mint, from what the first real packaging run of
  this repository's own surface requires.
- **Whether Stage 2's judgment half eventually reads `benchmark.json` instead of the body.**
  Decided once at least one skill in this plugin has a committed benchmark — evidence first, rule
  after.
- **Whether `settings.json` findings are ever auto-fixed.** This plan only reports them. Revisited
  when the sweep has run on a repo whose hook wiring is actually broken.

## Risks

- **The plan is large.** Mitigation: the phase ordering in decision 10 — any section can be the
  last one applied and the plugin still releases.
- **Trimming 28 descriptions silently breaks trigger firing.** Mitigation: trimming is bounded to
  restated boundaries (decision 9), `lint` verifies caps and trigger position after every edit, and
  the eval skill's description tuning is run on any skill whose triggers had to change.
- **Tool and doctrine drift apart.** Mitigation: one owner per fact — `lint`'s checks are the
  normative statement of the mechanical rules and `doctrine.md`/`taxonomy.md` cite the codes
  instead of restating thresholds.
- **The interpreter resolution problem this repo already has** (`python3`/`py` resolving to the
  Windows Store stub). Mitigation: `skills.py` reuses the resolution fallback the `specs/` skills
  already carry, and every task that runs it declares the command it verified with.
- **Extending the inventory widens the sweep's blast radius.** Mitigation: `agents/`,
  `settings.json`, and `workflows/` are **report-only** in this plan — no rename, no move, no
  write — so the confirmed plan's write set is unchanged from today's.
- **`skills.py` becomes a second implementation of rules `okf-validate.py` already applies to the
  registry doc.** Mitigation: `skills.py` owns the GENERATED zone's *content*; the doc's OKF
  conformance (frontmatter, index listing, log) stays `okf-validate.py`'s, and the tasks state the
  split explicitly.
