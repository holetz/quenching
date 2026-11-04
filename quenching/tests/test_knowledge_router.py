"""The knowledge router names every flow it routes ."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
ROUTER = REPO / "quenching/commands/knowledge/knowledge.md"
FLOWS = ('add', 'learn', 'define', 'glossary-backfill', 'import', 'import-memory', 'align', 'status', 'documentation-plan', 'documentation-write', 'documentation-review', 'documentation-build', 'documentation-produce')
TYPED_ONLY = ()


class KnowledgeRouter(unittest.TestCase):
    def setUp(self):
        self.text = ROUTER.read_text(encoding="utf-8")

    def test_every_flow_has_a_row_and_a_reference(self):
        for flow in FLOWS:
            with self.subTest(flow=flow):
                self.assertRegex(self.text, rf"\| `{flow}` \| \[knowledge-flows/{flow}\.md\]")
                ref = REPO / "quenching/assets/references/knowledge-flows" / f"{flow}.md"
                self.assertTrue(ref.is_file())

    def test_typed_only_commands_are_not_rows(self):
        for name in TYPED_ONLY:
            with self.subTest(name=name):
                self.assertIsNone(re.search(rf"\| `{name}` \|", self.text))

    def test_grant_is_the_approved_one(self):
        head = self.text.split("---")[1]
        self.assertIn("allowed-tools: Bash(cq:*), Bash(cq.cmd:*), Read", head)
        self.assertNotIn("disable-model-invocation", head)
        self.assertNotIn("model:", head)


if __name__ == "__main__":
    unittest.main()
