# Git hooks (`.githooks/`)

Repo-tracked git hooks. Git does not enable a custom hooks path automatically,
so enable them **once per clone**:

```bash
make hooks          # or: git config core.hooksPath .githooks
```

## `pre-commit` — version stamp

Stamps [`plugins/claude-quenching/VERSION`](../plugins/claude-quenching/VERSION)
— the file the `quenching-management` skill reads to announce its version, and
which is **packaged with the plugin** — with the current short commit hash on
every commit, staging it so the value ships inside the commit. During
development the version **is** the commit hash; at release it becomes a real
semver and this hook can be retired.

Because a commit can't contain its own hash, the stamped value is the tip that
becomes the new commit's **parent** (the latest built revision). The working
tree stays clean — nothing is left modified after a commit.
