---
type: concept
title: Building with the tool being built
description: In this repository the tool that records a task's progress is the same one the task edits, so an edit halfway through can leave `cq` itself unrunnable and the box impossible to tick — which makes certain tasks inseparable and forces capturing, before editing, everything the next step will need to read
resource: plugins/quenching/assets/bin/**, plugins/quenching/assets/references/specs-execute/execution.md
tags: [automation, self-hosting, bootstrapping, specs, execution]
timestamp: 2026-08-17
audience: both
authority: current
source: multi-spec execution session of 2026-08-17 — specs remover-secao-stray-de-um-documento (the fold_stray_heading import); refined by remover-agrupamento-de-commits-por-secao (2026-08-30)
maintainer: quenching
---

# Building with the tool being built

`cq` verifies the task, ticks its box and commits the task-level change. `cq` is also, frequently,
**what the task is editing**. As long as those two sentences are true at the same time, the
execution procedure has an intermediate state in which it cannot record its own progress.

## The two forms this takes

**The broken window.** A task adds to a module the import of a function the *next* task will write.
Between one commit and the other, every `cq specs` fails on the import — including the `cq specs
task --check` that would close the first box. The two tasks are not two: they are one, and
declaring separate `files:` does not separate them. Measured when `granular.py` started importing
`fold_stray_heading` before `parse/edit.py` existed.

**The ground that moves.** A task fixes the mechanism it itself uses to commit. The task-level
commit chain must remain usable while its command and references are changing, so the procedure
captures before editing everything the next step will need to read.

## What this forces

- **Capture before editing** everything a later step will need to read: the base sha, the reference
  output, the prior behaviour. After the edit, the source may no longer answer what it answered.
- **Treat a broken window as a single task.** If the intermediate state leaves `cq` unrunnable, the
  boundary between the two tasks does not exist in practice — and `## Impact` ought to say so,
  instead of leaving execution to discover it.
- **Prove the change against a copy of the prior code**, not against the memory of what it did:
  loading the pre-change implementation from `git show <base>:<path>` into a separate module and
  comparing the two outputs is what separates "equivalent" from "looks equivalent".

The compensating property is that the fix proves itself in the same run: a focused history fixture
keeps two task commits distinct at a section boundary while the command and reference contracts
contain no section-level history rewrite.
