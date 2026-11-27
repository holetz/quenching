# /quenching-specs create — step 1, classify the input

**Prose** → the sentence path. **A path to an existing `.md`**, an explicit ask to convert a plan,
or a plan already developed in this session — including the contents of `<proposed_plan>` — → the
plan-source path. Use the complete plan available in the conversation as the source; it does not
need an intermediate file. With no argument and no identifiable plan in the conversation, ask what
to capture. Never search plan directories automatically for a candidate. This is the one decision
the CLI cannot make: `specs_write(verb="create")` (step 5) resolves the backend and the workspace on its own.
