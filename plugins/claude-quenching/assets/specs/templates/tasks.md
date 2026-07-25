# Tasks — <TITLE>

<!-- Checkboxes are `- [ ] <id> <text>`, grouped under `## N. <Section>` headings.
     `specs.py task --plan <n> --check <id>` flips one mechanically — never hand-edit the
     `[ ]` / `[x]` character.

     A checkbox MAY carry indented metadata lines directly beneath it. They are parsed by
     `specs.py` and are purely additive: a task without them behaves exactly as it always
     did, and every tasks.md written before this format parses unchanged.

       - [ ] 3.2 Add rate limiting to the auth middleware
             files: src/middleware/auth.ts, src/config/limits.ts (new)
             pattern: src/middleware/cors.ts
             verify: pnpm test middleware/

     files:    the paths this task may touch. Declaring them is what PERMITS the task to be
               handed to an executor sub-agent, and what makes a `[P]` marker checkable.
     pattern:  an existing file to imitate — the cheapest context an executor can be given.
     verify:   the command that proves the task done. When it runs is the plan's
               `verification` policy in `.specs.json`, not this file's business.

     `[P]` right after the id marks a task parallel-eligible:

       - [ ] 3.3 [P] Add the rate-limit config loader

     It is set HERE, at propose time, and NEVER inferred while applying. It is honoured only
     when the marked tasks' `files:` sets are provably disjoint and none of them writes into
     `docs/` — `specs.py` checks the disjunction mechanically rather than judging it in prose.
     Serial execution is the default and needs no marker. -->

## 1. <Section>

- [ ] 1.1 <first task>
- [ ] 1.2 <next task>
