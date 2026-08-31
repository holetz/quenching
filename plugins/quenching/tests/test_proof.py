"""Executable properties for the proof front, starting with the ratchet invariant."""

import json
import importlib
import os
import random
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.proof.ci import discover_ci
from quenching.proof.checks import conditional_status, run_checks
from quenching.proof.inventory import build_inventory
from quenching.proof.model import Fixture, Layer, ProofInventory, TestModule
from quenching.proof.ratchet import evaluate
from quenching.proof.readme import render_readme_document, write_readme

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden"
PLUGIN_ROOT = HERE.parent
LAYER_COMMAND = PLUGIN_ROOT / "commands" / "proof" / "layer" / "new.md"
HOOK_TEMPLATE = PLUGIN_ROOT / "assets" / "templates" / "proof" / "collection-hook.py.tmpl"
FIXTURE_TEMPLATE = PLUGIN_ROOT / "assets" / "templates" / "proof" / "layer-fixtures.py.tmpl"


class FrozenProofPayloads(unittest.TestCase):
    def test_all_read_payloads_are_frozen_as_json_objects(self):
        for name in ("proof-inventory.json", "proof-doctor.json", "proof-ratchet-check.json",
                     "proof-status.json"):
            with self.subTest(name=name):
                payload = json.loads((GOLDEN / name).read_text(encoding="utf-8"))
                self.assertIsInstance(payload, dict)


class TheCoverageRatchet(unittest.TestCase):
    def test_raise_is_monotonic_over_a_random_sequence(self):
        generator = random.Random(1048)
        values = [generator.uniform(0, 100) for _ in range(40)]
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            coverage = root / "coverage.json"
            floor = root / ".coverage-floor.json"
            floor.write_text(json.dumps({"version": 1, "floors": {"src": 0}}),
                             encoding="utf-8")
            config = {
                "repoRoot": str(root),
                "proofRoot": str(root / "tests"),
                "ratchetPath": str(floor),
                "measuredRoots": [{"relative": "src"}],
            }
            previous = 0.0
            for value in values:
                coverage.write_text(json.dumps({
                    "files": {"src/module.py": {
                        "covered_lines": value, "num_statements": 100}},
                    "totals": {"percent_covered": value},
                }), encoding="utf-8")
                payload, code = evaluate(config, mode="raise")
                current = json.loads(floor.read_text(encoding="utf-8"))["floors"]["src"]
                self.assertGreaterEqual(current, previous)
                self.assertAlmostEqual(current, max(previous, value), places=6)
                if value < previous:
                    self.assertEqual(1, code)
                    self.assertFalse(payload["ok"])
                previous = current


class GeneratedProofReadme(unittest.TestCase):
    def _inventory(self, root: Path) -> ProofInventory:
        return ProofInventory(
            str(root), str(root / "tests"),
            layers=(Layer("unit", "unit", "nothing", 2, True),),
            test_modules=(TestModule("unit/test_math.py", "unit", "unit", test_count=1),),
            fixtures=(Fixture("value", "fixtures/conftest.py", True),),
        )

    def test_write_is_idempotent_and_preserves_authored_prose(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            proof_root = root / "tests"
            proof_root.mkdir()
            path = proof_root / "README.md"
            authored = ("# Test policy\n\nHand-written context.\n\n"
                        "### A heading shaped like generated prose\n\nKeep this.\n")
            path.write_text(authored, encoding="utf-8")
            inventory = self._inventory(root)

            self.assertTrue(write_readme(inventory))
            first = path.read_text(encoding="utf-8")
            self.assertFalse(write_readme(inventory))
            self.assertEqual(first, path.read_text(encoding="utf-8"))
            self.assertTrue(first.startswith(authored + "\n"))
            self.assertIn("\n<!-- quenching-proof-readme-end -->\n", first)
            self.assertEqual(first, render_readme_document(first, inventory))


class ProofLayerBodyContracts(unittest.TestCase):
    def test_mint_templates_cover_targets_with_and_without_a_collection_hook(self):
        hook = HOOK_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("QUENCHING PROOF COLLECTION HOOK: BEGIN", hook)
        self.assertIn("pytest_collection_modifyitems", hook)
        self.assertIn("LAYER_MARKERS", hook)
        self.assertIn("<layer-directory>", hook)
        self.assertIn("QUENCHING PROOF COLLECTION HOOK: END", hook)
        fixture = FIXTURE_TEMPLATE.read_text(encoding="utf-8")
        self.assertIn("QUENCHING PROOF FIXTURE LIBRARY: BEGIN", fixture)
        self.assertIn("<reach>", fixture)

        authored_hook = "# target-owned collection rule\n"
        minted_block = (hook.replace("<layer-directory>", "unit")
                        .replace("<marker-name>", "unit"))
        installed = authored_hook + "\n" + minted_block
        self.assertEqual(authored_hook, installed[:len(authored_hook)])
        self.assertIn("QUENCHING PROOF COLLECTION HOOK: BEGIN", installed)

        fresh_install = minted_block
        self.assertEqual(minted_block, fresh_install)
        self.assertNotIn(authored_hook, fresh_install)

    def test_layer_body_names_separate_migration_and_interruption_boundaries(self):
        body = LAYER_COMMAND.read_text(encoding="utf-8")
        self.assertIn("proposed existing-test moves", body)
        self.assertIn("separately confirmed", body)
        self.assertIn("first layer", body)
        self.assertIn("five coupled structural edits", body)
        self.assertIn("failed intermediate edit", body)
        self.assertIn("target suite is never run", body)

    def test_declined_migration_and_interrupted_mint_leave_explicit_boundaries(self):
        body = LAYER_COMMAND.read_text(encoding="utf-8")
        self.assertIn("A declined migration leaves every", body)
        self.assertIn("test path unchanged", body)
        self.assertIn("Do not move tests until the separate migration confirmation is affirmative", body)
        self.assertIn("all five declarations complete", body)
        self.assertIn("doctor names", body)
        self.assertIn("precisely", body)
        self.assertIn("Existing hook rules and authored README prose survive", body)


class ProofFixtureTrees(unittest.TestCase):
    def _target(self, *, layers=None, measured=None, addopts="--strict-markers",
                markers=("unit",), coverage_floor=80, ci=True,
                randomized=True, extra_surfaces=(), extra_tests=None, conftest=None, ops=False):
        raw_layers = layers if layers is not None else {
            "unit": {"reach": "nothing", "budget": 2, "required": True}}
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".claude").mkdir()
            config = {"proof": {"proofRoot": "tests", "layers": raw_layers,
                                 "measuredRoots": list(measured or ("src",))}}
            if ops:
                config["ops"] = {"opsRoot": "scripts", "router": "pyproject.toml"}
            (root / ".claude" / "quenching.json").write_text(
                json.dumps(config), encoding="utf-8")
            (root / "tests" / "unit").mkdir(parents=True)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "tests" / "unit" / "test_math.py").write_text(
                "import src.app\n\ndef test_add(): pass\n", encoding="utf-8")
            if extra_tests:
                for relative, source in extra_tests.items():
                    path = root / "tests" / relative
                    path.parent.mkdir(parents=True, exist_ok=True)
                    path.write_text(source, encoding="utf-8")
            if conftest is not None:
                (root / "tests" / "conftest.py").write_text(conftest, encoding="utf-8")
            for surface in extra_surfaces:
                path = root / surface / "module.py"
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text("VALUE = 1\n", encoding="utf-8")
            if ops:
                (root / "scripts").mkdir()
                (root / "scripts" / "run.py").write_text("def main(): pass\n", encoding="utf-8")
            pyproject = (
                "[tool.pytest.ini_options]\n"
                f"addopts = {addopts!r}\n"
                f"markers = {list(markers)!r}\n"
                "\n[tool.coverage.run]\nsource = ['src']\n"
            )
            if coverage_floor is not None:
                pyproject += f"\n[tool.coverage.report]\nfail_under = {coverage_floor}\n"
            (root / "pyproject.toml").write_text(pyproject, encoding="utf-8")
            if ci:
                workflow = root / ".github" / "workflows"
                workflow.mkdir(parents=True)
                order = " --random-order" if randomized else ""
                (workflow / "proof.yml").write_text(
                    f"steps:\n  - run: cq proof doctor --json\n  - run: pytest{order}\n",
                    encoding="utf-8")
            inventory, err = build_inventory(str(root))
            self.assertEqual({}, err)
            assert inventory is not None
            write_readme(inventory)
            return {item.code for item in run_checks(inventory)}

    def _codes(self, **kwargs):
        return self._target(**kwargs)

    def test_clean_tree_has_no_findings(self):
        self.assertEqual(set(), self._codes())

    def test_each_shape_code_has_a_fixture_tree(self):
        cases = {
            "pf-unlayered": {"layers": {}, "extra_tests": {"test_root.py": "def test_root(): pass\n"}},
            "pf-unmarked": {"markers": ()},
            "pf-loose-fixture": {"extra_tests": {
                "unit/test_a.py": "import pytest\n@pytest.fixture\ndef value(): return 1\n",
                "unit/test_b.py": "import pytest\n@pytest.fixture\ndef value(): return 2\n",
            }},
            "pf-fat-conftest": {"conftest": "import pytest\n@pytest.fixture\ndef value(): return 1\n"},
            "pf-unmeasured-surface": {"extra_surfaces": ("bundle",)},
            "pf-no-floor": {"coverage_floor": None},
            "pf-stop-first": {"addopts": "--strict-markers --maxfail=1"},
            "pf-empty-layer": {"layers": {
                "unit": {"reach": "nothing", "budget": 2, "required": True},
                "data": {"reach": "tree", "budget": 5, "required": True},
            }},
        }
        for code, kwargs in cases.items():
            with self.subTest(code=code):
                self.assertIn(code, self._codes(**kwargs))

    def test_ci_and_order_codes_have_distinct_fixture_trees(self):
        self.assertIn("pf-no-ci", self._codes(ci=False))
        self.assertIn("pf-order-unproven", self._codes(
            ci=True, randomized=False, extra_tests={"unit/test_ci.py": "def test_ci(): pass\n"}))

    def test_untested_entrypoint_is_conditional_and_uses_ops_inventory(self):
        self.assertNotIn("pf-untested-entrypoint", self._codes())
        self.assertIn("pf-untested-entrypoint", self._codes(ops=True))
        self.assertNotIn("pf-untested-entrypoint", self._codes(
            ops=True, extra_tests={"unit/test_run.py": "import run\ndef test_run(): pass\n"}))

    def test_silent_untested_entrypoint_reports_not_applicable_without_ops(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            inventory = ProofInventory(str(root), str(root / "tests"))
            codes = {item.code for item in run_checks(inventory)}
            self.assertNotIn("pf-untested-entrypoint", codes)
            self.assertEqual(
                {"pf-untested-entrypoint": "not-applicable — ops is not configured"},
                conditional_status(inventory),
            )

    def test_minimal_correction_retires_each_finding_code(self):
        cases = {
            "pf-unlayered": (
                {"layers": {}, "extra_tests": {"test_root.py": "def test_root(): pass\n"}}, {}),
            "pf-unmarked": ({"markers": ()}, {}),
            "pf-loose-fixture": ({"extra_tests": {
                "unit/test_a.py": "import pytest\n@pytest.fixture\ndef value(): return 1\n",
                "unit/test_b.py": "import pytest\n@pytest.fixture\ndef value(): return 2\n",
            }}, {}),
            "pf-fat-conftest": ({"conftest": "import pytest\n@pytest.fixture\ndef value(): return 1\n"}, {}),
            "pf-unmeasured-surface": ({"extra_surfaces": ("bundle",)}, {}),
            "pf-no-floor": ({"coverage_floor": None}, {}),
            "pf-stop-first": ({"addopts": "--strict-markers --maxfail=1"}, {}),
            "pf-empty-layer": ({"layers": {
                "unit": {"reach": "nothing", "budget": 2, "required": True},
                "data": {"reach": "tree", "budget": 5, "required": True},
            }}, {}),
            "pf-no-ci": ({"ci": False}, {}),
            "pf-order-unproven": ({"randomized": False}, {}),
            "pf-untested-entrypoint": (
                {"ops": True},
                {"ops": True, "extra_tests": {
                    "unit/test_run.py": "import run\ndef test_run(): pass\n"}}),
        }
        for code, (bad, good) in cases.items():
            with self.subTest(code=code):
                self.assertIn(code, self._codes(**bad))
                self.assertNotIn(code, self._codes(**good))

    def test_each_supported_ci_provider_can_invoke_the_gate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            files = {
                ".github/workflows/proof.yml": "run: cq proof doctor --json\n",
                ".gitlab-ci.yml": "script: cq proof doctor --json\n",
                "azure-pipelines.yml": "- script: cq proof doctor --json\n",
                ".pre-commit-config.yaml": "entry: cq proof doctor --json\n",
            }
            for relative, source in files.items():
                path = root / relative
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(source, encoding="utf-8")
            rows = discover_ci(str(root))
            self.assertEqual({"github-actions", "gitlab-ci", "azure-pipelines", "pre-commit"},
                             {row.provider for row in rows})
            self.assertTrue(all(row.runs_gate for row in rows))

    def test_all_five_commands_refuse_to_execute_the_target_suite(self):
        from quenching.proof.cli import main

        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / ".claude").mkdir()
            (root / "tests" / "unit").mkdir(parents=True)
            (root / "src").mkdir()
            (root / "src" / "app.py").write_text("VALUE = 1\n", encoding="utf-8")
            (root / "tests" / "unit" / "test_math.py").write_text(
                "import src.app\ndef test_add(): pass\n", encoding="utf-8")
            (root / ".claude" / "quenching.json").write_text(json.dumps({
                "proof": {
                    "proofRoot": "tests",
                    "layers": {"unit": {"reach": "nothing", "required": True}},
                    "measuredRoots": ["src"],
                },
            }), encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[tool.pytest.ini_options]\n"
                "addopts = '--strict-markers'\nmarkers = ['unit']\n"
                "\n[tool.coverage.run]\nsource = ['src']\n"
                "\n[tool.coverage.report]\nfail_under = 80\n", encoding="utf-8")
            (root / ".github" / "workflows").mkdir(parents=True)
            (root / ".github" / "workflows" / "proof.yml").write_text(
                "run: cq proof doctor --json pytest --random-order\n", encoding="utf-8")
            (root / ".coverage-floor.json").write_text(
                json.dumps({"version": 1, "floors": {"src": 80}}), encoding="utf-8")
            (root / "coverage.json").write_text(json.dumps({
                "files": {"src/app.py": {"covered_lines": 8, "num_statements": 10}},
                "totals": {"percent_covered": 80},
            }), encoding="utf-8")
            inventory, err = build_inventory(str(root))
            self.assertEqual({}, err)
            assert inventory is not None
            write_readme(inventory)
            forbidden = mock.Mock(side_effect=AssertionError("proof command executed the target"))
            with mock.patch.object(subprocess, "run", forbidden), \
                    mock.patch.object(os, "system", forbidden), \
                    mock.patch.object(importlib, "import_module", forbidden):
                for command in ("inventory", "doctor", "ratchet", "status", "readme"):
                    with self.subTest(command=command):
                        self.assertEqual(0, main(["--root", str(root), command, "--json"]))


if __name__ == "__main__":
    unittest.main()
