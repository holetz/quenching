---
type: task
title: Split the backlog-zone renderer out of specs.py
description: specs.py has passed the ~1,200-line threshold its own design set for splitting, and is now 1,388 lines
timestamp: 2026-07-25
tags: [specs, tooling, maintainability]
---

# Split the backlog-zone renderer out of specs.py

The `refine-and-execute-specs-flow` plan's design named a threshold in its Risks section: if
`specs.py` passes ~1,200 lines, split the backlog-zone renderer into a module "rather than growing
one file past reviewability — and note it, do not do it silently." Six features landed in that plan
and the file is now 1,388 lines, so the threshold is crossed and the split was not done. This task
is the note. Any split has to keep the script stdlib-only and self-contained, since an installed
copy under a target's `.claude/hooks/specs.py` must keep working on its own.
