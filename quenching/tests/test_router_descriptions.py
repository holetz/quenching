"""The description of a router is a map of intent per flow, in pt-BR and English.

The description is the only text always in context, so it must name every flow of the router's
table in its first sentence, quote at least one pt-BR and one English trigger per flow, quote a
trigger by its second sentence, stay within the portable 1,024 characters and end on a
`Not for:` boundary. The language of a trigger is a heuristic declared here (`PT_WORDS` and the
accented letters); the test proves a candidate exists for every flow, not that the wording is good.
"""
from __future__ import annotations

import pathlib
import re
import unittest

import _paths  # noqa: F401
from quenching.common.frontmatter import parse_frontmatter
from quenching.components.commands.lint import router_flows

SKILLS = pathlib.Path(__file__).resolve().parents[1] / "skills"
CAP = 1024
ROUTERS = ("specs", "git", "knowledge", "components", "design", "ops", "proof", "toolchain",
           "delivery", "security", "opensource")
ALSO = ("align", "handoff")
PT_WORDS = {"de", "do", "da", "um", "uma", "para", "como", "os", "as", "o", "que", "essa", "esse",
            "este", "esta", "no", "na", "estão", "e"}
ACCENTED = re.compile(r"[áàâãéêíóôõúç]")
QUOTED = re.compile(r'"([^"]+)"')


def is_pt(phrase: str) -> bool:
    return bool(ACCENTED.search(phrase)) or any(w in PT_WORDS for w in re.findall(r"[a-zà-ú]+", phrase.lower()))


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def load(name: str) -> tuple[dict, dict]:
    path = SKILLS / f"quenching-{name}" / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    cmd = {"path": str(path), "body": text.split("---", 2)[2]}
    return parse_frontmatter(text), router_flows(cmd)


def segment(description: str, flow: str) -> str:
    """The text of one flow's clause: from `<flow>` (or `<flow> (only when named)`) and its colon to
    the next `;` or the end of the map."""
    body = description.split("Not for:")[0]
    m = re.search(rf"(?<![a-z0-9-]){re.escape(flow)}(?: \(only when named\))?:(.*?)(?:;|$)", body, re.S)
    return m.group(1) if m else ""


class RouterDescriptions(unittest.TestCase):
    def test_thirteen_skills_are_covered(self):
        on_disk = sorted(p.parent.name.removeprefix("quenching-") for p in SKILLS.glob("*/SKILL.md"))
        self.assertEqual(sorted(ROUTERS + ALSO), on_disk)

    def test_every_description_is_within_the_portable_cap_and_ends_on_the_boundary(self):
        for name in ROUTERS + ALSO:
            with self.subTest(skill=name):
                description = str(load(name)[0]["description"])
                self.assertLessEqual(len(description), CAP)
                self.assertIn("Not for:", description)
                self.assertTrue(description.rstrip().endswith("."))
                self.assertEqual(description.count("Not for:"), 1)
                self.assertNotIn("Not for:", description.split("Not for:")[0])

    def test_first_sentence_names_every_flow_and_a_trigger_comes_by_the_second(self):
        for name in ROUTERS:
            with self.subTest(skill=name):
                fm, flows = load(name)
                self.assertTrue(flows, "a router has a table of flows")
                parts = sentences(str(fm["description"]))
                first = parts[0]
                for flow in flows:
                    self.assertRegex(first, rf"(?<![a-z0-9-]){re.escape(flow)}(?![a-z0-9-])", flow)
                self.assertTrue(QUOTED.search(" ".join(parts[:2])), "a trigger by the second sentence")
                self.assertNotIn("disable-model-invocation", fm)

    def test_every_flow_has_a_pt_br_and_an_english_trigger(self):
        for name in ROUTERS:
            fm, flows = load(name)
            description = str(fm["description"])
            for flow in flows:
                with self.subTest(skill=name, flow=flow):
                    phrases = QUOTED.findall(segment(description, flow))
                    self.assertTrue(any(is_pt(p) for p in phrases), f"no pt-BR trigger for {flow}")
                    self.assertTrue(any(not is_pt(p) for p in phrases), f"no English trigger for {flow}")

    def test_the_flowless_skills_carry_both_languages(self):
        for name in ALSO:
            with self.subTest(skill=name):
                description = str(load(name)[0]["description"])
                phrases = QUOTED.findall(description)
                self.assertTrue(any(is_pt(p) for p in phrases))
                self.assertTrue(any(not is_pt(p) for p in phrases))
                self.assertTrue(QUOTED.search(" ".join(sentences(description)[:2])))

    def test_the_check_can_fail(self):
        self.assertFalse(is_pt("open a PR"))
        self.assertTrue(is_pt("abrir um PR"))
        self.assertEqual(segment('Run one x flow: a, b. a: "um"; b: "dois". Not for: z.', "b"), ' "dois". ')


if __name__ == "__main__":
    unittest.main()
