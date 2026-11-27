---
allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read, Grep, Glob, Bash(python3:*), Bash(py:*), AskUserQuestion, Skill
---

# /quenching-specs create — capture one spec, one screen, one turn

**Input**: `$ARGUMENTS` — a short description of the problem, a path to a plan
file, or a plan already developed in this session (including a `<proposed_plan>` block). With no
argument and no identifiable plan in the conversation, ask what to capture.

Creates ONE spec: `/quenching-specs develop` fills its sections, `/quenching-specs execute` builds
it, and `/quenching-specs conclude` closes it out under the same identity.

**One file per step.** Each step below keeps its `**Done when:**` here; how to run it lives in the
step's own file, which a run loads when that step runs and not before. The references a step
cites (the spec layout and gates, the tool surface, the report mold, tool resolution) are cited
by that step's file, never here.

## The one rule: effort proportional to input

This command has two inputs of wildly different richness, and exactly one behaviour: **write down
what you were given, and nothing more.**


| Input                   | What gets written                        |
| ----------------------- | ----------------------------------------- |
| a sentence              | a descriptive title, `## Problem` |
| a plan, from a file or this session | every section the plan actually supports |

The same richness decides the `complexity` this command computes and writes (step 4), **inversely**:
a sentence carries the least evidence, so its definition questions still need a human, while a plan
file already answered most of them. The develop pass re-evaluates the level when it closes.

## Workflow

### 1. Classify the input

Run it from [step 1](.agents/skills/quenching-specs/references/specs-create/step-1-classify.md), read whole.

**Done when:** the path is chosen.

### 2. Choose the title

Run it from [step 2](.agents/skills/quenching-specs/references/specs-create/step-2-title.md), read whole.

**Done when:** a descriptive title is in hand.

### 3. Plan-source path only — read it, and read the bundle

Run it from [step 3](.agents/skills/quenching-specs/references/specs-create/step-3-plan-source.md), read whole.

**Done when:** the plan's parts are classified, or the sentence path skipped this.

### 4. Resolve a subject, a type, tags and `complexity` — decide, never ask

Run it from [step 4](.agents/skills/quenching-specs/references/specs-create/step-4-metadata.md), read whole.

**Done when:** a subject, a type, zero or more tags and a `complexity` level are each resolved (to
a value, or explicitly to none) and reasoned; metadata may be absent, but `complexity` is always
resolved.

### 5. Capture in ONE call

Run it from [step 5](.agents/skills/quenching-specs/references/specs-create/step-5-capture.md), read whole.

**Done when:** `specs_write(verb="create")` exited 0, `validate` ran in the same call, and the locator it
returned is in hand.

### 6. The one screen — capture, correction and direction

Run it from [step 6](.agents/skills/quenching-specs/references/specs-create/step-6-screen.md), read whole.

**Done when:** the screen has been shown and the human's answer — a correction, a direction, or
both — has been fully honoured.

## Invariants to never violate

- Never interrogate — no scope, task, design, or policy questions on either path.
- Never write a heading the input did not support.
- Never invent content a source plan lacks.
- **Never carry a plan's merge obligations into `## Tasks`.** On the plan-source path a native plan's
  "Etapas" routinely end in a version bump, a changelog entry or *update the docs*; none of them
  converts, because what the release *is* is unknowable until the last task lands.
  `/quenching-specs conclude` owns them, along with the `/docs/` the work *reveals* and the cycle's
  own closing actions. A standard the plan declares the spec will write still becomes a checkbox.
- Never accept a generated title or a `titleize` fallback when the input lacks a descriptive title.
- **Never ask for a metadata field before the spec exists.** Subject, type, tags and `complexity`
  are resolved and written in step 5; the human is asked only after, on the closing screen.
- **Never invoke `/quenching-specs develop` without the human having chosen a direction** on the
  closing screen — a correction alone, with no direction named, ends the run at option B.
- **Never print the closing screen without naming what was presumed and why** — every subject,
  type, tag and `complexity` level carries its reason.
