"""The per-user bootstrap script the deploy generates: read-only `--check`, listed and backed-up
`--write`, idempotence, and JSON with comments left alone. Every run uses a temporary HOME."""

import json
import os
import pathlib
import stat
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
TEMPLATE = PLUGIN_ROOT / "assets" / "bootstrap" / "bootstrap.py"
POSIX = os.name != "nt"


class Machine:
    """A throwaway home, repository and PATH, with the script rendered under it."""

    def __init__(self, harnesses, vscode=False):
        self._tmp = tempfile.TemporaryDirectory()
        root = pathlib.Path(self._tmp.name)
        self.home = root / "home"
        self.repo = root / "repo"
        self.bin = root / "bin"
        for folder in (self.home, self.repo / ".quenching" / "bootstrap", self.bin):
            folder.mkdir(parents=True)
        config = json.dumps({"version": "test", "harnesses": harnesses, "vscode": vscode})
        self.script = self.repo / ".quenching" / "bootstrap" / "bootstrap.py"
        self.script.write_text(TEMPLATE.read_text(encoding="utf-8").replace("__CONFIG__", config),
                               encoding="utf-8")
        self.launcher_dir = self.home / ".local" / "bin"
        self.on_path = [str(self.launcher_dir)]
        self.calls = root / "calls.txt"

    def fake(self, name):
        """A stand-in executable on PATH that records its argv."""
        path = self.bin / name
        path.write_text(f'#!/bin/sh\necho "{name} $*" >> "{self.calls}"\n', encoding="utf-8")
        path.chmod(0o755)

    def run(self, *args):
        env = {"HOME": str(self.home), "USERPROFILE": str(self.home),
               "XDG_CONFIG_HOME": str(self.home / ".config"),
               "CLAUDE_CONFIG_DIR": str(self.home / ".claude"),
               "PATH": os.pathsep.join([*self.on_path, str(self.bin), "/usr/bin", "/bin"]),
               "PYTHONDONTWRITEBYTECODE": "1"}
        return subprocess.run([sys.executable, "-I", str(self.script), *args], env=env,
                              capture_output=True, text=True, encoding="utf-8")

    def tree(self):
        return sorted(str(p.relative_to(self.home)) for p in self.home.rglob("*"))

    def close(self):
        self._tmp.cleanup()


@unittest.skipUnless(POSIX, "the POSIX launcher and `#!/bin/sh` stand-ins")
class TheBootstrapScript(unittest.TestCase):
    def machine(self, *args, **kwargs):
        machine = Machine(*args, **kwargs)
        self.addCleanup(machine.close)
        return machine

    def test_check_is_read_only_and_reports_the_launcher(self):
        machine = self.machine(["claude"])
        before = machine.tree()
        done = machine.run("--check")
        self.assertEqual(1, done.returncode, done.stdout)
        self.assertIn("todo   launcher", done.stdout)
        self.assertEqual(before, machine.tree())

    def test_default_mode_is_check(self):
        machine = self.machine([])
        self.assertEqual(1, machine.run().returncode)
        self.assertFalse((machine.launcher_dir / "cq").exists())

    def test_write_lists_before_it_writes_and_is_idempotent(self):
        machine = self.machine([])
        first = machine.run("--write")
        self.assertEqual(0, first.returncode, first.stdout + first.stderr)
        self.assertLess(first.stdout.index("about to write outside the repository"),
                        first.stdout.index("done   launcher"))
        launcher = machine.launcher_dir / "cq"
        self.assertTrue(launcher.stat().st_mode & stat.S_IXUSR)
        self.assertIn(str(machine.repo), launcher.read_text(encoding="utf-8"))
        after = machine.tree()
        second = machine.run("--write")
        self.assertEqual(0, second.returncode)
        self.assertIn("nothing to write", second.stdout)
        self.assertEqual(after, machine.tree())

    def test_a_different_launcher_is_backed_up_before_it_is_replaced(self):
        machine = self.machine([])
        machine.launcher_dir.mkdir(parents=True)
        (machine.launcher_dir / "cq").write_text("#!/bin/sh\necho mine\n", encoding="utf-8")
        done = machine.run("--write")
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        saved = list((machine.repo / ".quenching" / "bootstrap" / "backups").rglob("*cq"))
        self.assertEqual(1, len(saved))
        self.assertEqual("#!/bin/sh\necho mine\n", saved[0].read_text(encoding="utf-8"))
        self.assertIn("exec", (machine.launcher_dir / "cq").read_text(encoding="utf-8"))

    def test_a_launcher_dir_off_path_is_manual_and_never_edits_a_profile(self):
        machine = self.machine([])
        machine.on_path = []
        done = machine.run("--write")
        self.assertEqual(1, done.returncode)
        self.assertIn("manual launcher-path", done.stdout)
        self.assertFalse((machine.home / ".bashrc").exists())

    def test_the_global_opencode_depth_is_set_in_strict_json(self):
        machine = self.machine(["opencode"])
        config = machine.home / ".config" / "opencode" / "opencode.json"
        config.parent.mkdir(parents=True)
        config.write_text(json.dumps({"experimental": {"todo": True}}), encoding="utf-8")
        done = machine.run("--write")
        self.assertEqual(1, done.returncode, done.stdout)  # the vitrine has no checkout: manual
        document = json.loads(config.read_text(encoding="utf-8"))
        self.assertEqual({"todo": True, "subagent_depth": 4}, document["experimental"])
        self.assertEqual(1, len(list((machine.repo / ".quenching").rglob("*opencode.json"))))

    def test_a_global_config_with_comments_is_manual_and_untouched(self):
        machine = self.machine(["opencode"])
        config = machine.home / ".config" / "opencode" / "opencode.jsonc"
        config.parent.mkdir(parents=True)
        text = '{\n  // mine\n  "experimental": {"todo": true}\n}\n'
        config.write_text(text, encoding="utf-8")
        done = machine.run("--write")
        self.assertIn("manual opencode-depth", done.stdout)
        self.assertIn('"subagent_depth": 4', done.stdout)
        self.assertEqual(text, config.read_text(encoding="utf-8"))

    def test_no_global_experimental_block_needs_nothing(self):
        machine = self.machine(["opencode"])
        done = machine.run("--check")
        self.assertIn("ok     opencode-depth", done.stdout)

    def test_the_vitrine_is_listed_when_a_checkout_is_given(self):
        machine = self.machine(["opencode"])
        package = machine.repo / "integrations" / "opencode-vitrine"
        (package / "dist").mkdir(parents=True)
        (package / "package.json").write_text("{}", encoding="utf-8")
        done = machine.run("--write")
        self.assertEqual(0, done.returncode, done.stdout + done.stderr)
        config = machine.home / ".config" / "opencode" / "opencode.json"
        self.assertEqual([str(package)], json.loads(config.read_text(encoding="utf-8"))["plugins"])
        self.assertEqual(0, machine.run("--check").returncode)

    def test_claude_plugins_run_only_what_is_missing(self):
        machine = self.machine(["claude"])
        machine.fake("claude")
        done = machine.run("--write")
        # the stand-in installs nothing, so the re-check after the write still finds it pending
        self.assertEqual(1, done.returncode, done.stdout + done.stderr)
        calls = machine.calls.read_text(encoding="utf-8").splitlines()
        self.assertEqual(["claude plugin marketplace add holetz/quenching",
                          "claude plugin install quenching-hud@quenching --scope user",
                          "claude plugin install quenching-cache@quenching --scope user"], calls)
        plugins = machine.home / ".claude" / "plugins"
        plugins.mkdir(parents=True)
        (plugins / "known_marketplaces.json").write_text('{"quenching": {}}', encoding="utf-8")
        (plugins / "installed_plugins.json").write_text(json.dumps({"plugins": {
            "quenching-hud@quenching": [{}], "quenching-cache@quenching": [{}]}}), encoding="utf-8")
        again = machine.run("--check")
        self.assertEqual(0, again.returncode, again.stdout)
        self.assertEqual(3, len(machine.calls.read_text(encoding="utf-8").splitlines()))

    def test_claude_files_are_backed_up_before_the_cli_changes_them(self):
        machine = self.machine(["claude"])
        machine.fake("claude")
        plugins = machine.home / ".claude" / "plugins"
        plugins.mkdir(parents=True)
        (plugins / "installed_plugins.json").write_text('{"plugins": {}}', encoding="utf-8")
        machine.run("--write")
        saved = list((machine.repo / ".quenching" / "bootstrap" / "backups").rglob("*installed_plugins.json"))
        self.assertEqual(1, len(saved))

    def test_vscode_items_only_when_declared(self):
        machine = self.machine(["claude"])
        self.assertNotIn("vscode", machine.run("--check").stdout)
        declared = self.machine([], vscode=True)
        declared.fake("code")
        done = declared.run("--write")
        settings = declared.home / ".config" / "Code" / "User" / "settings.json"
        self.assertEqual(100, json.loads(settings.read_text(encoding="utf-8"))["chat.agent.maxRequests"])
        self.assertIn("code --install-extension GitHub.copilot-chat", done.stdout)


class ThePathHelper(unittest.TestCase):
    def load(self):
        namespace = {"__name__": "bootstrap_under_test", "__file__": str(TEMPLATE)}
        text = TEMPLATE.read_text(encoding="utf-8").replace("__CONFIG__", "{}")
        exec(compile(text, str(TEMPLATE), "exec"), namespace)
        return namespace

    def test_an_entry_already_present_is_not_appended_again(self):
        helper = self.load()["with_path_entry"]
        sep = os.pathsep
        self.assertEqual(f"a{sep}b", helper("a", "b"))
        self.assertEqual("a", helper("a", "a"))

    def test_the_windows_launcher_resolves_the_nearest_repository_first(self):
        namespace = self.load()
        text = namespace["WINDOWS_LAUNCHER"].replace("@REPO@", "C:\\repo")
        self.assertLess(text.index("goto run"), text.index(":fallback"))
        self.assertIn('set "dir=C:\\repo"', text)
        self.assertTrue(all(line.endswith("\r") for line in text.split("\n")[:-1]))


if __name__ == "__main__":
    unittest.main()
