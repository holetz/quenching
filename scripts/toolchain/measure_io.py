#!/usr/bin/env python3
"""Measure the test suite's I/O cost: wall time, temp footprint, block writes and disk flushes.

Reproducible baseline for the I/O spec: every improvement comes back with a before and an after
measured by this same script. Stdlib only. Output is ephemeral (it can be remade in minutes) and
lands in `.quenching/measure/<stamp>/`: one `report.json`, one `report.md` and each variant's log.

Variants (`--variants`, comma-separated, run in order):

  gate      `bash scripts/verify_repo.sh` whole (suite + every other check)
  auto      the gate's pytest invocation with `-n auto`
  n4        the same with `-n 4`
  serial    the same with `-p no:xdist` (single process)

Each variant runs with `TMPDIR` pointed at a dedicated empty directory under `--tmp-root` (default:
the system temp dir, i.e. what the suite uses today), so the temp footprint is attributable. A
sampler THREAD — never a detached loop — walks that directory every `--sample-every` seconds and
records the peak bytes and entries; it dies with this process.

Linux also records, from `getrusage(RUSAGE_CHILDREN)`, the 512-byte blocks the variant's process
tree wrote, and, from `/proc/diskstats`, the write ops, sectors and flush requests on the device
under the checkout (followed through dm-crypt/LVM to the physical disk). Diskstats is machine-wide: concurrent activity (another worktree's gate)
inflates it, so the report prints the machine's I/O PSI beside it. Other platforms record wall
time and footprint only and say the counters are unavailable.

`--durations` adds `--durations=30` to the `serial` variant and classifies the slowest tests as
"lógica pura", "filesystem" or "git/subprocess" from their module's source.
"""

from __future__ import annotations

import argparse
import datetime as _dt
import json
import os
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import threading
import time

ROOT = pathlib.Path(__file__).resolve().parents[2]
PYTEST_BASE = [
    "uv", "run", "python", "-m", "pytest", "quenching/tests", "-q", "-p", "randomly",
    "--cov=quenching/assets/bin/quenching",
]
VARIANTS = {
    "gate": ["bash", "scripts/verify_repo.sh"],
    "auto": [*PYTEST_BASE, "-n", "auto"],
    "n4": [*PYTEST_BASE, "-n", "4"],
    "serial": [*PYTEST_BASE, "-p", "no:xdist"],
}


def _device_of(path: pathlib.Path) -> str | None:
    """The /proc/diskstats name backing `path` (dm-N under LVM/dm-crypt), or None off Linux."""
    try:
        dev = os.stat(path).st_dev
    except OSError:
        return None
    sysfs = pathlib.Path(f"/sys/dev/block/{os.major(dev)}:{os.minor(dev)}")
    if not sysfs.exists():
        return None
    node = sysfs.resolve()
    # dm-crypt/LVM devices report no flushes: follow `slaves/` down to the physical disk, whose
    # whole-disk node (nvme0n1, not the nvme0n1p3 partition) carries the flush counter.
    while (node / "slaves").is_dir() and any((node / "slaves").iterdir()):
        node = next((node / "slaves").iterdir()).resolve()
    if (node / "partition").exists():
        node = node.parent
    return node.name


def _diskstats(device: str | None) -> dict | None:
    if not device:
        return None
    try:
        for line in pathlib.Path("/proc/diskstats").read_text().splitlines():
            f = line.split()
            if f[2] == device:
                out = {"writes": int(f[7]), "sectors_written": int(f[9]), "write_ms": int(f[10])}
                if len(f) >= 20:
                    out["flushes"] = int(f[18])
                return out
    except OSError:
        return None
    return None


def _psi() -> str | None:
    try:
        return pathlib.Path("/proc/pressure/io").read_text().strip().replace("\n", " | ")
    except OSError:
        return None


class Sampler(threading.Thread):
    """Peak bytes and entries under one directory; a daemon thread owned by this process."""

    def __init__(self, root: pathlib.Path, every: float):
        super().__init__(daemon=True)
        self.root, self.every = root, every
        self.peak_bytes = self.peak_entries = 0
        self.stop = threading.Event()

    def _walk(self) -> tuple[int, int]:
        size = entries = 0
        for dirpath, dirnames, filenames in os.walk(self.root, onerror=lambda e: None):
            entries += len(dirnames) + len(filenames)
            for name in filenames:
                try:
                    size += os.lstat(os.path.join(dirpath, name)).st_size
                except OSError:
                    pass
        return size, entries

    def run(self) -> None:
        while not self.stop.wait(self.every):
            size, entries = self._walk()
            self.peak_bytes = max(self.peak_bytes, size)
            self.peak_entries = max(self.peak_entries, entries)


def _rusage_children():
    try:
        import resource
    except ImportError:
        return None
    return resource.getrusage(resource.RUSAGE_CHILDREN)


def run_variant(name: str, extra: list[str], tmp_root: pathlib.Path, out: pathlib.Path,
                every: float) -> dict:
    tmp = tmp_root / f"tmp-{name}"
    shutil.rmtree(tmp, ignore_errors=True)
    tmp.mkdir(parents=True)
    env = dict(os.environ, TMPDIR=str(tmp), TEMP=str(tmp), TMP=str(tmp))
    cmd = [*VARIANTS[name], *extra]
    # The disk measured is the checkout's physical disk: with TMPDIR on tmpfs the temp root has no
    # block device, and what still reaches the SSD (coverage data, .venv reads) is the point.
    device = _device_of(ROOT)
    disk_before, ru_before = _diskstats(device), _rusage_children()
    sampler = Sampler(tmp, every)
    sampler.start()
    psi_before = _psi()
    start = time.monotonic()
    with (out / f"{name}.log").open("w", encoding="utf-8") as fh:
        rc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=fh, stderr=subprocess.STDOUT).returncode
    wall = time.monotonic() - start
    sampler.stop.set()
    sampler.join()
    ru_after, disk_after = _rusage_children(), _diskstats(device)
    result = {
        "variant": name, "cmd": cmd, "exit": rc, "wall_s": round(wall, 1),
        "tmp_root": str(tmp), "tmp_device": _device_of(tmp) or "tmpfs/none", "disk": device,
        "tmp_peak_mb": round(sampler.peak_bytes / 2**20, 1),
        "tmp_peak_entries": sampler.peak_entries,
        "tmp_left_entries": sum(1 for _ in tmp.rglob("*")),
        "psi_before": psi_before, "psi_after": _psi(),
    }
    if ru_before and ru_after:
        result["tree_written_mb"] = round((ru_after.ru_oublock - ru_before.ru_oublock) * 512 / 2**20, 1)
    if disk_before and disk_after:
        delta = {k: disk_after[k] - disk_before[k] for k in disk_after if k in disk_before}
        delta["mb_written"] = round(delta["sectors_written"] * 512 / 2**20, 1)
        result["disk_delta"] = delta
    shutil.rmtree(tmp, ignore_errors=True)
    return result


_DURATION = re.compile(r"^\s*([\d.]+)s (call|setup|teardown)\s+(\S+)")


def classify_durations(log: pathlib.Path, limit: int = 30) -> list[dict]:
    rows = []
    for line in log.read_text(encoding="utf-8", errors="replace").splitlines():
        m = _DURATION.match(line)
        if m:
            rows.append({"seconds": float(m[1]), "phase": m[2], "test": m[3]})
    sources: dict[str, str] = {}
    for row in rows[:limit]:
        module = row["test"].split("::")[0]
        if module not in sources:
            try:
                sources[module] = (ROOT / module).read_text(encoding="utf-8")
            except OSError:
                sources[module] = ""
        src = sources[module]
        if re.search(r"subprocess|[\"']git[\"']|_git\(|\bgit\(", src):
            row["class"] = "git/subprocess"
        elif re.search(r"tempfile|tmp_path|write_text|open\(|shutil", src):
            row["class"] = "filesystem"
        else:
            row["class"] = "lógica pura"
    return rows[:limit]


def main() -> int:
    ap = argparse.ArgumentParser(description=(__doc__ or "").splitlines()[0])
    ap.add_argument("--variants", default="gate,auto,n4,serial")
    ap.add_argument("--tmp-root", type=pathlib.Path, default=None,
                    help="where each variant's TMPDIR lives (default: the system temp dir)")
    ap.add_argument("--sample-every", type=float, default=2.0)
    ap.add_argument("--durations", action="store_true")
    ap.add_argument("--label", default="")
    ap.add_argument("--seed", default="12345", help="PYTEST_RANDOMLY_SEED, for comparable runs")
    args = ap.parse_args()

    stamp = _dt.datetime.now().strftime("%Y%m%dT%H%M%S")
    out = ROOT / ".quenching" / "measure" / (stamp + (f"-{args.label}" if args.label else ""))
    out.mkdir(parents=True)
    tmp_root = pathlib.Path(tempfile.mkdtemp(prefix="quenching-measure-", dir=args.tmp_root))
    os.environ["PYTEST_RANDOMLY_SEED"] = args.seed
    results = []
    try:
        for name in [v.strip() for v in args.variants.split(",") if v.strip()]:
            if name not in VARIANTS:
                print(f"unknown variant: {name}", file=sys.stderr)
                return 2
            extra = [] if name == "gate" else [f"--randomly-seed={args.seed}"]
            if name == "serial" and args.durations:
                extra.append("--durations=30")
            print(f"==> {name}", flush=True)
            res = run_variant(name, extra, tmp_root, out, args.sample_every)
            if name == "serial" and args.durations:
                res["slowest"] = classify_durations(out / f"{name}.log")
            results.append(res)
            print(json.dumps({k: v for k, v in res.items() if k != "slowest"}, ensure_ascii=False),
                  flush=True)
    finally:
        shutil.rmtree(tmp_root, ignore_errors=True)
    report = {"stamp": stamp, "label": args.label, "platform": sys.platform,
              "cpus": os.cpu_count(), "results": results}
    (out / "report.json").write_text(json.dumps(report, indent=2, ensure_ascii=False),
                                     encoding="utf-8")
    lines = ["| variante | exit | parede (s) | pico tmp (MB) | pico entradas | escrito pela árvore (MB) "
             "| writes no disco | flushes no disco |", "|---|---|---|---|---|---|---|---|"]
    for r in results:
        d = r.get("disk_delta", {})
        lines.append(f"| {r['variant']} | {r['exit']} | {r['wall_s']} | {r['tmp_peak_mb']} | "
                     f"{r['tmp_peak_entries']} | {r.get('tree_written_mb', 'n/d')} | "
                     f"{d.get('writes', 'n/d')} | {d.get('flushes', 'n/d')} |")
    (out / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(out)
    # The measurement is the deliverable: a failing test is reported in the variant's log and
    # `exit` column, not turned into a failed measurement.
    return 0


if __name__ == "__main__":
    sys.exit(main())
