"""`resource` entries whose written form the resolver used to misread.

Two defects, one shape: the parser and the resolver each disagreed with the CONVENTION the
shipped skeleton writes, so docs telling the truth were reported as lying about themselves.
Measured on the plugin's own bundle the day they were fixed: 7 of 12 `resource-unresolved`.
"""
import pathlib
import tempfile
import unittest

import _paths  # noqa: F401 — must precede the quenching import
from quenching.knowledge.resource import check_resource, parse_resource


def _doc(resource: str) -> str:
    return ("---\n"
            "type: standard\n"
            "title: Subject\n"
            "description: A doc that declares what it governs.\n"
            f"resource: {resource}\n"
            "timestamp: 2026-09-01\n"
            "---\n\n# Subject\n")


class LeadingSlashEntries(unittest.TestCase):
    """`/docs/**` means the CHECKOUT root, which is how `_entry_contains` always read it.

    Resolution joined it onto the root and got an absolute path back, globbing from `/` — so an
    entry that counted as a bundle aggregate one branch later `matched nothing on disk`.
    """

    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = pathlib.Path(self.tmp.name)
        self.bundle = self.root / "docs"
        (self.bundle / "standards").mkdir(parents=True)
        (self.root / ".design").mkdir()
        (self.root / ".design" / "tokens.json").write_text("{}\n", encoding="utf-8")
        self.doc = self.bundle / "standards" / "subject.md"

    def tearDown(self):
        self.tmp.cleanup()

    def _codes(self, resource):
        self.doc.write_text(_doc(resource), encoding="utf-8")
        return [(code, msg) for _sev, code, msg
                in check_resource(self.doc.read_text(encoding="utf-8"), str(self.doc), str(self.bundle))]

    def test_a_leading_slash_glob_over_an_existing_home_resolves(self):
        self.assertEqual(self._codes("/.design/**"), [])

    def test_the_same_glob_without_the_slash_resolves_identically(self):
        self.assertEqual(self._codes(".design/**"), self._codes("/.design/**"))

    def test_a_leading_slash_path_resolves(self):
        self.assertEqual(self._codes("/.design/tokens.json"), [])

    def test_a_leading_slash_entry_over_a_home_that_is_absent_still_reports(self):
        # The half that must keep firing: the fix reads the slash, it does not excuse the entry.
        codes = self._codes("/.specs/**")
        self.assertEqual([code for code, _ in codes], ["resource-unresolved"])

    def test_the_bundle_aggregate_resolves_and_is_still_exempt_from_resource_self(self):
        # `/docs/**` contains the doc AND the bundle root: it must resolve without raising
        # `resource-self`. Before the fix it did the opposite on both counts.
        self.assertEqual(self._codes("/docs/**"), [])


class BraceGroupSplitting(unittest.TestCase):
    """A `{a,b}` group is ONE written entry, classified `unknown` and never judged.

    Splitting on commas first cut it into pieces, and a piece from the middle of the group
    carries no brace at all — so it was classified `path` and reported against a doc that never
    wrote it.
    """

    def test_a_brace_group_stays_one_unknown_entry(self):
        self.assertEqual(parse_resource("docs/architecture/{design.md,ops.md,proof.md}"),
                         [("docs/architecture/{design.md,ops.md,proof.md}", "unknown")])

    def test_commas_outside_a_group_still_split(self):
        self.assertEqual(parse_resource("src/**, docs/index.md"),
                         [("src/**", "glob"), ("docs/index.md", "path")])

    def test_a_group_beside_a_plain_entry_splits_only_at_the_top_level(self):
        self.assertEqual(parse_resource("a/{x,y}/**, b/z.md"),
                         [("a/{x,y}/**", "unknown"), ("b/z.md", "path")])

    def test_a_group_is_never_resolved_so_it_raises_nothing(self):
        with tempfile.TemporaryDirectory() as tmp:
            bundle = pathlib.Path(tmp) / "docs"
            bundle.mkdir()
            doc = bundle / "subject.md"
            doc.write_text(_doc("docs/{a.md,b.md,c.md}"), encoding="utf-8")
            self.assertEqual(check_resource(doc.read_text(encoding="utf-8"), str(doc), str(bundle)), [])

    def test_an_unbalanced_brace_degrades_to_one_unknown_entry_never_to_false_paths(self):
        # A typo silences the remainder rather than fabricating entries out of it. That is the
        # module's standing doctrine — guessing at syntax nobody writes turns a WARN into noise —
        # and the closing brace below shows the split resumes as soon as the depth is balanced.
        self.assertEqual([kind for _entry, kind in parse_resource("a/{x.md, b.md")],
                         ["unknown"])
        self.assertEqual(parse_resource("a}/x.md, b.md"),
                         [("a}/x.md", "unknown"), ("b.md", "path")])


if __name__ == "__main__":
    unittest.main()
