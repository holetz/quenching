"""`docs/project/commands.md` is derived from the README command tables and must list the same set.

The catalog condenses long rows by hand, so descriptions may differ; the set of commands may not. A
command added to the README manual without reaching the catalog (or the reverse) fails here, naming it.
"""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[3]
ROW = re.compile(r"^\| `(/quenching:[^`]+)` \|", re.MULTILINE)


def _commands(path: pathlib.Path) -> set[str]:
    return set(ROW.findall(path.read_text(encoding="utf-8")))


class CommandsCatalogLockstep(unittest.TestCase):
    def test_catalog_lists_exactly_the_readme_commands(self):
        readme = _commands(REPO / "plugins/quenching/README.md")
        catalog = _commands(REPO / "docs/project/commands.md")
        self.assertTrue(readme, "the README command tables parsed to nothing")
        self.assertEqual(sorted(readme - catalog), [], "in the README, missing from docs/project/commands.md")
        self.assertEqual(sorted(catalog - readme), [], "in docs/project/commands.md, missing from the README")


if __name__ == "__main__":
    unittest.main()
