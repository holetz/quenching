---
slug: declare-repo-body-language
title: Declare the repo's body language in docs/standards so every command reads it for free
verification: per-section
priority: {level: 16, criticality: high, date: 2026-07-29}
refined: {mode: adversarial, date: 2026-07-29}
approved: {date: 2026-07-29}
---

# Declare the repo's body language in docs/standards so every command reads it for free

<!-- ONE spec is ONE file for its whole lifecycle. Phases enrich it; they never split it.

     `specs.py new` stamps the frontmatter and `## Problem` ALONE — a captured spec is four
     lines of body, not a fourteen-heading skeleton. Every other heading below is created on
     first write by `specs.py section <slug> "<Heading>" --write`, which inserts it in the
     canonical position with the guidance comment kept here.

     THE STAGE-SCOPED EXPLICIT-NONE RULE. A heading is required — and required to carry
     `- none — <reason>` when it has nothing in it — only once ITS OWN gate is reached:

       new (capture)        `## Problem`
       ready (derived)      the nine definition sections (`## Problem` .. `## Risks`)
                            AND `## Tasks`
       ready (warn only)    `## Overview` non-empty, `## Handoff` non-empty
       promote -> archive/  `## Outcome`

     `ready` is a DERIVED STAGE, not a folder: a spec lives in `plans/` for its whole active
     life, and filling those ten sections is what makes it ready. Nothing refuses on that
     gate — it is a floor `execute` reports against, and the human's go-ahead is the
     `approved:` frontmatter record, asked for inline.

     Before its gate, a heading's absence is NOT an omission — it is a not-yet. After its
     gate, three rules decide whether a section counts as filled:

       1. `- none — <reason>` counts as filled. An omission and a null are different facts.
       2. A heading present with an EMPTY body is malformed and refuses. It is neither an
          answer nor a not-yet.
       3. An absent heading before its gate is legal.

     Headings are a PARSED contract — canonical English, exactly as written here. Body prose
     follows the repo's language. A heading outside this set is a stray and validate flags it.

     AUDIENCE. Each section names who reads it. `## Overview`/`## Problem`/`## Proposal`/
     `## Design` are for the human — examples and plain language belong there.
     `## Handoff`/`## Tasks` are for agents — terse, with `files:`/`verify:`/`pattern:`
     metadata. An orchestrator never sends the human sections to an executor; that is what
     lets one file serve both audiences without bloating agent context. -->

## Overview

Binds the unbound phrase "the repo's language", which six clauses across the standards and the
shipped references defer to and none of them defines. A repository declares its body language as a
BCP-47 tag in one line of its **root** harness file — in context at session start, and working
without a `docs/` bundle — while a shipped standards doc **owns** the rule those six clauses now cite
instead of restating. The declared language governs every body, agent-facing sections included.

The owner lands in a new `docs/standards/agents/` subject — *how we instruct agents* — which grows
the locked canonical tree by one, because `naming/` governs names and this rule names nothing, and
`automation/` collides in the repositories most likely to adopt the bundle.

`/docs:align` asks once on adoption; silence stays unconstrained, so adoption is opt-in per
repository and nothing becomes retroactively non-conformant.
## Problem

Spec bodies are written in English today, which makes them hard to read for the users of a
repository whose working language is not English (Portuguese, for instance). The canonical-surface
rule already fixes what must stay English — folder names, file slugs, frontmatter keys, `type`
values — but it says nothing about where a repository *declares* which language its bodies should
be written in, so today every command either guesses or leaves it to whoever is typing.

That declaration needs a home of its own in the repo — preferably under `docs/standards/` — and
reaching it has to be nearly free for the agent: cheap enough that knowing the correct setting is
never a reason to skip checking. A hook that reads it automatically is one candidate mechanism.

## Proposal

Six clauses — two in `docs/standards/`, four in `assets/references/` — defer body prose to "the
repo's language", and nothing anywhere binds that phrase to a value. This spec binds it, with one
mechanism serving both this repository and every repository the plugin aligns.

A repository declares its body language in one line of its **root** harness file (`CLAUDE.md` /
`AGENTS.md`): in context at session start, costing zero tool calls, and working in a repository that
has `specs/` and no `docs/` bundle. **Only the root harness carries the declaration.** A nested
harness file (`docs/standards/CLAUDE.md`) loads when that folder is touched, not at session start,
so it would deliver none of the zero cost the shape is chosen for.

The statement of the rule gets **one owner** — `docs/standards/naming/body-language.md`, shipped in
the skeleton under `assets/docs/`. The six clauses stop restating the rule and cite that doc
instead: the collapse `docs/standards/architecture/plugin-layout.md` already argues for, applied to
a rule that had been written out six times.

`/docs:align` asks the language **once**, when a repository adopts the bundle, and writes the line
into the root harness; `/docs:harness` keeps it thereafter. **Silence keeps its current meaning** —
a repository that declares nothing is under no constraint, exactly as the six `MAY` clauses read
today. Nothing becomes retroactively non-conformant and no adopted repository has to change.

Afterwards, an agent that needs to know which language a body is written in reads it for free at
session start, instead of guessing or asking whoever is typing.
## Out of Scope

- **Translating the bodies that already exist.** Declaring a language does not rewrite the
  thirty-five English docs under `docs/standards/`, nor any target repository's. That is a
  migration, and it is its own spec.
- **Machine enforcement.** No natural-language check enters `okf-validate.py` —
  `assets/references/docs-align/conformance.md` already records that a validator cannot reliably
  detect a document's language. The declaration is applied by convention, as it is today.
- **The canonical surface.** Folder names, file slugs, frontmatter keys, `type` values and the
  parsed `##` headings stay canonical English. This is the existing rule in
  `docs/standards/naming/command-surface.md`, named here as the boundary this spec complements —
  not something it changes.
- **The plugin's own surface.** The twenty-six command `description`s and every body under
  `commands/**` are English, whatever language a target repository declares.

## Impact

**Code and content this spec touches:** the six restating sites listed in `## Design`;
`docs/index.md` and `plugins/quenching/assets/docs/index.md`, whose "only `audience: human`
material follows the repo's language" line is narrower than what this spec decides;
`plugins/quenching/assets/references/docs-align/taxonomy.md`, whose §The canonical tree (locked)
grows by one subject; the two `standards/index.md` subtopic lists and the two new
`agents/index.md` subject listings (reserved listings, not standards — which is why they are not
bulleted below); `plugins/quenching/commands/docs/align.md` (the one-time question on adoption);
and `plugins/quenching/commands/docs/harness.md` (the declaration line as a KEEP that never
paraphrases the rule).

### Standards this spec will write into docs/standards/

- `docs/standards/agents/body-language.md` — the rule's single owner, written twice at the same
  bundle-relative path: once into the shipped skeleton under
  `plugins/quenching/assets/docs/`, and once into this repository's own bundle, so the repo that
  ships the rule is also its first consumer
## Validation

- `grep -rn "the repo.s language" docs/ plugins/quenching/assets/references/` returns the five citing
  sites and **no** restatement of the rule, plus `okf-spec.md`'s deliberate self-contained
  statement. A sixth restatement anywhere is a failure.
- The root harness line carries a value and a citation and **no paraphrase of the rule** — the
  invariant that keeps this design compliant with `/docs:harness` §Move, never copy.
- `grep -n 'agents/' plugins/quenching/assets/references/docs-align/taxonomy.md` shows the subject
  inside §The canonical tree (locked), and both `standards/index.md` files carry its subtopic row.
  A subject that exists on disk but not in the locked tree is the nonconformity this spec is
  correcting, not a state it may leave behind.
- `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` and the same on `docs`
  both report `0 error(s), 0 warning(s)` with the new subject and the new standards doc in place.
## Design

**Rule and value are two different facts, in one place each.** The harness line carries the
**value** and a citation; the standards doc carries the **contract** — what declaring means, what
silence means. Neither paraphrases the other. That is what keeps the mechanism on the right side of
`/docs:harness` §Move, never copy: a rule restated in a harness file is precisely the drift that
command exists to remove, while a value plus a citation is not a restatement.

**The value is a BCP-47 tag** (`pt-BR`, `en`), not a language name. A name invites `Português`,
`portugues` and `Portuguese` to mean the same thing, and no citation resolves that; a tag is one
string with one spelling.

**The declared language governs every body**, `## Handoff` and `## Tasks` included — those stay
terse, because they are agent context, but terse in the declared language. This is wider than
`docs/index.md`, which today scopes the rule to `audience: human` material only, so that line and
its skeleton twin are reconciled as part of this spec (see `## Impact`).

**The owner is `docs/standards/agents/body-language.md`** — a new subject, and the locked tree grows
by one to hold it. The subject is *how we instruct agents*: what the always-on surface declares to
whoever reads it at session start. Two nearer-looking homes were rejected on the record in
`## Alternatives Considered`; the short form is that `naming/` governs names and this rule names
nothing, and `automation/` collides in the repositories most likely to adopt the bundle — a repo
whose own product is automation cannot tell "how we drive Claude Code" from "our automation domain"
under one folder. `automation/` is also not in the shipped set: it is this repository's local
subject, which is precisely the ambiguity being avoided.

Growing the locked tree overlaps the queued `revise-standards-subject-folders`; see `## Risks`.

The four `assets/references/**` sites cite the owner by its bundle-relative path, which **only
resolves once the skeleton is installed** — accepted, with the mitigation that task ordering ships
the doc before any site is edited to cite it. In a repository that uses `specs/` and never adopts
the bundle the citation does not resolve; see `## Risks`.

The collapse, by layer:

| Layer | Site | After |
| --- | --- | --- |
| `docs/standards` | `naming/command-surface.md:118` | cites the owner |
| `docs/standards` | `workflows/plan-artifacts.md:69` | cites the owner |
| `assets/references` | `specs-develop/spec-driven.md:119` | cites the owner |
| `assets/references` | `docs-align/taxonomy.md:117` | cites the owner |
| `assets/references` | `docs-align/migration.md:40` | cites the owner |
| `assets/references` | `docs-align/okf-spec.md:111` | **keeps a self-contained statement** — it is the contract other implementers read, and a format spec that defers to a repo-local doc stops being self-describing |
## Alternatives Considered

| Approach | Why it lost |
| --- | --- |
| **The owner under `naming/`** — where the clause being bound already lives | Neighbourhood, not belonging. `docs/standards/naming/index.md` scopes the subject to "the globally unique, predictable **names** this repo commits to", and the skeleton's twin scopes it to **data** naming outright — `tables · columns · descriptions · schemas-catalogs`. Which natural language prose is written in names nothing. Putting it there meant stretching a declared subject from inside a task. |
| **The owner under `automation/`** | The best-fitting existing folder — the carrier is the always-on harness and `automation/context-budget.md` already governs that budget — and rejected anyway, because it collides in exactly the repositories that adopt this bundle: one whose product *is* automation cannot distinguish "how we drive Claude Code" from "our automation domain" under one folder. It is also not in the shipped nine; it is this repo's local subject, which is the same ambiguity one level down. |
| **A key on `docs/index.md`**, beside `okf_version` | Machine-readable buys nothing here: `docs-align/conformance.md` records that no validator will ever branch on this value, so the only consumer is the agent — which reads the harness for free. It also costs an edit to `okf-spec.md`, whose line 92 pins that listing to `okf_version` alone, colliding with the queued `upgrade-okf-to-v0-2`. And it excludes a repository with `specs/` and no bundle. |
| **A `SessionStart` hook injecting the value** | A process per session, forever, to deliver a constant the auto-loaded harness already delivers for nothing. `docs/standards/automation/hooks.md` asks a hook to justify its scope; this one cannot. |
| **The standards doc alone, with no carrier** | Gives the rule a home, an authority and a maintainer, but nothing makes an agent read it — discovery is exactly the cost `## Problem` says must stay near zero. |
| **Do nothing** | The six clauses say `MAY`, so a repository writing Portuguese is already conformant without declaring anything. Rejected because the gap is not conformance: it is that an agent has no way to *know*, which is what makes it guess. |
## Open Decisions

- **Is `AGENTS.md` a carrier on equal footing with `CLAUDE.md`?** This spec assumes it is, because
  the plugin already treats the pair as one in nine places and `/docs:harness` sweeps both. **How it
  will be decided:** by the sibling spec `decide-agents-md-harness-default`, not by this one. If it
  makes `AGENTS.md` the default target, what changes is the owner doc's wording, not this
  mechanism — which is why this spec does not wait on it.

## Risks

- **This spec now grows the locked tree, which `revise-standards-subject-folders` also intends to
  revise.** Two specs editing the same declared subject set can each land a half of it. **Accepted,
  with the boundary stated:** this spec adds exactly one subject and touches no other, and the
  sibling spec remains free to revise the set as a whole afterwards — including renaming what this
  one added. What this spec must not do is pre-empt that revision by reorganizing subjects it does
  not need. If the sibling lands first, task 1 shrinks to a row in whatever set it produced.
- **The citation does not resolve in a repository that never adopts the bundle.** A `specs/`-only
  repository reads a reference citing `docs/standards/agents/body-language.md`, which it does not
  have. **Accepted risk** — the alternative was an owner under `assets/`, which would put the rule
  outside the bundle it governs. Mitigation: the four reference citations name the doc as *the
  bundle's*, so a repository without one reads a pointer to something it knowingly does not have,
  rather than a broken promise.
- **`agents/` is read as "agent definitions" rather than "how we instruct agents".** The name is
  short enough to invite the narrower reading, and `docs/standards/automation/agents.md` already
  holds the `.claude/agents/` definition contract. Mitigated by the subject `index.md` stating the
  boundary in its first line, and by that existing doc being a candidate to move there when the
  sibling spec revises the set — not by this one.
- **Rule and value drift apart.** Mitigated by the `## Validation` invariant: the harness line never
  paraphrases the rule, so there is nothing for it to drift from.
- **Task ordering.** Editing a site to cite the doc before the skeleton ships it leaves a dangling
  citation in a released plugin. Mitigated by the ordering declared in `## Tasks`.
## Handoff

Nothing built yet — tasks 1–7 open, none blocked, none committed. Two orderings are load-bearing:
task 1 opens the subject before anything is written into it, and task 2 ships the owner before task 5
makes any site cite it.

State a fresh executor cannot derive:

- The `agents/` subject exists in neither tree. Task 1 creates it **and** declares it in
  `taxonomy.md` §The canonical tree (locked) — editing that section is intended here, not a slip.
- Do not fold `docs/standards/automation/agents.md` into the new subject. It is the `.claude/agents/`
  definition contract, it stays where it is, and moving it belongs to
  `revise-standards-subject-folders`.
- The owner doc exists nowhere yet. Both writes are creations.
- The six sites still restate the rule verbatim. `okf-spec.md` is the one that keeps its statement —
  do not collapse it.
- `docs/index.md` and `plugins/quenching/assets/docs/index.md` still scope the rule to
  `audience: human`; task 4 widens them. Reading them before task 4 gives the pre-decision wording.
- This session runs without a `plan/` branch: isolation was declined because the session's
  designated branch is mandated. No `branch` record is stamped, and commits land on that branch.
- `verification: per-section` — verify at each task's own boundary, per that task's `verify:`.
## Tasks

Ordered, and the ordering is load-bearing twice: task 1 opens the subject before anything is written
into it, and task 2 ships the owner before task 5 makes any site cite it — or a released plugin
carries a dangling citation. Each task names its declared `docs/standards/**` path on its own
checkbox line, because `sp-impact-uncovered` matches that line and not the `files:` continuation.

- [ ] 1 Open the `agents/` subject in both trees — folder + `index.md` in the skeleton and in this
  repo, the subject added to `taxonomy.md` §The canonical tree (locked), and a subtopic row in both
  `standards/index.md`. The subject's boundary: how we instruct agents — what the always-on surface
  declares. Distinct from `automation/` (this repo's local subject for the command surface itself).
  files: `plugins/quenching/assets/references/docs-align/taxonomy.md`, `plugins/quenching/assets/docs/standards/index.md`, `plugins/quenching/assets/docs/standards/agents/index.md`, `docs/standards/index.md`, `docs/standards/agents/index.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` and `... docs` both report `0 error(s), 0 warning(s)`
- [ ] 2 Ship the owner in the skeleton at `docs/standards/agents/body-language.md` under `assets/docs/`
  States what declaring means, that only the **root** harness carries it, that the value is a BCP-47
  tag, and that silence means no constraint. Full OKF frontmatter; `authority: background` until the
  rule is proven by use.
  files: `plugins/quenching/assets/docs/standards/agents/body-language.md`, `plugins/quenching/assets/docs/standards/agents/index.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py assets/docs` → `0 error(s), 0 warning(s)`
- [ ] 3 Install the same owner at `docs/standards/agents/body-language.md` in this repo's bundle, and
  declare this repository's own body language in the root harness — the dogfood the spec claims.
  files: `docs/standards/agents/body-language.md`, `docs/standards/agents/index.md`, `CLAUDE.md`
  verify: `python3 plugins/quenching/assets/hooks/okf-validate.py docs` → `0 error(s), 0 warning(s)`
- [ ] 4 Reconcile the two index lines that scope the rule to `audience: human` with this spec's
  decision that the declared language governs every body.
  files: `docs/index.md`, `plugins/quenching/assets/docs/index.md`
  verify: `grep -n 'audience: human' docs/index.md plugins/quenching/assets/docs/index.md` shows no
  language clause narrowed by audience
- [ ] 5 Collapse the six restating sites to cite the owner; `okf-spec.md` keeps its self-contained
  statement with the reason recorded inline.
  files: `docs/standards/naming/command-surface.md`, `docs/standards/workflows/plan-artifacts.md`, `plugins/quenching/assets/references/specs-develop/spec-driven.md`, `plugins/quenching/assets/references/docs-align/taxonomy.md`, `plugins/quenching/assets/references/docs-align/migration.md`, `plugins/quenching/assets/references/docs-align/okf-spec.md`
  verify: the `## Validation` grep returns five citing sites and no restatement
- [ ] 6 Teach `/docs:align` to ask the body language once on adoption and write the line into the
  root harness file.
  files: `plugins/quenching/commands/docs/align.md`
  verify: `grep -n 'body language' plugins/quenching/commands/docs/align.md`
- [ ] 7 Teach `/docs:harness` that the declaration line is a KEEP and must never paraphrase the
  rule — the invariant `## Validation` asserts.
  files: `plugins/quenching/commands/docs/harness.md`
  verify: `grep -n 'body language' plugins/quenching/commands/docs/harness.md`
