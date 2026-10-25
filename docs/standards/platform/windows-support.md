---
type: standard
title: Windows without administrator rights — the supported prerequisites and what the port covers
description: What "supported on Windows without administrator rights" means for the cq tool, the user-scope prerequisites, the three code paths that were POSIX-only (process groups, symlinks, the PATH launcher) and the one CI job that exercises them
resource: plugins/quenching/assets/bin/quenching/codex/probe.py, plugins/quenching/assets/bin/quenching/git/worktree.py, plugins/quenching/bin/cq.cmd, scripts/generate_plugin_modules.py, .github/workflows/ci.yml
tags: [windows, platform, prerequisites, junction, process-group]
timestamp: 2026-10-25
audience: both
authority: current
source: spec 2090 (windows-without-admin)
maintainer: quenching
---

# Windows without administrator rights

<!-- rules -->

`cq` runs on Windows for a user who holds no administrator rights. Nothing in the supported path
asks for elevation, a developer-mode switch or a system-wide install.

**Prerequisites, all installable at user scope:** Python 3.11 or newer, `git`, and `gh` when a
command talks to the forge. The `py` launcher or `python` must resolve on the user's `PATH`.

**What the port covers:**

- **Process groups.** `group_kwargs()` and `stop()` in `codex/probe.py` own starting a child in its
  own group and stopping its whole tree: `start_new_session` and `os.killpg` on POSIX,
  `CREATE_NEW_PROCESS_GROUP` and `taskkill /F /T` on Windows. `implement.py` and `review.py` call
  them and name no POSIX signal.
- **Shared paths.** `cq git worktree link` and `add` try `os.symlink`; when Windows refuses it for
  want of the privilege they create a directory junction with `mklink /J`, which needs none. A
  junction counts as a link wherever the code reads one (re-link, removal audit).
- **The `cq` launcher.** `bin/cq.cmd` sits beside `bin/cq`, runs `assets\bin\cq` with `py -3`
  (else `python`) and returns its exit code.

**What it does not cover:** the whole `scripts/verify_repo.sh` gate (it needs bash and uv), the
POSIX hook scripts and `scripts/githooks`, and `scripts/run_evals.py`.

**Proof:** one `windows-latest` job in the PR gate runs the Windows-sensitive unit tests. It
patches `os.name` and `os.symlink` for the branches and runs them natively on a Windows runner.
The standard stays `background` until that job has run green on a pull request.

<!-- rationale -->

Each of the three paths failed silently or loudly on a stock Windows account: `os.killpg` and
`signal.SIGKILL` do not exist there, `os.symlink` raises without the privilege, and a POSIX
`bin/cq` is not a command to `cmd.exe`. A junction is the one link type a standard user can create.
