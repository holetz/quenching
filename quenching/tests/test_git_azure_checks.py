"""`cq git pr checks` reads the Azure web URL `pr create` prints, in the GitHub vocabulary."""
from __future__ import annotations

import contextlib
import io
import json
from types import SimpleNamespace
import unittest
from unittest import mock

import _paths  # noqa: F401
from quenching.git import azure_pull, pull
from quenching.git.pr import normalize_azure_pull_request


URL = "https://dev.azure.com/org/Some%20Project/_git/repo/pullrequest/226343"


def _policy(status: str, *, build: bool = True, blocking: bool = True, expired: bool = False) -> dict:
    return {"configuration": {"id": 1, "isEnabled": True, "isBlocking": blocking,
                              "type": {"id": azure_pull.BUILD_POLICY if build else "other",
                                       "displayName": "Repository gate" if build else "Reviewers"}},
            "status": status, "context": {"isExpired": expired}}


class AzurePrChecks(unittest.TestCase):
    def read(self, url: str = URL, *, policies=None, code: int = 0) -> tuple[int, dict]:
        self.calls = []

        def az(*argv):
            self.calls.append(list(argv))
            return code, json.dumps(policies if policies is not None else []), "az: denied"

        with mock.patch.object(azure_pull, "_az", side_effect=az), \
                mock.patch.object(pull, "_gh") as gh, \
                contextlib.redirect_stdout(io.StringIO()) as out:
            rc = pull.cmd_pr(SimpleNamespace(action="checks", url=url, json=True))
        gh.assert_not_called()
        return rc, json.loads(out.getvalue())

    def test_each_azure_state_maps_to_the_verb_vocabulary(self):
        for policies, state in (([_policy("approved")], "green"),
                                ([_policy("rejected")], "red"),
                                ([_policy("notApplicable")], "skipped"),
                                ([_policy("running")], "pending"),
                                ([_policy("approved", expired=True)], "pending"),
                                ([_policy("approved", build=False)], "none")):
            rc, payload = self.read(policies=policies)
            self.assertEqual(rc, 0, payload)
            self.assertEqual((payload["provider"], payload["state"]), ("azure", state), policies)
        self.assertEqual(payload["reason"], "no-policy")
        self.assertIn("--org=https://dev.azure.com/org", self.calls[0])
        self.assertIn("--id=226343", self.calls[0])

    def test_unreadable_policies_are_an_error_with_the_az_message(self):
        rc, payload = self.read(code=1)
        self.assertEqual(rc, 0, payload)
        self.assertEqual((payload["state"], payload["reason"]), ("error", "unreadable"))
        self.assertIn("denied", payload["message"])

    def test_the_url_pr_create_prints_is_accepted(self):
        web = normalize_azure_pull_request({
            "pullRequestId": 233839,
            "url": "https://dev.azure.com/org/p/_apis/git/repositories/r/pullRequests/233839",
            "repository": {"webUrl": "https://dev.azure.com/org/TI/_git/riscos-plataforma"}})["webUrl"]
        rc, payload = self.read(web, policies=[_policy("approved")])
        self.assertEqual((rc, payload["state"], payload["url"]), (0, "green", web))
        self.assertIn("--id=233839", self.calls[0])

    def test_legacy_visualstudio_url_reads_its_own_organization(self):
        for prefix in ("", "DefaultCollection/"):
            rc, payload = self.read(f"https://org.visualstudio.com/{prefix}P/_git/r/pullrequest/7",
                                    policies=[_policy("approved")])
            self.assertEqual((rc, payload["state"]), (0, "green"))
            self.assertIn("--org=https://org.visualstudio.com", self.calls[0])

    def test_a_malformed_url_is_refused_before_az(self):
        for url in (f"{URL} --x", URL.replace("pullrequest", "pullrequests"),
                    URL.replace("/226343", "/0")):
            with mock.patch.object(azure_pull, "_az") as az, \
                    contextlib.redirect_stdout(io.StringIO()) as out:
                rc = pull.cmd_pr(SimpleNamespace(action="checks", url=url, json=True))
            az.assert_not_called()
            self.assertEqual(rc, 2, url)
            self.assertEqual(json.loads(out.getvalue())["code"], "git-pr-url-invalid")


if __name__ == "__main__":
    unittest.main()
