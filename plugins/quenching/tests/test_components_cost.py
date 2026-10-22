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
            "[rules](${CLAUDE_PLUGIN_ROOT}/assets/references/" + "front/rules.md) §Rule\n",
            encoding="utf-8",
        )
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=None, ratchet=None, json=True), str(root))
        payload = json.loads(output.getvalue())
        self.assertEqual(status, 0)
        self.assertEqual(payload["commandCount"], 1)
        row = payload["commands"][0]
        self.assertEqual(row["bodyBytes"], len(("\nBody é.\n\n[rules](${CLAUDE_PLUGIN_ROOT}/assets/references/" + "front/rules.md) §Rule").encode()))
        self.assertEqual(row["wholeReferences"], [])
        self.assertEqual(row["sections"], [{"path": "front/rules.md", "heading": "Rule", "bytes": len("Binding rule.".encode())}])
        self.assertEqual(row["totalBytes"], row["bodyBytes"] + row["sections"][0]["bytes"])
        self.assertEqual(payload["totalBytes"], row["totalBytes"])
        self.assertEqual(payload, json.loads(output.getvalue()))
        self.assertIn("cost", DISPATCH)
        self.assertEqual(build_parser().parse_args(["cost", "--json"]).cmd, "cost")

    def test_whole_references_are_charged_once_per_command(self):
        root, references = surface()
        (references / "rules.md").write_text("## Rule\n\nWhole.\n", encoding="utf-8")
        body = "\n".join([
            "Body.",
            "[one](${CLAUDE_PLUGIN_ROOT}/assets/references/" + "front/rules.md)",
            "[two](${CLAUDE_PLUGIN_ROOT}/assets/references/" + "front/rules.md)",
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
            "[rules](${CLAUDE_PLUGIN_ROOT}/assets/references/" + "front/rules.md) §Missing\n",
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

    def test_non_utf8_ratchet_baseline_is_a_structured_finding(self):
        root, _ = surface()
        (root / "commands" / "front" / "verb.md").write_text(
            "---\ndescription: do it\n---\n\nBody.\n", encoding="utf-8")
        baseline = pathlib.Path(tempfile.mkdtemp()) / "cost.json"
        baseline.write_bytes(b"\xff\xfe")
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=None, ratchet=str(baseline), json=True), str(root))
        self.assertEqual(status, 1)
        self.assertEqual(json.loads(output.getvalue())["findings"][0]["code"], "ct-cost-ratchet")


class CostTargetsThePathItNames(unittest.TestCase):
    def _target(self):
        root, references = surface()
        (references / "r.md").write_text("## Rule\n\nBinding.\n", encoding="utf-8")
        (root / "commands" / "front" / "a.md").write_text(
            "---\ndescription: a\n---\n\nA body.\n\n[r](assets/references/front/r.md) §Rule\n",
            encoding="utf-8")
        (root / "commands" / "front" / "b.md").write_text(
            "---\ndescription: b\n---\n\nB.\n", encoding="utf-8")
        return root

    def _cost(self, path, cwd, ratchet=None):
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_cost(SimpleNamespace(path=str(path) if path else None,
                                              ratchet=ratchet, json=True), str(cwd))
        return status, json.loads(output.getvalue())

    def test_root_commands_dir_and_file_are_measured_from_another_cwd(self):
        target, cwd = self._target(), pathlib.Path(tempfile.mkdtemp())
        (cwd / "commands").mkdir()
        (cwd / "commands" / "other.md").write_text("---\ndescription: o\n---\n\nO.\n",
                                                   encoding="utf-8")
        for path, count in ((target, 2), (target / "commands", 2),
                            (target / "commands" / "front" / "a.md", 1)):
            status, payload = self._cost(path, cwd)
            self.assertEqual(status, 0, path)
            self.assertEqual(payload["commandCount"], count, path)
            self.assertEqual(payload["root"], str(target), path)
        status, payload = self._cost(target / "commands" / "front" / "a.md", cwd)
        self.assertEqual(payload["commands"][0]["sections"][0]["heading"], "Rule")

    def test_ratchet_compares_the_target_not_the_cwd_surface(self):
        target, cwd = self._target(), pathlib.Path(tempfile.mkdtemp())
        _, measured = self._cost(target, cwd)
        baseline = cwd / "b.json"
        baseline.write_text(json.dumps({"totalBytes": measured["totalBytes"] - 1}),
                            encoding="utf-8")
        status, payload = self._cost(target, cwd, ratchet=str(baseline))
        self.assertEqual(status, 1)
        self.assertEqual(payload["findings"][0]["code"], "ct-cost-regression")
        self.assertEqual(payload["findings"][0]["currentBytes"], measured["totalBytes"])

    def test_a_path_with_no_command_is_refused_even_with_a_ratchet(self):
        target, cwd = self._target(), pathlib.Path(tempfile.mkdtemp())
        (cwd / "empty" / "commands").mkdir(parents=True)
        (cwd / "nomd").mkdir()
        (cwd / "nomd" / "x.txt").write_text("x", encoding="utf-8")
        (cwd / "notes.txt").write_text("x", encoding="utf-8")
        baseline = cwd / "b.json"
        baseline.write_text(json.dumps({"totalBytes": 100}), encoding="utf-8")
        for path in (cwd / "missing", cwd / "empty" / "commands", cwd / "empty", cwd / "nomd",
                     cwd / "notes.txt"):
            for ratchet in (None, str(baseline)):
                status, payload = self._cost(path, cwd, ratchet=ratchet)
                self.assertEqual(status, 1, (path, ratchet))
                self.assertEqual(payload["findings"][0]["code"], "sk-no-commands", path)
                self.assertNotIn("ratchet", payload, path)
                self.assertEqual(payload["root"], str(path), path)


if __name__ == "__main__":
    unittest.main()
