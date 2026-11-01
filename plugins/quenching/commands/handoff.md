---
description: >-
  Compact the current conversation into a handoff stored beside its spec, ready for another agent
  to continue. Use for "generate a handoff" or "prepare a handoff for the next session". Not for:
  implementing → the owning command.
argument-hint: "What will the next session be used for?"
allowed-tools: Bash(cq:*), Bash(mktemp:*), Read, Write, AskUserQuestion
---

**Input**: `$ARGUMENTS` (the focus of the next session).

The handoff is a file the next session READS BEFORE IT ACTS, and it belongs to a spec whenever one
exists: it is stored on the `quenching` branch under `specs/artifacts/<id>/`, travels with
`cq specs push`, and is readable from any clone — not left in a temp directory that the next
machine cannot see.

## Workflow

### 1. Fix the next session's focus

Use `$ARGUMENTS` when provided. When it is omitted, use the main unfinished objective in the
current conversation as the focus. **Done when:** the focus is fixed in one sentence.

### 2. Resolve the spec, never invent one

An id already stated in the conversation or in `$ARGUMENTS` wins. Otherwise resolve the current
branch:

```bash
cq specs find --branch "$(git branch --show-current)" --json
```

One match → that id. No match, no store, or any failure → **no spec**, and the report says so
explicitly: a standalone handoff is honest, an invented id is not. **Done when:** the spec id or
its explicit absence is decided.

### 3. Name and draft the handoff

Name it `handoff-<YYYY-MM-DD>-<focus-slug>.md` — the session's date, then a kebab-case slug of the
focus. Write the draft to `.quenching/handoff/<name>` with the Write tool: that path is the
sanctioned ephemeral location, and the draft doubles as the fallback when no store answers.

Compose the summary for the fixed focus: objective, current status, decisions, completed work, open
work, validation evidence, blockers, and next actions. Reference existing PRDs, plans, ADRs,
issues, commits, diffs, or other artifacts by path or URL instead of duplicating their contents.
Suggest skills for the next session when they apply. **Done when:** the draft contains enough
context to resume the work and points to existing artifacts rather than copying them.

### 4. Store it through the door, then read it back

```bash
cq specs artifact write --spec <id> --name <name> --from .quenching/handoff/<name>
cq specs push
```

Omit `--spec` when step 2 found none: the artifact then lives under `specs/artifacts/_handoffs/`.
The write leaves the handoff in the clone's pending ref; the push sends it. Then read it back
through the same door:

```bash
cq specs artifact read --spec <id> --name <name>
```

Branch on the exit code, never on prose. The write refusing with `sp-artifact-unsupported`,
`sp-artifact-no-store` or a backend refusal means this repository has no store to hold it: the
`.quenching/handoff/` draft IS the handoff, and the report says it stayed local. Any OTHER refusal
is reported as the failure it is — it never silently becomes the fallback. A failed
`cq specs push` (offline, lease taken) leaves the artifact pending and the report says
`not sent — cq specs push`. **Done when:** the artifact was read back and matches the draft, or the
fallback is stated with the reason it was taken.

## Invariants

- Keep the handoff focused on the next session's work.
- Reference durable artifacts instead of duplicating their contents.
- Suggest only skills that are relevant to the recorded next actions.
- Never write the handoff into a file only this machine can see without saying so.
