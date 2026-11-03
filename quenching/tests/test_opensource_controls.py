"""Ownership, completeness and evidence boundaries of the offline controls catalog."""
import copy
import importlib.util
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "scripts/check_opensource_controls.py"
SPEC = importlib.util.spec_from_file_location("opensource_controls_check", SCRIPT)
checker = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(checker)
CATALOG = checker.load(checker.DATA / "controls.json")
BASELINE = checker.load(checker.DATA / "baseline-2026.08.28.json")


class CatalogIntegrity(unittest.TestCase):
    def setUp(self):
        self.catalog = copy.deepcopy(CATALOG)
        self.baseline = copy.deepcopy(BASELINE)

    def rejects(self, code):
        errors = checker.check(self.catalog, self.baseline)
        self.assertTrue(any(item.startswith("osc-" + code + ":") for item in errors), errors)

    def test_complete_pinned_baseline_and_all_reference_items(self):
        self.assertEqual([], checker.check(self.catalog, self.baseline))
        self.assertEqual(41, len(self.baseline["controls"]))
        requirements = [r for c in self.baseline["controls"] for r in c["requirements"]]
        self.assertEqual(64, sum(r["state"] == "active" for r in requirements))
        self.assertEqual(["OSPS-BR-01.02"], [r["id"] for r in requirements if r["state"] == "retired"])
        self.assertEqual(20, len(self.catalog["sources"]["scorecard"]["items"]))

    def test_missing_owner(self):
        del self.catalog["controls"][0]["owner"]
        self.rejects("owner")

    def test_multiple_owners(self):
        self.catalog["controls"][0]["owner"] = ["git", "security"]
        self.rejects("owner")

    def test_extra_owner_field_cannot_bypass_scalar_owner(self):
        self.catalog["controls"][0]["owners"] = ["git", "security"]
        self.rejects("schema")

    def test_unknown_owner(self):
        self.catalog["controls"][0]["owner"] = "unassigned"
        self.rejects("owner")

    def test_duplicate_control(self):
        self.catalog["controls"].append(copy.deepcopy(self.catalog["controls"][0]))
        self.rejects("duplicate")

    def test_missing_osps_control(self):
        self.catalog["controls"].pop(0)
        self.rejects("coverage")

    def test_missing_requirement(self):
        self.catalog["controls"][2]["requirements"].pop()
        self.rejects("coverage")

    def test_duplicate_requirement(self):
        control = self.catalog["controls"][0]
        control["requirements"].append(copy.deepcopy(control["requirements"][0]))
        self.rejects("duplicate")

    def test_applicability_drift(self):
        self.catalog["controls"][0]["requirements"][0]["levels"] = [2, 3]
        self.rejects("coverage")

    def test_boolean_level_is_not_an_integer_maturity_level(self):
        self.catalog["controls"][0]["requirements"][0]["levels"] = [True, 2, 3]
        self.rejects("levels")

    def test_retired_requirement_cannot_be_reactivated(self):
        self.catalog["controls"][4]["requirements"][1]["state"] = "active"
        self.rejects("coverage")

    def test_retired_requirement_has_no_assessment_route(self):
        self.catalog["controls"][4]["requirements"][1]["evidence"]["paths"] = [".github/workflows/**"]
        self.rejects("state")

    def test_provider_absence_is_not_local_measurement(self):
        self.catalog["controls"][0]["measurable_without_provider"] = True
        self.rejects("provider")

    def test_requirement_provider_flag_matches_evidence(self):
        self.catalog["controls"][0]["requirements"][0]["provider_required"] = False
        self.rejects("provider")

    def test_mixed_ci_permissions_keep_provider_dependency(self):
        control = next(c for c in self.catalog["controls"] if c["id"] == "OSPS-AC-04")
        self.assertFalse(control["measurable_without_provider"])
        self.assertEqual([True, False], [r["provider_required"] for r in control["requirements"]])
        self.assertEqual([[2, 3], [3]], [r["levels"] for r in control["requirements"]])

    def test_source_reference_must_resolve(self):
        self.catalog["controls"][2]["references"][0]["source"] = "unknown-framework"
        self.rejects("reference")

    def test_related_does_not_claim_full_equivalence(self):
        self.catalog["controls"][2]["references"][0]["relation"] = "equivalent"
        self.rejects("reference")

    def test_reference_items_have_one_routing_owner(self):
        self.catalog["controls"][0]["references"].append(
            copy.deepcopy(self.catalog["controls"][2]["references"][0]))
        self.rejects("reference")

    def test_supplement_deletion_leaves_a_visible_reference_gap(self):
        self.catalog["controls"] = [c for c in self.catalog["controls"] if c["id"] != "COMMUNITY-CITATION"]
        self.rejects("reference")

    def test_supplements_cannot_gain_osps_levels_or_become_required(self):
        control = self.catalog["controls"][-1]
        control["optional"] = False
        control["requirements"][0]["levels"] = [1]
        self.rejects("optional")
        self.rejects("levels")

    def test_local_evidence_must_remain_inside_repository(self):
        self.catalog["controls"][0]["requirements"][0]["evidence"]["paths"] = ["../secrets"]
        self.rejects("evidence")

    def test_snapshot_loss_cannot_hide_catalog_loss(self):
        self.baseline["controls"].pop(0)
        self.catalog["controls"].pop(0)
        self.rejects("snapshot")

    def test_release_version_cannot_float(self):
        self.catalog["baseline"]["version"] = "latest"
        self.rejects("baseline")

    def test_malformed_structures_report_findings_instead_of_crashing(self):
        for key, value in [("owner", {}), ("references", None), ("framework", []),
                           ("requirements", "unknown"), ("title", None)]:
            with self.subTest(key=key):
                broken = copy.deepcopy(CATALOG)
                broken["controls"][0][key] = value
                self.assertTrue(checker.check(broken, BASELINE))
        for key, value in [("state", []), ("levels", {}), ("evidence", None), ("id", {})]:
            with self.subTest(requirement_key=key):
                broken = copy.deepcopy(CATALOG)
                broken["controls"][0]["requirements"][0][key] = value
                self.assertTrue(checker.check(broken, BASELINE))


class CatalogCommand(unittest.TestCase):
    def test_command_works_from_an_unrelated_directory_without_network(self):
        with tempfile.TemporaryDirectory() as directory:
            run = subprocess.run([sys.executable, str(SCRIPT)], cwd=directory,
                                 capture_output=True, text=True)
        self.assertEqual(0, run.returncode, run.stdout + run.stderr)
        self.assertIn("41 OSPS", run.stdout)

    def test_duplicate_json_owner_keys_are_rejected(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "controls.json"
            path.write_text('{"owner":"git","owner":"security"}')
            run = subprocess.run([sys.executable, str(SCRIPT), "--catalog", str(path)],
                                 capture_output=True, text=True)
        self.assertEqual(1, run.returncode)
        self.assertIn("duplicate JSON key: owner", run.stdout)

    def test_missing_or_malformed_json_is_a_failing_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "catalog.json"
            for content in (None, "{", "null"):
                with self.subTest(content=content):
                    if content is not None:
                        path.write_text(content)
                    run = subprocess.run([sys.executable, str(SCRIPT), "--catalog", str(path)],
                                         capture_output=True, text=True)
                    self.assertEqual(1, run.returncode)
                    self.assertNotIn("Traceback", run.stderr)

    def test_gate_invokes_catalog_checker(self):
        gate = (ROOT / "scripts/verify_repo.sh").read_text()
        self.assertIn('run_check "open source controls catalog"', gate)
        self.assertIn("python3 scripts/check_opensource_controls.py", gate)


if __name__ == "__main__":
    unittest.main()
