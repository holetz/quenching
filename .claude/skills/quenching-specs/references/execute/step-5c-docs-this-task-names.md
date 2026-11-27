# /quenching-specs execute — step 5 c

Loaded only when this sub-step runs, together with the step 5 loop in [step-5-implement-tasks.md](.claude/skills/quenching-specs/references/execute/step-5-implement-tasks.md); the flow index is [execute.md](.claude/skills/quenching-specs/references/execute.md).

c. **Write only the `/docs/` this task names.** When this task writes `/docs/`, load the rule that
   draws the line between declared and emergent, and the boundary it crosses:

   ```text
   components_read(verb="read", path=".agents/quenching/references/specs-execute/execution-delegation.md", sections=["§Declared versus emergent"])
   components_read(verb="read", path=".agents/quenching/references/specs-develop/spec-driven.md", sections=["§Boundary"])
   ```

   A `/docs/standards/` path declared under `## Impact` and named by this task is part of its
   deliverable — written through the insert procedure in
   [knowledge-add/homes.md](.agents/quenching/references/knowledge-add/homes.md) §The frontmatter
   stamp §Updating `index.md` §Enriching the glossary §Self-check; stamp `authority` honestly and
   self-check against [knowledge-align/conformance.md](.agents/quenching/references/knowledge-align/conformance.md)
   §Concept docs §Resource integrity. Anything else the work reveals costs one line —
   `specs_write(verb="discover", spec=<id>, text=<finding>)` — and no authoring.
