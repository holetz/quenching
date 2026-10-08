"""The fail-closed branches of the `surface-load checks` block in `scripts/verify_repo.sh`.

The block is cut out of the real script between its two markers and run in a scratch tree with a
stub `functional-checks.sh` and a controlled PATH, so the test never bills a `claude -p` session and
never drifts from the script it guards. A marker that disappears fails the test instead of letting
it pass empty.
"""

import pathlib
import shutil
import subprocess
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "verify_repo.sh"
START = "printf '\\n==> surface-load checks\\n'"
END = "printf '\\nRepository verification passed.\\n'"
BASH = shutil.which("bash")


def _block() -> str:
    text = SCRIPT.read_text()
    assert START in text and END in text, "surface-load markers moved in verify_repo.sh"
    return text[text.index(START) : text.index(END)]


class SurfaceLoadBlock(unittest.TestCase):
    def run_block(self, *, functional=None, claude=False, stub_rc=0):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            checks = root / "plugins" / "quenching" / "assets" / "checks"
            checks.mkdir(parents=True)
            (checks / "functional-checks.sh").write_text(f"exit {stub_rc}\n")
            fakebin = root / "fakebin"
            fakebin.mkdir()
            (fakebin / "bash").symlink_to(BASH)
            if claude:
                fake = fakebin / "claude"
                fake.write_text("#!/bin/sh\nexit 0\n")
                fake.chmod(0o755)
            env = {"PATH": str(fakebin)}
            if functional is not None:
                env["QUENCHING_FUNCTIONAL"] = functional
            return subprocess.run(
                [BASH, "-c", _block()], cwd=root, env=env, capture_output=True, text=True
            )

    def test_without_the_opt_in_it_skips_and_stays_green(self):
        run = self.run_block()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("SKIPPED", run.stdout)

    def test_requested_without_claude_on_path_fails(self):
        run = self.run_block(functional="1")
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("claude", run.stderr)

    def test_an_inconclusive_exit_2_fails(self):
        run = self.run_block(functional="1", claude=True, stub_rc=2)
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("exit 2", run.stderr)

    def test_a_failing_exit_1_fails(self):
        run = self.run_block(functional="1", claude=True, stub_rc=1)
        self.assertEqual(run.returncode, 1, run.stdout)

    def test_a_passing_measurement_passes(self):
        run = self.run_block(functional="1", claude=True, stub_rc=0)
        self.assertEqual(run.returncode, 0, run.stderr)


if __name__ == "__main__":
    unittest.main()
