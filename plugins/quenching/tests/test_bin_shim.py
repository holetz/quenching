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
import pathlib
import subprocess
import sys
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
SHIM = PLUGIN_ROOT / "bin" / "cq"
REAL = PLUGIN_ROOT / "assets" / "bin" / "cq"
VERSION = (PLUGIN_ROOT / "VERSION").read_text().strip()


class ThePathShim(unittest.TestCase):
    def test_it_is_there_and_executable(self):
        """Claude Code executes it off PATH, so the bit is the feature, not a nicety."""
        self.assertTrue(SHIM.is_file(), f"the shim does not resolve: {SHIM}")
        self.assertTrue(os.access(SHIM, os.X_OK), f"the shim carries no execute bit: {SHIM}")

    def test_it_exposes_ten_pillars(self):
        run = subprocess.run([sys.executable, str(REAL), "--help"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        choices = next(line.strip() for line in run.stdout.splitlines()
                       if line.strip().startswith("{") and line.strip().endswith("}"))
        pillars = set(choices[1:-1].split(","))
        self.assertEqual(10, len(pillars))
        self.assertEqual({"specs", "knowledge", "design", "components", "ops", "proof", "git",
                          "toolchain", "delivery", "security"}, pillars)

    def test_it_answers_the_version_lockstep(self):
        run = subprocess.run([str(SHIM), "--version"], capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(run.stdout.strip(), VERSION)

    def test_each_pillar_uses_the_same_version_grammar(self):
        pillars = ("specs", "knowledge", "design", "components", "ops", "proof", "git",
                   "toolchain", "delivery", "security")
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
