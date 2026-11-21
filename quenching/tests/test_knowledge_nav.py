from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401
from quenching.knowledge.nav import NavUnclosedError, generate, kept_titles, replace_nav


CONFIG = """[project]
site_name = "Docs"
nav = [
  "index.md",
  { "Intervalos [0, 1)" = [
    "how-to/index.md",
  ] },
]
theme = "x" # [not a bracket that counts
"""


class ReplaceNavTests(unittest.TestCase):
    def test_brackets_inside_strings_and_comments_do_not_count(self) -> None:
        block = 'nav = [\n  "index.md",\n]'
        out = replace_nav(CONFIG, block)
        self.assertEqual(
            out,
            '[project]\nsite_name = "Docs"\n' + block + '\n'
            'theme = "x" # [not a bracket that counts\n',
        )

    def test_literal_string_and_escaped_quote_are_skipped(self) -> None:
        config = "nav = [\n  { 'a [' = [\n    \"b\\\" [/index.md\",\n  ] },\n]\nrest = 1\n"
        self.assertEqual(replace_nav(config, "nav = []"), "nav = []\nrest = 1\n")

    def test_an_unclosed_nav_array_raises(self) -> None:
        config = '[project]\nnav = [\n  "index.md",\n'
        with self.assertRaises(NavUnclosedError):
            replace_nav(config, 'nav = [\n  "index.md",\n]')

    def test_kept_titles_keeps_a_bracketed_title(self) -> None:
        self.assertEqual(kept_titles(CONFIG), {"how-to": "Intervalos [0, 1)"})

    def test_a_new_page_under_a_bracketed_title_reaches_the_nav(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp) / "docs"
            (root / "how-to").mkdir(parents=True)
            (root / "index.md").write_text("# Home\n")
            (root / "how-to" / "index.md").write_text("# Intervalos [0, 1)\n")
            config = Path(tmp) / "zensical.toml"
            config.write_text('[project]\nnav = [\n]\n')
            current, desired = generate(str(root), str(config))
            config.write_text(desired)
            self.assertIn('{ "Intervalos [0, 1)" = [', desired)

            (root / "how-to" / "new.md").write_text("# New\n")
            current, desired = generate(str(root), str(config))
            self.assertNotEqual(current, desired)
            self.assertIn('"how-to/new.md",', desired)
            config.write_text(desired)
            current, desired = generate(str(root), str(config))
            self.assertEqual(current, desired)


if __name__ == "__main__":
    unittest.main()
