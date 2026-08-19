"""Golden contracts for provider selection and refusal.

The fixtures are intentionally small: the durable output is the provider/refusal payload, not a
snapshot of a local workspace that no longer exists.
"""
from __future__ import annotations

import json
import pathlib
import unittest

import capture_golden as cg


class ProviderGoldenContract(unittest.TestCase):
    def test_every_provider_case_matches_its_frozen_payload(self):
        for result in cg.capture_all():
            with self.subTest(fixture=result["fixture"]):
                expected = json.loads(
                    (cg.FIXTURE_DIR / result["fixture"]).read_text(encoding="utf-8"))
                self.assertEqual(json.loads(result["stdout"]), expected)
                self.assertEqual(result["stderr"], "")
                self.assertEqual(result["exit"], 0 if "config" in result["fixture"]
                                 else 2)

    def test_capture_cases_cover_both_providers_and_both_refusals(self):
        results = cg.capture_all()
        fixtures = {r["fixture"] for r in results}
        self.assertEqual(fixtures, set(cg.CASES[name]["fixture"] for name in cg.CASES))
        self.assertEqual(
            {json.loads(r["stdout"]).get("backend") for r in results
             if "config" in r["fixture"]},
            {"github", "azure-boards"},
        )
        self.assertEqual(
            {json.loads(r["stdout"]).get("code") for r in results
             if "refusal" in r["fixture"]},
            {"sp-provider-unknown", "sp-backend-removed"},
        )


if __name__ == "__main__":
    unittest.main()
