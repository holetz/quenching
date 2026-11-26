"""`_paths` isolates the client's session selectors, so a suite run directly measures the tree and
never the operator's own Copilot session."""
import os
import pathlib
import subprocess
import sys
import unittest

TESTS = pathlib.Path(__file__).resolve().parent


class CopilotSelectorTests(unittest.TestCase):
    def test_importing_paths_drops_the_copilot_selectors(self):
        env = dict(os.environ, COPILOT_HOME="/operator/copilot", QUENCHING_COPILOT_HOME="/operator/other")
        code = ("import _paths, os; "
                "print(os.environ.get('COPILOT_HOME'), os.environ.get('QUENCHING_COPILOT_HOME'))")
        done = subprocess.run([sys.executable, "-c", code], cwd=TESTS, env=env,
                              capture_output=True, text=True, check=True)
        self.assertEqual(done.stdout.strip(), "None None")


if __name__ == "__main__":
    unittest.main()
