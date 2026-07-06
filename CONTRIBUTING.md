# Contributing — maintaining the `claude-quenching` method

This repository hosts a **living method**, not just a static plugin. The shipped
skill ([`plugins/claude-quenching/skills/quenching-management/`](plugins/claude-quenching/skills/quenching-management/))
describes **only the present** — what the method does today. There is **no separate
evolution log**: the history of how the method got here lives in **git**, and the
commit message is where you record anything about a change worth remembering beyond
its diff.

## The maintainer skill

There is **one** dev-only maintainer skill, at the repository root in
[`.claude/skills/quenching-maintainer/`](.claude/skills/quenching-maintainer/) —
**never shipped, never installed into a target repo.** It runs **inline** in the
maintainer's conversation, so the maintainer sees the surgical change directly.

**[`quenching-maintainer`](.claude/skills/quenching-maintainer/SKILL.md)** accepts
**mixed directions in a single invocation** and makes the changes directly in
`SKILL.md` / `references/` / `assets/`:

- **Revise a section** — sharpen a smell, prune bloat, fix a stale source, merge
  duplicates, clarify a criterion.
- **Evolve a concept** — add or reshape something the method doesn't yet handle,
  grounded in current Claude/Claude Code practice.
- **Change the main skill** — edit the `SKILL.md` workflow itself.
- **Analyze a repository/session** — audit the method's own source for drift and
  contradiction, or mine a real application session under `~/.claude/projects/` for
  field evidence and apply the fixes it justifies.

A request may combine several of these — e.g. "audit that run **and** fix the smell
it tripped over **and** tighten step 5." Trigger it with *"evolve/refine/critique
the method"*, *"revise section X"*, *"change the main skill"*, *"run a retrospective
on session Y"*, *"harvest field feedback"*, or any mix.

> **No log to keep in sync.** Earlier versions of this method split the work across
> three skills (`evolutionist` / `reviewer` / `retrospective`) and recorded every
> edit as an ADR round/revision in an `evolution/` layer. That apparatus is gone.
> Do **not** reintroduce round/revision numbering, a spine, an exclusion index, a
> review queue, or an advance backlog. Make the change; commit it; move on.

## How to change the method

1. Invoke `quenching-maintainer` with what you want done (one direction or several).
2. It locates the relevant surface, reads only what's relevant, makes the surgical
   change(s), self-checks the invariants, and reports what changed.
3. Keep `SKILL.md` focused on application (the 8 steps) and under ~500 lines — push
   detail to `references/`. The active spec is **present-tense only**; if a change
   has history worth keeping, put it in the commit message, not in the spec.
4. When the change is worth a commit, use the `commit-incremental` skill to slice it
   into atomic commits.

## Grounding a change

When a change hinges on how Claude or Claude Code actually behaves (a new skills /
hooks / sub-agent / CLAUDE.md capability), verify it against **current** official
Anthropic sources — `docs.claude.com`, the engineering blog — dated, rather than
assuming. This is about getting the change right, not a bureaucratic gate: a wording
cleanup or a bloat prune needs no citation.

## Evaluating the method (the curator is a production tool)

This method **is an agent tool**, so it is evaluated against **realistic tasks**,
not by inspection. When a change alters a detection rule (a smell / grep / "good"
criterion), sanity-check it against **fixtures** — small sample repos with one
**known planted gap** each — reading three measures:

- **Hit rate per dimension** — was the planted gap flagged in the right dimension,
  with `file:line` evidence?
- **False-negative rate (the metric that matters most)** — did a real gap slip
  through? A false negative is worse than a false positive: the base *looks*
  audited and isn't.
- **Cost (tokens) per dimension** — does one dimension consume disproportionately
  (a candidate to push to the auditor sub-agent)?

The *fit-to-repo* layer (Step 4 emphasis modulation) is evaluated the same way, with
**planted-profile fixtures** carrying the **expected emphasis/roadmap** as ground
truth — measuring **prescription-hit** and **prescription-false-negative** (a
clearly-shaped repo that came out with flat emphasis). A fixture with an
**ambiguous shape** expects **flat emphasis** as the correct answer (strong emphasis
there is over-prescription).

## Repository conventions

- The plugin is **self-contained and portable** — no change may reintroduce coupling
  to a specific repo or to an external skill.
- The payloads under `assets/` are **inert installers**, not active components — they
  must never become auto-discoverable native skills/hooks of the plugin.
- The `.claude/skills/` and `mkdocs/` layers are **dev-only** and must stay outside
  `plugins/claude-quenching/` so they are never shipped.
