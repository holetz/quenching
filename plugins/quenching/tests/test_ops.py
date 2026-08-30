"""Focused proofs for the ops verifier's registry boundary."""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.ops.checks import check_registry_stale
from quenching.ops.cli import _status_payload
from quenching.ops.doctor import inspect_ops
from quenching.ops.model import EntryPoint, Inventory, Router


HERE = pathlib.Path(__file__).resolve().parent
GOLDEN = HERE / "fixtures" / "golden" / "ops-registry-absent.json"


class RegistryStale(unittest.TestCase):
    def test_absent_registry_is_silent_until_a_generator_can_create_one(self):
        expected = json.loads(GOLDEN.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / "run.py").write_text(
                "def main():\n    return 0\n\n"
                "if __name__ == '__main__':\n    raise SystemExit(main())\n",
                encoding="utf-8",
            )
            inventory = Inventory(
                str(root),
                Router("../pyproject.toml", "python-console-script", False),
                (EntryPoint("run.py", "run", "/run", "", language="python"),),
            )
            self.assertFalse((root / "registry.md").exists())
            self.assertEqual(check_registry_stale(inventory), expected["findings"])


class GoldenPayloads(unittest.TestCase):
    def test_doctor_and_status_match_the_frozen_inventory_shape(self):
        doctor_expected = json.loads(
            (HERE / "fixtures" / "golden" / "ops-doctor.json").read_text(encoding="utf-8"))
        status_expected = json.loads(
            (HERE / "fixtures" / "golden" / "ops-status.json").read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as raw:
            root = pathlib.Path(raw)
            (root / ".claude").mkdir()
            scripts = root / "scripts" / "pkg"
            scripts.mkdir(parents=True)
            (root / ".claude" / "quenching.json").write_text(
                json.dumps({"opsRoot": "scripts", "router": "pyproject.toml"}),
                encoding="utf-8")
            (root / "pyproject.toml").write_text(
                "[project.scripts]\nrun = 'pkg.run:main'\n", encoding="utf-8")
            (scripts / "run.py").write_text(
                '"""Run a job."""\nimport argparse\n'
                'parser = argparse.ArgumentParser()\nparser.add_argument("--json")\n',
                encoding="utf-8")
            (scripts / "deploy.sh").write_text("#!/bin/sh\n", encoding="utf-8")

            payload, err = inspect_ops(str(root / "scripts"))
            self.assertEqual(err, {})
            assert payload is not None
            payload["root"] = "<OPS_ROOT>"
            self.assertEqual(payload, doctor_expected)
            self.assertEqual(_status_payload(payload), status_expected)


if __name__ == "__main__":
    unittest.main()
