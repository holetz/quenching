"""A frontmatter write that cannot land is refused, and an inline list respects its quotes."""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.parse.fields import (UnclosedFence, set_frontmatter_key,
                                          set_frontmatter_record, strip_frontmatter_keys)

UNCLOSED = "---\nid: 9\ntitle: x\n## Problem\nx\n"


class InlineListQuotes(unittest.TestCase):
    def test_a_hash_inside_a_quoted_tag_survives(self):
        fm = parse_frontmatter('---\nid: 9\ntags: ["area", "sprint #3"]\n---\nx')
        self.assertEqual(fm["tags"], ["area", "sprint #3"])

    def test_a_comma_inside_a_quote_does_not_split(self):
        fm = parse_frontmatter('---\nid: 9\ntags: ["a, b", c]  # note\n---\nx')
        self.assertEqual(fm["tags"], ["a, b", "c"])

    def test_a_trailing_comment_is_still_stripped(self):
        fm = parse_frontmatter("---\nid: 9\ntags: [a, b] # note\n---\nx")
        self.assertEqual(fm["tags"], ["a", "b"])


class UnclosedFenceRefuses(unittest.TestCase):
    def test_key_writer_raises(self):
        with self.assertRaises(UnclosedFence):
            set_frontmatter_key(UNCLOSED, "outcome", "abandoned")

    def test_record_writer_raises(self):
        with self.assertRaises(UnclosedFence):
            set_frontmatter_record(UNCLOSED, "refined", {"mode": "compose"})

    def test_strip_raises(self):
        with self.assertRaises(UnclosedFence):
            strip_frontmatter_keys(UNCLOSED, ("tags",))

    def test_a_closed_fence_still_writes(self):
        out = set_frontmatter_key("---\nid: 9\n---\nx\n", "outcome", "done")
        self.assertIn("outcome: done", out)


if __name__ == "__main__":
    unittest.main()
