"""The shared worker budget: what a gate takes, what a peer gets, and what a dead gate leaves.

The two properties that matter cannot be proven inside one process: another gate's slots are only
invisible to us because the kernel holds a lock, and a killed holder only stops holding because the
kernel closes its descriptors. Both cases therefore run a real child process; the rest of the file
exercises the pure decisions (platform paths, core count, share) and the pytest hook surface.
"""

from __future__ import annotations

import io
import os
import pathlib
import subprocess
import sys
import tempfile
import time
import unittest
from types import SimpleNamespace
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import slots  # noqa: E402

CHILD = """
import pathlib, sys, time
sys.path.insert(0, {root!r})
from scripts.toolchain import slots
held = slots.acquire(root=pathlib.Path({slot_root!r}), total={total}, timeout={timeout})
print("held", [slot.index for slot in held.slots], flush=True)
time.sleep({sleep})
"""


def child(slot_root: pathlib.Path, total: int = 6, timeout: float = 5, sleep: float = 30):
    script = CHILD.format(root=str(REPO_ROOT), slot_root=str(slot_root), total=total,
                          timeout=timeout, sleep=sleep)
    return subprocess.Popen([sys.executable, "-c", script], cwd=REPO_ROOT,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)


class Paths(unittest.TestCase):
    def test_linux_follows_xdg_then_home(self):
        self.assertEqual(pathlib.Path("/cache"), slots.cache_root({"XDG_CACHE_HOME": "/cache"}))
        self.assertEqual(pathlib.Path("/home/u/.cache"), slots.cache_root({"HOME": "/home/u"},
                                                                          platform="linux"))

    def test_windows_uses_local_appdata_then_the_temp_dir(self):
        self.assertEqual(pathlib.Path("C:/Users/u/AppData/Local"),
                         slots.cache_root({"LOCALAPPDATA": "C:/Users/u/AppData/Local"},
                                          platform="win32"))
        fallback = slots.cache_root({}, platform="win32")
        self.assertEqual(pathlib.Path(tempfile.gettempdir()), fallback)

    def test_the_slot_root_override_wins_and_is_created(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = pathlib.Path(tmp) / "nested"
            got = slots.slot_root({slots.ROOT_ENV: str(target)})
            self.assertEqual(target, got)
            self.assertTrue(target.is_dir())


class Cores(unittest.TestCase):
    CPUINFO = (
        "processor\t: 0\nphysical id\t: 0\ncpu cores\t: 4\n\n"
        "processor\t: 1\nphysical id\t: 0\ncpu cores\t: 4\n\n"
        "processor\t: 8\nphysical id\t: 1\ncpu cores\t: 4\n\n"
    )

    def test_physical_cores_sums_each_package_once(self):
        self.assertEqual(8, slots.physical_cores(self.CPUINFO, available=16))

    def test_an_unparseable_cpuinfo_falls_back_to_the_available_cpus(self):
        self.assertEqual(12, slots.physical_cores("nonsense\n\n", available=12))

    def test_the_total_slot_count_can_be_overridden(self):
        self.assertEqual(3, slots.total_slots({slots.SLOTS_ENV: "3"}))
        self.assertGreaterEqual(slots.total_slots({slots.SLOTS_ENV: "nonsense"}), 1)

    def test_a_lone_gate_reserves_half_and_three_gates_split_in_three(self):
        self.assertEqual(5, slots.share(10, 1))
        self.assertEqual(3, slots.share(10, 3))
        self.assertEqual(1, slots.share(1, 4))


class Acquisition(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = pathlib.Path(self._tmp.name)

    def test_a_second_process_takes_the_complement_not_the_same_slots(self):
        mine = slots.acquire(root=self.root, total=6, timeout=1)
        self.addCleanup(mine.release)
        self.assertEqual([0, 1, 2], [slot.index for slot in mine.slots])
        peer = child(self.root, total=6, sleep=1)
        out, err = peer.communicate(timeout=30)
        self.assertEqual(0, peer.returncode, err)
        self.assertIn("held [3, 4, 5]", out)

    def test_a_killed_holder_releases_its_slots(self):
        peer = child(self.root, total=6, sleep=60)
        self.assertTrue(peer.stdout.readline().startswith("held"))
        peer.kill()
        peer.wait(timeout=30)
        deadline = time.monotonic() + 5
        while time.monotonic() < deadline:
            got = slots.acquire(root=self.root, total=6, limit=6, timeout=0.2)
            if len(got) == 6:
                got.release()
                break
            got.release()
            time.sleep(0.1)
        else:
            self.fail("a killed gate kept its slots")

    def test_no_free_slot_waits_the_timeout_then_runs_serially(self):
        mine = slots.acquire(root=self.root, total=2, limit=2, timeout=1)
        self.assertEqual(2, len(mine))
        self.addCleanup(mine.release)
        with mock.patch.dict(os.environ, {slots.TIMEOUT_ENV: "0.2"}):
            out = io.StringIO()
            got = slots.acquire(root=self.root, total=2, timeout=0.2, stream=out)
            self.addCleanup(got.release)
        self.assertEqual(0, len(got))
        self.assertIn("no free slot", out.getvalue())
        self.assertIn("pid", out.getvalue())


class Plugin(unittest.TestCase):
    def test_auto_workers_are_the_held_slots(self):
        config = SimpleNamespace(_quenching_held=slots.Held([slots.Slot(i, -1) for i in range(3)]))
        self.assertEqual(3, slots.pytest_xdist_auto_num_workers(config))

    def test_the_budget_is_acquired_once_per_process(self):
        config = SimpleNamespace()
        held = slots.Held([slots.Slot(0, -1), slots.Slot(1, -1)])
        with mock.patch.object(slots, "acquire", return_value=held) as budget:
            self.assertEqual(2, slots._budget(config))
            self.assertEqual(2, slots._budget(config))
        self.assertEqual(1, budget.call_count)

    def test_an_explicit_worker_count_is_clamped_and_the_worker_list_rebuilt(self):
        config = SimpleNamespace(
            _quenching_held=slots.Held([slots.Slot(0, -1), slots.Slot(1, -1)]),
            option=SimpleNamespace(numprocesses=8, tx=["popen"] * 8))
        slots.pytest_configure(config)
        self.assertEqual(2, config.option.numprocesses)
        self.assertEqual(["popen", "popen"], config.option.tx)

    def test_a_worker_never_takes_a_budget(self):
        config = SimpleNamespace(workerinput={"workerid": "gw0"})
        self.assertEqual(0, slots.pytest_xdist_auto_num_workers(config))
        self.assertFalse(hasattr(config, "_quenching_held"))


if __name__ == "__main__":
    unittest.main()
