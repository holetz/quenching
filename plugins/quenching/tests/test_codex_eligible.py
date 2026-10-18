"""Executable proofs for `cq codex eligible` — the quota is always a stub, never the real Codex."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.codex import main
from quenching.codex.config import DEFAULTS
from quenching.codex.eligible import eligibility, reserved, run_eligible, task_tokens


def settings(**executor) -> dict:
    return {**DEFAULTS, "maxUsedPercent": dict(DEFAULTS["maxUsedPercent"]),
            "executor": {**DEFAULTS["executor"], **executor}}


def task(files=("src/a.py",), verify=None, state=" ") -> dict:
    return {"id": "2.1", "files": list(files), "verify": verify, "checked": state == "x",
            "blocked": state == "!"}


class Quota:
    def __init__(self, state="available", reason="primary 10% < 70%"):
        self.state, self.reason, self.seen = state, reason, []

    def __call__(self, settings: dict) -> dict:
        self.seen.append(settings)
        return {"state": self.state, "reason": self.reason}


class EligibilityTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = self.tmp.name
        os.makedirs(os.path.join(self.root, "src"))
        self.write("src/a.py", 400)

    def tearDown(self):
        self.tmp.cleanup()

    def write(self, rel: str, size: int) -> None:
        with open(os.path.join(self.root, rel), "w", encoding="utf-8") as handle:
            handle.write("x" * size)

    def test_small_task_takes_the_small_model_and_effort(self):
        quota = Quota()
        payload, code = eligibility(task(), settings(modelSmall="small-m"), self.root, quota)
        self.assertEqual(code, 0)
        self.assertEqual((payload["class"], payload["model"]), ("small", "small-m"))
        self.assertEqual(payload["tokens"], 100)
        self.assertEqual(payload["reasoningEffort"], "medium")
        self.assertNotIn("sandbox", payload)

    def test_large_task_with_verify_is_verified(self):
        self.write("src/a.py", 4000)
        payload, code = eligibility(task(verify="make test"),
                                    settings(maxTaskTokens=100, modelVerified="v-m"),
                                    self.root, Quota())
        self.assertEqual(code, 0)
        self.assertEqual((payload["class"], payload["model"]), ("verified", "v-m"))

    def test_verified_task_with_a_protected_oracle_takes_the_small_tier(self):
        self.write("src/a.py", 4000)
        row = {"oracleProtected": True, "smallTierEligible": True}
        payload, code = eligibility(task(verify="make test"), settings(maxTaskTokens=100),
                                    self.root, Quota(), row)
        self.assertEqual(code, 0)
        self.assertEqual((payload["class"], payload["model"]), ("verified", "gpt-6-luna"))

    def test_verified_task_without_the_small_tier_keeps_sol(self):
        self.write("src/a.py", 4000)
        for row in (None, {"oracleProtected": False, "smallTierEligible": True},
                    {"oracleProtected": True, "smallTierEligible": False}):
            payload, code = eligibility(task(verify="make test"), settings(maxTaskTokens=100),
                                        self.root, Quota(), row)
            self.assertEqual((code, payload["model"]), (0, "gpt-6.1-sol"), row)

    def test_large_task_without_verify_stays_with_claude(self):
        self.write("src/a.py", 4000)
        quota = Quota()
        payload, code = eligibility(task(), settings(maxTaskTokens=100), self.root, quota)
        self.assertEqual(code, 1)
        self.assertIn("no verify:", payload["reason"])
        self.assertEqual(quota.seen, [], "the quota is not asked for an ineligible task")

    def test_new_file_costs_nothing_and_annotation_is_stripped(self):
        self.assertEqual(task_tokens(self.root, ["src/new.py (new)"]), 0)
        payload, code = eligibility(task(files=["src/new.py (new)"]), settings(), self.root,
                                    Quota())
        self.assertEqual(code, 0)

    def test_docs_and_knowledge_are_never_codex(self):
        for path in ("docs/standards/architecture/codex-pillar.md", "/docs/index.md", "knowledge/a.md"):
            payload, code = eligibility(task(files=["src/a.py", path]), settings(), self.root,
                                        Quota())
            self.assertEqual(code, 1, path)
            self.assertIn("docs/ or knowledge/", payload["reason"])

    def test_no_files_disabled_or_closed_task_is_not_eligible(self):
        self.assertEqual(eligibility(task(files=[]), settings(), self.root, Quota())[1], 1)
        self.assertEqual(eligibility(task(), settings(enabled=False), self.root, Quota())[1], 1)
        self.assertEqual(eligibility(task(state="x"), settings(), self.root, Quota())[1], 1)

    def test_quota_is_judged_under_the_reserve_and_ignores_cross_review_off(self):
        quota = Quota(state="unavailable", reason="over the ceiling")
        base = {**settings(reservePercent=10), "crossReview": "off"}
        payload, code = eligibility(task(), base, self.root, quota)
        self.assertEqual(code, 1)
        self.assertIn("10% reserve", payload["reason"])
        self.assertEqual(quota.seen[0]["crossReview"], "auto")
        self.assertEqual(quota.seen[0]["maxUsedPercent"], {"primary": 70, "secondary": 80})

    def test_reserve_never_goes_below_zero(self):
        self.assertEqual(reserved(settings(reservePercent=100))["maxUsedPercent"],
                         {"primary": 0, "secondary": 0})


class FakeBackend:
    def __init__(self, info):
        self.info = info

    def read_spec(self, spec_id):
        if self.info is None:
            return None, {"code": "sp-not-found", "message": f"no spec {spec_id}"}
        return self.info, {}


class CliTest(unittest.TestCase):
    def run_cli(self, info, *argv):
        out = io.StringIO()
        with mock.patch("quenching.codex.eligible.open_backend",
                        return_value=(FakeBackend(info), {})), \
                mock.patch("quenching.codex.eligible.probe", Quota()), \
                tempfile.TemporaryDirectory() as root, contextlib.redirect_stdout(out):
            code = main(["eligible", "--root", root, "--json", *argv])
        return code, json.loads(out.getvalue())

    def test_eligible_task_exits_0(self):
        code, payload = self.run_cli({"tasks": [task(files=["src/new.py (new)"])]},
                                     "--spec", "7", "--task", "2.1")
        self.assertEqual(code, 0)
        self.assertEqual(payload["spec"], "7")
        self.assertEqual(payload["class"], "small")

    def test_missing_task_and_spec_refuse(self):
        code, payload = self.run_cli({"tasks": []}, "--spec", "7", "--task", "2.1")
        self.assertEqual((code, payload["code"]), (2, "codex-task-missing"))
        code, payload = self.run_cli(None, "--spec", "7", "--task", "2.1")
        self.assertEqual((code, payload["code"]), (2, "codex-spec-missing"))

    def test_run_eligible_reports_an_unopenable_store(self):
        with mock.patch("quenching.codex.eligible.open_backend",
                        return_value=(None, {"message": "no store"})):
            payload, code = run_eligible("/nowhere", settings(), "7", "2.1", Quota())
        self.assertEqual((code, payload["code"]), (2, "codex-specs-unreadable"))


if __name__ == "__main__":
    unittest.main()
