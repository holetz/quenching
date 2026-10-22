"""Azure completion must preserve the GitHub route's CI, head and cleanup fences."""
from __future__ import annotations

import contextlib
import copy
import io
import json
from pathlib import Path
from types import SimpleNamespace
import unittest
from unittest import mock

import _paths  # noqa: F401
from quenching.git import azure_pull, pull


URL = "https://dev.azure.com/org/Some%20Project/_git/repo/pullrequest/226343"
HEAD = "a" * 40
PR = {"pullRequestId": 226343, "status": "active", "isDraft": False,
      "mergeStatus": "succeeded", "lastMergeSourceCommit": {"commitId": HEAD},
      "sourceRefName": "refs/heads/plan/spec", "targetRefName": "refs/heads/master"}
BUILD = {"configuration": {"id": 1, "isEnabled": True, "isBlocking": True,
                           "type": {"id": azure_pull.BUILD_POLICY,
                                    "displayName": "Repository gate"}},
         "status": "approved"}


class AzureMergeTests(unittest.TestCase):
    def run_merge(self, *, prs=None, policies=None, policy_code=0, patch_code=0,
                  url=URL, wait=0, unreadable=False):
        snapshots = iter(prs if prs is not None else [PR, PR, {**PR, "status": "completed"}])
        self.calls, self.bodies = [], []

        def az(*argv):
            self.calls.append(list(argv))
            if argv[:4] == ("repos", "pr", "policy", "list"):
                return policy_code, json.dumps([BUILD] if policies is None else policies), "denied"
            if "--http-method=PATCH" in argv:
                path = next(a.split("=", 1)[1] for a in argv if a.startswith("--in-file="))
                self.bodies.append(json.loads(Path(path).read_text(encoding="utf-8")))
                return patch_code, "{}", "policy refused"
            return 0, "not json" if unreadable else json.dumps(next(snapshots)), ""

        with mock.patch.object(azure_pull, "_az", side_effect=az), \
                mock.patch.object(pull, "_gh") as gh, \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(SimpleNamespace(action="merge", url=url, wait=wait, json=True))
        gh.assert_not_called()
        return code, json.loads(out.getvalue())

    def test_green_build_completes_with_pinned_head_and_fixed_options(self):
        code, result = self.run_merge()
        self.assertEqual(code, 0, result)
        self.assertTrue(result["ok"])
        self.assertEqual(result["provider"], "azure-boards")
        self.assertEqual(self.bodies, [{
            "status": "completed", "lastMergeSourceCommit": {"commitId": HEAD},
            "completionOptions": {"mergeStrategy": "noFastForward", "squashMerge": False,
                                  "bypassPolicy": False, "deleteSourceBranch": False,
                                  "transitionWorkItems": False}}])
        for call in self.calls:
            self.assertIn("--org=https://dev.azure.com/org", call)
        reads = [call for call in self.calls if "--http-method=GET" in call]
        self.assertEqual(len(reads), 3)
        self.assertIn("project=Some Project", reads[0])
        self.assertIn("repositoryId=repo", reads[0])
        self.assertIn("pullRequestId=226343", reads[0])
        path = next(a.split("=", 1)[1] for call in self.calls for a in call
                    if a.startswith("--in-file="))
        self.assertFalse(Path(path).exists())

    def test_already_completed_is_read_only_even_without_ci(self):
        code, result = self.run_merge(prs=[{**PR, "status": "completed"}])
        self.assertEqual(code, 0, result)
        self.assertTrue(result["alreadyMerged"])
        self.assertEqual(len(self.calls), 1)
        self.assertEqual(self.bodies, [])

    def test_legacy_visualstudio_url_uses_its_own_organization(self):
        for prefix in ("", "DefaultCollection/"):
            code, result = self.run_merge(
                url=f"https://org.visualstudio.com/{prefix}Project/_git/repo/pullrequest/226343")
            self.assertEqual(code, 0, result)
            self.assertIn("--org=https://org.visualstudio.com", self.calls[0])

    def test_missing_ci_never_means_green(self):
        review = copy.deepcopy(BUILD)
        review["configuration"]["type"]["id"] = "minimum-reviewers"
        disabled = copy.deepcopy(BUILD)
        disabled["configuration"]["isEnabled"] = False
        for policies in ([], [review], [disabled]):
            code, result = self.run_merge(policies=policies)
            self.assertEqual((code, result["reason"]), (1, "no-checks"))
            self.assertEqual(self.bodies, [])

    def test_red_pending_skipped_and_unreadable_evidence_never_complete(self):
        for status, reason in (("rejected", "failed"), ("queued", "pending"),
                               ("running", "pending"), ("notApplicable", "skipped-required"),
                               ("broken", "checks-unreadable"), (None, "checks-unreadable")):
            with self.subTest(status=status):
                code, result = self.run_merge(policies=[{**BUILD, "status": status}])
                self.assertEqual((code, result["reason"]), (1, reason))
                self.assertEqual(self.bodies, [])
        for policies in ([None], [{"configuration": None}], [{**BUILD, "context": []}]):
            code, result = self.run_merge(policies=policies)
            self.assertEqual((code, result["reason"]), (1, "checks-unreadable"))
        code, result = self.run_merge(policy_code=1)
        self.assertEqual((code, result["reason"]), (1, "checks-unreadable"))
        code, result = self.run_merge(unreadable=True)
        self.assertEqual((code, result["reason"]), (1, "merge-state"))

    def test_expired_build_and_pending_review_block_an_approved_build(self):
        code, result = self.run_merge(policies=[{**BUILD, "context": {"isExpired": True}}])
        self.assertEqual((code, result["reason"]), (1, "pending"))
        review = copy.deepcopy(BUILD)
        review["configuration"]["type"]["id"] = "minimum-reviewers"
        review["status"] = "running"
        code, result = self.run_merge(policies=[BUILD, review])
        self.assertEqual((code, result["reason"]), (1, "pending"))
        self.assertEqual(self.bodies, [])

    def test_moved_head_target_draft_conflicts_or_closed_pr_never_complete(self):
        changes = ({"lastMergeSourceCommit": {"commitId": "b" * 40}},
                   {"targetRefName": "refs/heads/other"}, {"isDraft": True},
                   {"mergeStatus": "conflicts"}, {"status": "abandoned"},
                   {"pullRequestId": 99}, {"isDraft": None})
        for change in changes:
            with self.subTest(change=change):
                code, result = self.run_merge(prs=[PR, {**PR, **change}])
                self.assertEqual((code, result["reason"]), (1, "merge-state"))
                self.assertEqual(self.bodies, [])

    def test_refused_or_asynchronous_patch_is_not_success(self):
        code, result = self.run_merge(prs=[PR, PR, PR], patch_code=1)
        self.assertEqual((code, result["reason"]), (1, "merge-refused"))
        for change, reason in (({"mergeStatus": "queued"}, "pending"),
                               ({"mergeStatus": "succeeded"}, "pending"),
                               ({"mergeStatus": "rejectedByPolicy"}, "merge-refused"),
                               ({"lastMergeSourceCommit": {"commitId": "b" * 40}}, "merge-state"),
                               ({"pullRequestId": 99}, "merge-state")):
            code, result = self.run_merge(prs=[PR, PR, {**PR, **change}])
            self.assertEqual((code, result["reason"]), (1, reason))
            self.assertFalse(result["ok"])

    def test_pending_policies_are_polled_before_writing(self):
        answers = iter([("pending", ["gate"], ""), ("green", [], "")])
        with mock.patch.object(azure_pull, "_checks", side_effect=lambda *args: next(answers)), \
                mock.patch.object(azure_pull.time, "sleep") as sleep, \
                contextlib.redirect_stderr(io.StringIO()):
            code, result = self.run_merge(wait=60)
        self.assertEqual(code, 0, result)
        sleep.assert_called_once_with(azure_pull.POLL_S)

    def test_asynchronous_completion_is_polled_until_confirmed(self):
        with mock.patch.object(azure_pull.time, "sleep") as sleep:
            code, result = self.run_merge(wait=60, prs=[PR, PR,
                {**PR, "mergeStatus": "queued"}, {**PR, "status": "completed"}])
        self.assertEqual(code, 0, result)
        sleep.assert_called_once_with(azure_pull.POLL_S)
        self.assertEqual(len(self.bodies), 1)

    def test_malformed_urls_and_invalid_wait_do_not_reach_az(self):
        for url, wait in ((URL + "\n", 0), (URL + "?x=1", 0), (URL + " --bypass-policy", 0),
                          (URL.replace("226343", "0"), 0), (URL, -1), (URL, 600)):
            code, _ = self.run_merge(url=url, wait=wait)
            self.assertEqual(code, 2)
            self.assertEqual(self.calls, [])


if __name__ == "__main__":
    unittest.main()
