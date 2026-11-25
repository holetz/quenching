"""`docs/project/commands.md` is derived from the README command tables and must list the same set.

The catalog condenses long rows by hand, so descriptions may differ; the set of commands may not. A
command added to the README manual without reaching the catalog (or the reverse) fails here, naming it.
"""
import pathlib
import re
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
import _paths  # noqa: F401, E402
from quenching.mcp import catalog  # noqa: E402

REPO = pathlib.Path(__file__).resolve().parents[2]
ROW = re.compile(r"^\| `(/quenching-[^`]+)` \|", re.MULTILINE)


def _commands(path: pathlib.Path) -> set[str]:
    return set(ROW.findall(path.read_text(encoding="utf-8")))


class CommandsCatalogLockstep(unittest.TestCase):
    def test_catalog_lists_exactly_the_readme_commands(self):
        readme = _commands(REPO / "quenching/README.md")
        catalog = _commands(REPO / "docs/project/commands.md")
        self.assertTrue(readme, "the README command tables parsed to nothing")
        self.assertEqual(sorted(readme - catalog), [], "in the README, missing from docs/project/commands.md")
        self.assertEqual(sorted(catalog - readme), [], "in docs/project/commands.md, missing from the README")


class SpecIdSchema(unittest.TestCase):
    IDS = {"specs_validate": "spec", "specs_parallel": "spec", "specs_claim_acquire": "claim_id"}

    def test_spec_id_tools_publish_string_or_integer(self):
        for name, dest in self.IDS.items():
            props = catalog.describe(name, catalog.CATALOG[name])["inputSchema"]["properties"]
            self.assertEqual(props[dest]["type"], ["string", "integer"], name)

    def test_every_spec_id_destination_is_an_id(self):
        for name, row in catalog.CATALOG.items():
            props = catalog.describe(name, row)["inputSchema"]["properties"]
            for dest in catalog.SPEC_ID_DESTS & set(props):
                self.assertEqual(props[dest]["type"], ["string", "integer"], f"{name}.{dest}")

    def test_integer_id_reaches_the_verb_as_a_string(self):
        cmd, _ = catalog.argv(catalog.CATALOG["specs_validate"], {"spec": 494}, "/tmp")
        self.assertIn("--spec=494", cmd)
        self.assertTrue(all(isinstance(part, str) for part in cmd))

    def test_other_arguments_stay_strict(self):
        with self.assertRaises(catalog.ToolArgs):
            catalog.argv(catalog.CATALOG["specs_validate"], {"spec": True}, "/tmp")


if __name__ == "__main__":
    unittest.main()
