# Prompt prefix under the quenching hooks — audit and measurement protocol

Spec: 462 — Prefixo de prompt estável sob os hooks do quenching. Static audit date: 2026-11-25.

## Static audit — one row per body

The two bodies share one dispatcher process and one installed line; the audit read every string
each body can emit and the dispatcher's combination rule.

| Body | Event / matcher | Channels | Volatile token in the text? | Proof |
| --- | --- | --- | --- | --- |
| `deny-claude-coauthor` | `PreToolUse` · `Bash\|PowerShell` | `permissionDecision: deny`, `additionalContext` | no — both messages are constant literals | `test_hook_prefix` refuses clock, path, pid, uuid, call id and ANSI |
| `warn-git-add-all` | `PreToolUse` · `Bash\|PowerShell` | `systemMessage`, `additionalContext` | no — both messages are constant literals | `test_hook_prefix` refuses clock, path, pid, uuid, call id and ANSI |
| `dispatch` | shared by the two | one JSON object combining the bodies in declaration order | no — it joins the bodies' constants | `test_hook_prefix` compares the whole answer byte for byte |

Measured static result, 2026-11-25: the same event answers identical bytes from the project root
and from `quenching/tests`, under `PYTHONHASHSEED` 0 and 1, under `TZ=UTC` and
`TZ=America/Sao_Paulo`, and on repetition. The `test_hook_prefix` module is the check (6 tests,
all green). RED evidence: the subdirectory case fails on the base worktree with 4 failures before
the root walk exists.

The root resolution that makes the answer independent of the caller: `CLAUDE_PROJECT_DIR`, then
`COPILOT_PROJECT_DIR`, then a walk up from the working directory to the first ancestor carrying
`.git` (the worktree root); with no `.git` above the cwd the absence guard prints `{}`. A
`.agents` above the project never answers for it.

## What the clients write — dated observation, not a contract

Observed 2026-11-25. Claude Code's CLI writes `hook.start` and `hook.end` events around each hook
execution in its session transcript. VS Code Copilot Chat records cache segments carrying a
`cacheType` in its own local cache-explorer storage. Both are private client formats: they are
recorded here as the shape a future reading starts from, never as an interface this repository
may parse or automate.

## VS Code cache explorer protocol — executed by a human, dated

Every step below is `unmeasured-live` until the session runs it; this artifact then carries the
observed numbers, the panel name, the VS Code build and the date.

1. Open the cache explorer and record the panel's exact name, the VS Code build and the date —
   `unmeasured-live`.
2. Two consecutive requests with no hook firing keep the same cached prefix size —
   `unmeasured-live`.
3. A `git add .` that fires `warn-git-add-all` appends the warning after the prefix and changes no
   earlier segment — `unmeasured-live`.
4. A commit carrying a Claude co-author trailer, denied by `deny-claude-coauthor`, changes only
   the tail — `unmeasured-live`.
5. Repeat steps 3 and 4 on Windows with PowerShell and cmd, and confirm the installed line finds
   the dispatcher from a subdirectory — `unmeasured-live`.

## Verdict

`unmeasured-live` — the static bytes are proved by `test_hook_prefix`; the position the client
gives those bytes in the prompt cache has not been read live yet. The protocol above is the only
step that replaces this verdict.
