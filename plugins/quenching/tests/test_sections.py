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

import io
import json
import unittest
from contextlib import redirect_stdout

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.sections import markdown_sections, select_sections
from quenching.specs.commands.output import Emitter
from quenching.specs.commands.validate import cmd_validate
from quenching.specs.parse.edit import resolve_heading_name
from quenching.specs.parse.sections import parse_sections
from quenching.specs.parse.text import body_after_frontmatter
from quenching.specs.schema import canonical_headings
from test_specs_section_write import _Args, _Workspace

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
        heading outside the canonical thirteen. Running the list through that filter would prove the
    filter and leave the rule untested. `resolve_heading_name` is the same function the verb runs
    in production, handed the fixture's headings instead of the canonical thirteen.
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


STRAY_FIXTURE = '''---
slug: alpha
title: um documento que já carrega uma seção stray
date: 2026-08-17
---

# um documento que já carrega uma seção stray

## Problem

O problema.

## Outcome

O que aconteceu.

## O que mudou

Quatro linhas que ninguém quer perder.

```bash
## isto não é um heading
```

## Risks

Um risco.
'''

NO_ANCHOR_FIXTURE = '''---
slug: alpha
title: um documento cujo primeiro título já é o stray
date: 2026-08-17
---

# um documento cujo primeiro título já é o stray

## Preâmbulo órfão

Texto sem nenhuma seção canônica acima dele.

## Problem

O problema.
'''


class _FoldWorkspace(_Workspace):
    """`_Workspace` plus the three readings the fold cases assert over.

    It reuses the write path's own fixture machinery — a real files-backend workspace driven
    through `cmd_section` — rather than a second copy of it, for the reason that file already
    states: the refusal ladder is proved through the command that ships, never through a
    re-reading of its rule written inside the test."""

    def read_spec(self):
        info, error = self.backend.read_spec("alpha")
        self.assertFalse(error, error)
        return info["text"]

    def validate_codes(self):
        """The codes `cq specs validate` actually emits for this spec — the finding whose
        closure is the whole point of the fold, asked of the validator itself."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            cmd_validate(_Args(), self.root, Emitter())
        return [f["code"] for f in json.loads(buf.getvalue())["findings"]]

    def canonical_index(self):
        """Every canonical section and the line it starts on — the shape that must be
        IDENTICAL across a fold, because a fold that reorders the document is the risk the
        operation was designed around."""
        canon = set(canonical_headings())
        sections = parse_sections(body_after_frontmatter(self.read_spec()))
        return [(h, s["lineno"]) for h, s in sections.items() if h in canon]


class TheFoldOfAStrayHeading(_FoldWorkspace):
    """`cq specs section <slug> --fold "<Stray>"` — the ONE path that admits a heading outside
    the thirteen, and the only way an `sp-stray-heading` already on disk can be closed."""

    spec_text = STRAY_FIXTURE

    def test_every_other_way_of_naming_a_stray_still_exits_2(self):
        """The negative pair, and the half that matters: the admission is local to `--fold`,
        so if it ever leaks the prevention that closed the door is gone with it."""
        cases = (("a plain read", {"heading": "O que mudou"}, None),
                 ("a --write over the stray", {"heading": "O que mudou", "write": True},
                  "corpo novo\n"),
                 ("a stream carrying the stray", {"heading": "Outcome", "write": True},
                  "## Outcome\n\nA\n\n## O que mudou\n\nB\n"))
        for why, kw, stdin in cases:
            with self.subTest(why=why):
                code, obj = self.run_section(stdin=stdin, **kw)
                self.assertEqual(code, 2, obj)
                self.assertEqual(obj["code"], "sp-stray-heading", obj)

    def test_the_fold_preserves_the_text_closes_the_finding_and_moves_nothing(self):
        before, index_before = self.read_spec(), self.canonical_index()
        self.assertIn("sp-stray-heading", self.validate_codes())

        code, obj = self.run_section(fold="O que mudou")
        self.assertEqual(code, 0, obj)
        self.assertEqual(obj["host"], "Outcome", obj)

        self.assertEqual(self.read_spec(),
                         before.replace("\n## O que mudou\n", "\n### O que mudou\n"),
                         "a fold demotes ONE heading and touches nothing else in the document")
        self.assertNotIn("sp-stray-heading", self.validate_codes())
        self.assertEqual(self.canonical_index(), index_before,
                         "no canonical section may change position across a fold")

        host = parse_sections(body_after_frontmatter(self.read_spec()))["Outcome"]["body"]
        for line in ("### O que mudou", "Quatro linhas que ninguém quer perder.",
                     "## isto não é um heading"):
            self.assertIn(line, host, "the whole stray body belongs to its host now")

    def test_fold_refuses_a_canonical_heading_and_a_name_no_stray_answers(self):
        for why, name, code in (("a canonical section is never a stray", "Outcome",
                                 "sp-fold-not-stray"),
                                ("a typo is answered by the candidate list", "O que ficou",
                                 "sp-fold-unknown-stray")):
            with self.subTest(why=why):
                before = self.read_spec()
                rc, obj = self.run_section(fold=name)
                self.assertEqual(rc, 2, obj)
                self.assertEqual(obj["code"], code, obj)
                self.assertEqual(self.read_spec(), before)


class TheFoldWithNoAnchor(_FoldWorkspace):
    """A stray with no canonical section above it. A fold that "works" here is worse than the
    refusal, because it invents an owner for text whose author never chose one."""

    spec_text = NO_ANCHOR_FIXTURE

    def test_it_refuses_with_its_own_message_and_writes_nothing(self):
        before = self.read_spec()
        code, obj = self.run_section(fold="Preâmbulo órfão")
        self.assertEqual(code, 2, obj)
        self.assertEqual(obj["code"], "sp-fold-no-anchor", obj)
        self.assertEqual(self.read_spec(), before)
        self.assertIn("sp-stray-heading", self.validate_codes())


if __name__ == "__main__":
    unittest.main()
