---
name: quenching-specs-plan-refine
description: >-
  Interrogates an existing plan's artifacts until they are worth building — generating the
  questions nobody thought to ask, ONE at a time with an inline recommendation, and applying
  every accumulated answer in a SINGLE edit at the end. Use when the user asks to "refine the
  plan", "challenge this plan", "poke holes in the proposal", "what am I missing here", "critique
  the design", "run a premortem", "what alternatives did we skip", or "interview me about this
  plan". Four modes select the technique — interview (default; fills the gaps the artifacts
  leave), critic (attacks it as a hostile reviewer), premortem (assumes it already failed and
  works backwards), alternatives (forces the shapes nobody weighed) — each with a declared stop
  condition, so a refinement terminates instead of wandering. Records refined {mode, date} in
  .specs.json, dropping validate's sp-unrefined warning. Never edits code or writes into docs/,
  and never gates: an unrefined plan may always be built. Not for: applying an edit the human
  already formulated → quenching-specs-plan-update (reactive, where this is generative);
  open-ended thinking before any plan exists → quenching-specs-explore (unbounded, where this
  targets one plan and must terminate); creating a missing artifact →
  quenching-specs-plan-propose.
when_to_use: >-
  interrogating a plan's artifacts to surface what nobody asked, then applying the answers in
  one edit. An already-formulated edit is quenching-specs-plan-update; pre-plan thinking is
  quenching-specs-explore.
allowed-tools: Bash(python3:*), Bash(py:*), Read, Glob, Grep, Write, Edit, AskUserQuestion
user-invocable: false
---

# quenching-specs-plan-refine — interrogate a plan until it is worth building

A plan reaches `applyReady` the moment `proposal.md` and `tasks.md` have content. Nothing in that
gate requires anyone to have **disagreed** with it. This skill is the disagreement: it generates
the questions the artifacts never answered, puts them to the human one at a time, and folds the
answers back in.

It is **generative**, which is what separates it from its two neighbours.
`quenching-specs-plan-update` waits for an edit the human already formulated and reconciles it;
`quenching-specs-explore` thinks freely with no target and no stop condition. This skill produces
the questions itself, aims them at one plan's artifacts, and **terminates**.

The four mode scripts and the three shared mechanics live in
[references/techniques.md](references/techniques.md) — read it before running a mode; it is the
owner of the technique, and this body never restates it.

The spec-driven facts (the `specs/` layout, the artifact graph, the artifact formats, the
`specs.py` surface) live in
[../quenching-specs-plan-propose/references/spec-driven.md](../quenching-specs-plan-propose/references/spec-driven.md);
the per-artifact authoring doctrine — the explicit-none rule, the parsed `## Impact` — in
[../quenching-specs-plan-propose/references/artifacts.md](../quenching-specs-plan-propose/references/artifacts.md).

## Resolving the tool

Resolve `specs.py` by the fallback in
[../quenching-specs-backlog-add/references/backlog-zone.md](../quenching-specs-backlog-add/references/backlog-zone.md)
§Resolving the tool: `${CLAUDE_PLUGIN_ROOT}/assets/bin/specs.py` first, then the target's
`.claude/hooks/specs.py`, else the manual fallback (**say so in the report**). Invoke with
`python3`/`py`; branch on the **exit code** (0 ok · 1 findings · 2 refusal) and the `--json`,
never on prose.

**Input**: optionally a plan name and/or a mode (`/specs:plan:refine <plan> --mode critic`).
Either may be omitted; neither is ever guessed silently.

## Steps

### 1. Select the plan

A name was given → use it. Otherwise infer from conversation context, or auto-select when exactly
one active plan exists, or run `specs.py list --json` and pick with **AskUserQuestion** (most
recently modified marked "(Recommended)"). Announce: "Refining plan: `<name>`" and how to override.

Run `specs.py status --plan "<name>" --json`. A plan whose `proposal` is not `done` has nothing to
interrogate — say so and point at `/specs:plan:propose <name>`, then stop.
**Done when:** one plan is selected and its artifact paths are resolved.

### 2. Choose the mode

If the input named one, use it. Otherwise offer all four with **AskUserQuestion**, marking the one
the plan's own state argues for — the recommendation is data, not a coin flip:

| Recommend | When the plan's state shows |
| --- | --- |
| `interview` (default) | `## Out of Scope`, `## Validation`, or `## Open Decisions` is missing or `- none` with no reason; `sp-design-scaffold` is open |
| `critic` | the plan is large, or it reaches into product code, or a `## Impact` standard is uncovered |
| `premortem` | the plan is risky or irreversible — a migration, a rename with a blast radius, a release |
| `alternatives` | `## Alternatives Considered` is absent, empty, or records only one option |

**Done when:** exactly one mode is chosen and named back to the user.

### 3. Read everything the questions must stand on

Read `proposal.md`, `design.md`, and `tasks.md` at the paths `status` resolved — never assume
filenames. If the repo carries an OKF bundle (`docs/index.md` with `okf_version`), also read
`docs/standards/` for the subjects the plan touches and `docs/knowledge/glossary.md`, so the
questions use the repo's own vocabulary and can catch a plan that contradicts a binding contract.
No bundle → skip silently.

Questions must be **specific to this plan**. A question that would read identically against any
plan is noise; delete it rather than ask it.
**Done when:** the artifacts and the relevant standards are read.

### 4. Run the mode — one question at a time

Follow the mode's script in [references/techniques.md](references/techniques.md), under the three
shared mechanics it owns: **one question at a time** with an inline recommendation, **accumulate,
never write mid-flow**, and the mode's **declared stop condition**.

Nothing is written to any artifact during this step. Keep a running list of
`(question, answer, which artifact and section it lands in)`.
**Done when:** the mode's stop condition is met, or the user calls it.

### 5. Present ONE consolidated edit → one OK

Show every accumulated answer as a single plan: per artifact, per section, what changes and the
answer it came from. Anything that turned out to belong outside the plan — a durable rule, a term,
a follow-up task — is listed as a **routed offer**, not an edit (§Guardrails).

Wait for the confirmation. Declined → nothing is written, and the questions and answers are still
reported so the thinking is not lost.
**Done when:** the user has answered.

### 6. Apply, and record the refinement

Apply the confirmed edits to the artifacts, keeping every section in its format per
[artifacts.md](../quenching-specs-plan-propose/references/artifacts.md) — an emptied section
becomes an explicit `- none — <reason>`, never a deleted heading.

Then write the record into `specs/<plan>/.specs.json`, merging into the existing JSON (never
rewriting the file from scratch — `name`, `title`, `created`, `backlogTask`, and `verification`
must survive):

```json
"refined": { "mode": "critic", "date": "2026-07-25" }
```

Re-run `specs.py validate --plan "<name>"` and confirm `sp-unrefined` is gone.
**Done when:** the artifacts are edited, the record is written, and validate is clean.

### 7. Report

The plan and mode; how many questions were asked and answered; the artifacts and sections edited;
the routed offers and whether each was taken; and the next step — `/specs:plan:apply <name>` when
the plan is apply-ready, `/specs:plan:propose <name>` when an artifact is still missing.
**Done when:** the summary is shown.

## Guardrails

- **Never edits code, never writes into `docs/`.** This skill touches a plan's three artifacts and
  `.specs.json`, nothing else. A durable rule surfaced by a question routes to
  `quenching-docs-add`, an understanding to `quenching-docs-learn`, a term to
  `quenching-docs-define`, an out-of-scope follow-up to `quenching-specs-backlog-add` — **offered,
  never auto-written**.
- **One question at a time.** A batch of five questions gets one shallow answer; the mechanic is
  owned by [references/techniques.md](references/techniques.md) and is not optional.
- **Every question carries a recommendation.** "What should the failure budget be?" is work handed
  back to the human. "I'd cap it at five attempts — enough for a flaky test, short of a loop.
  Agree?" is a question they can answer in one word.
- **Accumulate and apply once.** No artifact is edited mid-interrogation, so a refinement the user
  abandons halfway leaves the plan exactly as it was.
- **Refinement never gates.** `applyReady` is untouched and `sp-unrefined` is a warning by design;
  never refuse to let a plan proceed because it was not refined.
- **Never invent an answer the human did not give.** An unanswered question is recorded in
  `## Open Decisions` with how it will be decided — that is a result, not a failure.
- **Never fabricate the record.** `refined` is written only after a real pass with real answers.
