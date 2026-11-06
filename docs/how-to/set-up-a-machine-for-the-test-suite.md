---
type: how-to
title: Set up a machine for the test suite
description: Make a development machine's test runs cheap — what the suite already does with no step, and the optional per-OS changes that need or do not need admin.
resource: scripts/verify_repo.sh
tags:
  - how-to
  - tests
  - performance
timestamp: 2026-11-06
audience: human
authority: current
source: spec 2181 — the measured baseline and the temp-root matrix in its Design
maintainer: Israel Holetz
---

# Set up a machine for the test suite

*Audience: anyone running `bash scripts/verify_repo.sh` · No step here is required · Every step is
optional and reversible*

The suite writes several hundred megabytes of temporary files per run. Left on the disk, that is
the I/O the rest of the machine competes with; in RAM, almost all of it disappears. The gate already
chooses a RAM-backed root when the machine offers one, so **the default path needs no setup at
all** — this page is for a machine where you want to confirm the choice, widen it, or tune how many
workers a run takes.

## What happens with no setup

`scripts/verify_repo.sh` resolves one temp root through `scripts/toolchain/tmproot.py` and exports
it as `TMPDIR`/`TEMP`/`TMP` before pytest starts. In order, it accepts:

1. `QUENCHING_TEST_TMPDIR`, when you set it;
2. Linux: `$XDG_RUNTIME_DIR`, then `/dev/shm`, each only while it is a tmpfs, writable and has at
   least 512 MB free;
3. Windows: an existing Dev Drive, then `%LOCALAPPDATA%` when it is not inside a synced folder;
4. the system temp dir, with a `NOTICE` on stderr.

A direct `pytest` run gets the same root from `quenching/tests/_paths.py`, so the choice does not
depend on entering through the gate.

## Check what your machine chose

```bash
python3 -m scripts.toolchain.tmproot --explain
```

It prints each candidate and why it was accepted or refused, then the chosen root on stdout. A gate
run prints the root and the worker count at the top:

```
temp root: /run/user/1000/quenching-gate-1234-abcd
workers: auto
```

## Linux, without admin

Nothing to do on a desktop session: `$XDG_RUNTIME_DIR` (`/run/user/<uid>`) is a tmpfs owned by you,
and the resolver takes it. `/dev/shm` is the second choice, and it is shared with other users, which
is why it is not first.

If you want a specific location, set the override for one run:

```bash
QUENCHING_TEST_TMPDIR=/dev/shm/quenching bash scripts/verify_repo.sh
```

An override that does not exist or is not writable fails the run loudly instead of silently falling
back — a typo must not put 700 MB somewhere you were trying to protect.

## Linux, with admin (optional)

Two system-wide changes help further. Both affect the whole machine, so measure before and after
and keep the one that pays on your hardware.

**`/tmp` as a tmpfs.** Debian 13 already does this; Ubuntu does not. With `systemd`, a drop-in:

```bash
sudo cp /usr/share/systemd/tmp.mount /etc/systemd/system/tmp.mount
sudo sed -i 's/^Options=.*/Options=mode=1777,strictatime,nosuid,nodev,size=4G/' \
  /etc/systemd/system/tmp.mount
sudo systemctl daemon-reload && sudo systemctl enable --now tmp.mount
```

The `size=` cap matters: without it, a runaway process can fill RAM and push the machine into swap.
The resolver accepts `/tmp` as a candidate only while it is a tmpfs with room, so the step is
self-cancelling if you undo it.

**dm-crypt workqueue flags.** On a LUKS root, `no_read_workqueue,no_write_workqueue` in
`/etc/crypttab` can raise throughput; reports on NVMe vary, and the gain is not guaranteed. It needs
a reboot and it applies to the whole disk, so it is not part of the default path.

## Windows, without admin

The resolver uses `%LOCALAPPDATA%` when it is outside OneDrive, Dropbox and similar synced folders,
which keeps the suite's churn out of file synchronization. Nothing to configure.

## Windows, with admin (optional)

A **Dev Drive** is the supported fast volume: a ReFS volume with Defender performance mode
automatically on. Create one in Settings → System → Storage → Advanced → Disks & volumes → Create
Dev Drive, or with `fsutil devdrv create`. The resolver prefers an existing Dev Drive over
`%LOCALAPPDATA%`.

A RAM disk is not recommended on Windows: it needs a driver and admin rights, and a Dev Drive gets
most of the gain without either. Defender exclusions are blocked under Tamper Protection on managed
machines, so do not plan around them.

## Tune one run

| Variable | Effect |
| --- | --- |
| `QUENCHING_TEST_WORKERS` | xdist worker count; `auto` by default. Lower it when several gates run at once so they share the cores instead of thrashing |
| `QUENCHING_TEST_TMPDIR` | the temp root for this run; no filesystem-type requirement |

```bash
QUENCHING_TEST_WORKERS=4 bash scripts/verify_repo.sh
```

## What this does not change

The root holds temporary files only. Coverage data stays in `.quenching/coverage/`, the
documentation build stays in `site/` and `.cache/`, and the deployed-surface check reads the tree as
it is. CI keeps running on disk-backed runners, so a test that only passes because its temp files
are in RAM still has to pass there.

macOS has no tmpfs candidate in the resolver: it falls back to the system temp dir. Point
`QUENCHING_TEST_TMPDIR` at a RAM disk you created if you want the same effect there.
