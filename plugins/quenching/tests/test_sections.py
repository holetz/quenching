"""ONE copy of the section rule's canonical case list, run against BOTH readers.

THIS FILE IS THE HOME OF `SECTION_FIXTURE` AND `SECTION_CASES`. They lived byte-identically in
the pre-refactor specs and components scripts under a comment reading `EDIT BOTH, OR NEITHER` —
a rule enforced by nothing but whoever remembered it, and the two scripts could not import each
other because each
installed standalone into a target's `.claude/hooks/`. The package removed that constraint; this
file removes the duplicate, in the same move and for the same reason `CANONICAL_CASES` came to
live in `test_frontmatter.py`.

The list covers only what BOTH readers answer the same way: level-2 sections. Each supplies an
adapter over its own implementation, so **the list is the contract and neither reader is the
reference** — the phrasing the original selftest already used for this pair. What is one pillar's
alone stays with that pillar: the specs reader's canonical-heading vocabulary, and the components
reader's `#`/`###` resolution over free markdown (`test_components.py`).
"""

import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.sections import markdown_sections, select_sections
from quenching.specs.parse.edit import resolve_heading_name
from quenching.specs.parse.sections import parse_sections

SECTION_FIXTURE = '''---
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

SECTION_CASES = {
    "index": ["Alpha", "Beta", "Gamma"],
    "cases": [
        {"why": "sub-headings travel with their parent, and the section stops at the "
                "next heading of the same level",
         "ask": ["Alpha"],
         "contains": ["Alpha body.", "### Alpha sub", "Sub body that belongs to Alpha."],
         "excludes": ["Beta continues"]},
        {"why": "a fenced block containing `## ` never splits the section",
         "ask": ["Beta"],
         "contains": ["## not a heading", "Beta continues after the fence."],
         "excludes": ["Gamma ends"]},
        {"why": "tilde fences count too, and the last section runs to end of file",
         "ask": ["Gamma"],
         "contains": ["## fenced by tildes", "Gamma ends the file."],
         "excludes": []},
        {"why": "the citation form the bodies already use resolves: `§X` and `## X` "
                "are the same request, and N sections come back in the order asked",
         "ask": ["§Gamma", "## Alpha"],
         "contains": ["Gamma ends the file.", "Alpha body."],
         "excludes": [],
         "order": ["Gamma", "Alpha"]},
        {"why": "neither frontmatter nor the preamble above the first section ever "
                "leaks into a section that does not own it",
         "ask": ["Alpha", "Beta", "Gamma"],
         "contains": [],
         "excludes": ["type: standard", "Preamble under a level-1 heading."]},
        {"why": "a unique prefix resolves, so a citation need not reproduce a long "
                "heading's punctuation",
         "ask": ["Gam"],
         "contains": ["Gamma ends the file."],
         "excludes": []},
        {"why": "a section that does not exist is a refusal that names it, never an "
                "empty answer",
         "ask": ["Delta"],
         "missing": ["Delta"]},
    ],
}


def specs_reader(text: str, wanted: list[str] | None) -> tuple[list[dict], list[str]]:
    """The specs pillar's rule, behind the shared adapter shape.

    It goes through `parse_sections` rather than the `section` verb because the list pins the
    SECTIONING rule — where a section starts and stops — while the verb additionally refuses a
    heading outside the canonical fourteen. Running the list through that filter would prove the
    filter and leave the rule untested. `resolve_heading_name` is the same function the verb runs
    in production, handed the fixture's headings instead of the canonical fourteen.
    """
    rows = [{"heading": h, "level": 2, "body": v["body"]}
            for h, v in parse_sections(text).items()]
    if wanted is None:
        return rows, []
    index = {r["heading"]: r for r in rows}
    got, missing = [], []
    for name in wanted:
        hit = resolve_heading_name(name, list(index))
        (got.append(index[hit]) if hit else missing.append(name))
    return got, missing


def components_reader(text: str, wanted: list[str] | None) -> tuple[list[dict], list[str]]:
    """The components pillar's rule, behind the same adapter shape."""
    heads = markdown_sections(text)
    if wanted is None:
        return heads, []
    return select_sections(heads, wanted)


READERS = {"specs": specs_reader, "components": components_reader}


class TheSectionRule(unittest.TestCase):
    """Both readers, one list. A case that stops holding for either one fails here."""

    def test_the_level_two_index_is_the_same_for_both_readers(self):
        for pillar, reader in READERS.items():
            with self.subTest(pillar=pillar):
                heads = [h["heading"] for h in reader(SECTION_FIXTURE, None)[0]
                         if h.get("level", 2) == 2]
                self.assertEqual(heads, SECTION_CASES["index"],
                                 "a fenced line was read as a heading, or one was missed")

    def test_every_canonical_case_holds_for_both_readers(self):
        for pillar, reader in READERS.items():
            for case in SECTION_CASES["cases"]:
                with self.subTest(pillar=pillar, ask=case["ask"], why=case["why"]):
                    got, missing = reader(SECTION_FIXTURE, case["ask"])
                    want_missing = case.get("missing", [])
                    self.assertEqual(missing, want_missing, case["why"])
                    if want_missing:
                        continue
                    body = "\n".join(f"{'#' * s.get('level', 2)} {s['heading']}\n{s['body']}"
                                     for s in got)
                    for needle in case["contains"]:
                        self.assertIn(needle, body, case["why"])
                    for needle in case["excludes"]:
                        self.assertNotIn(needle, body, case["why"])
                    if "order" in case:
                        self.assertEqual([s["heading"] for s in got], case["order"], case["why"])


if __name__ == "__main__":
    unittest.main()
