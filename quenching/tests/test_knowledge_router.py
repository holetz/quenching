"""The knowledge router names every flow it routes ."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
ROUTER = REPO / "quenching/skills/quenching-knowledge/SKILL.md"
FLOWS = ('add', 'learn', 'define', 'glossary-backfill', 'import', 'import-memory', 'align', 'status', 'documentation-plan', 'documentation-write', 'documentation-review', 'documentation-build', 'documentation-produce')
EXPLICIT_MENTION = ()


def covered(tool, granted):
    """A tool is covered when granted verbatim or under a broader `Bash(<prefix>:*)`."""
    entries = [t.strip() for t in re.split(r",\s*(?![^()]*\))", granted)]
    if tool in entries:
        return True
    if not tool.startswith("Bash("):
        return False
    if "Bash" in entries:
        return True
    cmd = tool[len("Bash("):-1]
    for entry in entries:
        if entry.startswith("Bash(") and entry.endswith(":*)"):
            prefix = entry[len("Bash("):-3]
            if cmd.startswith(prefix + " ") or cmd.startswith(prefix + ":"):
                return True
    return False


class KnowledgeRouter(unittest.TestCase):
    def setUp(self):
        self.text = ROUTER.read_text(encoding="utf-8")

    def test_every_flow_has_a_row_and_a_reference(self):
        for flow in FLOWS:
            with self.subTest(flow=flow):
                self.assertRegex(self.text, rf"\| `{flow}` \| \[references/{flow}\.md\]\(\.agents/skills/quenching-knowledge/references/{flow}\.md\)")
                ref = ROUTER.parent / "references" / f"{flow}.md"
                self.assertTrue(ref.is_file())

    def test_unscoped_bash_states_its_reason(self):
        front = self.text.split("---")[1]
        if re.search(r"(^|, )Bash(,|$)", front):
            self.assertIn("**Why `Bash` is unrestricted here.**", self.text)

    def test_grant_is_the_union_of_the_flows(self):
        front = self.text.split("---")[1]
        granted = re.search(r"^allowed-tools: (.*)$", front, re.M).group(1)
        self.assertNotIn("disable-model-invocation", front)
        for flow in FLOWS:
            ref = (ROUTER.parent / "references" / f"{flow}.md").read_text(encoding="utf-8")
            tools = re.search(r"^allowed-tools: (.*)$", ref, re.M).group(1)
            for tool in re.split(r",\s*(?![^()]*\))", tools):
                with self.subTest(flow=flow, tool=tool):
                    cmd = tool.strip()
                    self.assertTrue(covered(cmd, granted), cmd)


if __name__ == "__main__":
    unittest.main()
