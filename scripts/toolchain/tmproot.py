"""Choose the one directory the test suite's temporary files live under.

Temporary files are the suite's dominant write load: a full run writes ~690 MB through the process
tree, and on a laptop that lands on the same NVMe the rest of the machine is using. Putting that
root in RAM removes almost all of it, and every `tempfile` call — in a test, in an xdist worker, in
a `git` child — follows `TMPDIR`/`TEMP`/`TMP` with no test edited. This module picks that root once.

Order (the first acceptable candidate wins):

1. `QUENCHING_TEST_TMPDIR`, an explicit override. No filesystem-type requirement: the human asked
   for this path, and a typo must fail loudly instead of silently landing ~700 MB somewhere else.
2. Linux: `$XDG_RUNTIME_DIR`, then `/dev/shm`, each accepted only when it is a tmpfs, writable and
   has at least :data:`MIN_FREE_BYTES` free (the measured peak is under 100 MB; the margin covers
   several concurrent gates).
3. Windows: an existing Dev Drive, then `%LOCALAPPDATA%` when it is not inside a synced folder.
4. The system temp dir, with a `NOTICE` on stderr: the run still works, and the disk pays.

Stdlib only, and importable from `quenching/tests/_paths.py` — the module a test run reaches before
`tempfile` caches its answer. Run it as `python -m scripts.toolchain.tmproot` to print the root.
"""

from __future__ import annotations

import dataclasses
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile

MIN_FREE_BYTES = 512 * 2**20
ENV_KEYS = ("TMPDIR", "TEMP", "TMP")
OVERRIDE = "QUENCHING_TEST_TMPDIR"
_SYNCED = ("onedrive", "dropbox", "google drive", "icloud")


class TempRootError(RuntimeError):
    """An explicit root that cannot be used, or no candidate at all."""


@dataclasses.dataclass(frozen=True)
class Candidate:
    """One place the root could live, in preference order."""

    path: pathlib.Path
    kind: str                  # explicit | ram | disk
    label: str                 # how the notice and `--explain` name its origin
    tmpfs: bool = False        # require a tmpfs mount
    notice: str | None = None  # printed when this candidate is the one chosen


@dataclasses.dataclass(frozen=True)
class Resolution:
    """The chosen root, why it was chosen, and what to tell the human."""

    path: pathlib.Path
    kind: str
    label: str
    notice: str | None


def _mounts() -> list[tuple[str, str]]:
    """`(mount point, fstype)` from `/proc/mounts`, longest mount point first."""
    rows: list[tuple[str, str]] = []
    try:
        text = pathlib.Path("/proc/mounts").read_text(encoding="utf-8", errors="replace")
    except OSError:
        return rows
    for line in text.splitlines():
        fields = line.split()
        if len(fields) >= 3:
            rows.append((fields[1].replace("\\040", " "), fields[2]))
    return sorted(rows, key=lambda row: len(row[0]), reverse=True)


def _is_tmpfs(path: pathlib.Path, mounts: list[tuple[str, str]] | None = None) -> bool:
    """Whether `path` sits on a tmpfs mount, decided by the longest mount point covering it."""
    target = os.path.realpath(path)
    for mount, fstype in mounts if mounts is not None else _mounts():
        if target == mount or target.startswith(mount.rstrip("/") + "/"):
            return fstype == "tmpfs"
    return False


def _free_bytes(path: pathlib.Path) -> int:
    try:
        return shutil.disk_usage(path).free
    except OSError:
        return 0


def _writable(path: pathlib.Path) -> bool:
    return path.is_dir() and os.access(path, os.W_OK | os.X_OK)


def _has_room(path: pathlib.Path) -> bool:
    return _free_bytes(path) >= MIN_FREE_BYTES


def _dev_drives() -> list[pathlib.Path]:
    """Drives `fsutil devdrv query` reports, or none when the command is absent or refused."""
    try:
        proc = subprocess.run(["fsutil", "devdrv", "query"], capture_output=True, text=True,
                              timeout=5)
    except (OSError, subprocess.SubprocessError):
        return []
    if proc.returncode != 0:
        return []
    drives = []
    for token in proc.stdout.replace(":", ": ").split():
        if len(token) == 2 and token[0].isalpha() and token[1] == ":":
            drives.append(pathlib.Path(token + "\\"))
    return drives


def candidates(environ=None, platform: str | None = None) -> list[Candidate]:
    """The ordered candidates for this machine, before any of them is probed."""
    env = os.environ if environ is None else environ
    system = sys.platform if platform is None else platform
    found: list[Candidate] = []

    override = env.get(OVERRIDE)
    if override:
        found.append(Candidate(pathlib.Path(override), "explicit", OVERRIDE))

    disk_notice = (
        "NOTICE: no RAM-backed temp root is available; the test suite's temporary files go to "
        f"{tempfile.gettempdir()} on disk, which is the I/O cost this repository is trying to "
        f"remove. Set {OVERRIDE} to choose another path."
    )

    if system.startswith("win"):
        for drive in _dev_drives():
            found.append(Candidate(drive, "ram", "Dev Drive", notice=None))
        local = env.get("LOCALAPPDATA")
        if local and not any(word in local.lower() for word in _SYNCED):
            found.append(Candidate(pathlib.Path(local), "disk", "LOCALAPPDATA"))
        found.append(Candidate(pathlib.Path(tempfile.gettempdir()), "disk", "system temp",
                               notice=disk_notice))
        return found

    for variable in ("XDG_RUNTIME_DIR",):
        value = env.get(variable)
        if value and not any(c.path == pathlib.Path(value) for c in found):
            found.append(Candidate(pathlib.Path(value), "ram", variable, tmpfs=True))
    found.append(Candidate(pathlib.Path("/dev/shm"), "ram", "/dev/shm", tmpfs=True))
    found.append(Candidate(pathlib.Path(tempfile.gettempdir()), "disk", "system temp",
                           notice=disk_notice))
    return found


def _rejection(candidate: Candidate, mounts=None) -> str | None:
    """Why this candidate cannot be used, or None when it can."""
    if not candidate.path.is_dir():
        return "does not exist"
    if not _writable(candidate.path):
        return "is not writable"
    if candidate.tmpfs and not _is_tmpfs(candidate.path, mounts):
        return "is not a tmpfs mount"
    if candidate.kind == "ram" and not _has_room(candidate.path):
        return f"has less than {MIN_FREE_BYTES // 2**20} MB free"
    return None


def resolve(environ=None, platform: str | None = None) -> Resolution:
    """Pick the root, or raise :class:`TempRootError` when the explicit one cannot be used."""
    mounts = None if platform not in (None, "linux") else _mounts()
    rejected: list[str] = []
    for candidate in candidates(environ, platform):
        reason = _rejection(candidate, mounts)
        if reason is None:
            return Resolution(candidate.path, candidate.kind, candidate.label, candidate.notice)
        rejected.append(f"{candidate.label} ({candidate.path}) {reason}")
        if candidate.kind == "explicit":
            raise TempRootError(f"{OVERRIDE}={candidate.path} was rejected: it {reason}. "
                                "Fix or unset it; an explicit root is never silently replaced.")
    raise TempRootError("no usable temp root: " + "; ".join(rejected))


def export(path, environ=None) -> None:
    """Point this process and every child it starts at `path`."""
    env = os.environ if environ is None else environ
    for key in ENV_KEYS:
        env[key] = str(path)
    tempfile.tempdir = str(path)


def apply(environ=None, platform: str | None = None, stream=None) -> Resolution:
    """Resolve and export, printing the resolution's notice when it carries one."""
    resolution = resolve(environ, platform)
    export(resolution.path, environ)
    if resolution.notice:
        print(resolution.notice, file=stream or sys.stderr, flush=True)
    return resolution


def main(argv: list[str] | None = None) -> int:
    import argparse

    parser = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    parser.add_argument("--explain", action="store_true", help="print each candidate and its fate")
    args = parser.parse_args(argv)
    if args.explain:
        mounts = _mounts()
        for candidate in candidates():
            reason = _rejection(candidate, mounts)
            print(f"{candidate.label:16} {candidate.path}  "
                  f"{'ok' if reason is None else 'rejected: ' + reason}", file=sys.stderr)
    try:
        resolution = resolve()
    except TempRootError as exc:
        print(f"tmproot: {exc}", file=sys.stderr)
        return 2
    if resolution.notice:
        print(resolution.notice, file=sys.stderr, flush=True)
    print(resolution.path)
    return 0


if __name__ == "__main__":
    sys.exit(main())
