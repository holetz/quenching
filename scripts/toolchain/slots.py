"""Share the machine's worker budget across the gates that run at the same time.

`-n auto` is right on an idle machine and wrong in company: measured on this repository, one gate
alone ran in 57 s, two gates at full `auto` took 399 s, and the same two at four workers each took
227 s. What is wrong is not `auto`; it is every gate resolving `auto` against the whole machine
independently. This plugin gives them one budget.

Slots are ordinary files under the user cache, each held with the kernel's own file lock
(`flock` on POSIX, `LockFileEx` through `msvcrt.locking` on Windows). A process that dies releases
its locks with its file descriptors, so a killed gate leaks nothing and no cleanup runs on the
failure path. Each gate also registers itself, so a second gate knows how many peers are live and
takes `cores / max(2, live)` — half the machine for one gate, because the peer that starts a second
later must find its half free. A gate that finds no slot waits, printing the holders' pids, up to
`QUENCHING_TEST_SLOT_TIMEOUT` seconds, then runs serially instead of failing: a budget is a
performance decision, never a correctness one.

Load it with `-p scripts.toolchain.slots`; `scripts/toolchain/test.py` and the gate do. The
`unittest` fallback path does not, and simply runs without a budget.

Knobs (all optional):

* `QUENCHING_TEST_SLOTS` — total slots, default the physical core count;
* `QUENCHING_TEST_SLOT_ROOT` — where the slot files live;
* `QUENCHING_TEST_SLOT_TIMEOUT` — seconds to wait for a free slot (default 300).
"""

from __future__ import annotations

import atexit
import contextlib
import dataclasses
import importlib.util
import os
import pathlib
import re
import sys
import tempfile
import time

SLOTS_ENV = "QUENCHING_TEST_SLOTS"
ROOT_ENV = "QUENCHING_TEST_SLOT_ROOT"
TIMEOUT_ENV = "QUENCHING_TEST_SLOT_TIMEOUT"
# Set by a run that already holds slots; a pytest it spawns from inside a test is nested and must
# not queue behind its own parent, nor add workers the parent did not budget for. It runs serially.
HELD_ENV = "QUENCHING_TEST_SLOTS_HELD"
HAS_XDIST = importlib.util.find_spec("xdist") is not None
DEFAULT_TIMEOUT = 300.0
_POLL = 0.2
_STALE_SECONDS = 5.0


@dataclasses.dataclass
class Slot:
    """One held slot: the open descriptor is the lock, so it lives as long as this object."""

    index: int
    fd: int

    def release(self) -> None:
        if self.fd < 0:
            return
        with contextlib.suppress(OSError):
            _unlock(self.fd)
        with contextlib.suppress(OSError):
            os.close(self.fd)
        self.fd = -1


def _try_lock(fd: int) -> bool:
    try:
        if os.name == "nt":
            import msvcrt

            os.lseek(fd, 0, os.SEEK_SET)
            msvcrt.locking(fd, msvcrt.LK_NBLCK, 1)
        else:
            import fcntl

            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except OSError:
        return False
    return True


def _unlock(fd: int) -> None:
    if os.name == "nt":
        import msvcrt

        os.lseek(fd, 0, os.SEEK_SET)
        msvcrt.locking(fd, msvcrt.LK_UNLCK, 1)
    else:
        import fcntl

        fcntl.flock(fd, fcntl.LOCK_UN)


def _open(path: pathlib.Path) -> int:
    flag = os.O_RDWR | os.O_CREAT | getattr(os, "O_BINARY", 0)
    fd = os.open(str(path), flag, 0o600)
    if os.fstat(fd).st_size == 0:
        os.write(fd, b"0")
    return fd


def cache_root(environ=None, platform: str | None = None) -> pathlib.Path:
    """The user's cache directory, per platform, with a temp-dir fallback."""
    env = os.environ if environ is None else environ
    system = (platform or sys.platform).lower()
    if system.startswith("win"):
        base = env.get("LOCALAPPDATA") or env.get("APPDATA")
        if base:
            return pathlib.Path(base)
        return pathlib.Path(tempfile.gettempdir())
    base = env.get("XDG_CACHE_HOME")
    if base:
        return pathlib.Path(base)
    home = env.get("HOME")
    if home:
        return pathlib.Path(home) / ".cache"
    return pathlib.Path(tempfile.gettempdir())


def slot_root(environ=None, platform: str | None = None) -> pathlib.Path:
    """Where the slot and registration files live; the env override wins."""
    env = os.environ if environ is None else environ
    override = env.get(ROOT_ENV)
    root = pathlib.Path(override) if override else cache_root(env, platform) / "quenching" / "gate-slots"
    root.mkdir(parents=True, exist_ok=True)
    return root


def physical_cores(cpuinfo: str | None = None, available: int | None = None) -> int:
    """Physical cores when the platform can say, else the CPUs available to this process."""
    fallback = available or os.cpu_count() or 1
    if cpuinfo is None:
        try:
            cpuinfo = pathlib.Path("/proc/cpuinfo").read_text(encoding="utf-8")
        except OSError:
            return fallback
    cores: dict[str, int] = {}
    for block in cpuinfo.split("\n\n"):
        fields = dict(
            (match.group(1).strip(), match.group(2).strip())
            for match in (re.match(r"([^:]+):\s*(.*)", line) for line in block.splitlines()) if match
        )
        if "physical id" in fields and "cpu cores" in fields:
            try:
                cores[fields["physical id"]] = int(fields["cpu cores"])
            except ValueError:
                return fallback
    total = sum(cores.values())
    return total or fallback


def total_slots(environ=None) -> int:
    env = os.environ if environ is None else environ
    raw = env.get(SLOTS_ENV)
    if raw:
        try:
            return max(1, int(raw))
        except ValueError:
            return max(1, physical_cores())
    return max(1, physical_cores())


def _holders(root: pathlib.Path) -> list[int]:
    pids: list[int] = []
    for path in sorted(root.glob("slot-*.lock")):
        try:
            fd = _open(path)
        except OSError:
            continue
        if _try_lock(fd):
            _unlock(fd)
            os.close(fd)
            continue
        with contextlib.suppress(OSError):
            os.lseek(fd, 0, os.SEEK_SET)
            pids.append(int(os.read(fd, 32).decode("ascii", "replace").strip() or 0))
        os.close(fd)
    return [pid for pid in pids if pid]


@dataclasses.dataclass
class Gate:
    """This process's registration file; its lock proves the gate is alive to its peers."""

    path: pathlib.Path
    fd: int

    def release(self) -> None:
        if self.fd < 0:
            return
        with contextlib.suppress(OSError):
            _unlock(self.fd)
        with contextlib.suppress(OSError):
            os.close(self.fd)
        self.fd = -1
        with contextlib.suppress(OSError):
            self.path.unlink()


def _register(root: pathlib.Path) -> Gate | None:
    name = f"gate-{os.getpid()}-{os.urandom(4).hex()}.lock"
    path = root / name
    try:
        fd = _open(path)
    except OSError:
        return None
    if not _try_lock(fd):
        os.close(fd)
        return None
    os.lseek(fd, 0, os.SEEK_SET)
    os.truncate(fd, 0)
    os.write(fd, str(os.getpid()).encode("ascii"))
    return Gate(path, fd)


def live_gates(root: pathlib.Path) -> int:
    """How many gates currently hold a registration, counting the caller's own."""
    live = 0
    for path in sorted(root.glob("gate-*.lock")):
        try:
            fd = _open(path)
        except OSError:
            continue
        if _try_lock(fd):
            _unlock(fd)
            os.close(fd)
            with contextlib.suppress(OSError):
                if time.time() - path.stat().st_mtime > _STALE_SECONDS:
                    path.unlink()
            continue
        live += 1
        os.close(fd)
    return max(1, live)


def share(total: int, live: int) -> int:
    """Slots one gate may take: half for a lone gate, an even split when peers are live."""
    return max(1, total // max(2, live))


@dataclasses.dataclass
class Held:
    """The slots this process holds, plus its registration; `release` undoes both."""

    slots: list[Slot]
    gate: Gate | None = None

    def __len__(self) -> int:
        return len(self.slots)

    def release(self) -> None:
        for slot in self.slots:
            slot.release()
        if self.gate is not None:
            self.gate.release()


def acquire(limit: int | None = None, root: pathlib.Path | None = None, total: int | None = None,
            timeout: float | None = None, stream=None) -> Held:
    """Hold up to `limit` slots (or this gate's share), waiting when none is free."""
    out = sys.stderr if stream is None else stream
    total = total if total is not None else total_slots()
    root = root if root is not None else slot_root()
    timeout = timeout if timeout is not None else float(
        os.environ.get(TIMEOUT_ENV, DEFAULT_TIMEOUT))
    gate = _register(root)
    want = limit if limit is not None else share(total, live_gates(root))
    want = max(1, min(want, total))
    deadline = time.monotonic() + timeout
    held: list[Slot] = []
    waited = False
    while True:
        for index in range(total):
            if len(held) >= want:
                break
            if any(slot.index == index for slot in held):
                continue
            try:
                fd = _open(root / f"slot-{index}.lock")
            except OSError:
                continue
            if _try_lock(fd):
                os.lseek(fd, 0, os.SEEK_SET)
                os.truncate(fd, 0)
                os.write(fd, str(os.getpid()).encode("ascii"))
                held.append(Slot(index, fd))
            else:
                os.close(fd)
        if held or time.monotonic() >= deadline:
            break
        if not waited:
            holders = ", ".join(f"pid {pid}" for pid in _holders(root)) or "unknown"
            print(f"[slots] no free slot ({holders}); waiting up to {timeout:.0f} s", file=out,
                  flush=True)
            waited = True
        time.sleep(_POLL)
    print(f"[slots] {len(held)} of {total} slot(s) under {root}", file=out, flush=True)
    held_result = Held(held, gate)
    if held:
        os.environ[HELD_ENV] = str(len(held))
        atexit.register(held_result.release)
    return held_result


# --------------------------------------------------------------------------- #
# The pytest plugin. `-n auto` is answered before `pytest_configure` runs, so
# `pytest_xdist_auto_num_workers` is where the budget is taken; an explicit `-n N` is clamped in
# `pytest_configure`, including the worker list xdist already materialised.
# --------------------------------------------------------------------------- #
def _budget(config, want: int | None = None) -> int:
    cached = getattr(config, "_quenching_held", None)
    if cached is not None:
        return len(cached)
    inherited = os.environ.get(HELD_ENV, "")
    if inherited.isdigit() and int(inherited) > 0:
        config._quenching_slots = 0
        return 0
    config._quenching_held = acquire(limit=want)
    return len(config._quenching_held)


def xdist_auto_num_workers(config) -> int:  # pragma: no cover - exercised by real runs
    if hasattr(config, "workerinput"):
        return 0
    return _budget(config)


# Without xdist the hookspec does not exist and pluggy refuses an unknown hook at collection. A
# serial run needs no budget either, so both the hook and the acquisition are absent there.
if HAS_XDIST:
    pytest_xdist_auto_num_workers = xdist_auto_num_workers


def pytest_configure(config) -> None:  # pragma: no cover - exercised by real runs
    if hasattr(config, "workerinput") or not HAS_XDIST:
        return
    requested = getattr(config.option, "numprocesses", None)
    if requested in (None, 0):
        return  # a serial run asks for no workers, so it reserves no budget
    budget = _budget(config, want=requested if isinstance(requested, int) else None)
    if isinstance(requested, int) and requested > budget:
        config.option.numprocesses = budget
        if getattr(config.option, "tx", None):
            config.option.tx = ["popen"] * budget


def main(argv: list[str] | None = None) -> int:
    """`python -m scripts.toolchain.slots` prints what this machine and this gate would get."""
    del argv
    root = slot_root()
    total = total_slots()
    live = live_gates(root)
    print(f"slots: {total} total, root {root}, live gates {live}, share {share(total, live)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
