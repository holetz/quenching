# scripts/maintenance — one-off operational

**One-off and potentially destructive operational routines**: sandbox clones,
backup, data migration, permission setting.

**Flags-off by default:** each step is gated by a flag at the top of `main()`, most
**off** by default, to prevent accidental destructive execution (poka-yoke from
dim 14 applied to operations). Runs **on demand**, never in the automatic pipeline.

> Replace/add the real modules and register each one in the map at
> [../README.md](../README.md). Remove this folder if the repo has no operational
> routines.
