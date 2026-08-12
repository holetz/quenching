"""The one thing in `cmd_selftest` that was never a unit test: the embedded assets' lockstep.

`schema.json` and `templates/spec.md` are duplicated as constants inside the specs pillar, so a
copy with no adjacent assets can still stamp a capture. A duplicate nobody checks is a bug with a
delay on it, and this is the check — the last reason `selftest` had to exist as a subcommand.

It is here rather than there because of how the original failed: `cmd_selftest` answered
`skipped: true` and **exit 0** when it could not find the assets, a path written for the installed
copy that silently came to cover a wrong path too. `test_the_assets_are_found_at_all` is that skip
turned into an assertion — the drift check cannot be switched off by a path that stops resolving.
"""

import json
import pathlib
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.schema import DEFAULT_SCHEMA, TEMPLATE_SPEC, ASSET_DIR, _behavioral

ASSETS = pathlib.Path(ASSET_DIR)
PROSE_KEYS = ("note", "why")


class EmbeddedAssets(unittest.TestCase):
    def test_the_assets_are_found_at_all(self):
        """`ASSET_DIR` resolves. The check below cannot pass vacuously on a path that moved."""
        self.assertTrue(ASSETS.is_dir(), f"ASSET_DIR does not resolve: {ASSET_DIR}")
        self.assertTrue((ASSETS / "schema.json").is_file())
        self.assertTrue((ASSETS / "templates" / "spec.md").is_file())

    def test_the_embedded_schema_has_not_drifted_from_schema_json(self):
        on_disk = json.loads((ASSETS / "schema.json").read_text(encoding="utf-8"))
        self.assertEqual(_behavioral(on_disk), _behavioral(DEFAULT_SCHEMA))

    def test_the_embedded_template_is_byte_for_byte_spec_md(self):
        self.assertEqual((ASSETS / "templates" / "spec.md").read_text(encoding="utf-8"),
                         TEMPLATE_SPEC)

    def test_stripping_the_prose_is_load_bearing_and_not_decoration(self):
        """Why the comparison above goes through `_behavioral` at all.

        `schema.json` carries `note`/`why` for whoever reads it; the embedded fallback never has.
        Comparing them raw is `False` by construction, so a refactor that drops `_behavioral` as
        dead weight turns a passing lockstep into one that reports drift on every conformant pair
        — which is exactly how it was lost once already, moving `DEFAULT_SCHEMA` into this module.
        """
        on_disk = json.loads((ASSETS / "schema.json").read_text(encoding="utf-8"))
        self.assertNotEqual(on_disk, DEFAULT_SCHEMA)
        self.assertEqual([], [key for key in PROSE_KEYS
                              if key in json.dumps(_behavioral(on_disk))])


if __name__ == "__main__":
    unittest.main()
