"""The specs router names every flow it routes ."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
ROUTER = REPO / "quenching/skills/quenching-specs/SKILL.md"
FLOWS = ("create", "develop", "execute", "conclude", "triage", "status", "orchestrate", "improve", "board", "autopilot")
EXPLICIT_MENTION = ("autopilot",)


class SpecsRouter(unittest.TestCase):
    def setUp(self):
        self.text = ROUTER.read_text(encoding="utf-8")

    def test_every_flow_has_a_row(self):
        for flow in FLOWS:
            with self.subTest(flow=flow):
                self.assertRegex(self.text, rf"\| `{flow}` \| \[references/{flow}\.md\]\(\.agents/skills/quenching-specs/references/{flow}\.md\)")

    def test_every_flow_reference_exists_and_declares_its_grant(self):
        for flow in FLOWS:
            with self.subTest(flow=flow):
                ref = ROUTER.parent / "references" / f"{flow}.md"
                self.assertTrue(ref.is_file())
                self.assertRegex(ref.read_text(encoding="utf-8"), r"\A---\nallowed-tools: ")

    def test_router_grant_covers_every_flow_grant(self):
        front = self.text.split("---")[1]
        granted = re.search(r"^allowed-tools: (.*)$", front, re.M).group(1)
        names = {t.split("(")[0].strip() for t in granted.split(",")}
        self.assertIn("Bash", names)
        for flow in FLOWS:
            ref = (ROUTER.parent / "references" / f"{flow}.md").read_text(encoding="utf-8")
            tools = re.search(r"^allowed-tools: (.*)$", ref, re.M).group(1)
            for tool in tools.split(","):
                with self.subTest(flow=flow, tool=tool.strip()):
                    self.assertIn(tool.split("(")[0].strip(), names)

    def test_unscoped_bash_states_its_reason(self):
        self.assertIn("**Why `Bash` is unrestricted here.**", self.text)

    def test_explicit_mention_flows_are_stated(self):
        text = " ".join(self.text.split())
        for name in EXPLICIT_MENTION:
            with self.subTest(name=name):
                self.assertIn(f"`{name}` runs only on an explicit mention", text)

    def test_declared_autonomy_is_explicit_and_the_one_invariant_exception(self):
        text = " ".join(self.text.split())

        self.assertIn("## Declared autonomy", text)
        self.assertIn("recognised, never inferred", text)
        self.assertIn('"Execute isto" is not a declaration', text)
        self.assertIn("`orchestrator-forced`", text)
        self.assertIn("ends with **one report**", text)
        self.assertIn("except under §Declared autonomy", text)


if __name__ == "__main__":
    unittest.main()
