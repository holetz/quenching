"""Executable proofs for the ``cq opensource`` front: aggregation, level, applicability, apply."""
from __future__ import annotations

import json
import pathlib
import subprocess
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.controls.evaluate import load_catalog
from quenching.opensource.aggregate import _level, doctor, status, template_integrity

CQ = pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin" / "cq"


def _cq(*args: str) -> tuple[int, dict]:
    run = subprocess.run([sys.executable, str(CQ), *args], capture_output=True, text=True)
    return run.returncode, json.loads(run.stdout)


def _block(*requirements: tuple[str, list[int], str]) -> dict:
    return {"controls": [{"id": "C", "requirements": [
        {"id": rid, "levels": levels, "state": state} for rid, levels, state in requirements]}]}


class AggregateTest(unittest.TestCase):
    def test_every_catalog_owner_has_one_block_built_by_owner_controls(self):
        with tempfile.TemporaryDirectory() as root:
            payload = status(root)
        self.assertTrue(payload["readOnly"])
        self.assertEqual(load_catalog()["owners"], [block["owner"] for block in payload["owners"]])
        for block in payload["owners"]:
            self.assertTrue(block["readOnly"])
            self.assertTrue(block["command"].startswith("/quenching-"))

    def test_an_empty_root_reports_the_license_and_contributing_findings(self):
        with tempfile.TemporaryDirectory() as root:
            code, payload = _cq("--root", root, "opensource", "status", "--json")
        self.assertEqual(1, code)
        codes = {row["code"] for row in payload["findings"]}
        self.assertTrue({"os-license-missing", "os-contributing-missing"} <= codes, codes)
        self.assertNotIn("os-conduct-missing", codes)
        self.assertIn("os-conduct-missing", {row["code"] for row in payload["advisories"]})

    def test_findings_only_name_controls_this_front_owns(self):
        catalog = load_catalog()
        owned = {c["id"] for c in catalog["controls"] if c["owner"] == "opensource"}
        with tempfile.TemporaryDirectory() as root:
            payload = status(root)
        self.assertTrue(all(row["control"] in owned for row in payload["findings"]))

    def test_the_level_climbs_only_over_met_levels(self):
        met = _block(("a", [1], "present"), ("b", [2], "not-measured"), ("c", [3], "missing"))
        result = _level([met], set())
        self.assertEqual(1, result["level"])
        self.assertEqual(["met", "unknown", "unmet"],
                         [result["levels"][str(n)]["state"] for n in (1, 2, 3)])
        self.assertEqual(["b"], result["levels"]["2"]["blocking"])

    def test_optional_and_retired_requirements_never_block_a_level(self):
        block = _block(("a", [1], "retired"))
        block["controls"].append({"id": "OPT", "requirements": [
            {"id": "o", "levels": [1], "state": "missing"}]})
        self.assertEqual(3, _level([block], {"OPT"})["level"])

    def test_an_unknown_level_stops_the_climb(self):
        result = _level([_block(("a", [1], "not-measured"), ("b", [2], "present"))], set())
        self.assertEqual(0, result["level"])
        self.assertEqual("met", result["levels"]["2"]["state"])


class DoctorTest(unittest.TestCase):
    def test_no_signal_is_not_applicable_and_not_drift(self):
        with tempfile.TemporaryDirectory() as root:
            code, payload = _cq("--root", root, "opensource", "doctor", "--json")
        self.assertEqual(0, code)
        self.assertEqual("not-applicable", payload["applicability"]["state"])
        self.assertEqual([], payload["findings"])

    def test_a_license_file_makes_the_front_applicable(self):
        with tempfile.TemporaryDirectory() as root:
            pathlib.Path(root, "LICENSE").write_text("MIT\n")
            payload = doctor(root)
        self.assertEqual("applicable", payload["applicability"]["state"])
        self.assertEqual(["LICENSE"], payload["applicability"]["signals"])
        self.assertIn("os-contributing-missing", {row["code"] for row in payload["findings"]})

    def test_the_pinned_templates_are_intact(self):
        self.assertEqual([], template_integrity())

    def test_a_missing_root_is_a_refusal(self):
        code, payload = _cq("--root", "/nonexistent/quenching-root", "opensource", "status", "--json")
        self.assertEqual(2, code)
        self.assertEqual("os-root-missing", payload["code"])


if __name__ == "__main__":
    unittest.main()
