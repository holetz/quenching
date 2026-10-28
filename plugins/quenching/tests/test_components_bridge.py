"""Executable proofs for `cq components bridge`: the Claude Code copy of `.agents/skills`."""
from __future__ import annotations

import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.components.commands import bridge
from quenching.components.commands.cli import main as components_main

SKILL = "---\nname: mlops-comum\ndescription: Shared MLOps rules.\n---\n# Body\n"


class Bridge(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.repo = pathlib.Path(tmp.name)
        skill = self.repo / ".agents" / "skills" / "mlops-comum"
        (skill / "references").mkdir(parents=True)
        (skill / "SKILL.md").write_text(SKILL)
        (skill / "references" / "notes.md").write_text("notes\n")
        self.copy = self.repo / ".claude" / "skills" / "mlops-comum"

    def run_cli(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = components_main(["bridge", "--target", str(self.repo), "--json", *argv])
        return code, json.loads(out.getvalue() or "{}")

    def test_write_copies_the_folder_with_the_marker_and_the_manifest(self):
        code, payload = self.run_cli("--write")
        self.assertEqual((0, 1), (code, payload["skills"]))
        text = (self.copy / "SKILL.md").read_text()
        self.assertTrue(text.startswith("---\nname: mlops-comum\n"))
        self.assertIn(bridge.marker("mlops-comum") + "\n# Body", text)
        self.assertEqual("notes\n", (self.copy / "references" / "notes.md").read_text())
        manifest = json.loads((self.repo / bridge.MANIFEST).read_text())
        self.assertEqual(bridge.VERIFIED_CLAUDE_CODE, manifest["verifiedClaudeCode"])
        self.assertEqual({"mlops-comum/SKILL.md", "mlops-comum/references/notes.md"},
                         set(manifest["files"]))

    def test_check_is_clean_after_write_and_fails_on_drift(self):
        self.run_cli("--write")
        self.assertEqual(0, self.run_cli("--check")[0])
        (self.copy / "SKILL.md").write_text("edited by hand\n")
        code, payload = self.run_cli("--check")
        self.assertEqual(1, code)
        self.assertEqual([{"path": "mlops-comum/SKILL.md", "change": "edited"}], payload["changes"])

    def test_check_fails_on_a_new_source_skill(self):
        self.run_cli("--write")
        other = self.repo / ".agents" / "skills" / "docs-comunicado"
        other.mkdir()
        (other / "SKILL.md").write_text(SKILL.replace("mlops-comum", "docs-comunicado"))
        self.assertEqual(1, self.run_cli("--check")[0])

    def test_orphan_copy_is_removed_on_write(self):
        self.run_cli("--write")
        for path in sorted((self.repo / ".agents" / "skills" / "mlops-comum").rglob("*"),
                           reverse=True):
            path.unlink() if path.is_file() else path.rmdir()
        (self.repo / ".agents" / "skills" / "mlops-comum").rmdir()
        code, payload = self.run_cli("--check")
        self.assertEqual(1, code)
        self.assertTrue(all(c["change"] == "orphan" for c in payload["changes"]))
        self.assertEqual(0, self.run_cli("--write")[0])
        self.assertFalse(self.copy.exists())

    def test_a_folder_the_bridge_did_not_generate_is_never_overwritten(self):
        self.copy.mkdir(parents=True)
        (self.copy / "SKILL.md").write_text("the human's own\n")
        code, _ = self.run_cli("--write")
        self.assertEqual(2, code)
        self.assertEqual("the human's own\n", (self.copy / "SKILL.md").read_text())

    def test_a_file_added_by_hand_to_a_generated_folder_is_drift_and_is_removed(self):
        self.run_cli("--write")
        (self.copy / "extra.md").write_text("hand\n")
        code, payload = self.run_cli("--check")
        self.assertEqual((1, [{"path": "mlops-comum/extra.md", "change": "orphan"}]),
                         (code, payload["changes"]))
        self.run_cli("--write")
        self.assertFalse((self.copy / "extra.md").exists())
        self.assertEqual(0, self.run_cli("--check")[0])

    def test_the_marker_follows_a_crlf_frontmatter(self):
        text = bridge.with_marker("---\r\nname: x\r\n---\r\nBody\r\n", "x")
        self.assertEqual("---\r\nname: x\r\n---\r\n" + bridge.marker("x") + "\r\nBody\r\n", text)


if __name__ == "__main__":
    unittest.main()
