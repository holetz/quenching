---
description: >-
  Read another project's quenching specs as a to-do list, without writing anything. Triggers on
  "what is left to do in <project>", "list the open specs", "read the specs of <project>", "show
  the tasks of spec <id>", or "what should I work on next". Not for: creating, developing,
  executing or closing a spec → the full `quenching` plugin's /quenching:specs:* commands.
argument-hint: "[spec-id] [--root <checkout>]"
allowed-tools: Bash(cq-specs-read:*), Bash(python3:*)
---

# /quenching-specs-reader:read — read a specs front, never write it

The specs live in the project's repository provider (GitHub Issues or Azure Boards). This command
reads them through `cq-specs-read`, a read-only `cq specs` that refuses every write with exit 2.

Arguments: `$ARGUMENTS`

## Workflow

1. **Resolve the tool.** Run `cq-specs-read --help`; if it is not on `PATH`, use
   `python3 "${CLAUDE_PLUGIN_ROOT}/bin/cq-specs-read"` for every call below.
   **Done when:** one invocation form answered `--help` with exit 0.
2. **Resolve the project.** A path in the arguments is passed as `--root <path>`. Otherwise the
   tool reads `QUENCHING_SPECS_ROOT`, then the working directory. If a call refuses with
   `sp-provider-unknown` or `sp-read-root`, say that the project checkout is not configured and
   show the remedy: add `"env": {"QUENCHING_SPECS_ROOT": "<absolute checkout path>"}` to this
   project's `.claude/settings.json`, or pass `--root`. Then stop.
   **Done when:** the root is known, or the refusal and its remedy are reported.
3. **Without a spec id: read the front.** Run `cq-specs-read next --front --json`. Present each
   candidate in the order returned, as one line per spec: `#<id> <title>` · `<stage>` ·
   `<tasks.checked>/<tasks.total>` tasks (plus `<tasks.blocked>` blocked when non-zero) · the
   `path` URL. `top` is the recommended next spec; say so. For archived work, the human must ask
   and the call is `cq-specs-read list --phase archive --lean --json`.
   **Done when:** every candidate is listed, or an empty front is stated as empty.
4. **With a spec id: read that spec.** Run `cq-specs-read show --spec <id> --json` and list its
   `tasks` grouped by state: open (`" "`), blocked (`"!"`), done (`"x"`). When the human needs the
   why, run `cq-specs-read section <id> Problem,Proposal --json`; for a single task's detail, run
   `cq-specs-read show --spec <id> --task <task-id> --json`.
   **Done when:** the spec's open and blocked tasks are listed with the spec's URL.
5. **Report.** Relay the JSON faithfully: never invent a task, a stage or a priority the payload
   does not carry, and report a refusal's `code` and `message` verbatim.
   **Done when:** the answer cites only what the tool returned.

## Invariants

- Never write the provider, and never try: `new`, `task`, `record`, `promote`, `discover` and
  `section --write` are refused by the tool, and asking for them means the human needs the full
  `quenching` plugin.
- Never call `gh` or `az` to change an issue or work item as a substitute for a refused verb.
- The output is data for the human. Writing it into this project (a note, a checklist file) is a
  separate request, never a side effect of reading.
