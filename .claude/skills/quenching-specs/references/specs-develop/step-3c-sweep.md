### 3c. Run the dependency sweep — once, at the pass's open
Skip whole where `### Mapa de dependências` already sits under `## Design`: a spec is swept at most
once. **This step opens nothing** — step 3b's two calls already carry both the `## Design` it reads
and the §Gathering the evidence that governs it.

Otherwise dispatch one read-only `Task` sub-agent under the **wider** profile of §Gathering the
evidence, briefed with whichever of `## Problem` / `## Proposal` is filled, asked for the one table
that section names: every file the proposal's own area touches or is touched by, and what breaks or
goes orphaned if it changes.

**When the executor has no `Task` tool** (a sub-agent profile declaring `task: false`), the sweep is
neither skipped nor improvised: the executor runs it itself, inline, with the read-only tools it
holds and under the same **wider** profile, writing nothing but the table. The map's date line then
reads `(varredura inline: executor sem Task)`, so a later pass can tell it from a sub-agent's map.

**The orchestrator holds the result; the sub-agent never writes it.** The table waits for step 7's
own consolidated write, landing as `### Mapa de dependências` under `## Design`, dated.
**Done when:** the spec already carries a map, or this pass holds the sub-agent's table to write at
step 7.
