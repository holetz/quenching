---
name: quenching-handoff
description: "Compacta a conversa atual em um documento de handoff para outro agente continuar o trabalho. Use quando o usuário pedir para \"gerar um handoff\", \"compactar a conversa num handoff\", \"preparar handoff para a próxima sessão\" ou \"resumir esta sessão para outro agente continuar\"."
---

<!-- GENERATED FROM plugins/quenching/commands/handoff.md -->


# quenching-handoff — compact the current conversation into a handoff document

**Input**: `$ARGUMENTS` (o foco da próxima sessão).

## Workflow

### 1. Fix the next session's focus

Use `$ARGUMENTS` when provided. When it is omitted, use the main unfinished objective in the
current conversation as the focus. **Done when:** the handoff's focus is fixed.

### 2. Create and inspect the destination

Run:

```bash
mktemp -t handoff-XXXXXX.md
```

Read the returned path before writing to it. **Done when:** the destination path is captured and
the newly created file has been read.

### 3. Compose the handoff

Summarize the current conversation so a fresh agent can continue the work. Tailor it to the fixed
focus and include the objective, current status, decisions, completed work, open work, validation
evidence, blockers, and useful next actions. Suggest skills for the next session when they apply.
Reference existing PRDs, plans, ADRs, issues, commits, diffs, or other artifacts by path or URL
instead of duplicating their contents. **Done when:** the draft contains enough context to resume
the work and points to existing artifacts rather than copying them.

### 4. Write and verify

Write the handoff to the inspected temporary path, then read it back. Report the resulting path.
**Done when:** the file exists, is non-empty, and its read-back succeeds.

## Invariants

- Keep the handoff focused on the next session's work.
- Reference durable artifacts instead of duplicating their contents.
- Suggest only skills that are relevant to the recorded next actions.
