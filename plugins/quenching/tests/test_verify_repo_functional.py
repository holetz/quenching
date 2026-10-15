"""The fail-closed branches of the `surface-load checks` block in `scripts/verify_repo.sh`.

The block is cut out of the real script between its two markers and run in a scratch tree with a
stub `functional-checks.sh` and a controlled PATH, so the test never bills a `claude -p` session and
never drifts from the script it guards. A marker that disappears fails the test instead of letting
it pass empty.
"""

import json
import pathlib
import shutil
import subprocess
import tempfile
import unittest

REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent.parent.parent
SCRIPT = REPO_ROOT / "scripts" / "verify_repo.sh"
START = "printf '\\n==> surface-load checks\\n'"
END = "printf '\\nRepository verification passed.\\n'"
BASH = shutil.which("bash")
FUNCTIONAL = REPO_ROOT / "plugins" / "quenching" / "assets" / "checks" / "functional-checks.sh"


def _block() -> str:
    text = SCRIPT.read_text()
    assert START in text and END in text, "surface-load markers moved in verify_repo.sh"
    return text[text.index(START) : text.index(END)]


class SurfaceLoadBlock(unittest.TestCase):
    def run_block(self, *, functional=None, claude=False, stub_rc=0):
        with tempfile.TemporaryDirectory() as tmp:
            root = pathlib.Path(tmp)
            checks = root / "plugins" / "quenching" / "assets" / "checks"
            checks.mkdir(parents=True)
            (checks / "functional-checks.sh").write_text(f"exit {stub_rc}\n")
            fakebin = root / "fakebin"
            fakebin.mkdir()
            (fakebin / "bash").symlink_to(BASH)
            if claude:
                fake = fakebin / "claude"
                fake.write_text("#!/bin/sh\nexit 0\n")
                fake.chmod(0o755)
            env = {"PATH": str(fakebin)}
            if functional is not None:
                env["QUENCHING_FUNCTIONAL"] = functional
            return subprocess.run(
                [BASH, "-c", _block()], cwd=root, env=env, capture_output=True, text=True
            )

    def test_without_the_opt_in_it_skips_and_stays_green(self):
        run = self.run_block()
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertIn("SKIPPED", run.stdout)

    def test_requested_without_claude_on_path_fails(self):
        run = self.run_block(functional="1")
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("claude", run.stderr)

    def test_an_inconclusive_exit_2_fails(self):
        run = self.run_block(functional="1", claude=True, stub_rc=2)
        self.assertEqual(run.returncode, 1, run.stdout)
        self.assertIn("exit 2", run.stderr)

    def test_a_failing_exit_1_fails(self):
        run = self.run_block(functional="1", claude=True, stub_rc=1)
        self.assertEqual(run.returncode, 1, run.stdout)

    def test_a_passing_measurement_passes(self):
        run = self.run_block(functional="1", claude=True, stub_rc=0)
        self.assertEqual(run.returncode, 0, run.stderr)


class GeneratedModuleArrangements(unittest.TestCase):
    """functional-checks loads the generated modules, never the source, and refuses unbuilt trees."""

    def run_checks(self, *args, repo=None):
        argv = [BASH, str(FUNCTIONAL), *args]
        if repo is not None:
            argv.append(str(repo))
        return subprocess.run(argv, capture_output=True, text=True)

    def test_guards_pass_on_the_module_form(self):
        for flag in ("--selfcheck", "--selftest"):
            run = self.run_checks(flag)
            self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
            self.assertNotIn("FAIL", run.stdout)

    def test_selftest_rejects_the_source_and_modules_outside_the_arrangement(self):
        run = self.run_checks("--selftest")
        self.assertIn("rejected the unloaded source path", run.stdout)
        self.assertIn("rejected a module outside the specs-only arrangement", run.stdout)

    def test_an_ungenerated_module_tree_is_inconclusive_before_any_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            assets = repo / "plugins" / "quenching" / "assets"
            assets.mkdir(parents=True)
            modules = [
                {"name": "quenching-align", "path": "plugins/quenching-align", "owned": {}},
                {"name": "quenching-specs", "path": "plugins/quenching-specs", "owned": {}, "cqPathOwner": True},
            ]
            (assets / "modules.json").write_text(json.dumps({"modules": modules}))
            manifest = repo / "plugins" / "quenching-specs" / ".claude-plugin"
            manifest.mkdir(parents=True)
            (manifest / "plugin.json").write_text("{}")
            run = self.run_checks(repo=repo)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
        self.assertIn("plugins/quenching-align", run.stderr)

    def test_a_manifest_without_principal_modules_is_inconclusive(self):
        with tempfile.TemporaryDirectory() as tmp:
            repo = pathlib.Path(tmp)
            assets = repo / "plugins" / "quenching" / "assets"
            assets.mkdir(parents=True)
            (assets / "modules.json").write_text(json.dumps({"modules": [{"name": "quenching", "path": "plugins/quenching"}]}))
            run = self.run_checks(repo=repo)
        self.assertEqual(run.returncode, 2, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
