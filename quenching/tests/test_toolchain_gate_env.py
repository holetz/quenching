"""`scripts/verify_repo.sh` pins the timezone before anything runs, so every tier of the gate
renders dates the same way on a laptop, in an agent session and in CI — and runs every `python3`
from the project's own environment."""

import pathlib
import re
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — the suite's temp root and git isolation, before any test runs
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
import _tools  # noqa: E402

SCRIPT = pathlib.Path(__file__).resolve().parent.parent.parent / "scripts" / "verify_repo.sh"


class TheGateEnvironment(unittest.TestCase):
    def test_tz_is_exported_as_utc_before_the_first_check(self):
        text = SCRIPT.read_text(encoding="utf-8")
        pin = re.search(r"^export TZ=UTC$", text, re.M)
        self.assertIsNotNone(pin, "verify_repo.sh no longer exports TZ=UTC")
        self.assertLess(pin.start(), text.index("pytest_args="))
        self.assertLess(pin.start(), text.index("run_check \""))

    def test_python3_in_the_gate_and_in_its_bash_children_is_the_venv(self):
        # On Windows the PATH's `python3` is the Microsoft Store alias, with none of the dev group.
        text = SCRIPT.read_text(encoding="utf-8")
        start = text.index("# Every `python3` below")
        end = text.index("export -f python3")
        block = text[start:end] + "export -f python3\n"
        with tempfile.TemporaryDirectory() as tmp:
            venv_python = pathlib.Path(tmp, ".venv", "bin", "python")
            venv_python.parent.mkdir(parents=True)
            venv_python.write_text('#!/bin/sh\necho "venv $*"\n', encoding="utf-8")
            venv_python.chmod(0o755)
            program = (
                f'ROOT="$(cd "{pathlib.Path(tmp).as_posix()}" && pwd)"\n{block}'
                'python3 -c gate\n"$BASH" -c "python3 -c child"\n'
            )
            run = subprocess.run([_tools.bash(), "-c", program], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.split("\n")[:2], ["venv -c gate", "venv -c child"])
        self.assertLess(start, text.index("TMPROOT="), "python3 is resolved after its first use")


if __name__ == "__main__":
    unittest.main()
