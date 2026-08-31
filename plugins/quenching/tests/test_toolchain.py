"""Executable proofs for the toolchain probe, inventory and C1 finding vocabulary."""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.toolchain.doctor import doctor


HERE = pathlib.Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden" / "toolchain-results.json"


class ToolchainResults(unittest.TestCase):
    def _run(self, files: dict[str, str]) -> tuple[dict, int]:
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            for name, content in files.items():
                path = root / name
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(content, encoding="utf-8")
            payload, err, code = doctor(str(root))
            self.assertEqual({}, err)
            assert payload is not None
            return payload, code

    def test_absent_is_explicit_not_applicable(self):
        payload, code = self._run({})
        self.assertEqual(0, code)
        self.assertEqual("not-applicable", payload["applicability"]["state"])
        self.assertIsNone(payload["inventory"])
        self.assertEqual([], payload["findings"])

    def test_conformant_inventory_is_stable_and_read_only(self):
        payload, code = self._run({
            "pyproject.toml": (
                "[project]\nname = 'demo'\nversion = '1.0'\nrequires-python = '>=3.11'\n"
                "[build-system]\nbuild-backend = 'setuptools.build_meta'\n"
                "[tool.ruff]\nline-length = 88\n"),
            "uv.lock": "version = 1\n[[package]]\nname = 'demo'\nversion = '1.0'\n",
            ".python-version": "3.11\n",
        })
        self.assertEqual(0, code)
        self.assertTrue(payload["ok"])
        self.assertEqual(["pyproject.toml"],
                         [item["path"] for item in payload["inventory"]["manifests"]])
        self.assertEqual(["uv.lock"],
                         [item["path"] for item in payload["inventory"]["locks"]])
        self.assertEqual([".python-version"],
                         [item["path"] for item in payload["inventory"]["languagePins"]])
        self.assertEqual([], payload["findings"])

    def test_mechanical_results_cover_lock_duplicate_and_generated_drift(self):
        payload, code = self._run({
            "pyproject.toml": (
                "# quenching-arbiters-sha256 " + "0" * 64 + "\n"
                "# quenching-arbiters-data {\"artifact\":\"pyproject.toml\",\"entries\":[]}\n"
                "[project]\nname = 'demo'\n[tool.uv]\npackage = false\n"
                "[tool.prettier]\nsemi = false\n"),
            "package.json": '{"name":"demo","prettier":{"semi":true}}\n',
            "package-lock.json": '{\n',
            "uv.lock": "version = 1\n",
        })
        self.assertEqual(1, code)
        self.assertEqual({"tc-lock-stale", "tc-config-duplicate", "tc-generated-stale"},
                         {item["code"] for item in payload["findings"]})
        self.assertTrue(all(item["band"] == "Mechanical" for item in payload["findings"]))

    def test_structural_results_cover_runtime_pin_backend_and_arbiter(self):
        payload, code = self._run({
            "pyproject.toml": (
                "[project]\nname = 'demo'\nrequires-python = '>=3.11'\n"
                "[dependency-groups]\ndev = ['ruff>=1.0']\n"
                "[tool.pytest]\naddopts = ''\n"),
            ".python-version": "3.10\n",
        })
        self.assertEqual(1, code)
        codes = {item["code"] for item in payload["findings"]}
        self.assertEqual({"tc-runtime-drift", "tc-tool-unpinned", "tc-build-backend-missing",
                          "tc-key-unarbitered"}, codes)
        self.assertTrue(all(item["band"] == "Structural" for item in payload["findings"]))

    def test_judgement_boundary_has_no_initial_tc_code(self):
        payload, code = self._run({
            "package.json": '{"name":"demo","version":"1.0.0"}\n',
        })
        self.assertEqual(0, code)
        self.assertEqual([], payload["findings"])
        self.assertEqual([], json.loads(GOLDEN.read_text(encoding="utf-8"))["judgement"]["codes"])


class FrozenToolchainResults(unittest.TestCase):
    def test_golden_declares_all_result_classes(self):
        payload = json.loads(GOLDEN.read_text(encoding="utf-8"))
        self.assertEqual({"absent", "conformant", "mechanical", "structural", "judgement"},
                         set(payload))
        self.assertEqual({"tc-lock-stale", "tc-config-duplicate", "tc-generated-stale"},
                         set(payload["mechanical"]["codes"]))
        self.assertEqual({"tc-runtime-drift", "tc-tool-unpinned", "tc-build-backend-missing",
                          "tc-key-unarbitered"}, set(payload["structural"]["codes"]))


if __name__ == "__main__":
    unittest.main()
