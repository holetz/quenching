"""`shared.ci.enforce` — whether the merge demands green CI, and what stands in when it does not.

The key is a project key read raw from the repository file. A red, skipped-required or unreadable
check refuses under every value; a relaxed value accepts a PR with no check (and, under `off`, one
with checks pending) only with `--gate-exit 0`.
"""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from types import SimpleNamespace
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common.config import USER_CONFIG_ENV
from quenching.config import ci
from quenching.config.effective import effective
from quenching.config.schema import REGISTRY, validate
from quenching.git import azure_pull, pull
from quenching.security.probe import ci_enforcement

GH_URL = "https://github.com/o/r/pull/42"
AZ_URL = "https://dev.azure.com/org/Project/_git/repo/pullrequest/7"
HEAD = "a" * 40
AZ_PR = {"pullRequestId": 7, "status": "active", "isDraft": False, "mergeStatus": "succeeded",
         "lastMergeSourceCommit": {"commitId": HEAD}, "sourceRefName": "refs/heads/plan/x",
         "targetRefName": "refs/heads/main"}
RED_ENDS = ("red", "skipped", "error")


class Repo(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name, "repo")
        (self.repo / ".agents").mkdir(parents=True)
        self.user = pathlib.Path(tmp.name, "user.json")
        patch = mock.patch.dict(os.environ, {USER_CONFIG_ENV: str(self.user)})
        patch.start()
        self.addCleanup(patch.stop)
        self.cwd = os.getcwd()
        os.chdir(self.repo)
        self.addCleanup(os.chdir, self.cwd)

    def declare(self, enforce, layer="repo"):
        doc = json.dumps({"shared": {"ci": {"enforce": enforce}}})
        path = {"repo": self.repo / ".agents" / "quenching.json",
                "local": self.repo / ".agents" / "quenching.local.json", "user": self.user}[layer]
        path.write_text(doc, encoding="utf-8")


class TheJudgement(unittest.TestCase):
    def test_required_demands_every_check_green(self):
        self.assertEqual((True, None), ci.judge("required", "green", None))
        self.assertEqual((False, "no-checks"), ci.judge("required", "none", 0))
        self.assertEqual((False, "pending"), ci.judge("required", "pending", 0))

    def test_when_present_accepts_only_the_absence_of_checks_and_only_with_the_gate(self):
        self.assertEqual((False, "gate-proof-required"), ci.judge("when-present", "none", None))
        self.assertEqual((False, "gate-proof-required"), ci.judge("when-present", "none", 1))
        self.assertEqual((True, None), ci.judge("when-present", "none", 0))
        self.assertEqual((False, "pending"), ci.judge("when-present", "pending", 0))

    def test_off_also_accepts_pending_with_the_gate(self):
        self.assertEqual((True, None), ci.judge("off", "pending", 0))
        self.assertEqual((False, "gate-proof-required"), ci.judge("off", "pending", None))

    def test_a_red_never_passes_under_any_value(self):
        for mode in ci.ENFORCE:
            for state in ("red", "failed", "skipped", "error", "checks-unreadable"):
                self.assertEqual((False, None), ci.judge(mode, state, 0), (mode, state))


class TheProjectLayerAlone(Repo):
    def test_default_is_required_and_a_project_value_is_read(self):
        self.assertEqual(("required", []), ci.read(str(self.repo)))
        self.declare("when-present")
        self.assertEqual(("when-present", []), ci.read(str(self.repo)))

    def test_a_bad_value_falls_back_to_required_and_is_named(self):
        self.declare("sometimes")
        value, warnings = ci.read(str(self.repo))
        self.assertEqual("required", value)
        self.assertIn("shared.ci.enforce", warnings[0])

    def test_the_local_and_user_layers_never_relax_it(self):
        self.declare("off", layer="local")
        self.declare("off", layer="user")
        self.assertEqual("required", ci.read(str(self.repo))[0])
        (self.repo / ".agents" / "quenching.json").write_text("{}", encoding="utf-8")
        result = ci_enforcement(self.repo)
        self.assertEqual(("present", ["local", "user"]),
                         (result.state, result.details["ignoredLayers"]))

    def test_the_effective_view_ignores_the_user_layer_and_names_the_project_one(self):
        self.declare("off", layer="user")
        rows = {r["key"]: r for r in effective(str(self.repo))["values"]}
        self.assertEqual(("required", "default"),
                         (rows["shared.ci.enforce"]["value"], rows["shared.ci.enforce"]["source"]))
        self.declare("off")
        rows = {r["key"]: r for r in effective(str(self.repo))["values"]}
        self.assertEqual(("off", "repository"),
                         (rows["shared.ci.enforce"]["value"], rows["shared.ci.enforce"]["source"]))

    def test_the_security_status_reports_a_relaxed_project(self):
        self.declare("off")
        self.assertEqual("relaxed", ci_enforcement(self.repo).state)

    def test_the_registry_holds_it_as_a_project_enum(self):
        entry = REGISTRY["shared.ci.enforce"]
        self.assertEqual(("project", "required"), (entry["scope"], entry["default"]))
        self.assertIsNone(validate("shared.ci.enforce", "when-present")[1])
        self.assertIsNotNone(validate("shared.ci.enforce", "never")[1])


class TheGitHubMerge(Repo):
    def merge(self, state, **flags):
        checks = [{"name": "gate", "bucket": "pass"}] if state == "green" else []
        args = SimpleNamespace(action="merge", url=GH_URL, wait=0, json=True, **flags)
        with mock.patch.object(pull, "_checks", return_value=(state, checks, "")), \
                mock.patch.object(pull, "_is_merged", return_value=False), \
                mock.patch.object(pull, "_view", return_value=("abc", "CLEAN")), \
                mock.patch.object(pull, "_gh", return_value=(0, "", "")) as gh, \
                mock.patch.object(pull, "sync_store", return_value={"ok": True}), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(args)
        merged = any(call.args[:2] == ("pr", "merge") for call in gh.call_args_list)
        return code, json.loads(out.getvalue()), merged

    def test_required_refuses_no_checks_even_with_the_gate_and_the_old_flag(self):
        code, result, merged = self.merge("none", gate_exit=0, allow_no_checks=True)
        self.assertEqual((1, "no-checks", False), (code, result["reason"], merged))
        self.assertIn("shared.ci.enforce", result["message"])

    def test_when_present_merges_no_checks_only_with_the_gate(self):
        self.declare("when-present")
        code, result, merged = self.merge("none")
        self.assertEqual((1, "gate-proof-required", False), (code, result["reason"], merged))
        code, result, merged = self.merge("none", gate_exit=1)
        self.assertEqual((1, False), (code, merged))
        code, result, merged = self.merge("none", gate_exit=0)
        self.assertEqual((0, True), (code, merged))
        self.assertEqual({"enforce": "when-present", "checks": "none", "gateExit": 0},
                         result["ciRelaxed"])

    def test_when_present_still_waits_for_pending_checks(self):
        self.declare("when-present")
        code, result, merged = self.merge("pending", gate_exit=0)
        self.assertEqual((1, "pending", False), (code, result["reason"], merged))

    def test_off_merges_pending_with_the_gate(self):
        self.declare("off")
        code, _result, merged = self.merge("pending", gate_exit=0)
        self.assertEqual((0, True), (code, merged))

    def test_a_red_check_never_merges_under_any_value(self):
        for mode in ci.ENFORCE:
            self.declare(mode)
            for state in RED_ENDS:
                code, result, merged = self.merge(state, gate_exit=0)
                self.assertEqual((1, False), (code, merged), (mode, state))

    def test_a_green_pr_merges_without_any_gate_proof(self):
        for mode in ci.ENFORCE:
            self.declare(mode)
            code, result, merged = self.merge("green")
            self.assertEqual((0, True), (code, merged), mode)
            self.assertNotIn("ciRelaxed", result)


class TheAzureMerge(Repo):
    def merge(self, policies, **flags):
        snapshots = iter([AZ_PR, AZ_PR, {**AZ_PR, "status": "completed"}])
        build = {"configuration": {"id": 1, "isEnabled": True, "isBlocking": True,
                                   "type": {"id": azure_pull.BUILD_POLICY, "displayName": "gate"}}}
        bodies = []

        def az(*argv):
            if argv[:4] == ("repos", "pr", "policy", "list"):
                return 0, json.dumps([{**build, "status": s} for s in policies]), ""
            if argv[:2] == ("rest", "--method=patch"):
                bodies.append(argv)
                return 0, "{}", ""
            return 0, json.dumps(next(snapshots)), ""

        args = SimpleNamespace(action="merge", url=AZ_URL, wait=0, json=True, **flags)
        with mock.patch.object(azure_pull, "_az", side_effect=az), \
                mock.patch.object(azure_pull, "sync_store", return_value={"ok": True}), \
                mock.patch.object(pull, "sync_store", return_value={"ok": True}), \
                contextlib.redirect_stdout(io.StringIO()) as out:
            code = pull.cmd_pr(args)
        return code, json.loads(out.getvalue()), bool(bodies)

    def test_no_build_policy_needs_a_relaxed_key_and_the_gate(self):
        code, result, completed = self.merge([], gate_exit=0, allow_no_checks=True)
        self.assertEqual((1, "no-checks", False), (code, result["reason"], completed))
        self.declare("when-present")
        code, result, completed = self.merge([])
        self.assertEqual((1, "gate-proof-required", False), (code, result["reason"], completed))
        code, result, completed = self.merge([], gate_exit=0)
        self.assertEqual((0, True), (code, completed))
        self.assertTrue(result["noChecksAccepted"])

    def test_a_rejected_policy_never_completes_under_any_value(self):
        for mode in ci.ENFORCE:
            self.declare(mode)
            code, result, completed = self.merge(["rejected"], gate_exit=0)
            self.assertEqual((1, "failed", False), (code, result["reason"], completed), mode)

    def test_a_running_policy_completes_only_under_off(self):
        self.declare("when-present")
        code, result, completed = self.merge(["running"], gate_exit=0)
        self.assertEqual((1, "pending", False), (code, result["reason"], completed))
        self.declare("off")
        code, _result, completed = self.merge(["running"], gate_exit=0)
        self.assertEqual((0, True), (code, completed))


if __name__ == "__main__":
    unittest.main()
