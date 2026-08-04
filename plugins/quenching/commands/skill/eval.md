---
description: Measure whether a skill/command teaches anything — with/without runs, graded on evidence. Triggers on "measure whether this command teaches anything", "run the with/without eval on this skill", "tune this command's description on the hit rates". Not for: minting or editing ONE command's body → /skill:new.
argument-hint: [skill-name]
allowed-tools: Bash(python3:*), Bash(py:*), Read, Grep, Glob, Write, Edit, Task, AskUserQuestion
---

# /quenching:skill:eval — measure whether a skill teaches anything

The plugin's doctrine says triggers belong in the second sentence, that a step needs a checkable
criterion, that a body earns its context. Every one of those is a **hypothesis**. This skill is
how one stops being a hypothesis: run the cases with the skill and without it, and read the
difference.

The premise is `superpowers`': *if you didn't watch an agent fail without the skill, you don't
know if the skill teaches the right thing.* A with-only run cannot tell a skill that works from a
task the model could already do.

The artifact shapes — `evals.json`, `grading.json`, `benchmark.json` — the assertion-quality
rules, and the description-tuning loop live in
[skill-eval/evaluation.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-eval/evaluation.md), adopted from Anthropic's `skill-creator` so
this plugin's evals stay readable by the tool most adopting repos already have. This body owns
the workflow; that file owns the formats and never gets restated here.

## Doctrine

- **Both arms, always.** A case runs twice: once with the skill available, once with it absent.
  Reporting only the with-skill arm measures the model, not the skill.
- **Isolated subagents, never this context.** Each arm is a fresh `Task`. An arm that ran in this
  conversation has already read the skill — the without-arm would be contaminated by the very
  text it is supposed to lack.
- **Evidence or it did not happen.** Every assertion is graded pass/fail with a **quoted excerpt**
  from that arm's output. A grade with no quote is not a grade; mark it `unknown` and say so.
- **A zero delta is a finding, not a failure to report around.** If both arms pass equally, the
  skill taught nothing on those cases — which is information about the skill or about the cases,
  and the report says which it cannot distinguish.
- **This never duplicates `lint`.** The caps, trigger position, the boundary, body length, step
  criteria, tool scoping are `skills.py lint`'s and are reported by code. This skill measures
  **behaviour**; a clean lint is its precondition, not its subject.
- **Never rewrites the body.** Authoring is `/quenching:skill:new`'s. A finding here is reported
  with the `/quenching:skill:new <name>` invocation that acts on it — except the description, which step 7
  may edit under its own confirmation, because a trigger's fate is decided by the hit rates this
  skill just measured.

## Resolving the tool

Resolve `skills.py` per
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool §Write the resolved path literally on every invocation; branch on the
**exit code** (0 ok · 1 findings · 2 refusal) and the `--json`.

**Input**: optionally a skill name. If omitted, infer from context; if more than one is plausible,
ask with **AskUserQuestion** — never guess which skill is being measured.

## Workflow

### 1. Select the skill and check its floor
Resolve the skill folder. Run `skills.py lint <skill-folder> --json`: an **error** means the skill
does not load as intended and any measurement would describe a broken skill — report it and stop.
A **warn** is noted in the report and does not block.
**Done when:** one skill is named back to the user and `lint` has run.

### 2. Read the command as its own specification
Read the command file and every reference it points to. The description's promise —
*when it fires, and what exists when it finishes* — is what the cases must test. Note each
distinct branch the workflow can take; a branch with no case is untested surface.
**Done when:** every branch and every promise is listed.

### 3. Derive the cases
Per [skill-eval/evaluation.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-eval/evaluation.md) §Writing cases: one case per branch, each
a realistic user prompt plus assertions about the **observable outcome** — a file that exists, a
zone regenerated, a command reported as run — never about the wording of the reply. Include at
least one case the skill should **decline** (its `Not for:` boundary), and the should-trigger /
should-not-trigger prompts step 7 needs.
**Done when:** every branch has a case and every case has at least one observable assertion.

### 4. Present ONE plan → gate on the OK
Show: the skill, the case list with each case's branch and assertions, the arm count
(cases × 2), and the trigger prompts. State the cost plainly — this is the one skill on the front
that spawns subagents per run, and the human is authorizing that spend.
**Done when:** the user has answered; declined → nothing written, run ends.

### 5. Write the case set, then run both arms
Write `evals.json` into the tree mirroring the command's path — `.claude/evals/<path>/` in a
target repo, `${CLAUDE_PLUGIN_ROOT}/assets/evals/<path>/` in this plugin
([skill-eval/evaluation.md](${CLAUDE_PLUGIN_ROOT}/assets/references/skill-eval/evaluation.md)
§Where the artifacts live). Then, per case, dispatch **two** `Task` subagents — one told the
skill is available, one given the same prompt with no reference to it. Pin both to the session
model; **never `haiku`** (a cheaper judge changes what the delta measures). Record each arm's
output, token count, and duration.

Arms are independent: dispatch them concurrently, and a subagent that dies is recorded as
`error`, never silently dropped.
**Done when:** every case has two recorded arms or a recorded error.

### 6. Grade with evidence, then aggregate
Grade every assertion in every arm pass/fail with a quoted excerpt, into the per-case
`grading.json`. Aggregate into `benchmark.json`: pass rate, tokens, and duration for each arm and
the **delta** between them.
**Done when:** `grading.json` and `benchmark.json` exist and every assertion carries a grade with
evidence or an explicit `unknown`.

### 7. Tune the description on the hit rates (optional, own confirmation)
Run the should-trigger and should-not-trigger prompts and count how often the description routes
correctly. A trigger no should-trigger prompt reaches is **sediment**; a should-not-trigger prompt
that fires is a boundary the description fails to state. Propose the edit, show the measured rates
behind it, and apply on its own OK — then re-run `skills.py lint` so the caps still hold.
**Done when:** the rates are reported and the edit is applied or declined.

### 8. Report
The skill; cases run; pass rate with and without, and the delta; tokens and duration for each arm;
every assertion graded `unknown` and why; the trigger hit rates; and the artifacts written. Say
plainly when the delta is **zero** — that is the outcome this skill exists to surface, and burying
it makes the whole run decorative.
**Done when:** the delta is stated in the report as a number.

## Invariants

- Never run only the with-skill arm, and never reuse this context as an arm.
- Never grade without evidence — `unknown` is an honest grade, an unquoted pass is not.
- Never downgrade an arm's model to `haiku`; the delta is only comparable between equal arms.
- Never rewrite a skill body here — report it with its `/quenching:skill:new` invocation. The description is
  the single exception, and only under step 7's own confirmation.
- Never duplicate a `skills.py lint` check; report its findings by code and move on.
- Never hand this command file `context: fork` — steps 4 and 7 gate mid-flow.
