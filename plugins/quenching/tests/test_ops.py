"""Focused proofs for the ops verifier's registry boundary."""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.ops.checks import (
    check_adhoc_root,
    check_disabled_check,
    check_no_router,
    check_orphan,
    check_registry_stale,
    check_unarmed_write,
    check_undocumented,
    check_untyped_exit,
    inventory_digest,
    run_checks,
)
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


class FindingFixtures(unittest.TestCase):
    def _inventory(self, source: str, *, lifecycle: str | None = "active",
                   router: Router | None = None, registry: str | None = None) -> Inventory:
        root = pathlib.Path(self.raw.name)
        (root / "run.py").write_text(source, encoding="utf-8")
        if registry is not None:
            (root / "registry.md").write_text(registry, encoding="utf-8")
        return Inventory(
            str(root),
            router or Router("pyproject.toml", "python-console-script", True),
            (EntryPoint("run.py", "run", "/run", "", lifecycle=lifecycle),),
        )

    def setUp(self):
        self.raw = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.raw.cleanup()

    def test_one_minimal_fixture_trips_each_code(self):
        cases = (
            ("op-undocumented", check_undocumented,
             "def main():\n    return 0\n", "active", None, ""),
            ("op-registry-stale", check_registry_stale,
             "def main():\n    return 0\n", "active", None,
             "<!-- quenching-ops-registry-sha256 " + "0" * 64 + " -->\n`run.py`\n"),
            ("op-adhoc-root", check_adhoc_root,
             "from pathlib import Path\nROOT = Path(__file__).resolve()\n", "active", None, None),
            ("op-untyped-exit", check_untyped_exit,
             "def main():\n    return 0\n\n"
             "if __name__ == '__main__':\n    main()\n", "active", None, None),
            ("op-unarmed-write", check_unarmed_write,
             "import requests\nrequests.write('payload')\n", "active", None, None),
            ("op-disabled-check", check_disabled_check,
             "def main():\n    # verify()\n    return 0\n", "active", None, None),
            ("op-orphan", check_orphan,
             "def main():\n    return 0\n", None, None, None),
            ("op-no-router", check_no_router,
             "def main():\n    return 0\n", "active",
             Router("pyproject.toml", "python-console-script", False), None),
        )
        for code, check, source, lifecycle, router, registry in cases:
            with self.subTest(code=code):
                inventory = self._inventory(source, lifecycle=lifecycle,
                                            router=router, registry=registry)
                self.assertEqual([finding.code for finding in check(inventory)], [code])

    def test_a_conformant_fixture_is_silent_for_all_eight_checks(self):
        source = (
            "from argparse import ArgumentParser\n"
            "def main():\n"
            "    parser = ArgumentParser()\n"
            "    parser.add_argument('--write')\n"
            "    return 0\n\n"
            "if __name__ == '__main__':\n"
            "    raise SystemExit(main())\n"
        )
        inventory = self._inventory(source)
        registry = ("<!-- quenching-ops-registry-start -->\n"
                    f"<!-- quenching-ops-registry-sha256 {inventory_digest(inventory)} -->\n"
                    "`run.py` — active\n"
                    "<!-- quenching-ops-registry-end -->\n")
        inventory = self._inventory(source, registry=registry)
        self.assertEqual(run_checks(inventory), [])


if __name__ == "__main__":
    unittest.main()
