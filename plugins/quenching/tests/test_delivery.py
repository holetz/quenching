"""Executable proofs for the delivery probe, inventory and C3 findings."""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.delivery.doctor import doctor


HERE = pathlib.Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden" / "delivery-results.json"


class DeliveryResults(unittest.TestCase):
    def _run(self, files: dict[str, str]) -> tuple[dict, int]:
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            payload, error, code = doctor(str(root))
            self.assertEqual({}, error)
            assert payload is not None
            return payload, code

    def test_absent_is_explicit_not_applicable(self):
        payload, code = self._run({})
        self.assertEqual(0, code)
        self.assertEqual("not-applicable", payload["applicability"]["state"])
        self.assertIsNone(payload["inventory"])
        self.assertEqual([], payload["findings"])

    def test_config_without_delivery_namespace_is_not_applicable(self):
        payload, code = self._run({".claude/quenching.json": "{}\n"})
        self.assertEqual(0, code)
        self.assertEqual("not-applicable", payload["applicability"]["state"])
        self.assertIsNone(payload["inventory"])
        self.assertEqual([], payload["findings"])

    def test_conformant_workflow_is_stable_and_read_only(self):
        payload, code = self._run({
            ".github/workflows/ci.yml": (
                "name: CI\non: [push, pull_request]\njobs:\n"
                "  test:\n    runs-on: ubuntu-latest\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "        with:\n          python-version: '3.11'\n"
                "      - run: python -m unittest\n"
            ),
        })
        self.assertEqual(0, code)
        self.assertTrue(payload["ok"])
        self.assertEqual([".github/workflows/ci.yml"],
                         [item["path"] for item in payload["inventory"]["workflows"]])
        self.assertEqual([], payload["findings"])

    def test_structural_findings_cover_pipeline_reachability_and_provenance(self):
        payload, code = self._run({
            ".github/workflows/broken.yml": (
                "name: Broken\non: push\njobs:\n"
                "  test:\n    needs: missing\n    steps:\n      - run: pytest\n"
                "  py310:\n    steps:\n      - uses: actions/checkout@v4\n"
                "        - uses: actions/setup-python@v5\n"
                "          python-version: '3.10'\n"
                "  py311:\n    steps:\n      - uses: actions/checkout@v4\n"
                "        - uses: actions/setup-python@v5\n"
                "          python-version: '3.11'\n"
                "  release:\n    needs: missing-release\n    steps:\n      - run: echo pending\n"
            ),
        })
        self.assertEqual(1, code)
        codes = {item["code"] for item in payload["findings"]}
        self.assertTrue({
            "delivery-stage-unreachable",
            "delivery-checkout-missing",
            "delivery-setup-missing",
            "delivery-runtime-drift",
            "delivery-release-unreachable",
        } <= codes)
        self.assertTrue(all(item["band"] == "Structural"
                            for item in payload["findings"]))

    def test_judgement_findings_preserve_owner_boundaries(self):
        payload, code = self._run({
            ".github/workflows/release.yml": (
                "name: Release\non: push\npermissions:\n  contents: write\njobs:\n"
                "  publish:\n    environment: production\n    steps:\n"
                "      - uses: actions/checkout@v4\n"
                "      - uses: actions/setup-python@v5\n"
                "      - run: python -m build && twine upload dist/*\n"
            ),
        })
        self.assertEqual(1, code)
        codes = {item["code"] for item in payload["findings"]}
        self.assertEqual({"delivery-environment-policy", "delivery-publish-scope",
                          "delivery-permission-policy"}, codes)
        self.assertTrue(all(item["band"] == "Judgement"
                            for item in payload["findings"]))

    def test_second_provider_equivalent_target_uses_gitlab_shape(self):
        payload, code = self._run({
            ".gitlab-ci.yml": (
                "workflow:\n  rules:\n    - if: $CI_COMMIT_BRANCH\n"
                "stages:\n  - build\n  - release\n"
                "build:\n  stage: build\n  image: python:3.12\n  script:\n"
                "    - python -m build\n"
                "release:\n  stage: release\n  needs: [build]\n"
                "  image: python:3.12\n  script:\n    - echo complete\n"
            ),
        })
        self.assertEqual(0, code)
        workflow = payload["inventory"]["workflows"][0]
        self.assertEqual("gitlab", workflow["provider"])
        self.assertEqual(["build", "release"], workflow["jobs"])
        self.assertEqual(["build", "release"], workflow["stages"])
        self.assertEqual(["python:3.12", "python:3.12"],
                         [runtime for job in workflow["jobDetails"]
                          for runtime in job["runtimes"]])
        self.assertEqual([], payload["findings"])

    def test_unmeasured_provider_is_not_reported_as_conformant(self):
        payload, code = self._run({
            ".claude/quenching.json": '{"delivery": {"provider": "jenkins"}}\n',
        })
        self.assertEqual(1, code)
        self.assertEqual("applicable", payload["applicability"]["state"])
        self.assertEqual([], payload["inventory"]["workflows"])
        self.assertEqual("delivery-provider-policy", payload["findings"][0]["code"])


class FrozenDeliveryResults(unittest.TestCase):
    def test_golden_declares_all_result_classes(self):
        payload = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual({"absent", "conformant", "mechanical", "structural",
                          "judgement", "not-measured"}, set(payload))
        self.assertEqual([], payload["mechanical"]["codes"])
        self.assertEqual({"delivery-stage-unreachable", "delivery-checkout-missing",
                          "delivery-setup-missing", "delivery-runtime-drift",
                          "delivery-release-unreachable"},
                         set(payload["structural"]["codes"]))
        self.assertEqual({"delivery-provider-policy", "delivery-environment-policy",
                          "delivery-publish-scope", "delivery-permission-policy"},
                         set(payload["judgement"]["codes"]))


if __name__ == "__main__":
    unittest.main()
