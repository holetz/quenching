# SessionLane

One live session: who it is, what it is doing, what it did in the last hour.

Identity is the branch, the host, the worktree and a short session id, so that sessions on one checkout can be told apart (D9). The host is a neutral `.tag`, `Claude Code` or `OpenCode`, never a heat or state colour. An OpenCode session has no process to check, so its tag carries a `data-tip` saying the state comes from recent activity. The radar is 60 bars of per-minute activity, in `muted`, because activity is not a state. Sub-agents hang beneath as tracks. Exists only under `--sessions`. Refinement R13.
