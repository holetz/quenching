"""Focused proofs for the ops verifier's registry boundary."""
from __future__ import annotations

import json
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401 — must precede the `quenching` import
from quenching.ops.checks import check_registry_stale
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


if __name__ == "__main__":
    unittest.main()
