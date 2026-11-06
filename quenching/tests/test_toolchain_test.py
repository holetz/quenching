"""The affected runner: the argv it builds, the fallback it states, and the layer it defers.

`build` and `plan` are pure enough to assert directly; the end-to-end case runs a real, tiny
selection so a broken launcher (a wrong `-p`, a filter that hides everything) fails here rather
than in a task lane.
"""

from __future__ import annotations

import pathlib
import subprocess
import sys
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import test as runner  # noqa: E402


class Build(unittest.TestCase):
    def assert_no_marker_filter(self, argv: list[str]) -> None:
        filters = [argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == "-m"]
        self.assertNotIn("not integration", filters, argv)

    def test_the_integration_layer_is_filtered_and_the_plugin_loaded(self):
        argv = runner.build(["quenching/tests/test_x.py"], False, ["-q"])
        self.assertIn("scripts.toolchain.layers", argv)
        self.assertIn("not integration", argv)
        self.assertEqual("-q", argv[-1])

    def test_with_integration_drops_the_filter(self):
        argv = runner.build(["quenching/tests"], True, [])
        self.assert_no_marker_filter(argv)

    def test_the_targets_come_before_the_forwarded_arguments(self):
        argv = runner.build(["quenching/tests/test_a.py", "quenching/tests/test_b.py"], True, ["-k", "x"])
        self.assertEqual(["quenching/tests/test_a.py", "quenching/tests/test_b.py", "-k", "x"],
                         argv[-4:])


class Plan(unittest.TestCase):
    def test_without_affected_the_whole_suite_runs(self):
        targets, reason = runner.plan(REPO_ROOT, "origin/main", False)
        self.assertEqual(["quenching/tests"], targets)
        self.assertIsNone(reason)

    def test_a_global_change_states_why_the_whole_suite_runs(self):
        selection = runner.affected.Selection("main", ("pyproject.toml",), (),
                                              ("fail-open: pyproject.toml is global",), True)
        with mock.patch.object(runner.affected, "select", return_value=selection):
            targets, reason = runner.plan(REPO_ROOT, "main", True)
        self.assertEqual(["quenching/tests"], targets)
        self.assertIn("global", reason)

    def test_a_scoped_selection_returns_its_tests(self):
        selection = runner.affected.Selection("main", ("a.py",), ("quenching/tests/test_git.py",), (), False)
        with mock.patch.object(runner.affected, "select", return_value=selection):
            targets, reason = runner.plan(REPO_ROOT, "main", True)
        self.assertEqual(["quenching/tests/test_git.py"], targets)
        self.assertIsNone(reason)


    def test_explicit_paths_take_precedence_over_the_diff(self):
        targets, reason = runner.plan(REPO_ROOT, "main", False, ["quenching/tests/test_git.py"])
        self.assertEqual(["quenching/tests/test_git.py"], targets)
        self.assertIsNone(reason)


class EndToEnd(unittest.TestCase):
    def test_a_real_run_reports_the_deferred_layer(self):
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.toolchain.test",
             "quenching/tests/test_toolchain_layers.py", "-q"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("target(s) given", proc.stderr)
        self.assertIn("integration:", proc.stderr)
        self.assertIn("passed", proc.stdout)


if __name__ == "__main__":
    unittest.main()
