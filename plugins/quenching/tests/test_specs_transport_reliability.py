"""S5 — transport reliability: reads retry, writes never do, stale Azure writes are refused,
and the read-only guard sits at the lowest-level runner."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.specs.backends import azure as az_mod
from quenching.specs.backends import base as base_mod
from quenching.specs.backends import github as gh_mod
from quenching.specs.backends.azure import AzureBoardsBackend
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.github import GitHubBackend

TIMEOUT_GH = subprocess.TimeoutExpired(["gh"], 30)
TIMEOUT_AZ = subprocess.TimeoutExpired(["az"], 30)


class GhRetriesOnlyReads(unittest.TestCase):
    def test_a_post_that_times_out_is_attempted_exactly_once(self):
        with mock.patch("subprocess.run", side_effect=TIMEOUT_GH) as run, \
                mock.patch.object(gh_mod.time, "sleep") as sleep:
            result = gh_mod._gh_run(os.getcwd(), "api", "-X", "POST", "repos/o/r/issues",
                                    "--input", "-", stdin="{}")
        self.assertEqual(result[0], gh_mod.GH_TIMEOUT)
        self.assertEqual(result[3], 1)
        self.assertEqual(run.call_count, 1)
        sleep.assert_not_called()

    def test_field_flags_make_a_call_a_write_even_without_a_method(self):
        self.assertFalse(gh_mod._gh_is_read(("api", "repos/o/r/issues", "-f", "title=x")))
        self.assertTrue(gh_mod._gh_is_read(("api", "repos/o/r/issues")))
        self.assertTrue(gh_mod._gh_is_read(("api", "-X", "GET", "repos/o/r/issues")))
        self.assertFalse(gh_mod._gh_is_read(("api", "-X", "DELETE", "repos/o/r/x")))
        self.assertFalse(gh_mod._gh_is_read(("issue", "edit", "1")))

    def test_a_get_still_retries(self):
        with mock.patch("subprocess.run", side_effect=TIMEOUT_GH) as run, \
                mock.patch.object(gh_mod.time, "sleep"):
            result = gh_mod._gh_run(os.getcwd(), "api", "repos/o/r/issues")
        self.assertEqual(result[3], gh_mod.GH_MAX_ATTEMPTS)
        self.assertEqual(run.call_count, gh_mod.GH_MAX_ATTEMPTS)

    def test_retry_after_is_honoured_over_the_default_backoff(self):
        failed = subprocess.CompletedProcess(
            ["gh"], 1, stdout="", stderr="gh: secondary rate limit (HTTP 403)\nRetry-After: 7\n")
        passed = subprocess.CompletedProcess(["gh"], 0, stdout="{}", stderr="")
        with mock.patch("subprocess.run", side_effect=[failed, passed]), \
                mock.patch.object(gh_mod.time, "sleep") as sleep:
            gh_mod._gh_run(os.getcwd(), "api", "repos/o/r/issues")
        sleep.assert_called_once_with(7.0)

    def test_retry_after_is_capped(self):
        self.assertEqual(base_mod.parse_retry_after("Retry-After: 99999"),
                         base_mod.RETRY_AFTER_CAP_S)
        self.assertIsNone(base_mod.parse_retry_after("nothing here"))


class GhLeanListingIsHonest(unittest.TestCase):
    def setUp(self):
        gh_mod._LISTING_SUSPECT_ANNOUNCED.clear()

    def _lean(self, open_issues):
        backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=open_issues)
        err = io.StringIO()
        with mock.patch.object(gh_mod, "_gh_run", return_value=(0, "[]", "")), \
                contextlib.redirect_stderr(err):
            rows = backend._lean_rows()
        return rows, err.getvalue()

    def test_an_empty_lean_front_with_unknown_count_warns(self):
        rows, err = self._lean(None)
        self.assertEqual(rows, [])
        self.assertIn("eventually consistent", err)

    def test_an_empty_lean_front_with_a_known_zero_count_is_quiet(self):
        rows, err = self._lean(0)
        self.assertEqual((rows, err), ([], ""))

    def test_lean_rows_are_marked_eventual(self):
        backend = GitHubBackend("owner/repo", os.getcwd(), open_issues=0)
        payload = [{"number": 3, "title": "T", "state": "OPEN", "labels": []}]
        with mock.patch.object(gh_mod, "_gh_run", return_value=(0, json.dumps(payload), "")):
            rows = backend.list_specs(lean=True)
        self.assertEqual(rows[0]["consistency"], "eventual")


class AzureTransport(unittest.TestCase):
    def test_timeout_has_a_dedicated_refusal_and_reads_retry(self):
        with mock.patch("subprocess.run", side_effect=TIMEOUT_AZ) as run, \
                mock.patch.object(az_mod.time, "sleep"):
            code, _, err = az_mod._az_run(os.getcwd(), "boards", "query")
        self.assertEqual(code, az_mod.AZ_TIMEOUT)
        self.assertEqual(run.call_count, az_mod.AZ_MAX_ATTEMPTS)
        self.assertEqual(az_mod.az_refusal("querying", code, "", err)["code"], "sp-az-timeout")

    def test_a_create_that_times_out_is_not_repeated(self):
        with mock.patch("subprocess.run", side_effect=TIMEOUT_AZ) as run, \
                mock.patch.object(az_mod.time, "sleep"):
            code, _, _ = az_mod._az_run(os.getcwd(), "boards", "work-item", "create")
        self.assertEqual(code, az_mod.AZ_TIMEOUT)
        self.assertEqual(run.call_count, 1)

    def test_read_classification(self):
        read = az_mod._az_is_read
        self.assertTrue(read(("boards", "query")))
        self.assertTrue(read(("boards", "work-item", "show")))
        self.assertTrue(read(("devops", "invoke", "--resource", "workitemsbatch",
                              "--http-method", "POST")))
        self.assertTrue(read(("rest", "--uri", "x")))
        self.assertFalse(read(("rest", "--method", "PATCH", "--uri", "x")))
        self.assertFalse(read(("boards", "work-item", "create")))
        self.assertFalse(read(("devops", "invoke", "--resource", "workitems",
                               "--http-method", "POST")))

    def _backend(self):
        return AzureBoardsBackend("https://dev.azure.com/o", "P", {"plans": "New"},
                                  os.getcwd())

    def test_wiql_at_the_ceiling_is_refused(self):
        backend = self._backend()
        with self.assertRaises(BackendRefusal) as ctx:
            backend._guard_wiql("querying", [{"id": 1}] * az_mod.AZ_WIQL_LIMIT)
        self.assertEqual(ctx.exception.err["code"], "sp-az-wiql-truncated")
        self.assertEqual(len(backend._guard_wiql("querying", [{"id": 1}])), 1)

    def test_patch_temp_file_lives_outside_the_checkout_and_is_removed(self):
        with tempfile.TemporaryDirectory() as cwd:
            backend = AzureBoardsBackend("https://dev.azure.com/o", "P", {}, cwd)
            seen = {}

            def fake_run(run_cwd, *argv, **kw):
                path = argv[argv.index("--body") + 1][1:]
                seen["path"] = path
                seen["body"] = json.load(open(path))
                return 0, "{}", ""

            with mock.patch.object(az_mod, "_az_run", side_effect=fake_run):
                backend._az_patch("x", 5, [{"op": "add", "path": "/fields/A", "value": "v"}],
                                  rev=4)
            self.assertFalse(seen["path"].startswith(cwd))
            self.assertFalse(os.path.exists(seen["path"]))
            self.assertEqual(os.listdir(cwd), [])
            self.assertEqual(seen["body"][0], {"op": "test", "path": "/rev", "value": 4})

    def test_a_stale_revision_is_refused_as_a_stale_write(self):
        backend = self._backend()
        stale = (1, "", "ERROR: TF26071: This work item has been changed by someone else")
        with mock.patch.object(az_mod, "_az_run", return_value=stale):
            with self.assertRaises(BackendRefusal) as ctx:
                backend._az_patch("updating", 9, [{"op": "add", "path": "/fields/A",
                                                   "value": "v"}], rev=3)
        self.assertEqual(ctx.exception.err["code"], "sp-az-stale-write")
        self.assertEqual(ctx.exception.err["expectedRev"], 3)

    def test_a_patch_without_a_revision_sends_no_test_op(self):
        backend = self._backend()
        bodies = []

        def fake_run(cwd, *argv, **kw):
            bodies.append(json.load(open(argv[argv.index("--body") + 1][1:])))
            return 0, "{}", ""

        with mock.patch.object(az_mod, "_az_run", side_effect=fake_run):
            backend._az_patch("linking", 9, [{"op": "add", "path": "/relations/-",
                                              "value": {}}])
        self.assertTrue(all(op["op"] != "test" for op in bodies[0]))


class ReadOnlyAtTheTransport(unittest.TestCase):
    def setUp(self):
        self._before = SpecBackend.read_only
        SpecBackend.read_only = True

    def tearDown(self):
        SpecBackend.read_only = self._before

    def test_every_gh_write_shape_is_refused_before_a_process_starts(self):
        shapes = [("api", "-X", "POST", "p"), ("api", "-X", "PATCH", "p"),
                  ("api", "-X", "DELETE", "p"), ("api", "p", "-f", "a=b"),
                  ("issue", "edit", "1", "--type", "Bug")]
        with mock.patch("subprocess.run") as run:
            for argv in shapes:
                with self.assertRaises(BackendRefusal) as ctx:
                    gh_mod._gh_run(os.getcwd(), *argv)
                self.assertEqual(ctx.exception.err["code"], "sp-read-only")
            run.assert_not_called()

    def test_gh_reads_still_pass(self):
        ok = subprocess.CompletedProcess(["gh"], 0, stdout="[]", stderr="")
        with mock.patch("subprocess.run", return_value=ok):
            self.assertEqual(gh_mod._gh_run(os.getcwd(), "api", "p")[0], 0)

    def test_private_azure_helpers_are_refused_too(self):
        backend = AzureBoardsBackend("https://dev.azure.com/o", "P", {}, os.getcwd())
        with mock.patch("subprocess.run") as run:
            with self.assertRaises(BackendRefusal) as ctx:
                backend._az_patch("x", 1, [{"op": "add", "path": "/fields/A", "value": "v"}])
            self.assertEqual(ctx.exception.err["code"], "sp-read-only")
            with self.assertRaises(BackendRefusal):
                az_mod._az_run(os.getcwd(), "boards", "work-item", "create")
            run.assert_not_called()

    def test_the_batch_read_still_passes_under_the_guard(self):
        ok = subprocess.CompletedProcess(["az"], 0, stdout="{}", stderr="")
        with mock.patch("subprocess.run", return_value=ok):
            code = az_mod._az_run(os.getcwd(), "devops", "invoke", "--resource",
                                  "workitemsbatch", "--http-method", "POST")[0]
        self.assertEqual(code, 0)

    def test_the_environment_flag_works_without_the_class_flag(self):
        SpecBackend.read_only = False
        with mock.patch.dict(os.environ, {base_mod.READ_ONLY_ENV: "1"}):
            with self.assertRaises(BackendRefusal):
                gh_mod._gh_run(os.getcwd(), "api", "-X", "POST", "p")


if __name__ == "__main__":
    unittest.main()
