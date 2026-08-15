"""The multi-section write — the stream splitter, and the write path over it.

`cq specs section <slug> "<H1>,<H2>" --write` used to refuse (`sp-write-plural`) because stdin is
one stream and nothing said where one section's body ended. The delimiter chosen is the document's
own `## <Heading>` line, which is the exact form the plural READ already prints — so the two
round-trip and no second grammar was invented.

Every case below runs against the function that ships. `split_section_stream` takes its candidate
set as an argument for precisely that reason, the way `resolve_heading_name` already does:
`/.knowledge/standards/code/canonical-set-parsing.md` §A case must exercise the production function,
not a copy of its rule is what this file is answering to.
"""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.parse.edit import split_section_stream
from quenching.specs.schema import canonical_headings

CANON = canonical_headings()

# One row per shape a stdin stream can take. `expected` is what the SHIPPED splitter must return:
# `[]` is the claim "this stream is one raw body", which is what every caller had before the
# plural write existed and what the singular form must keep meaning.
SPLIT_CASES = (
    ("a raw body is not a stream",
     "corpo cru\nmais corpo", []),
    ("two blocks, in the order the stream carries them",
     "## Proposal\n\nA\n\n## Risks\n\nB\n", [("Proposal", "A"), ("Risks", "B")]),
    ("a fenced `## ` is content, never a cut",
     "## Proposal\n\n```\n## Risks\n```\n\nA\n",
     [("Proposal", "```\n## Risks\n```\n\nA")]),
    ("a stream that does not OPEN on a canonical heading is one raw body",
     "## Nao Canonico\n\nX\n", []),
    ("prose before the first heading is one raw body too",
     "preambulo\n\n## Proposal\n\nA\n", []),
    ("an unresolved heading AFTER the stream declared itself is a finding, not prose",
     "## Proposal\n\nA\n\n## Nao Canonico\n\nX\n", [("Proposal", "A"), (None, "X")]),
    ("a repeated heading survives as two blocks — the repeat is the finding",
     "## Proposal\n\nA\n\n## Proposal\n\nB\n", [("Proposal", "A"), ("Proposal", "B")]),
    ("a unique prefix resolves, exactly as it does on the command line",
     "## Out of\n\nA\n", [("Out of Scope", "A")]),
    ("an empty stream carries nothing",
     "", []),
    ("a heading with an empty body keeps the block",
     "## Proposal\n\n", [("Proposal", "")]),
    ("a level-3 heading belongs to its parent block",
     "## Impact\n\n### Product code this spec expects to touch\n\n- `a.py`\n",
     [("Impact", "### Product code this spec expects to touch\n\n- `a.py`")]),
)


class TheStreamSplitter(unittest.TestCase):
    """The cut rule, proved against `split_section_stream` itself."""

    def test_every_case_holds_for_the_shipped_splitter(self):
        for label, stream, expected in SPLIT_CASES:
            with self.subTest(label):
                self.assertEqual(split_section_stream(stream, CANON), expected)

    def test_the_candidate_set_is_an_argument_and_narrows_the_cut(self):
        """Handed a narrower set, the same stream stops resolving — which is what proves the
        cut reads the set it was given rather than a canonical list baked into the body."""
        stream = "## Proposal\n\nA\n\n## Risks\n\nB\n"
        self.assertEqual(split_section_stream(stream, ["Proposal"]),
                         [("Proposal", "A"), (None, "B")])


if __name__ == "__main__":
    unittest.main()
