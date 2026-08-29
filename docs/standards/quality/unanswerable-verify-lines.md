---
type: standard
title: Unanswerable verify lines
description: A `verify:` whose verdict does not come from the state of the code — the pattern the shell mangles before it compares, the YAML scalar the parser truncates before it reads, the entry point that exited 0 without running anything — and the rule of exercising the line in both directions at the moment it is written, never at the moment it has to close
resource: plugins/quenching/assets/references/specs-execute/execution.md, plugins/quenching/assets/references/specs-develop/*.md, docs/standards/workflows/task-execution.md
tags: [quality, verification, verify, authoring, shell-quoting, frontmatter]
timestamp: 2026-08-17
audience: both
authority: current
source: /quenching:specs:execute-queue queue of 2026-08-17 — three independent instances measured in the specs cq-specs-task-check-stale-subject-sem-commit, falha-de-leitura-do-backend-vira-front-vazio and validar-a-zona-generated-contra-o-disco
maintainer: quenching
---

# Unanswerable verify lines

<!-- rules -->

**A `verify:` answers about the state of the code, or it does not answer.** A line whose verdict is
decided by its own spelling — before anything at all is measured — is not a loose check: it is a
check that is not there. The two readings it produces are equally false, and one of them is green.

Three forms, all measured in a single queue of nine specs:

| The line | What mangles it | How it lies |
| --- | --- | --- |
| a grep whose pattern contains backticks, written inside **double quotes** | the shell does command substitution before grep sees the pattern | the pattern degrades into something that **never matches** — a red impossible to close |
| an **unquoted** YAML scalar containing `#` | the parser treats the rest of the line as a comment | the value arrives truncated, and the finding only shows up after the commit |
| an entry point that no longer exists (a module with no `__main__` guard, a retired `main()`) | nothing — it exits 0 | **green without running anything** |

**The rule: exercise the line in both directions at the moment it is written.** Run it against the
tree as it stands (it must give the red the task exists to close) and against the state the task
will produce (it must give green). A line that gives the same result in both directions does not
discriminate, and the cost of finding that out when the box has to be ticked is a whole run.

**Whoever finds such a line reports it, and never replaces it in silence.** Running the corrected
form to learn what it would say is legitimate and is what produces the evidence; rewriting the
`verify:` line so that it passes erases the assertion someone meant to make. Both go into the
report — what the line declared, and what the correct form measured.

<!-- rationale -->

The three instances appeared in different specs, written by different authors, in the same run —
which is the evidence that the cause is the way of writing, not one author's carelessness. None was
caught by `cq specs validate`, and none could be: the validator reads the line as text, and what is
wrong with it only manifests when the shell or the YAML parser interprets it. That is why the
mitigation is one of **authoring**, and not one more checker — the moment the information exists is
the moment the line is written.

The third form is the most expensive of the three, and the only one that gives nobody any trouble:
an impossible red costs the author the same day, but an empty green crosses the whole run, lands in
the PR and sustains a coverage claim that was never measured. It is the sibling of
[selftest-mutation.md](selftest-mutation.md) — a test never observed failing is not tested —
applied to a task's `verify:` instead of to a fixture case.

The scope is `verify:` because that is where the line runs with nobody watching. The same quoting
trap in a hand-typed command is seen and fixed in seconds.
