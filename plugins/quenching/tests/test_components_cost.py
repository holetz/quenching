import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401
from quenching.components.commands.cli import DISPATCH, build_parser
from quenching.components.commands.cost import cmd_cost


def surface() -> tuple[pathlib.Path, pathlib.Path]:
    root = pathlib.Path(tempfile.mkdtemp())
    (root / "commands" / "front").mkdir(parents=True)
    (root / "assets" / "references" / "front").mkdir(parents=True)
    return root, root / "assets" / "references" / "front"


class ComponentsCost(unittest.TestCase):
    def test_cost_is_registered_and_the_json_is_deterministic(self):
        root, references = surface()
        reference = references / "rules.md"
        reference.write_text("## Rule\n\nBinding rule.\n\n## Story\n\nRationale.\n", encoding="utf-8")
        (root / "commands" / "front" / "verb.md").write_text(
            "---\ndescription: do it\n---\n\nBody é.\n\n"
            "[rules](${CLAUDE_PLUGIN_ROOT}/assets/references/front/rules.md) §Rule\n",
            encoding="utf-8",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=None, ratchet=None, json=True), str(root))
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["commandCount"], 1)
        row = payload["commands"][0]
        self.assertEqual(row["bodyBytes"], len("\nBody é.\n\n[rules](${CLAUDE_PLUGIN_ROOT}/assets/references/front/rules.md) §Rule".encode()))
        self.assertEqual(row["wholeReferences"], [])
        self.assertEqual(row["sections"], [{"path": "front/rules.md", "heading": "Rule", "bytes": len("Binding rule.".encode())}])
        self.assertEqual(payload, json.loads(output.getvalue()))
        self.assertIn("cost", DISPATCH)
        self.assertEqual(build_parser().parse_args(["cost", "--json"]).cmd, "cost")

    def test_whole_references_are_charged_once_per_command(self):
        root, references = surface()
        (references / "rules.md").write_text("## Rule\n\nWhole.\n", encoding="utf-8")
        body = "\n".join([
            "Body.",
            "[one](${CLAUDE_PLUGIN_ROOT}/assets/references/front/rules.md)",
            "[two](${CLAUDE_PLUGIN_ROOT}/assets/references/front/rules.md)",
            "",
        ])
        (root / "commands" / "front" / "verb.md").write_text(
            "---\ndescription: do it\n---\n\n" + body, encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=None, ratchet=None, json=True), str(root))
        row = json.loads(output.getvalue())["commands"][0]
        self.assertEqual(status, 0)
        self.assertEqual(len(row["wholeReferences"]), 1)
        self.assertEqual(row["wholeReferences"][0]["bytes"], len("## Rule\n\nWhole.\n".encode()))

    def test_missing_section_is_an_error_and_ratchet_blocks_only_growth(self):
        root, references = surface()
        (references / "rules.md").write_text("## Rule\n\nWhole.\n", encoding="utf-8")
        (root / "commands" / "front" / "verb.md").write_text(
            "---\ndescription: do it\n---\n\n"
            "[rules](${CLAUDE_PLUGIN_ROOT}/assets/references/front/rules.md) §Missing\n",
            encoding="utf-8",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=None, ratchet=None, json=True), str(root))
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue())["findings"][0]["code"], "ct-cost-no-section")

        (root / "commands" / "front" / "verb.md").write_text(
            "---\ndescription: do it\n---\n\nBody.\n", encoding="utf-8")
        measured = io.StringIO()
        with contextlib.redirect_stdout(measured):
            self.assertEqual(cmd_cost(SimpleNamespace(path=None, ratchet=None, json=True), str(root)), 0)
        baseline = pathlib.Path(tempfile.mkdtemp()) / "cost.json"
        baseline.write_text(json.dumps({"totalBytes": 0}), encoding="utf-8")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=None, ratchet=str(baseline), json=True), str(root))
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue())["findings"][0]["code"], "ct-cost-regression")


if __name__ == "__main__":
    unittest.main()
