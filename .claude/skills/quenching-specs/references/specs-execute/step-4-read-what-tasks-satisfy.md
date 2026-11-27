# /quenching-specs execute — 4. Read what the tasks must satisfy

Loaded only when this step runs; the flow index is [execute.md](.claude/skills/quenching-specs/references/execute.md).

Ask for the `build` moment — the six sections an executor needs — never by naming them:

```text
specs_read(verb="section", spec=<id>, moment="build", scope="current")
```

Branch on the payload, never the exit code. `sections[].state`, already read once in step 2, is
the same fact this call's own `absent` list repeats: a section not yet `filled` — `## Handoff`
empty on a spec's first build is the ordinary case, not a finding — is read as empty.

`scope="current"` cuts **only** `## Handoff`, and the other five sections arrive whole: the
evergreen global block plus the `### N.` of the section the next actionable task sits in, flagged
`"scope": "current"` in the payload. Drop the flag only to audit the whole history of the block.
The path comes from what `status` resolved; never assume filenames. `## Impact` names the
`/docs/standards/` paths and the code this spec expects to touch.

Then, if the repo carries an OKF bundle (`/docs/index.md` with `okf_version`), read the
`/docs/standards/**.md` files the spec **declares** under `## Impact`, plus the ones the current
task's own text names — **never the folder** `/docs/standards/<subject>/`, the wrong and the
expensive unit ([execution-tooling.md](.agents/quenching/references/specs-execute/execution-tooling.md)
§Tooling asides has the measurement). Those files are **binding contracts** for
HOW the work is built, complementing the spec's own sections (WHAT to build). A task that
contradicts one is surfaced (step 5), never silently resolved. No bundle → skip silently.

A declared bullet may carry a `§`address beside its path — `/docs/standards/automation/skills.md
§Invocation and permission are authored decisions §The admission criterion`. With one, read
exactly those sections (`components_read(verb="read", path=<path>, sections=["§A", "§B"])`); with none,
read the file whole. Reading less is the spec author's assertion, never the executor's economy.

**Nothing scans the folder for a contract nobody declared**
([execution-tooling.md](.agents/quenching/references/specs-execute/execution-tooling.md)
§Tooling asides). The gap costs one line when it shows up — `specs_write(verb="discover")` records it while
building, and `/quenching-specs develop` repairs `## Impact`.

**Done when:** the spec's sections and the declared binding standards are read.
