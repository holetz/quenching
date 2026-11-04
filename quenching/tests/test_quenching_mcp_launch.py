"""The console scripts must work from an installed, asset-preserving layout."""
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import tomllib
import unittest

PLUGIN = Path(__file__).resolve().parents[1]


class LaunchTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory()
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name)
        cls.package = cls.root / "quenching_plugin"
        shutil.copytree(PLUGIN, cls.package, ignore=shutil.ignore_patterns("__pycache__"))
        shutil.copyfile(PLUGIN / "assets/bin/quenching_launch.py", cls.package / "launch.py")

    def invoke(self, script, args=(), requests=""):
        return subprocess.run(
            [sys.executable, "-c", f"from quenching_plugin.launch import {script}; "
             f"raise SystemExit({script}())", *args],
            cwd=self.root, input=requests, text=True, capture_output=True, timeout=30)

    def test_console_metadata_and_version(self):
        config = tomllib.loads((PLUGIN / "pyproject.toml").read_text())
        self.assertEqual(config["project"]["scripts"], {
            "cq": "quenching_plugin.launch:cq", "quenching-mcp": "quenching_plugin.launch:mcp"})
        self.assertEqual(config["project"]["dependencies"], [])
        result = self.invoke("cq", ["--version"])
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout.strip(), (PLUGIN / "VERSION").read_text().strip())

    def test_stdio_catalog_and_packaged_reference(self):
        uri = "quenching://references/git/commit.md"
        requests = [
            {"jsonrpc": "2.0", "id": 1, "method": "initialize", "params": {}},
            {"jsonrpc": "2.0", "id": 2, "method": "tools/list", "params": {}},
            {"jsonrpc": "2.0", "id": 3, "method": "resources/read", "params": {"uri": uri}},
        ]
        result = self.invoke("mcp", ["--root", str(self.root)],
                             "\n".join(map(json.dumps, requests)) + "\n")
        self.assertEqual(result.returncode, 0, result.stderr)
        replies = {item["id"]: item for item in map(json.loads, result.stdout.splitlines())}
        self.assertEqual(replies[1]["result"]["serverInfo"]["name"], "quenching")
        names = {item["name"] for item in replies[2]["result"]["tools"]}
        self.assertIn("components_read", names)
        self.assertIn("specs_status", names)
        self.assertIn("git_commit", names)
        self.assertIn("Commit", replies[3]["result"]["contents"][0]["text"])

    def test_cli_preserves_usage_exit(self):
        result = self.invoke("cq", ["not-a-pillar"])
        self.assertEqual(result.returncode, 3)
        self.assertNotIn("Traceback", result.stderr)


if __name__ == "__main__":
    unittest.main()
