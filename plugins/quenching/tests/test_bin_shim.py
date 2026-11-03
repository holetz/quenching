"""`bin/cq` — the shim Claude Code finds on PATH, and the one thing no other test would catch.

The shim is the only file in this plugin whose whole job is to be *equivalent* to another file.
Nothing about it is visible from the outside until a session tries a bare `cq`, and by then the
session that introduced the drift is over — the plugin registry, and the PATH entry with it, are
built at session start.

So the load-bearing assertion here is not "it runs": it is that invoking through the shim and
invoking `assets/bin/cq` directly produce the *same bytes and the same exit code*. That is the
claim `bin/cq`'s docstring makes about `os.execv`, and it is the one that goes silently false if
anyone ever rewrites it as an import — `assets/bin/cq` reaches its `quenching` package through the
`sys.path[0]` Python builds from the script's directory, which under any in-process form would be
`bin/`.
"""

import os
import json
import pathlib
import subprocess
import sys
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
REPO_ROOT = PLUGIN_ROOT.parent.parent
SHIM = PLUGIN_ROOT / "bin" / "cq"
REAL = PLUGIN_ROOT / "assets" / "bin" / "cq"
VERSION = (PLUGIN_ROOT / "VERSION").read_text().strip()


class ThePathShim(unittest.TestCase):
    def test_it_is_there_and_executable(self):
        """Claude Code executes it off PATH, so the bit is the feature, not a nicety."""
        self.assertTrue(SHIM.is_file(), f"the shim does not resolve: {SHIM}")
        self.assertTrue(os.access(SHIM, os.X_OK), f"the shim carries no execute bit: {SHIM}")

    def test_the_windows_launcher_forwards_arguments_and_the_exit_code(self):
        """`cq.cmd` is not runnable here, so its text carries the contract: the real entry point, `%*`, the exit code."""
        source = (PLUGIN_ROOT / "bin" / "cq.cmd").read_text(encoding="utf-8")
        self.assertIn("..\\assets\\bin\\cq", source)
        self.assertIn("py -3", source)
        self.assertIn("%*", source)
        self.assertIn("exit /b %ERRORLEVEL%", source)
        self.assertNotIn("execv", source)

    def test_it_exposes_fifteen_pillars(self):
        run = subprocess.run([sys.executable, str(REAL), "--help"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        choices = next(line.strip() for line in run.stdout.splitlines()
                       if line.strip().startswith("{") and line.strip().endswith("}"))
        pillars = set(choices[1:-1].split(","))
        self.assertEqual(15, len(pillars))
        self.assertEqual({"specs", "knowledge", "design", "components", "ops", "proof", "git",
                          "toolchain", "delivery", "security", "opensource", "codex", "portal", "config", "mcp"}, pillars)

    def test_it_answers_the_version_lockstep(self):
        run = subprocess.run([str(SHIM), "--version"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), VERSION)

    def test_every_published_version_surface_is_in_lockstep(self):
        """Every published consumer must receive the same version."""
        claude_manifest = json.loads(
            (PLUGIN_ROOT / ".claude-plugin" / "plugin.json").read_text(encoding="utf-8"))
        marketplace = json.loads(
            (REPO_ROOT / ".claude-plugin" / "marketplace.json").read_text(encoding="utf-8"))
        source = {
            "plugins/quenching/VERSION": VERSION,
            "plugins/quenching/.claude-plugin/plugin.json": claude_manifest["version"],
        }
        self.assertEqual({VERSION}, set(source.values()), source)
        marketplace_versions = {item["name"]: item["version"] for item in marketplace["plugins"]}
        self.assertEqual({"quenching-hud"}, set(marketplace_versions))
        self.assertEqual({VERSION}, set(marketplace_versions.values()), marketplace_versions)

    def test_the_entrypoint_declares_and_checks_the_python_floor_before_package_imports(self):
        source = REAL.read_text(encoding="utf-8")
        self.assertIn("PYTHON_FLOOR = (3, 11)", source)
        self.assertLess(source.index("if not _check_python_floor():"),
                        source.index("from quenching.common.output import"))
        self.assertIn("cq-python-floor:", source)

    def test_each_pillar_uses_the_same_version_grammar(self):
        pillars = ("specs", "knowledge", "design", "components", "ops", "proof", "git",
                   "toolchain", "delivery", "security", "opensource", "codex", "portal", "config")
        for pillar in pillars:
            with self.subTest(pillar=pillar):
                run = subprocess.run([str(SHIM), pillar, "--version"],
                                     capture_output=True, text=True)
                self.assertEqual(run.returncode, 0, run.stderr)
                self.assertEqual(run.stdout.strip(), f"cq {pillar} {VERSION}")

    def test_it_is_a_literally_equivalent_invocation(self):
        """Same argv through both doors — same stdout, same exit code. The `os.execv` claim."""
        argv = ["components", "doctor", "--root", str(PLUGIN_ROOT), "--json"]
        through_shim = subprocess.run([str(SHIM), *argv], capture_output=True, text=True)
        direct = subprocess.run([sys.executable, str(REAL), *argv], capture_output=True, text=True)
        self.assertEqual(through_shim.stdout, direct.stdout)
        self.assertEqual(through_shim.returncode, direct.returncode)

    def test_a_refusal_arrives_as_exit_2(self):
        """Every command body branches on 0/1/2. A shim that normalised one would break all of them."""
        run = subprocess.run([str(SHIM), "knowledge", "--root", "."], capture_output=True, text=True)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)

    def test_argparse_misuse_arrives_as_the_distinct_usage_exit(self):
        run = subprocess.run([str(SHIM), "knowledge", "--root", ".", "validate", "--bogus"],
                             capture_output=True, text=True)
        self.assertEqual(run.returncode, 3, run.stdout + run.stderr)
        self.assertIn("usage: cq knowledge validate", run.stderr)


if __name__ == "__main__":
    unittest.main()


class DeployedModules(unittest.TestCase):
    """A target's one cq reaches the modules `cq deploy --modules` installed, and names the rest."""

    @classmethod
    def setUpClass(cls):
        import tempfile
        (REPO_ROOT / ".quenching").mkdir(exist_ok=True)
        cls.tmp = tempfile.TemporaryDirectory(dir=REPO_ROOT / ".quenching")
        cls.roots = {}
        for selection in ("core", "all"):
            target = pathlib.Path(cls.tmp.name) / selection
            target.mkdir()
            subprocess.run(["git", "init", "-q"], cwd=target, check=True)
            subprocess.run([sys.executable, str(REAL), "deploy", "--target", str(target),
                            "--modules", selection, "--harness", "none", "--write"],
                           check=True, capture_output=True)
            cls.roots[selection] = target

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def cq(self, selection, *args):
        return subprocess.run([str(self.roots[selection] / ".agents/quenching/bin/cq"), *args],
                              capture_output=True, text=True)

    def test_a_core_target_refuses_an_undeployed_front_by_its_module(self):
        run = self.cq("core", "design", "--help")
        self.assertEqual(2, run.returncode, run.stdout)
        self.assertIn("quenching-design, which is not enabled", run.stderr)
        self.assertIn("cq deploy --modules", run.stderr)
        self.assertIn("(module quenching-design is not enabled)", self.cq("core", "--help").stdout)
        rows = {row["name"]: row["enabled"]
                for row in json.loads(self.cq("core", "modules", "--json").stdout)["modules"]}
        self.assertTrue(rows["quenching-specs"])
        self.assertFalse(rows["quenching-design"])

    def test_a_target_with_every_module_reaches_every_front(self):
        self.assertEqual(0, self.cq("all", "design", "--help").returncode)
        rows = json.loads(self.cq("all", "modules", "--json").stdout)["modules"]
        self.assertTrue(all(row["enabled"] for row in rows), rows)
