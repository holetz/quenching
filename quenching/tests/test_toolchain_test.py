"""The affected runner: the argv it builds, the fallback it states, and the layer it defers.

`build` and `plan` are pure enough to assert directly; the end-to-end case runs a real, tiny
selection so a broken launcher (a wrong `-p`, a filter that hides everything) fails here rather
than in a task lane.
"""

from __future__ import annotations

import importlib.util
import pathlib
import subprocess
import sys
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — the suite's temp root and git isolation, before any test runs
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
HAS_PYTEST = importlib.util.find_spec("pytest") is not None
HAS_XDIST = importlib.util.find_spec("xdist") is not None
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import test as runner  # noqa: E402


class Build(unittest.TestCase):
    def assert_no_marker_filter(self, argv: list[str]) -> None:
        filters = [argv[i + 1] for i, arg in enumerate(argv[:-1]) if arg == "-m"]
        self.assertNotIn("not integration", filters, argv)

    def test_the_integration_layer_is_filtered_and_the_plugin_loaded(self):
        argv = runner.build(["quenching/tests/test_git.py"], False, ["-q"])
        self.assertIn("scripts.toolchain.layers", argv)
        self.assertIn("not integration", argv)
        self.assertEqual("-q", argv[-1])

    def test_with_integration_drops_the_filter(self):
        argv = runner.build(["quenching/tests"], True, [])
        self.assert_no_marker_filter(argv)

    @unittest.skipUnless(HAS_XDIST, "the runner adds -n only when pytest-xdist is installed")
    def test_the_workers_default_to_auto_and_do_not_duplicate_a_choice(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            argv = runner.build(["a"], True, [])
        self.assertEqual("auto", argv[argv.index("-n") + 1])
        explicit = runner.build(["a"], True, ["-n", "4"])
        self.assertEqual(1, explicit.count("-n"))
        self.assertNotIn("auto", explicit)

    @unittest.skipUnless(HAS_XDIST, "the runner adds -n only when pytest-xdist is installed")
    def test_the_worker_count_can_be_overridden_by_the_environment(self):
        with mock.patch.dict("os.environ", {runner.WORKERS_ENV: "3"}, clear=True):
            argv = runner.build(["a"], True, [])
        self.assertEqual("3", argv[argv.index("-n") + 1])
        with mock.patch.dict("os.environ", {runner.WORKERS_ENV: ""}, clear=True):
            self.assertNotIn("-n", runner.build(["a"], True, []))

    def test_the_targets_come_before_the_forwarded_arguments(self):
        argv = runner.build(["quenching/tests/test_git.py", "quenching/tests/test_deploy.py"], True, ["-k", "x"])
        self.assertEqual(["quenching/tests/test_git.py", "quenching/tests/test_deploy.py", "-k", "x"],
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


class Forwarding(unittest.TestCase):
    def test_everything_after_the_separator_goes_to_pytest(self):
        head, extra = runner.split_forwarded(["--affected", "--", "-q", "-k", "audit"])
        self.assertEqual(["--affected"], head)
        self.assertEqual(["-q", "-k", "audit"], extra)

    def test_an_option_the_runner_does_not_know_is_an_error_not_a_target(self):
        with self.assertRaises(SystemExit):
            runner.main(["--affected", "-n", "2"])

    def test_the_base_can_come_from_the_environment(self):
        selection = runner.affected.Selection("main", ("a.py",), ("quenching/tests/test_git.py",), (), False)
        with mock.patch.dict("os.environ", {runner.BASE_ENV: "HEAD"}), \
                mock.patch.object(runner.affected, "select", return_value=selection) as select, \
                mock.patch.object(runner.subprocess, "call", return_value=0), \
                mock.patch.object(runner, "count_integration", return_value=0):
            runner.main(["--affected"])
        self.assertEqual("HEAD", select.call_args.args[1])


@unittest.skipUnless(HAS_PYTEST, "the end-to-end case runs pytest")
class EndToEnd(unittest.TestCase):
    def test_a_real_run_reports_the_deferred_layer(self):
        proc = subprocess.run(
            [sys.executable, "-m", "scripts.toolchain.test",
             "quenching/tests/test_toolchain_layers.py", "--", "-q"],
            cwd=REPO_ROOT, capture_output=True, text=True)
        self.assertEqual(0, proc.returncode, proc.stdout + proc.stderr)
        self.assertIn("target(s) given", proc.stderr)
        self.assertIn("integration:", proc.stderr)
        self.assertIn("passed", proc.stdout)


if __name__ == "__main__":
    unittest.main()
