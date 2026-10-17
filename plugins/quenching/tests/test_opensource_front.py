"""Executable proofs for the ``cq opensource`` front: aggregation, level, applicability, apply."""
from __future__ import annotations

import hashlib
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
from quenching.opensource.aggregate import TEMPLATES, _level, doctor, load_sources, status, template_integrity
from quenching.opensource.apply import Refusal, apply

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


class ApplyTest(unittest.TestCase):
    def test_every_upstream_template_matches_its_pinned_sha256(self):
        pinned = [e for e in load_sources()["templates"] if e.get("sha256")]
        self.assertEqual({"license", "conduct", "dco"}, {e["artifact"] for e in pinned})
        for entry in pinned:
            with self.subTest(path=entry["path"]):
                digest = hashlib.sha256((TEMPLATES / entry["path"]).read_bytes()).hexdigest()
                self.assertEqual(entry["sha256"], digest)
                self.assertTrue(entry["url"].startswith("https://"))

    def test_the_upstream_text_is_copied_with_only_its_declared_placeholder_filled(self):
        upstream = (TEMPLATES / "upstream" / "code_of_conduct.md").read_bytes()
        with tempfile.TemporaryDirectory() as root:
            code, payload = _cq("--root", root, "opensource", "apply", "--artifact", "conduct",
                                "--var", "contact=conduct@example.org", "--json")
            written = pathlib.Path(root, "CODE_OF_CONDUCT.md").read_bytes()
            again, refusal = _cq("--root", root, "opensource", "apply", "--artifact", "conduct",
                                 "--var", "contact=other@example.org", "--json")
            unchanged = pathlib.Path(root, "CODE_OF_CONDUCT.md").read_bytes()
        self.assertEqual(0, code)
        self.assertTrue(payload["written"])
        self.assertEqual(upstream.replace(b"[INSERT CONTACT METHOD]", b"conduct@example.org"), written)
        self.assertEqual(2, again)
        self.assertEqual("os-target-exists", refusal["code"])
        self.assertEqual(written, unchanged)

    def test_dry_run_writes_nothing(self):
        with tempfile.TemporaryDirectory() as root:
            result = apply(root, "pr-template", {}, dry_run=True)
            self.assertFalse(pathlib.Path(root, ".github").exists())
        self.assertFalse(result["written"])
        self.assertEqual(".github/PULL_REQUEST_TEMPLATE.md", result["target"])

    def test_the_license_is_selected_by_spdx_and_unvendored_ids_refuse(self):
        with tempfile.TemporaryDirectory() as root:
            apply(root, "license", {"spdx": "MIT", "year": "2026", "holders": "Ada"})
            self.assertIn("Copyright (c) 2026 Ada", pathlib.Path(root, "LICENSE").read_text())
            with self.assertRaises(Refusal) as caught:
                apply(root, "license", {"spdx": "GPL-3.0-only"}, dry_run=True)
        self.assertEqual("os-license-unvendored", caught.exception.payload["code"])

    def test_missing_and_undeclared_values_refuse(self):
        with tempfile.TemporaryDirectory() as root:
            for values, code in (({}, "os-var-missing"),
                                 ({"contact": "a", "extra": "b"}, "os-var-unknown")):
                with self.subTest(code=code), self.assertRaises(Refusal) as caught:
                    apply(root, "conduct", values)
                self.assertEqual(code, caught.exception.payload["code"])
            self.assertEqual([], list(pathlib.Path(root).iterdir()))

    def test_status_reads_without_writing(self):
        with tempfile.TemporaryDirectory() as root:
            status(root)
            doctor(root)
            self.assertEqual([], list(pathlib.Path(root).iterdir()))


class ReadinessRouteTest(unittest.TestCase):
    def test_the_route_reports_an_unmeasured_assessment_as_inconclusive(self):
        with tempfile.TemporaryDirectory() as root:
            code, payload = _cq("--root", root, "opensource", "readiness", "--json")
            self.assertEqual([], list(pathlib.Path(root).iterdir()))
        self.assertEqual(2, code)
        self.assertFalse(payload["grantsPublication"])
        self.assertEqual({"refused"}, {row["state"] for row in payload["coverage"]})

    def test_the_human_rendering_names_what_stayed_unmeasured(self):
        with tempfile.TemporaryDirectory() as root:
            run = subprocess.run([sys.executable, str(CQ), "--root", root, "opensource", "readiness"],
                                 capture_output=True, text=True)
        self.assertEqual(2, run.returncode)
        self.assertIn("unmeasured: secrets", run.stdout)
        self.assertIn("never a publication approval", run.stdout)


if __name__ == "__main__":
    unittest.main()
