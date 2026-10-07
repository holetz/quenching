---
paths:
  - "plugins/quenching/commands/**"
---

# Command bodies: no `context: fork` beside a mid-flow gate

Do not add `context: fork` beside a command's mid-flow gate. The minimal building cycle is the only
documented exception, and its review lives in the PR.
