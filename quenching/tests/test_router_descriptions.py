"""The description of a router names its flows; the body carries the map of intent per flow.

The description is the only text always in context, so it must name every flow of the router's
table in its first sentence, stay within 250 characters and end on a `Not for:` boundary. The map
of pt-BR and English triggers per flow lives in the body's `## Triggers by flow`, where it is read
only once the skill runs: at least one trigger of each language per flow. The language of a trigger is a heuristic declared here (`PT_WORDS` and the
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
CAP = 250
ROUTERS = ("specs", "git", "knowledge", "components")
ALSO = ("align", "handoff")
PT_WORDS = {"de", "do", "da", "um", "uma", "para", "como", "os", "as", "o", "que", "essa", "esse",
            "este", "esta", "no", "na", "estão", "e"}
ACCENTED = re.compile(r"[áàâãéêíóôõúç]")
QUOTED = re.compile(r'"([^"]+)"')


def is_pt(phrase: str) -> bool:
    return bool(ACCENTED.search(phrase)) or any(w in PT_WORDS for w in re.findall(r"[a-zà-ú]+", phrase.lower()))


def sentences(text: str) -> list[str]:
    return [s for s in re.split(r"(?<=[.!?])\s+", text.strip()) if s]


def triggers_map(body: str) -> str:
    """The body's `## Triggers by flow` section, up to the next heading."""
    m = re.search(r"^## Triggers by flow\n(.*?)(?=^## )", body, re.S | re.M)
    return m.group(1) if m else ""


def load(name: str) -> tuple[dict, dict]:
    path = SKILLS / f"quenching-{name}" / "SKILL.md"
    text = path.read_text(encoding="utf-8")
    cmd = {"path": str(path), "body": text.split("---", 2)[2]}
    return parse_frontmatter(text), router_flows(cmd)


def body_of(name: str) -> str:
    return (SKILLS / f"quenching-{name}" / "SKILL.md").read_text(encoding="utf-8").split("---", 2)[2]


def segment(description: str, flow: str) -> str:
    """The text of one flow's clause: from `<flow>` (or `<flow> (only when named)`) and its colon to
    the next `;` or the end of the map."""
    body = description.split("Not for:")[0]
    m = re.search(rf"(?<![a-z0-9-]){re.escape(flow)}(?: \(only when named\))?:(.*?)(?:;|$)", body, re.S)
    return m.group(1) if m else ""


class RouterDescriptions(unittest.TestCase):
    def test_six_skills_are_covered(self):
        on_disk = sorted(p.parent.name.removeprefix("quenching-") for p in SKILLS.glob("*/SKILL.md"))
        self.assertEqual(sorted(ROUTERS + ALSO), on_disk)

    def test_every_description_is_within_the_resident_budget_and_ends_on_the_boundary(self):
        for name in ROUTERS + ALSO:
            with self.subTest(skill=name):
                description = str(load(name)[0]["description"])
                self.assertLessEqual(len(description), CAP)
                self.assertIn("Not for:", description)
                self.assertTrue(description.rstrip().endswith("."))
                self.assertEqual(description.count("Not for:"), 1)
                self.assertNotIn("Not for:", description.split("Not for:")[0])

    def test_first_sentence_names_every_flow(self):
        for name in ROUTERS:
            with self.subTest(skill=name):
                fm, flows = load(name)
                self.assertTrue(flows, "a router has a table of flows")
                parts = sentences(str(fm["description"]))
                first = parts[0]
                for flow in flows:
                    self.assertRegex(first, rf"(?<![a-z0-9-]){re.escape(flow)}(?![a-z0-9-])", flow)
                self.assertNotIn("disable-model-invocation", fm)

    def test_every_flow_has_a_pt_br_and_an_english_trigger(self):
        for name in ROUTERS:
            fm, flows = load(name)
            description = triggers_map(body_of(name))
            self.assertTrue(description, "the body carries a `## Triggers by flow` map")
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

    def test_components_describes_itself_as_the_rule_book_and_the_minting(self):
        description = str(load("components")[0]["description"])
        flows = load("components")[1]
        self.assertLessEqual(len(description), CAP)
        for flow in ("rules", "entrypoint-new", "layer-new", "genre-new"):
            self.assertIn(flow, flows)
        head = description.split("Not for:")[0]
        self.assertRegex(head, r"Rules and creation")
        self.assertRegex(head, r"[Rr]ead before editing")

    def test_rules_flow_is_read_only_and_its_grant_is_inside_the_router_union(self):
        base = SKILLS / "quenching-components"
        ref = (base / "references" / "rules.md").read_text(encoding="utf-8")
        tools = re.search(r"^allowed-tools: (.*)$", ref, re.M).group(1)
        self.assertNotRegex(tools, r"\bWrite\b|\bEdit\b")
        router = re.search(r"^allowed-tools: (.*)$", (base / "SKILL.md").read_text(encoding="utf-8"), re.M).group(1)
        for tool in re.split(r",\s*(?![^()]*\))", tools):
            self.assertIn(tool.strip(), router)

    def test_the_check_can_fail(self):
        self.assertFalse(is_pt("open a PR"))
        self.assertTrue(is_pt("abrir um PR"))
        self.assertEqual(segment('Run one x flow: a, b. a: "um"; b: "dois". Not for: z.', "b"), ' "dois". ')


if __name__ == "__main__":
    unittest.main()
