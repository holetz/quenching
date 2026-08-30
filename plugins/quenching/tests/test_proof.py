"""Executable properties for the proof front, starting with the ratchet invariant."""

import json
import random
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.proof.ratchet import evaluate

HERE = Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden"


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


if __name__ == "__main__":
    unittest.main()
