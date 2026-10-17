"""Exercise the real functional harness with a deterministic, contaminated CLI.

The fake emits correct tool calls even when an unrelated plugin is loaded: checking
the expected calls alone cannot prove that a session was isolated.
"""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest


ROOT = pathlib.Path(__file__).resolve().parents[3]
SCRIPT = ROOT / "plugins/quenching/assets/checks/functional-checks.sh"
FAKE = r'''
import json, os, pathlib, sys
args = sys.argv[1:]
dirs = [args[i + 1] for i, a in enumerate(args) if a == "--plugin-dir"]
plugin = dirs[0]
isolated = "--setting-sources" in args and args[args.index("--setting-sources") + 1] == "project"
with open(os.environ["PROBE_LOG"], "a") as log:
    log.write(json.dumps({"isolated": isolated, "plugins": dirs}) + "\n")
plugins = [{"name": pathlib.Path(d).name, "path": d} for d in dirs] + [{"name": "cli", "path": "builtin"}]
if not isolated or os.environ.get("FOREIGN_PLUGIN"):
    plugins.append({"name": "unrelated", "path": "/plugins/cache/unrelated/1"})
mode = os.environ.get("REGISTRY_MODE", "valid")
if mode != "missing":
    print(json.dumps({"type": "system", "subtype": "init", "plugins": plugins if mode == "valid" else [{}]}))
prompt = args[args.index("--setting-sources") + 2] if isolated else args[-1]
if prompt.startswith("/quenching-align:align"):
    tool, data = "Skill", {"skill": "quenching-align:knowledge:align"}
elif prompt.startswith("/quenching-"):
    tool, data = "Read", {"file_path": plugin + "/assets/references/selftest.md"}
else:
    target = "quenching-specs:specs:create"
    if prompt.startswith("add a standard"):
        target = "quenching-align:knowledge:add"
    elif prompt.startswith("set up something"):
        target = "quenching-align:components:agent:new"
    elif prompt.startswith("I want something"):
        target = "quenching-align:components:hook:new"
    tool, data = "Skill", {"skill": target}
print(json.dumps({"message": {"content": [{"type": "tool_use", "name": tool, "input": data}]}}))
'''


class FunctionalSessionIsolation(unittest.TestCase):
    def run_harness(self, *, foreign=False, registry="valid"):
        with tempfile.TemporaryDirectory() as tmp:
            folder = pathlib.Path(tmp)
            fake = folder / "claude"
            fake.write_text(f"#!{sys.executable}\n" + FAKE, encoding="utf-8")
            fake.chmod(0o755)
            config = folder / "profile"
            config.mkdir()
            settings = config / "settings.json"
            original = '{"enabledPlugins":{"unrelated@example":true}}\n'
            settings.write_text(original, encoding="utf-8")
            log = folder / "calls.jsonl"
            env = {**os.environ, "PATH": f"{folder}{os.pathsep}{os.environ['PATH']}",
                   "CLAUDE_CONFIG_DIR": str(config), "PROBE_LOG": str(log),
                   "REGISTRY_MODE": registry, "GIT_CONFIG_COUNT": "2",
                   "GIT_CONFIG_KEY_0": "user.name", "GIT_CONFIG_VALUE_0": "Test",
                   "GIT_CONFIG_KEY_1": "user.email", "GIT_CONFIG_VALUE_1": "test@example.invalid"}
            env.pop("FOREIGN_PLUGIN", None)
            if foreign:
                env["FOREIGN_PLUGIN"] = "1"
            run = subprocess.run(["bash", str(SCRIPT), "--only", "1,2,3,4", str(ROOT)],
                                 env=env, capture_output=True, text=True)
            calls = [json.loads(line) for line in log.read_text().splitlines()]
            self.assertEqual(settings.read_text(encoding="utf-8"), original)
            return run, calls

    def test_every_probe_excludes_user_settings_and_keeps_the_checkout(self):
        run, calls = self.run_harness()
        self.assertEqual(run.returncode, 0, run.stdout + run.stderr)
        self.assertEqual(len(calls), 9)
        self.assertTrue(all(call["isolated"] for call in calls), calls)
        modules = sorted(str(ROOT / "plugins" / name) for name in (
            "quenching-specs", "quenching-align", "quenching-design", "quenching-ops",
            "quenching-proof", "quenching-toolchain", "quenching-delivery", "quenching-security"))
        self.assertTrue(all(sorted(call["plugins"]) == modules for call in calls), calls)

    def test_foreign_plugin_fails_even_with_the_expected_tool_calls(self):
        run, _ = self.run_harness(foreign=True)
        self.assertEqual(run.returncode, 1, run.stdout + run.stderr)
        self.assertIn("unrelated", run.stdout)

    def test_missing_or_malformed_registry_is_inconclusive(self):
        for registry in ("missing", "malformed"):
            with self.subTest(registry=registry):
                run, _ = self.run_harness(registry=registry)
                self.assertEqual(run.returncode, 2, run.stdout + run.stderr)
                self.assertIn("nothing could be measured", run.stdout)

    def test_selfcheck_rejects_an_unfiltered_session(self):
        with tempfile.TemporaryDirectory() as tmp:
            script = pathlib.Path(tmp) / "functional-checks.sh"
            source = SCRIPT.read_text(encoding="utf-8")
            source = source.replace(' --setting-sources project', '', 1)
            script.write_text(source, encoding="utf-8")
            run = subprocess.run(["bash", str(script), "--selfcheck", str(ROOT)],
                                 capture_output=True, text=True)
            self.assertEqual(run.returncode, 1, run.stdout + run.stderr)


if __name__ == "__main__":
    unittest.main()
