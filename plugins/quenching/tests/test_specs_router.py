"""The specs router names every flow it routes ."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[3]
ROUTER = REPO / "plugins/quenching/commands/specs/specs.md"
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


if __name__ == "__main__":
    unittest.main()
