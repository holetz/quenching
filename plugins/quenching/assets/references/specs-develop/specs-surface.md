# The `cq specs` surface — provider operations and their payloads

This file owns the provider-facing `cq specs` tool surface and the resolution contract its
commands use. The lifecycle document and the report shape live in their own focused references;
commands cite the smallest owner that answers the step they are running.

## The `cq specs` tool surface

<!-- rules -->

Uniform contract: `--json` on every subcommand; strict exit codes — **0** ok · **1** findings ·
**2** refusal. A command branches on the exit code and the JSON, never on prose.

`cq specs` is **stdlib-only Python**, in the same mold as `cq knowledge validate`: no runtime to install
and no dependency to declare. An external backend's transport is `subprocess` over the vendor's own
`gh` / `az`, so auth, paging and API errors are not this plugin's code — and the cost of that trade
is declared rather than hidden: such a backend does not work without the binary installed, and a
missing one is a **refusal (exit 2) naming it, never a traceback**.

| Command | Use |
| --- | --- |
| `cq specs new <name> [--title T] [--verification P] [--subject KEY] [--type KEY] [--tags LIST] [--complexity LEVEL]` | store a new spec in `plans` with `## Problem` as its only section by default, reporting the locator the backend allocated — the ID it hands out is what every later verb takes. The descriptive title is supplied at capture and the date is stamped into `date:` here and never again. `--subject` applies a declared `subjects.<KEY>`'s parent (where the backend has one) and fixed tags — folded into `--tags` where both are given, never overwritten by it. `--complexity` writes the record through the same path as `record priority`. Stdin, read when it is not a tty, carries N sections in the SAME multi-heading stream `section --write` reads and writes — the stream self-declares by opening on a canonical `## <Heading>`, with no single implied heading to fall back on, so an unopened or malformed stream refuses (`sp-stray-heading`/`sp-write-duplicate-heading`) before `create_spec` ever runs |
| `cq specs list [--json] [--lean]` | every spec, by folder and derived stage. `--lean` is the provider's own cheap index — ID, title, state and the visible `spec:` labels, no document body on the wire — measured 157 specs in 1.6 s / 70 KB against 4.8 s / 5.25 MB for the full listing. It does NOT feed the ranked table (`stage`, `tasks`, `priority` and `date` derive from the document), and says so in its own payload |
| `cq specs status --spec <id> [--json]` | sections present, derived stage, task progress with recorded subjects, the records, and the outstanding gates |
| `cq specs section <id> "<heading>[,<heading>…]" [--write]` | deterministic partial read of N sections in ONE call, returned in the order asked; `--write` writes N in one call too, each created in canonical position — the bodies arrive on stdin delimited by the same `## <Heading>` lines the read prints, and the set the stream carries must equal the set declared here or the call refuses without writing any of them. A stream that does not open on a canonical heading is one raw body under the one heading declared, exactly as before |
| `cq specs show --spec <id> [--task ID]… [--full]` | what `section` cannot say: the map of which headings and task ids exist (the default), ONE task's line and metadata, the whole document **only** under `--full`. Section bodies are `section`'s |
| `cq specs record <id> <name> [--set FIELD=VALUE]…` | read or **merge** ONE frontmatter record; fields not named survive, write-once records refuse (exit 2) with the value they hold |
| `cq specs tags\|assignee\|start\|target <id> [value]` | read one of the four STATE keys, or set it — never a record; `tags` **replaces** the whole list, it does not append |
| `cq specs verification <id> [<policy>]` | read the policy in force — and whether anything declared it — or set it. The post-capture writer: `new --verification` answers at the one moment nobody has an opinion yet |
| `cq specs config [--json]` | the repo's declared parameters — the backend, the specs branch, `worktreeSetup`, `azureStates`, `azurePlacement`, `azureColumns`, `subjects`, `tagCatalog` |
| `cq specs promote <id> --to archive [--outcome done\|abandoned] [--force]` | the one gated transition left; **exit 2** with the missing list, else the backend's own hop — closing the issue or work item, never a `git mv`: a provider-owned front has no phase directory to move a file between |
| `cq specs next --spec <id> [--json]` | THE single next action, carrying the task's `verify`/`files`/`pattern`/`[P]`; skips `[!]` |
| `cq specs next --front [--json] [--table] [--columns C,C] [--order rank\|priority]` | the **ranked candidate list** — the only place ordering logic lives. `--table` prints §The spec table itself, so a command quotes a rendering instead of re-aggregating a payload; `--columns` omits columns, never reorders them; `--order priority` swaps the four-factor ranking for the human's `priority.level` alone. `--table` with `--json` refuses (exit 2) — a table IS the human rendering |
| `cq specs task --spec <id> --check ID [--subject LINE] [--commit SHA] \| --uncheck ID \| --block ID --reason MSG` | flip, record, or block a checkbox mechanically; `--commit` is **additive** to `--subject`, never its replacement |
| `cq specs discover <id> <text>` | append one line to `## Discoveries` |
| `cq specs parallel --spec <id> [--json]` | verify each `[P]` group's `files:` sets are disjoint — **exit 1** when any group is ineligible |
| `cq specs validate [--spec <id>] [--by-code]` | the canonical heading set, the stage-scoped rule, the `sp-*` vocabulary. `--by-code` renders the same sweep as one line per `(code, severity)` with the count and the specs — grouped, never filtered |
| `cq specs doctor` | workspace shape — the two folders, strays, older layouts; remedies **declared** for the command to apply |
| `cq specs migrate` | one-way fold to the current layout (`backlog/` + `ready/` → `plans/`, and v1 three-file folders → one file); **exit 2** when there is nothing to migrate; `specs/archive/**` never touched |
| `cq specs export --spec <id> \| --all [--out DIR]` | dump the canonical markdown to disk — **write-only**; nothing reads it back and nothing syncs it, so it is a rescue copy for an external backend and never a second store |
| `cq specs selftest` | prove the embedded schema and template have not drifted from their asset files |

`--outcome` is the only content a promote ever writes.

**Archiving a spec with open tasks refuses.** `--outcome done` with unchecked `- [ ]` boxes exits 2
and lists them, overridable with `--force`; `--outcome abandoned` is always allowed, because
closing out a spec that will not be built is exactly the case where open tasks are expected.

There is no `init` (scaffold is an asset copy — the align's job). There is no `store` subcommand
either: the declared backend is read by `cq specs config`, never switched by a command mid-flight.

Templates live in `assets/specs/templates/spec.md` and are stamped by `cq specs new` — with the
same content embedded as a fallback constant in `cq specs` itself, so an installed copy under a
target's `.claude/hooks/` with no adjacent assets stamps an identical file. **Edit both or
neither.** A template's scaffold content must stay invisible to `has_real_content()`: only headings
and HTML comments, with any example inside a comment or written as a `<placeholder>`.

### Resolving the tool

Owned by
[align/tool-resolution.md](${CLAUDE_PLUGIN_ROOT}/assets/references/align/tool-resolution.md)
§Resolving the tool, §Write the resolved path literally on every invocation: bare `cq specs` where
the `bin/` shim is on `PATH`, else the plugin path `${CLAUDE_PLUGIN_ROOT}/assets/bin/cq specs`
invoked with `python3` or `py` (`allowed-tools: Bash(python3:*), Bash(py:*)`) — **two doors onto one
file, and no third rung**.
