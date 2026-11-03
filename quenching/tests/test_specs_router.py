"""The specs router names every flow it routes ."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
ROUTER = REPO / "quenching/commands/specs/specs.md"
FLOWS = ("create", "develop", "execute", "conclude", "triage", "status", "orchestrate")
TYPED_ONLY = ("autopilot", "improve", "board")


class SpecsRouter(unittest.TestCase):
    def setUp(self):
        self.text = ROUTER.read_text(encoding="utf-8")

    def test_every_flow_has_a_row(self):
        for flow in FLOWS:
            with self.subTest(flow=flow):
                self.assertRegex(self.text, rf"\| `{flow}` \| \[specs-flows/{flow}\.md\]")

    def test_typed_only_commands_are_not_rows(self):
        for name in TYPED_ONLY:
            with self.subTest(name=name):
                self.assertIsNone(re.search(rf"\| `{name}` \|", self.text))

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
