"""`/handoff` closes a session with a handoff the next one can actually find.

Three claims, each silent when it goes false: the body writes the handoff through the spec store
instead of a temp file, the grant admits exactly the `cq specs` verbs that takes, and the block it
prints carries a locator, the command that reads it and a prompt — with one spec id and one name
in all three, or the next session follows a dead path.

The four generated copies are the distributions' business (`test_commands_*`); this file reads the
source the deploy copies from.
"""
import pathlib
import re
import unittest

REPO = pathlib.Path(__file__).resolve().parents[2]
BODY = REPO / "quenching/commands/handoff.md"
LOCATOR = re.compile(r"quenching:specs/artifacts/(?P<owner>[^/\s]+)/(?P<name>[\w.-]+\.md)")
READ = re.compile(r"cq specs artifact read (?:--spec (?P<spec>\d+) )?--name (?P<name>[\w.-]+)")


def frontmatter(text: str) -> str:
    """The `---` block, or the empty string when the body carries none."""
    match = re.match(r"---\n(.*?)\n---\n", text, re.DOTALL)
    return match.group(1) if match else ""


def granted(text: str) -> str:
    for line in frontmatter(text).splitlines():
        if line.startswith("allowed-tools:"):
            return line.split(":", 1)[1].strip()
    return ""


def block(text: str) -> str:
    """The one fenced block that prints the direction: the fence holding `## Handoff`."""
    for fence in re.findall(r"```[a-z]*\n(.*?)```", text, re.DOTALL):
        if "## Handoff" in fence:
            return fence
    return ""


class TheBodySendsTheHandoffThroughTheStore(unittest.TestCase):
    def setUp(self):
        self.text = BODY.read_text(encoding="utf-8")

    def test_it_no_longer_invents_a_temp_path(self):
        self.assertNotIn("mktemp", self.text)
        self.assertNotIn("/tmp", self.text)

    def test_the_draft_lands_where_the_fallback_lives(self):
        # One path for the draft and for the no-store case, or the fallback points at nothing.
        self.assertIn(".quenching/handoff/<name>", self.text)
        self.assertIn("--from .quenching/handoff/<name>", self.text)

    def test_it_stores_beside_the_spec_and_sends_it(self):
        self.assertIn("cq specs artifact write --spec <id> --name <name>", self.text)
        self.assertIn(".agents/quenching/bin/cq specs push", self.text)
        self.assertIn("cq specs artifact read --spec <id> --name <name>", self.text)
        self.assertIn("specs/artifacts/_handoffs/", self.text)   # the no-spec destination

    def test_it_resolves_the_spec_and_never_invents_one(self):
        self.assertIn("cq specs find --branch", self.text)
        self.assertIn("no spec", self.text)

    def test_a_refusal_that_is_not_the_store_stays_a_failure(self):
        for code in ("sp-artifact-unsupported", "sp-artifact-no-store"):
            self.assertIn(code, self.text)
        self.assertIn("not sent — .agents/quenching/bin/cq specs push", self.text)


class TheGrantIsNarrow(unittest.TestCase):
    def setUp(self):
        self.text = BODY.read_text(encoding="utf-8")
        self.tools = granted(self.text)

    def test_it_names_the_three_verbs_it_runs(self):
        for verb in ("cq specs artifact", "cq specs find", "cq specs push"):
            self.assertIn(f"Bash({verb}:*)", self.tools)

    def test_it_grants_no_shell_it_does_not_use(self):
        self.assertNotIn("mktemp", self.tools)
        self.assertNotIn("Bash(cq:*)", self.tools)       # the unscoped shortcut this replaces
        self.assertNotIn("AskUserQuestion", self.tools)  # no confirmation gate in the body


class TheDirectionBlock(unittest.TestCase):
    def setUp(self):
        self.text = BODY.read_text(encoding="utf-8")
        self.block = block(self.text)

    def test_the_block_exists_and_opens_with_its_heading(self):
        self.assertTrue(self.block, "no fenced block carries `## Handoff`")
        self.assertTrue(self.block.startswith("## Handoff"))

    def test_it_carries_locator_read_command_and_prompt(self):
        locator = LOCATOR.search(self.block)
        read = READ.search(self.block)
        self.assertIsNotNone(locator, self.block)
        self.assertIsNotNone(read, self.block)
        self.assertIn("/quenching-specs-execute", self.block)

    def test_all_three_fields_name_the_same_artifact(self):
        locator = LOCATOR.search(self.block)
        read = READ.search(self.block)
        prompt = re.search(r"execute (\d+)", self.block)
        self.assertEqual(locator.group("owner"), read.group("spec"), self.block)
        self.assertEqual(locator.group("owner"), prompt.group(1), self.block)
        self.assertEqual(locator.group("name"), read.group("name"), self.block)

    def test_the_labels_follow_the_conversation_language(self):
        # The STRUCTURE is literal; the words are the target's. Stating the rule is what keeps a
        # pt-BR repository from printing English labels to its humans.
        self.assertIn("conversation's language", self.text)
        self.assertIn("Cole numa sessão nova:", self.block)

    def test_every_substitution_is_stated(self):
        for marker in ("nenhuma spec está atrelada", "não enviado", "só local"):
            self.assertIn(marker, self.text)


if __name__ == "__main__":
    unittest.main()
