"""The vitrines' ledger weighs every `cq specs` verb, and both copies of its WRITE list agree."""
from pathlib import Path
import re
import unittest

import _paths  # noqa: F401
from quenching.specs.commands.cli import build_parser

REPO = Path(__file__).resolve().parents[2]
SOURCES = {
    "claude-vitrine": REPO / "integrations/claude-vitrine/hooks/ledger.ts",
    "opencode-vitrine": REPO / "integrations/opencode-vitrine/src/specs.ts",
}

# The verbs that never change the store. A new CLI verb must land here or in both WRITE lists.
READ = {"schedule", "list", "status", "show", "next", "parallel", "find", "validate", "config",
        "doctor", "export", "mcp", "serve", "estimate"}
# Reads by default, writes under `--write`.
CONDITIONAL = {"section"}


def write_set(source: Path) -> set[str]:
    match = re.search(r"const WRITE = new Set\(\[(.*?)\]\)", source.read_text(encoding="utf-8"), re.S)
    if match is None:
        raise AssertionError(f"{source}: no `const WRITE = new Set([...])` literal")
    return set(re.findall(r"""['"]([a-z][a-z-]*)['"]""", match.group(1)))


def cli_verbs() -> set[str]:
    _, sub = build_parser()
    return set(sub.choices)


class VitrineWriteVerbs(unittest.TestCase):
    def test_both_vitrines_carry_the_same_write_list(self):
        claude, opencode = (write_set(path) for path in SOURCES.values())
        self.assertEqual(claude, opencode)

    def test_every_cli_verb_is_classified_once(self):
        writes = write_set(SOURCES["claude-vitrine"])
        self.assertEqual(set(), writes & READ, "a verb is both read and write")
        self.assertEqual(set(), (writes | READ) & CONDITIONAL)
        self.assertEqual(cli_verbs(), writes | READ | CONDITIONAL)

    def test_section_weighs_as_a_write_only_under_write_flag(self):
        for name, path in SOURCES.items():
            text = path.read_text(encoding="utf-8")
            with self.subTest(vitrine=name):
                self.assertRegex(text, r"""verb === ['"]section['"] && /\(\?:\^\|\\s\)--write\\b/""")


if __name__ == "__main__":
    unittest.main()
