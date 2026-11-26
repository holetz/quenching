"""The per-user bootstrap the deploy generates in `.quenching/bootstrap/`: written, never run, kept
out of the manifest's `files`, and not drift when a clone lacks it."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

from quenching.deploy import bootstrap  # noqa: E402
from quenching.deploy.cli import main as deploy_main  # noqa: E402

DIR = ".quenching/bootstrap"


class Generated(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.target = pathlib.Path(tmp.name)
        subprocess.run(["git", "-C", str(self.target), "init", "-q"], check=True,
                       capture_output=True)
        xdg = pathlib.Path(tempfile.mkdtemp(dir=tmp.name, prefix="xdg-"))
        env = mock.patch.dict(os.environ, {"XDG_CONFIG_HOME": str(xdg), "OPENCODE_CONFIG": ""})
        env.start()
        self.addCleanup(env.stop)
        precompile = mock.patch("quenching.deploy.cli._precompile", return_value=None)
        precompile.start()
        self.addCleanup(precompile.stop)

    def deploy(self, *argv):
        out = io.StringIO()
        with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
            code = deploy_main(["--target", str(self.target), *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def manifest(self):
        return json.loads((self.target / ".agents/.quenching-deploy.json").read_text(encoding="utf-8"))

    def test_a_write_generates_the_three_files_and_runs_none_of_them(self):
        code, payload = self.deploy("--write", "--harness", "claude")
        self.assertEqual(0, code, payload)
        for rel in bootstrap.FILES:
            self.assertTrue((self.target / rel).is_file(), rel)
        self.assertEqual([], [p for p in (self.target / DIR).iterdir() if p.is_dir()])
        config = (self.target / bootstrap.SCRIPT).read_text(encoding="utf-8")
        self.assertIn('"harnesses": ["claude"]', config)
        self.assertNotIn(bootstrap.PLACEHOLDER, config)
        if os.name != "nt":
            self.assertTrue(os.access(self.target / bootstrap.SH, os.X_OK))
        self.assertIn(b"\r\n", (self.target / bootstrap.CMD).read_bytes())
        self.assertTrue(any("bootstrap.sh --check" in line for line in payload["suggestions"]))

    def test_the_manifest_lists_them_outside_files(self):
        self.deploy("--write", "--harness", "claude")
        manifest = self.manifest()
        self.assertEqual(sorted(bootstrap.FILES), manifest["bootstrap"])
        self.assertFalse([rel for rel in manifest["files"] if rel.startswith(".quenching/")])

    def test_a_clone_without_them_is_not_drift_and_a_stale_copy_is(self):
        self.deploy("--write", "--harness", "claude")
        for rel in bootstrap.FILES:
            (self.target / rel).unlink()
        code, payload = self.deploy("--check")
        self.assertEqual(0, code, payload["changes"])
        self.deploy("--write")
        (self.target / bootstrap.SCRIPT).write_text("# stale\n", encoding="utf-8")
        code, payload = self.deploy("--check")
        self.assertEqual(1, code)
        self.assertEqual([{"path": bootstrap.SCRIPT, "change": "update"}], payload["changes"])
        self.assertEqual(0, self.deploy("--write")[0])
        self.assertEqual(0, self.deploy("--check")[0])

    def test_the_vscode_flag_follows_the_declared_projection(self):
        config = self.target / ".agents/quenching.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"shared": {"projections": ["github"]}}), encoding="utf-8")
        self.deploy("--write", "--harness", "claude")
        text = (self.target / bootstrap.SCRIPT).read_text(encoding="utf-8")
        self.assertIn('"vscode": true', text)

    def test_the_same_inputs_render_the_same_bytes(self):
        source = pathlib.Path(__file__).resolve().parent.parent
        first = bootstrap.files(source, "1.0.0", ["opencode", "claude"], False)
        second = bootstrap.files(source, "1.0.0", ["claude", "opencode"], False)
        self.assertEqual(first, second)

    def test_remove_deletes_them_and_keeps_the_backups(self):
        self.deploy("--write", "--harness", "claude")
        backups = self.target / DIR / "backups" / "20260101T000000"
        backups.mkdir(parents=True)
        (backups / "saved").write_text("mine", encoding="utf-8")
        code, payload = self.deploy("--remove", "--write")
        self.assertEqual(0, code, payload)
        for rel in bootstrap.FILES:
            self.assertFalse((self.target / rel).exists(), rel)
        self.assertTrue((backups / "saved").is_file())


if __name__ == "__main__":
    unittest.main()
