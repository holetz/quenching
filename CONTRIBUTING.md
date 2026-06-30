# Contributing — evolving the `claude-quenching` method

This repository hosts a **living method**, not just a static plugin. The shipped
skill ([`plugins/claude-quenching/skills/quenching-management/`](plugins/claude-quenching/skills/quenching-management/))
describes **only the present** — what the method does today. **How it got there**
(rounds, revisions, superseded decisions) lives **only** in the non-shipped
[`evolution/`](evolution/) layer.

> **Golden rule: do not edit the method by hand outside the flow below.** Editing
> `SKILL.md`/`references/`/`assets/` directly breaks the log that prevents
> re-attacking a solved problem (evolutionist) or losing the improvement trail
> (reviewer).

## The two maintainer agents

Both live at the repository root in [`.claude/agents/`](.claude/agents/) (dev-only —
**never installed into a target repo**), and both read the next action from the
spine [`evolution/README.md`](evolution/README.md) and write detail into the right
context file in [`evolution/log/`](evolution/log/).

- **[`quenching-evolutionist`](.claude/agents/quenching-evolutionist.md) — advances
  the frontier.** Each round (`R*`) makes **one** improvement beyond today's state,
  on a topic **not yet addressed**, and increments `current-round`. Trigger:
  *"evolve the method"*, *"run an evolution round"*.
- **[`quenching-reviewer`](.claude/agents/quenching-reviewer.md) — critiques and
  refines what already exists.** Each invocation (`Rev*`) revisits an
  already-made definition and improves it (sharpens a smell, fixes a stale source,
  merges/prunes, or supersedes a round) **without** advancing the frontier.
  Trigger: *"critique/review/refine the method"*, *"go back to a round"*.

The research input for both lives in [`evolution/research/`](evolution/research/).
Every round needs **≥1 citable source** (URL + date) or it does not close.

## How to evolve the method

1. Invoke the relevant agent (e.g. *"run an evolution round"* →
   `quenching-evolutionist`; *"refine round N"* → `quenching-reviewer`).
2. The agent reads the spine, picks the next frontier / revision target, does the
   research, makes **one surgical change**, and records the round/revision in the
   per-context log + updates the anchor state in the spine.
3. Keep `SKILL.md` focused on application (the 8 steps) and under ~500 lines —
   push detail to `references/`. The active spec is **present-tense only**.

## Evaluating the method (the curator is a production tool)

This method **is an agent tool**, so it is evaluated against **realistic tasks**,
not by inspection. Before closing a round that changes a detection rule
(smell / grep / "good" criterion), the evolutionist runs a **minimal harness** of
**fixtures** — small sample repos with one **known planted gap** each — and reads
three measures:

- **Hit rate per dimension** — was the planted gap flagged in the right dimension,
  with `file:line` evidence?
- **False-negative rate (the metric that matters most)** — did a real gap slip
  through? A false negative is worse than a false positive: the base *looks*
  audited and isn't.
- **Cost (tokens) per dimension** — does one dimension consume disproportionately
  (a candidate to push to the auditor sub-agent)?

The *fit-to-repo* layer (Step 4 emphasis modulation) is evaluated the same way, with
**planted-profile fixtures** that carry the **expected emphasis/roadmap** as ground
truth — measuring **prescription-hit** and **prescription-false-negative** (a
clearly-shaped repo that came out with flat emphasis). A fixture with an
**ambiguous shape** expects **flat emphasis** as the correct answer (strong emphasis
there is over-prescription). The fixture catalog lives in
[`evolution/research/14-eval-fixtures.md`](evolution/research/14-eval-fixtures.md).

## Repository conventions

- The plugin is **self-contained and portable** — no round may reintroduce coupling
  to a specific repo or to an external skill.
- The payloads under `assets/` are **inert installers**, not active components — they
  must never become auto-discoverable native skills/hooks of the plugin.
- The `evolution/`, `.claude/agents/` and `docs/` layers are **dev-only** and must
  stay outside `plugins/claude-quenching/` so they are never shipped.
