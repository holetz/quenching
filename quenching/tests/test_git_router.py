"""The git router names every flow it routes ."""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
ROUTER = REPO / "quenching/skills/quenching-git/SKILL.md"
FLOWS = ('branch', 'commit', 'merge', 'sync', 'pr-create', 'pr-review', 'pr-status',
         'cleanup', 'commit-incremental', 'push', 'revert')
EXPLICIT_MENTION = ('push', 'revert', 'cleanup')


def covered(tool, granted):
    """A tool is covered when granted verbatim or under a broader `Bash(<prefix>:*)`."""
    entries = [t.strip() for t in re.split(r",\s*(?![^()]*\))", granted)]
    if tool in entries:
        return True
    if not tool.startswith("Bash("):
        return False
    cmd = tool[len("Bash("):-1]
    for entry in entries:
        if entry.startswith("Bash(") and entry.endswith(":*)"):
            prefix = entry[len("Bash("):-3]
            if cmd.startswith(prefix + " ") or cmd.startswith(prefix + ":"):
                return True
    return False


class GitRouter(unittest.TestCase):
    def setUp(self):
        self.text = ROUTER.read_text(encoding="utf-8")

    def test_every_flow_has_a_row_and_a_reference(self):
        for flow in FLOWS:
            with self.subTest(flow=flow):
                self.assertRegex(self.text, rf"\| `{flow}` \| \[references/{flow}\.md\]\(\.agents/skills/quenching-git/references/{flow}\.md\)")
                ref = ROUTER.parent / "references" / f"{flow}.md"
                self.assertTrue(ref.is_file())

    def test_explicit_mention_flows_are_stated(self):
        text = " ".join(self.text.split())
        self.assertIn("`push`, `revert` and `cleanup` run only on an explicit mention", text)

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

    def test_commit_hook_block_does_not_travel(self):
        self.assertNotIn("hooks:", self.text.split("---")[1])


if __name__ == "__main__":
    unittest.main()
