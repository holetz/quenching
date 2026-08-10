"""The section rule over FREE markdown — the half of `skills.py`'s `cmd_selftest` that is
this pillar's OWN, migrated from its `selftest` subcommand.

`specs.py` and `skills.py` share ONE canonical case list (`SECTION_CASES`, run against
`SECTION_FIXTURE`) proving what both readers agree on: level-2 sections. That shared pair is
still duplicated verbatim in both scripts under an `EDIT BOTH, OR NEITHER` marker and belongs
to task 6.4, which gives the now-unified `quenching.components.sections` reader its one home
for that table — nothing about it is migrated here.

What IS this pillar's own, and covered below: `skills.py` also resolves `#` and `###` over
free markdown (a reference or a standard has headings at every level, unlike a spec's
fourteen `##`s), and it owns two ladders `specs.py` has no equivalent of — `--sections`
(comma-vs-address) and `--rules-only` (the binding sentence vs. its rationale). Each fixture
below is local to the assertion it drives, on purpose: growing the shared `SECTION_FIXTURE`
with a comma-bearing heading to serve the `--sections` ladder would change an index the 6.4
suite asserts on too.

`canonical_case_failures()` (the FRONTMATTER cases) is also not here — it moved to
`test_frontmatter.py` with the one parser that now answers for all three tools.
"""
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.sections import (
    RATIONALE_MARKER,
    RULES_MARKER,
    expand_section_args,
    markdown_sections,
    select_sections,
    split_rule_and_rationale,
)

# The same text both scripts embed as `SECTION_FIXTURE`; kept local here because only the
# every-level index and the `###` resolution below are this pillar's own — the level-2 table
# built on top of it (`SECTION_CASES`) is 6.4's to place.
FREE_MARKDOWN = '''---
type: standard
title: the section reader's fixture
---

# Top

Preamble under a level-1 heading.

## Alpha

Alpha body.

### Alpha sub

Sub body that belongs to Alpha.

## Beta

Beta opens with a fenced block whose lines look like headings:

```bash
## not a heading
### also not a heading
```

Beta continues after the fence.

## Gamma

~~~
## fenced by tildes
~~~

Gamma ends the file.
'''


class EveryLevelIndex(unittest.TestCase):
    """Free markdown has headings at every level, and a reference cited as `§The [P] check`
    is a `###`. A reader that only resolved `##` would refuse half the citations in the repo."""

    def test_every_heading_resolves_at_its_own_level_fences_included(self):
        got = [(h["level"], h["heading"]) for h in markdown_sections(FREE_MARKDOWN)]
        self.assertEqual(got, [(1, "Top"), (2, "Alpha"), (3, "Alpha sub"),
                               (2, "Beta"), (2, "Gamma")])


class SubHeadingResolution(unittest.TestCase):
    def test_a_level_3_heading_resolves_on_its_own_and_stops_at_the_next_same_or_shallower(self):
        sub, missing = select_sections(markdown_sections(FREE_MARKDOWN), ["Alpha sub"])
        self.assertEqual(missing, [])
        self.assertNotIn("Beta", sub[0]["body"])


# Local to the `--sections` ladder: a heading may carry a comma of its own, so a value is
# first resolved as an ADDRESS and only then split as a list. Not part of `SECTION_FIXTURE`
# on purpose — adding a comma heading there would change an index the 6.4 suite asserts on.
COMMA_HEADINGS = markdown_sections(
    "## What crosses, what stays\n\nCrossing body.\n\n"
    "## The procedure\n\nProcedure body.\n\n## Invariants\n\nInvariant body.\n")

SECTIONS_LADDER_CASES = (
    # the whole title wins, which is the bug this ladder exists to fix
    ("whole", ["What crosses, what stays"], ["What crosses, what stays"]),
    # a value that resolves to nothing is still a list
    ("list", ["The procedure,Invariants"], ["The procedure", "Invariants"]),
    # a PREFIX carrying a comma resolves whole too — the case that fails if step one is
    # exact-match alone, and the reason it is the whole ladder
    ("prefix", ["§What crosses, what"], ["§What crosses, what"]),
    # a name that resolves to nothing travels on, so `cmd_read` refuses BY NAME rather than
    # silently dropping it
    ("refusal", ["Delta"], ["Delta"]),
)


class SectionsLadder(unittest.TestCase):
    """`--sections`, this pillar's own — `specs.py`'s arm resolves name by name and splits
    nothing, so a comma case there would prove a rule that tool does not have."""

    def test_a_value_is_first_an_address_and_only_then_a_list(self):
        for label, ask, want in SECTIONS_LADDER_CASES:
            with self.subTest(case=label):
                self.assertEqual(expand_section_args(COMMA_HEADINGS, ask), want)


MARKED = (f"{RULES_MARKER}\nThe binding sentence.\n{RATIONALE_MARKER}\n"
          f"The measurement behind it.")
NESTED = (f"{RULES_MARKER}\nParent rule.\n\n### Sub one\n\n{RULES_MARKER}\nSub rule.\n"
          f"{RATIONALE_MARKER}\nSub story.\n\n### Sub two\n\nUnmarked sub rule.")

RULES_ONLY_CASES = (
    ("marked", MARKED, "The binding sentence.", True),
    ("no-rationale", f"{RULES_MARKER}\nOnly a rule.", "Only a rule.", True),
    ("unmarked", "A whole section nobody marked up.",
     "A whole section nobody marked up.", False),
    # a marker's reach ends at the next heading: one sub-section's rationale must not swallow
    # the sub-sections after it
    ("nested", NESTED,
     "Parent rule.\n\n### Sub one\n\nSub rule.\n\n### Sub two\n\nUnmarked sub rule.", True),
)


class RulesOnlyLadder(unittest.TestCase):
    """`--rules-only`, this pillar's own. The fallback arm is the one `## Validation` insists
    on: a missing marker must never become an empty answer, because a caller that asked for a
    rule and got silence proceeds as though the rule did not exist."""

    def test_the_four_arms_split_to_the_documented_rule_text_and_marked_flag(self):
        for label, body, want_text, want_marked in RULES_ONLY_CASES:
            with self.subTest(case=label):
                got_text, got_marked = split_rule_and_rationale(body)
                self.assertEqual(got_text.strip(), want_text)
                self.assertEqual(got_marked, want_marked)

    def test_no_arm_degrades_to_an_empty_answer(self):
        for label, body, _, _ in RULES_ONLY_CASES:
            with self.subTest(case=label):
                got_text, _ = split_rule_and_rationale(body)
                self.assertTrue(got_text.strip())


if __name__ == "__main__":
    unittest.main()
