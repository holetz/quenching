"""The frontmatter parser's contract: the canonical cases, every value form, and the two sidecars.

THIS FILE IS THE HOME OF `CANONICAL_CASES`. The table used to exist byte-identically in the
pre-refactor specs, components and OKF validator scripts, each copy carrying an `EDIT ALL THREE,
OR NONE` warning, because each script shipped standalone and could import nothing. One parser
replaced the three, so there is
one implementation left to hold to the table's word — and holding it there is a test's job, not a
selftest subcommand's. The three in-script copies go with the parsers they were guarding.
"""

import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.frontmatter import (
    ANOMALY_EXEMPT_KEYS,
    BLOCK_SCALAR_RE,
    frontmatter_anomalies,
    frontmatter_block,
    parse_frontmatter,
)


def doc(body: str) -> str:
    """A markdown file whose frontmatter is `body`."""
    return f"---\n{body}\n---\n\nbody\n"


def kinds(text: str) -> tuple[str, ...]:
    return tuple(sorted(a["kind"] for a in frontmatter_anomalies(text)))


# The canonical case list from `/.knowledge/standards/code/frontmatter-parser.md`.
#   (label, frontmatter body, expected `title`, expected anomaly kinds)
CANONICAL_CASES = [
    ("plain",                 "title: a plain value",              "a plain value",              ()),
    ("comment-after-space",   "title: a value # a note",           "a value",                    ("comment-stripped",)),
    ("hash-after-quote-char", "title: truncates at the first '#'", "truncates at the first '#'", ()),
    ("hash-in-backticks",     "title: the `#` character",          "the `#` character",          ()),
    ("hash-no-space",         "title: C#",                         "C#",                         ()),
    ("double-quoted-hash",    'title: "quoted # inside"',          "quoted # inside",            ()),
    ("single-quoted-hash",    "title: 'single # inside'",          "single # inside",            ()),
    ("quoted-then-comment",   'title: "quoted" # a note',          "quoted",                     ("comment-stripped",)),
    ("comment-only",          "title: # a note",                   "",                           ("comment-stripped",)),
    ("unterminated-quote",    'title: "unterminated',              '"unterminated',              ("unterminated-quote",)),
    ("duplicate-key",         "title: first\ntitle: second",       "second",                     ("duplicate-key",)),
    ("indented-continuation", "title:\n  a wrapped prose line",    "",                           ("indented-continuation",)),
]


class CanonicalCases(unittest.TestCase):
    """The standard's own table, run against the one parser that now answers for all three."""

    def test_canonical_cases_parse_to_the_documented_title(self):
        for label, body, want, _ in CANONICAL_CASES:
            with self.subTest(case=label):
                self.assertEqual(parse_frontmatter(doc(body)).get("title", "<missing>"), want)

    def test_canonical_cases_raise_the_documented_anomalies(self):
        for label, body, _, want in CANONICAL_CASES:
            with self.subTest(case=label):
                self.assertEqual(kinds(doc(body)), tuple(sorted(want)))


# (label, frontmatter body, expected type, expected value)
VALUE_FORMS = [
    ("scalar",            "k: a plain value",              str,  "a plain value"),
    ("quotes-stripped",   'k: "a quoted value"',           str,  "a quoted value"),
    ("comment-stripped",  "k: a value # a note",           str,  "a value"),
    ("inline-list",       "k: [a, b]",                     list, ["a", "b"]),
    ("block-list",        "k:\n  - a\n  - b",              list, ["a", "b"]),
    ("block-record",      "k:\n  a: one\n  b: two",        dict, {"a": "one", "b": "two"}),
    ("flow-map",          "k: {a: one, b: two}",           dict, {"a": "one", "b": "two"}),
    ("block-scalar-|",    "k: |\n  one\n  two",            str,  "one\ntwo"),
    ("block-scalar->-",   "k: >-\n  one\n  two",           str,  "one two"),
    # Borders already verified once and kept locked: an empty collection stays a collection of its
    # own kind, and quoting demotes a list back to the string a human deliberately wrote.
    ("empty-inline-list", "k: []",                         list, []),
    ("empty-flow-map",    "k: {}",                         dict, {}),
    ("quoted-list-shape", 'k: "[a, b]"',                   str,  "[a, b]"),
]


class ValueForms(unittest.TestCase):
    def test_every_value_form_parses_to_its_documented_type_and_value(self):
        for label, body, want_type, want in VALUE_FORMS:
            with self.subTest(form=label):
                got = parse_frontmatter(doc(body))["k"]
                self.assertIsInstance(got, want_type)
                self.assertEqual(got, want)

    def test_block_scalar_header_is_recognised_with_chomping_and_indent_indicators(self):
        for header in ("|", ">", "|-", ">-", "|+", ">2"):
            with self.subTest(header=header):
                self.assertEqual(BLOCK_SCALAR_RE.match(header).group(1), header[0])

    def test_block_scalar_header_does_not_match_a_value_that_merely_starts_with_a_pipe(self):
        self.assertIsNone(BLOCK_SCALAR_RE.match("| a table cell"))


class NormalizedUpward(unittest.TestCase):
    """The cells that changed when three parsers became one.

    Each pillar used to flatten the forms it could not read, and every one of those flattenings is
    a silent wrong answer a future edit could reintroduce. These tests assert the flattening is
    gone — the value form matrix above says what the answer is now, these say what it is not.
    """

    def _value(self, body: str):
        return parse_frontmatter(doc(body))["k"]

    def test_inline_list_normalized_upward_knowledge_gained_it(self):
        # the pre-refactor OKF validator script kept the literal `[a, b]`.
        got = self._value("k: [a, b]")
        self.assertNotEqual(got, "[a, b]")
        self.assertIsInstance(got, list)

    def test_block_list_normalized_upward_knowledge_gained_it(self):
        # the pre-refactor OKF validator script read an indented `- item` run as the empty string.
        got = self._value("k:\n  - a\n  - b")
        self.assertNotEqual(got, "")
        self.assertIsInstance(got, list)

    def test_block_record_normalized_upward_knowledge_and_components_gained_it(self):
        # the pre-refactor OKF validator and components scripts both read an indented `k: v` run
        # as the empty string.
        got = self._value("k:\n  a: one")
        self.assertNotEqual(got, "")
        self.assertIsInstance(got, dict)

    def test_flow_map_normalized_upward_knowledge_and_components_gained_it(self):
        # the pre-refactor OKF validator and components scripts both kept the literal `{a: one}`.
        got = self._value("k: {a: one}")
        self.assertNotEqual(got, "{a: one}")
        self.assertIsInstance(got, dict)

    def test_block_scalar_normalized_upward_knowledge_and_specs_gained_it(self):
        # the pre-refactor OKF validator and specs scripts both kept the bare indicator as the
        # value.
        got = self._value("k: |\n  one\n  two")
        self.assertNotEqual(got, "|")
        self.assertEqual(got, "one\ntwo")


class BlockSidecar(unittest.TestCase):
    """`frontmatter_block` — the two bits only the `knowledge` pillar acts on."""

    NO_FENCE = "# a heading\n\nbody\n"
    UNCLOSED = "---\ntitle: x\n\nbody with no closing fence\n"
    CLOSED = doc("title: x")

    def test_a_file_with_no_opening_fence_has_no_block_and_is_not_malformed(self):
        self.assertEqual(frontmatter_block(self.NO_FENCE), (False, True))

    def test_a_fence_that_never_closes_is_a_block_that_is_not_well_formed(self):
        self.assertEqual(frontmatter_block(self.UNCLOSED), (True, False))

    def test_a_closed_fence_is_a_well_formed_block(self):
        self.assertEqual(frontmatter_block(self.CLOSED), (True, True))

    def test_parse_cannot_tell_a_missing_fence_from_an_unclosed_one(self):
        # The whole reason the sidecar exists: both collapse to `{}` here, so the difference
        # between "no frontmatter" and "broken frontmatter" lives only in `frontmatter_block`.
        self.assertEqual(parse_frontmatter(self.NO_FENCE), {})
        self.assertEqual(parse_frontmatter(self.UNCLOSED), {})


class Anomalies(unittest.TestCase):
    """`frontmatter_anomalies` — a key the parser could not turn into a value, and nothing else."""

    # `hook.md` shape 1, written with a blank line under `hooks:`. The blank stops the block-record
    # reader dead (it demands an indented NON-blank line), so `parse_frontmatter` returns `""` for
    # a block that `parse_frontmatter_hooks` reads perfectly well — and without the exemption every
    # command authored this way collected a bogus `indented-continuation`.
    HOOKS_BLOCK = (
        '{key}:\n'
        '\n'
        '  PostToolUse:\n'
        '    - matcher: "Write|Edit"\n'
        '      hooks:\n'
        '        - type: command\n'
        '          command: "python3 check.py"\n'
    )

    def test_a_file_without_frontmatter_has_no_anomalies(self):
        self.assertEqual(frontmatter_anomalies("# a heading\n\nbody\n"), [])

    def test_no_form_the_parser_reads_is_reported_as_an_anomaly(self):
        for label, body, _, _ in VALUE_FORMS:
            if label == "comment-stripped":
                continue   # that row exists to raise one; the canonical table asserts it
            with self.subTest(form=label):
                self.assertEqual(kinds(doc(body)), ())

    def test_anomaly_names_the_key_and_carries_a_kind_and_a_detail(self):
        anomaly, = frontmatter_anomalies(doc("title: a value # a note"))
        self.assertEqual(anomaly["key"], "title")
        self.assertEqual(anomaly["kind"], "comment-stripped")
        self.assertIn("# a note", anomaly["detail"])

    def test_hooks_with_a_blank_line_before_the_first_event_reads_as_empty(self):
        self.assertEqual(parse_frontmatter(doc(self.HOOKS_BLOCK.format(key="hooks"))), {"hooks": ""})

    def test_hooks_is_exempt_because_the_components_pillar_has_its_own_reader_for_it(self):
        self.assertEqual(ANOMALY_EXEMPT_KEYS, {"hooks"})
        self.assertEqual(kinds(doc(self.HOOKS_BLOCK.format(key="hooks"))), ())

    def test_the_same_unreadable_block_under_any_other_key_is_still_reported(self):
        self.assertEqual(kinds(doc(self.HOOKS_BLOCK.format(key="settings"))),
                         ("indented-continuation",))


if __name__ == "__main__":
    unittest.main()
