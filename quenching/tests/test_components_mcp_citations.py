"""A body in an enforced front cites a `cq` verb as its MCP tool, never as the CLI."""
import pathlib
import sys
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.components import mcp_citations

ENFORCED = "skills/quenching-specs/references/develop.md"


def codes(body, path=ENFORCED):
    return [f["code"] for f in mcp_citations.findings(body, {"command": "-", "path": path})]


class CitationForm(unittest.TestCase):
    def test_a_cli_citation_of_a_verb_with_a_tool_is_an_error(self):
        found = mcp_citations.findings("Run `.agents/quenching/bin/cq specs status --spec 3 --json`.",
                                       {"command": "-", "path": ENFORCED})
        self.assertEqual([f["code"] for f in found], ["sk-cq-cli-citation"])
        self.assertEqual(found[0]["severity"], "error")
        self.assertIn("specs_status", found[0]["message"])
        self.assertEqual(found[0]["line"], 1)

    def test_the_reference_fronts_are_enforced_too(self):
        self.assertEqual(codes("cq specs validate --spec 3", "references/specs-develop/artifacts.md"),
                         ["sk-cq-cli-citation"])
        self.assertEqual(codes("cq git commit --subject s", ".agents/skills/quenching-specs/SKILL.md"),
                         ["sk-cq-cli-citation"])

    def test_every_quenching_front_and_shared_reference_is_enforced(self):
        for path in ("skills/quenching-git/references/branch.md",
                     "skills/quenching-knowledge/SKILL.md",
                     "references/git/isolation.md", "references/align/convergence.md",
                     ".agents/quenching/references/knowledge-align/conformance.md"):
            with self.subTest(path):
                self.assertEqual(codes("cq git state --json", path), ["sk-cq-cli-citation"])

    def test_the_tool_form_passes(self):
        body = ("Call `specs_status(spec=<id>)`, then "
                "`components_read(path=\"x.md\", sections=[\"§A\"], rules_only=true)` and "
                "`specs_record(spec=<id>, name=\"run\", fields={\"state\": \"done\"})`; "
                "`specs_status` alone is a mention.")
        self.assertEqual(codes(body), [])

    def test_a_verb_with_no_tool_stays_cli(self):
        for text in ("cq deploy --target . --write", "cq specs migrate --to git",
                     "cq specs claim take 3", "cq codex implement --spec 3", "cq specs serve"):
            with self.subTest(text):
                self.assertEqual(codes(text), [])

    def test_prose_that_names_no_verb_is_not_counted(self):
        self.assertEqual(codes("the cq specs write operations; cq git pr; cq is the launcher"), [])

    def test_a_marked_line_passes(self):
        self.assertEqual(codes("cd w && cq git commit --subject s <!-- cli: root -->"), [])

    def test_a_marker_alone_covers_the_following_fenced_block(self):
        body = "\n".join(["<!-- cli: atomic -->", "```bash",
                          "cq specs section 3 \"A,B\" --write <<'BODY'", "BODY", "```",
                          "", "cq specs validate --spec 3"])
        self.assertEqual(codes(body), ["sk-cq-cli-citation"])

    def test_a_hash_marker_inside_a_fence_covers_its_line(self):
        body = "```bash\ncq git state --json   # cli: root\ncq git base --json\n```"
        self.assertEqual(codes(body), ["sk-cq-cli-citation"])

    def test_a_marker_alone_covers_the_following_paragraph_only(self):
        body = "<!-- cli: by -->\ncq specs record 3 approved\n\ncq specs record 3 run"
        self.assertEqual(codes(body), ["sk-cq-cli-citation"])

    def test_an_unknown_tool_is_an_error(self):
        self.assertEqual(codes("call `specs_inexistente(spec=3)`"), ["sk-mcp-unknown-tool"])

    def test_a_body_outside_the_enforced_fronts_is_not_checked(self):
        for path in ("agents/spec-runner.md", ".claude/skills/my-own/SKILL.md",
                     ".agents/skills/my-own/references/notes.md",
                     "references/align/tool-resolution.md"):
            with self.subTest(path):
                self.assertEqual(codes("cq specs status --spec 3; specs_nope(x)", path), [])


if __name__ == "__main__":
    unittest.main()
