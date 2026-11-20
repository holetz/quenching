"""`/quenching-handoff` closes a session with a handoff the next one can actually find.

Three claims about the body, each silent when it goes false: it reads the facts and stores the
handoff through `cq specs handoff` instead of a temp file, the grant admits exactly the verbs it
takes, and the block it prints carries a locator, the command that reads it and a prompt — with one
spec id and one name in all three, or the next session follows a dead path. The verb itself is
`test_specs_handoff.py`; the four generated copies are the distributions' business.
"""
import pathlib
import re
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring

REPO = pathlib.Path(__file__).resolve().parents[2]
BODY = REPO / "quenching/skills/quenching-handoff/SKILL.md"
TEMPLATE = REPO / "quenching/skills/quenching-handoff/references/template.md"
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


class TheBodySendsTheHandoffThroughTheVerb(unittest.TestCase):
    def setUp(self):
        self.text = BODY.read_text(encoding="utf-8")

    def test_it_no_longer_invents_a_temp_path(self):
        self.assertNotIn("mktemp", self.text)
        self.assertNotIn("/tmp", self.text)

    def test_the_draft_lands_where_the_fallback_lives(self):
        self.assertIn(".quenching/handoff/<name>", self.text)
        self.assertIn("--from .quenching/handoff/<name>", self.text)

    def test_it_reads_the_facts_and_stores_through_one_verb(self):
        self.assertIn(".agents/quenching/bin/cq specs handoff facts --json", self.text)
        self.assertIn(".agents/quenching/bin/cq specs handoff write --from", self.text)
        self.assertIn("--push", self.text)
        self.assertIn("specs/artifacts/_handoffs/", self.text)   # the no-spec destination

    def test_it_follows_the_shared_template(self):
        self.assertIn(".agents/skills/quenching-handoff/references/template.md", self.text)
        self.assertTrue(TEMPLATE.is_file())

    def test_it_never_invents_a_spec(self):
        self.assertIn("never an invented one", self.text)

    def test_a_refusal_that_is_not_the_store_stays_a_failure(self):
        for code in ("sp-artifact-unsupported", "sp-artifact-no-store", "sp-handoff-incomplete"):
            self.assertIn(code, self.text)
        self.assertIn("never silently becomes the fallback", self.text)

    def test_it_names_the_cold_door(self):
        self.assertIn("/quenching-cache handoff", self.text)


class TheTemplateCarriesTheRequiredSections(unittest.TestCase):
    def test_the_sections_the_verb_requires_are_headings_of_the_template(self):
        from quenching.specs.commands.handoff import REQUIRED
        text = TEMPLATE.read_text(encoding="utf-8")
        for need in REQUIRED:
            self.assertRegex(text, rf"(?m)^{re.escape(need)}")


class TheGrantIsNarrow(unittest.TestCase):
    def setUp(self):
        self.text = BODY.read_text(encoding="utf-8")
        self.tools = granted(self.text)

    def test_it_names_the_verbs_it_runs(self):
        for verb in ("cq specs handoff", "cq specs artifact"):
            self.assertIn(f"Bash({verb}:*)", self.tools)

    def test_it_grants_no_shell_it_does_not_use(self):
        self.assertNotIn("mktemp", self.tools)
        self.assertNotIn("Bash(cq:*)", self.tools)
        self.assertNotIn("AskUserQuestion", self.tools)


class TheDirectionBlock(unittest.TestCase):
    def setUp(self):
        self.text = BODY.read_text(encoding="utf-8")
        self.block = block(self.text)

    def test_the_block_exists_and_opens_with_its_heading(self):
        self.assertTrue(self.block, "no fenced block carries `## Handoff`")
        self.assertTrue(self.block.startswith("## Handoff"))

    def test_all_three_fields_name_the_same_artifact(self):
        locator = LOCATOR.search(self.block)
        read = READ.search(self.block)
        prompt = re.search(r"execute (\d+)", self.block)
        self.assertEqual(locator.group("owner"), read.group("spec"), self.block)
        self.assertEqual(locator.group("owner"), prompt.group(1), self.block)
        self.assertEqual(locator.group("name"), read.group("name"), self.block)

    def test_the_example_is_what_the_verb_prints(self):
        from quenching.specs.commands.handoff import direction
        name = LOCATOR.search(self.block).group("name")
        shown = direction("pt", f"quenching:specs/artifacts/2138/{name}",
                          f".agents/quenching/bin/cq specs artifact read --spec 2138 --name {name}",
                          2138, sent=True, local=False)
        self.assertEqual(shown["block"] + "\n", self.block)

    def test_every_substitution_is_stated(self):
        self.assertIn("conversation's language", self.text)
        for marker in ("nenhuma spec está atrelada", "não enviado", "só local"):
            self.assertIn(marker, self.text)


if __name__ == "__main__":
    unittest.main()
