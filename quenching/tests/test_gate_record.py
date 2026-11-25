"""The gate record `scripts/verify_repo.sh` writes and `cq git pr merge` reads.

The writer is the repository's own script (`scripts/toolchain/gate_record.py`), the reader ships in
`quenching.config.ci`; the round trip below is what keeps the two halves of the contract together.
The gate's own wiring is checked on the script text, since a real gate run costs minutes.
"""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.config import ci

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))
from scripts.toolchain import gate_record  # noqa: E402


def git(root, *args):
    subprocess.run(["git", *args], cwd=root, check=True, capture_output=True, text=True)


def head_of(root):
    return subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True,
                          capture_output=True, text=True).stdout.strip()


class TheRecordRoundTrip(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = pathlib.Path(tmp.name)
        (self.root / ".agents").mkdir()
        git(self.root, "init", "-q")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q",
            "--allow-empty", "-m", "first")
        (self.root / ".gitignore").write_text(".quenching/\n", encoding="utf-8")
        git(self.root, "add", ".gitignore")
        git(self.root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "ignore")
        self.head = head_of(self.root)

    def test_a_green_gate_on_a_clean_tree_proves_its_head_and_only_it(self):
        gate_record.write(self.root, 0, "full")
        self.assertEqual(0, ci.proven_exit(str(self.root), self.head))
        self.assertIsNone(ci.proven_exit(str(self.root), "0" * 40))
        self.assertIsNone(ci.proven_exit(str(self.root), None))

    def test_the_record_carries_head_exit_scope_and_date(self):
        record = gate_record.write(self.root, 0, "affected")
        on_disk = json.loads((self.root / gate_record.RECORD).read_text(encoding="utf-8"))
        self.assertEqual(record, on_disk)
        self.assertEqual((1, self.head, 0, "affected", False),
                         (on_disk["schema"], on_disk["head"], on_disk["exit"], on_disk["scope"],
                          on_disk["dirty"]))
        self.assertRegex(on_disk["date"], r"^\d{4}-\d\d-\d\dT\d\d:\d\d:\d\dZ$")

    def test_a_failing_gate_records_its_exit_and_proves_it(self):
        gate_record.write(self.root, 1, "full")
        self.assertEqual(1, ci.proven_exit(str(self.root), self.head))

    def test_a_dirty_tree_proves_nothing(self):
        (self.root / "stray.txt").write_text("x", encoding="utf-8")
        self.assertTrue(gate_record.write(self.root, 0, "full")["dirty"])
        self.assertIsNone(ci.proven_exit(str(self.root), self.head))

    def test_clear_removes_the_record_and_a_missing_one_proves_nothing(self):
        gate_record.write(self.root, 0, "full")
        gate_record.clear(self.root)
        gate_record.clear(self.root)
        self.assertIsNone(ci.proven_exit(str(self.root), self.head))

    def test_the_cli_writes_and_clears(self):
        for argv in (["--root", str(self.root), "write", "--exit", "0", "--scope", "full"],):
            self.assertEqual(0, gate_record.main(argv))
        self.assertEqual(0, ci.proven_exit(str(self.root), self.head))
        self.assertEqual(0, gate_record.main(["--root", str(self.root), "clear"]))
        self.assertIsNone(ci.proven_exit(str(self.root), self.head))

    def test_outside_a_repository_no_record_is_written(self):
        with tempfile.TemporaryDirectory() as bare:
            self.assertIsNone(gate_record.write(pathlib.Path(bare), 0, "full"))


class TheGateScript(unittest.TestCase):
    text = (REPO_ROOT / "scripts" / "verify_repo.sh").read_text(encoding="utf-8")

    def test_the_gate_clears_at_the_start_and_writes_from_its_exit_trap(self):
        self.assertIn("python3 -m scripts.toolchain.gate_record clear", self.text)
        self.assertIn('gate_record write --exit "$rc"', self.text)
        self.assertIn("trap finish_gate EXIT", self.text)
        self.assertLess(self.text.index("gate_record clear"), self.text.index("trap finish_gate EXIT"))

    def test_the_trap_takes_the_status_before_anything_else_runs(self):
        body = self.text[self.text.index("finish_gate() {"):]
        self.assertTrue(body.split("\n")[1].strip() == "local rc=$?")


if __name__ == "__main__":
    unittest.main()
