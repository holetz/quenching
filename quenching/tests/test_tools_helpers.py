"""The portable PATH helpers in `_tools.py`, proved by running what they write.

Each test resolves the written program the way the product does, through `shutil.which` on the
isolated directory, and then runs it: a helper that writes a file nobody can execute would pass a
test that only checked the file exists.
"""

import os
import pathlib
import shutil
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


class FakeTool(unittest.TestCase):
    def test_a_fake_tool_is_found_on_the_isolated_path_and_runs_with_its_argv(self):
        with tempfile.TemporaryDirectory() as tmp:
            written = _tools.fake_tool(
                tmp, "codex", "import sys\nprint('fake', *sys.argv[1:])\nsys.exit(3)\n"
            )
            found = shutil.which("codex", path=tmp)
            self.assertIsNotNone(found, "shutil.which does not find the fake tool")
            self.assertEqual(pathlib.Path(found).resolve(), written.resolve())
            run = subprocess.run([found, "a b", "c"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 3, run.stderr)
        self.assertEqual(run.stdout.strip(), "fake a b c")


class LinkTool(unittest.TestCase):
    def test_a_real_tool_is_reachable_from_the_isolated_path_without_a_symlink_privilege(self):
        with tempfile.TemporaryDirectory() as tmp:
            _tools.link_tool(tmp, "git")
            found = shutil.which("git", path=tmp)
            self.assertIsNotNone(found)
            run = subprocess.run([found, "--version"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("git version", run.stdout)

    def test_a_missing_tool_is_refused_not_written(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(FileNotFoundError):
                _tools.link_tool(tmp, "quenching-no-such-tool")
            self.assertEqual(os.listdir(tmp), [])


class Bash(unittest.TestCase):
    def test_the_bash_runs_a_posix_script_and_is_never_the_wsl_launcher(self):
        found = _tools.bash()
        self.assertIsNotNone(found, "no bash: Git for Windows or a POSIX bash is required")
        if os.name == "nt":
            self.assertFalse(_tools._is_wsl_launcher(found), found)
        run = subprocess.run([found, "-c", 'printf "%s" "$((6 * 7))"'], capture_output=True,
                             text=True)
        self.assertEqual((run.returncode, run.stdout), (0, "42"), run.stderr)


if __name__ == "__main__":
    unittest.main()
