"""A merge verb that loses a race against a concurrent merge reports the PR as already merged."""
from __future__ import annotations

import contextlib
import io
import json
from types import SimpleNamespace
import unittest
from unittest import mock

import _paths  # noqa: F401
from quenching.git import azure_pull, pull
from test_git_azure_merge import BUILD, HEAD, PR, URL as AZURE_URL

GH_URL = "https://github.com/o/r/pull/7"
GREEN = [{"name": "gate", "bucket": "pass"}]


def run_github(*, view, merge_code=0, merged_after):
    """`view` answers `headRefOid,mergeStateStatus` reads; `merged_after` answers `state` reads."""
    states = iter(merged_after)
    views = iter(view)

    def gh(*argv):
        if argv[:2] == ("pr", "merge"):
            return merge_code, "", "Pull request is already merged"
        if "state" in argv:
            return 0, json.dumps({"state": next(states)}), ""
        return 0, json.dumps(next(views)), ""

    with mock.patch.object(pull, "_gh", side_effect=gh), \
            mock.patch.object(pull, "_checks", return_value=("green", GREEN, "")), \
            contextlib.redirect_stdout(io.StringIO()) as out:
        code = pull.cmd_pr(SimpleNamespace(action="merge", url=GH_URL, wait=0, json=True))
    return code, json.loads(out.getvalue())


CLEAN = {"headRefOid": "abc", "mergeStateStatus": "CLEAN"}


class GithubRaceTests(unittest.TestCase):
    def test_merge_refused_after_a_concurrent_merge_is_already_merged(self):
        code, result = run_github(view=[CLEAN, CLEAN], merge_code=1,
                                  merged_after=["OPEN", "MERGED"])
        self.assertEqual(code, 0, result)
        self.assertTrue(result["ok"] and result["alreadyMerged"])

    def test_merge_state_after_a_concurrent_merge_is_already_merged(self):
        code, result = run_github(view=[CLEAN, {"headRefOid": "abc", "mergeStateStatus": "UNKNOWN"}],
                                  merged_after=["OPEN", "MERGED"])
        self.assertEqual(code, 0, result)
        self.assertTrue(result["ok"] and result["alreadyMerged"])

    def test_an_open_pull_request_is_still_refused(self):
        code, result = run_github(view=[CLEAN, CLEAN], merge_code=1, merged_after=["OPEN", "OPEN"])
        self.assertEqual((code, result["ok"], result["reason"]), (1, False, "merge-refused"))
        code, result = run_github(view=[CLEAN, {"headRefOid": "abc", "mergeStateStatus": "BEHIND"}],
                                  merged_after=["OPEN", "OPEN"])
        self.assertEqual((code, result["reason"]), (1, "merge-state"))


class AzureRaceTests(unittest.TestCase):
    def run_merge(self, final):
        reads = iter([PR, PR, final])

        def az(*argv):
            if argv[:4] == ("repos", "pr", "policy", "list"):
                return 0, json.dumps([BUILD]), ""
            if "--http-method=PATCH" in argv:
                return 1, "", "already completed"
            return 0, json.dumps(next(reads)), ""

        with mock.patch.object(azure_pull, "_az", side_effect=az), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(SimpleNamespace(action="merge", url=AZURE_URL, wait=0, json=True))
        return code, json.loads(out.getvalue())

    def test_patch_refused_after_a_concurrent_completion_is_already_merged(self):
        code, result = self.run_merge({**PR, "status": "completed"})
        self.assertEqual(code, 0, result)
        self.assertTrue(result["ok"] and result["alreadyMerged"])

    def test_patch_refused_on_an_active_pull_request_is_still_refused(self):
        code, result = self.run_merge(PR)
        self.assertEqual((code, result["reason"]), (1, "merge-refused"))


if __name__ == "__main__":
    unittest.main()
