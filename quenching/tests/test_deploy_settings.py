"""The pure merge of quenching's hooks and `attribution` into `.claude/settings.json`."""

import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

from quenching.deploy import mcpfiles, settings  # noqa: E402

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _tools import bash  # noqa: E402

# The shells a hook command may land in, resolved once. `bash` is `_tools.bash()`: on Windows the
# bare name reaches the WSL launcher, which runs nothing when no distribution is installed.
SHELLS = {"bash": bash(), "sh": shutil.which("sh"), "pwsh": shutil.which("pwsh")}

COAUTHOR = {"name": "deny-claude-coauthor", "event": "PreToolUse", "matcher": "Bash", "timeout": 5}
WARN = {"name": "warn-git-add-all", "event": "PreToolUse", "matcher": "Bash", "timeout": 5}
USER_HOOK = {"type": "command", "command": "guard.sh"}


def want(*declared):
    return settings.desired_entries(list(declared))


def load(merged):
    return json.loads(merged.text)


class TheSettingsMerge(unittest.TestCase):
    def test_a_missing_file_gets_the_hook_and_the_empty_attribution(self):
        merged = settings.merge(None, want(COAUTHOR), settings.ATTRIBUTION)
        doc = load(merged)
        entry = doc["hooks"]["PreToolUse"][0]
        self.assertEqual("Bash", entry["matcher"])
        self.assertEqual(5, entry["hooks"][0]["timeout"])
        self.assertIn("'.agents/quenching/assets/hooks/dispatch.py'", entry["hooks"][0]["command"])
        self.assertTrue(entry["hooks"][0]["command"].startswith("python3 -I -c "))
        self.assertTrue(entry["hooks"][0]["command"].endswith('" deny-claude-coauthor'))
        self.assertEqual({"commit": "", "pr": ""}, doc["attribution"])
        self.assertEqual(["commit", "pr"], merged.attribution)

    def test_it_is_idempotent(self):
        first = settings.merge(None, want(COAUTHOR, WARN), settings.ATTRIBUTION, [])
        second = settings.merge(first.text, want(COAUTHOR, WARN), settings.ATTRIBUTION, first.attribution)
        self.assertEqual(first.text, second.text)
        self.assertEqual(["commit", "pr"], second.attribution)

    def test_the_users_entries_and_keys_survive_in_order(self):
        current = json.dumps({"enabledPlugins": {"context7": True},
                              "hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [USER_HOOK]}],
                                        "Stop": [{"hooks": [USER_HOOK]}]}})
        doc = load(settings.merge(current, want(COAUTHOR)))
        self.assertEqual({"context7": True}, doc["enabledPlugins"])
        self.assertEqual(USER_HOOK, doc["hooks"]["PreToolUse"][0]["hooks"][0])
        self.assertEqual(2, len(doc["hooks"]["PreToolUse"]))
        self.assertEqual([{"hooks": [USER_HOOK]}], doc["hooks"]["Stop"])

    def test_an_own_entry_is_updated_in_place(self):
        first = load(settings.merge(json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [USER_HOOK]}]}}), want(COAUTHOR)))
        first["hooks"]["PreToolUse"][1]["hooks"][0]["timeout"] = 99
        first["hooks"]["PreToolUse"].insert(0, {"matcher": "Edit", "hooks": [USER_HOOK]})
        doc = load(settings.merge(json.dumps(first), want(COAUTHOR)))
        self.assertEqual(5, doc["hooks"]["PreToolUse"][2]["hooks"][0]["timeout"])
        self.assertEqual(3, len(doc["hooks"]["PreToolUse"]))

    def test_a_mixed_group_loses_only_the_own_hook(self):
        own = {"type": "command", "command": settings.dispatch_command(["deny-claude-coauthor"]), "timeout": 5}
        current = json.dumps({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [USER_HOOK, own]}]}})
        merged = settings.merge(current, [])
        self.assertEqual({"hooks": {"PreToolUse": [{"matcher": "Bash", "hooks": [USER_HOOK]}]}}, load(merged))

    def test_removal_drops_the_emptied_group_event_and_hooks_key(self):
        added = settings.merge(None, want(COAUTHOR, WARN), settings.ATTRIBUTION)
        removed = settings.merge(added.text, [], None, added.attribution)
        self.assertEqual({}, load(removed))

    def test_a_narrower_selection_removes_only_the_module_that_left(self):
        added = settings.merge(None, want(COAUTHOR, WARN))
        narrowed = load(settings.merge(added.text, want(COAUTHOR)))
        commands = [h["command"] for g in narrowed["hooks"]["PreToolUse"] for h in g["hooks"]]
        self.assertEqual(1, len(commands))
        self.assertTrue(commands[0].endswith('" deny-claude-coauthor'))

    def test_one_matcher_gets_one_entry_running_every_body(self):
        doc = load(settings.merge(None, want(COAUTHOR, {**WARN, "timeout": 7})))
        group, = doc["hooks"]["PreToolUse"]
        hook, = group["hooks"]
        self.assertTrue(hook["command"].endswith('" deny-claude-coauthor warn-git-add-all'))
        self.assertEqual(7, hook["timeout"])
        other = want(COAUTHOR, {**WARN, "matcher": "Edit"})
        self.assertEqual(["Bash", "Edit"], [e["matcher"] for e in other])

    def test_the_old_one_entry_per_hook_layout_converges_in_one_pass(self):
        legacy = {"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [{"type": "command", "timeout": 5, "command": (
                "python3 -I -c \"import os,runpy,sys;p=os.path.join(os.environ.get('CLAUDE_PROJECT_DIR') "
                f"or os.getcwd(),'.agents/quenching/assets/hooks/{name}.py');runpy.run_path(p)\"")}]}
            for name in ("deny-claude-coauthor", "warn-git-add-all")]}}
        first = settings.merge(json.dumps(legacy), want(COAUTHOR, WARN))
        group, = load(first)["hooks"]["PreToolUse"]
        self.assertEqual([settings.dispatch_command(["deny-claude-coauthor", "warn-git-add-all"])],
                         [h["command"] for h in group["hooks"]])
        self.assertEqual(first.text, settings.merge(first.text, want(COAUTHOR, WARN)).text)

    def test_a_name_a_shell_could_expand_is_refused(self):
        for name in ("a b", "x;rm", "$x", "dispatch"):
            with self.subTest(name=name), self.assertRaises(ValueError):
                settings.dispatch_command([name])

    def test_attribution_keeps_a_value_the_user_set_and_warns(self):
        current = json.dumps({"attribution": {"commit": "Co-authored by me"}})
        merged = settings.merge(current, [], settings.ATTRIBUTION, [])
        doc = load(merged)
        self.assertEqual({"commit": "Co-authored by me", "pr": ""}, doc["attribution"])
        self.assertEqual(["pr"], merged.attribution)
        self.assertEqual(1, len(merged.warnings))

    def test_removal_keeps_attribution_the_user_owns(self):
        current = json.dumps({"attribution": {"commit": "", "pr": "mine"}})
        merged = settings.merge(current, [], None, ["commit", "pr"])
        self.assertEqual({"attribution": {"pr": "mine"}}, load(merged))
        untouched = settings.merge(json.dumps({"attribution": {"commit": ""}}), [], None, [])
        self.assertEqual({"attribution": {"commit": ""}}, json.loads(untouched.text))

    def test_a_semantically_equal_file_is_returned_byte_for_byte(self):
        current = '{"a":1}'
        self.assertEqual(current, settings.merge(current, []).text)
        self.assertIsNone(settings.merge(None, []).text)

    def test_it_refuses_what_it_cannot_merge_safely(self):
        for text in ("{not json", "[]", '{"hooks": []}', '{"hooks": {"PreToolUse": {}}}',
                     '{"attribution": "x"}'):
            with self.subTest(text=text):
                with self.assertRaises(settings.SettingsRefusal):
                    settings.merge(text, want(COAUTHOR), settings.ATTRIBUTION)

    def test_a_legacy_shell_entry_is_rewritten_in_place(self):
        legacy = ('test -f "$CLAUDE_PROJECT_DIR/.agents/quenching/assets/hooks/deny-claude-coauthor.sh" '
                  '|| exit 0; bash "$CLAUDE_PROJECT_DIR/.agents/quenching/assets/hooks/deny-claude-coauthor.sh"')
        current = json.dumps({"hooks": {"PreToolUse": [
            {"matcher": "Bash", "hooks": [USER_HOOK, {"type": "command", "command": legacy, "timeout": 5}]}]}})
        doc = load(settings.merge(current, want(COAUTHOR)))
        group, = doc["hooks"]["PreToolUse"]
        self.assertEqual([USER_HOOK["command"], settings.dispatch_command(["deny-claude-coauthor"])],
                         [h["command"] for h in group["hooks"]])

    def test_a_widened_matcher_moves_the_entry_instead_of_duplicating_it(self):
        added = settings.merge(None, want(COAUTHOR))
        widened = load(settings.merge(added.text, want({**COAUTHOR, "matcher": "Bash|PowerShell"})))
        self.assertEqual(["Bash|PowerShell"], [g["matcher"] for g in widened["hooks"]["PreToolUse"]])


class TheHooksPrefix(unittest.TestCase):
    """A hook runs on every shell call, so its prefix never goes through uv."""

    def test_a_direct_prefix_is_kept_without_a_warning(self):
        for prefix in (["python3"], ["py", "-3"], ["C:/Python312/python.exe"]):
            with self.subTest(prefix=prefix):
                self.assertEqual((prefix, None), mcpfiles.direct_prefix(prefix))

    def test_uv_and_uvx_give_way_to_the_recorded_direct_prefix(self):
        for prefix in (["uv", "run", "python"], ["uvx", "python"], ["C:\\bin\\UV.EXE", "run", "python"]):
            with self.subTest(prefix=prefix):
                chosen, warning = mcpfiles.direct_prefix(prefix, ["python"])
                self.assertEqual(["python"], chosen)
                self.assertIn("runs through uv", warning)

    def test_without_a_record_the_probe_picks_an_interpreter(self):
        chosen, warning = mcpfiles.direct_prefix(["uv", "run", "python"], ["uv", "run", "python"])
        self.assertNotIn(chosen[0], ("uv", "uvx"))
        self.assertIsNotNone(warning)


class ThePolyglotCommand(unittest.TestCase):
    """The same line must reach Python unchanged from bash, PowerShell and cmd."""

    def setUp(self):
        self.root = pathlib.Path(tempfile.mkdtemp())
        self.addCleanup(shutil.rmtree, self.root)
        hooks = self.root / settings.MARKER
        hooks.mkdir(parents=True)
        for name in ("dispatch", "deny-claude-coauthor", "warn-git-add-all"):
            shutil.copy(PLUGIN_ROOT / "assets" / "hooks" / f"{name}.py", hooks)

    def run_in(self, shell, command, payload, **env):
        argv = {"bash": [SHELLS["bash"], "-c", command], "sh": [SHELLS["sh"], "-c", command],
                "pwsh": [SHELLS["pwsh"], "-NoProfile", "-Command", command]}[shell]
        done = subprocess.run(argv, input=payload, capture_output=True, text=True, cwd=self.root,
                              env={**os.environ, "QUENCHING_ALLOW_CLAUDE_COAUTHOR": "", **env})
        self.assertEqual(0, done.returncode, done.stderr)
        return json.loads(done.stdout)

    def test_the_code_holds_nothing_a_shell_would_expand(self):
        command = settings.dispatch_command(["deny-claude-coauthor", "warn-git-add-all"])
        code = command.split(" -I -c ", 1)[1].rsplit(" deny-claude-coauthor", 1)[0]
        self.assertTrue(code.startswith('"') and code.endswith('"'))
        for char in ('"', "$", "`", "%", "!"):
            self.assertNotIn(char, code[1:-1], char)

    def test_the_declared_prefix_leads_the_command(self):
        command = settings.dispatch_command(["x"], ["py", "-3"])
        self.assertTrue(command.startswith("py -3 -I -c "))

    def test_it_runs_the_body_and_fails_open_without_it_in_every_available_shell(self):
        # The interpreter in its `/` spelling: bash would eat the `\` of `C:\...\python.exe`, and
        # every shell here reads `C:/.../python.exe` as the same program.
        python = pathlib.Path(sys.executable).as_posix()
        command = settings.dispatch_command(["deny-claude-coauthor", "warn-git-add-all"], [python])
        attributed = json.dumps({"tool_name": "Bash", "tool_input": {
            "command": 'git add -A; git commit -m x -m "Co-Authored-By: Claude <noreply@anthropic.com>"'}})
        shells = [shell for shell, path in SHELLS.items() if path]
        self.assertIn("bash", shells)
        for shell in shells:
            with self.subTest(shell=shell):
                out = self.run_in(shell, command, attributed, CLAUDE_PROJECT_DIR=str(self.root))
                self.assertEqual("deny", out["hookSpecificOutput"]["permissionDecision"])
                self.assertIn("/quenching-git commit", out["systemMessage"])  # both bodies, one process
                fallback = self.run_in(shell, command, attributed, CLAUDE_PROJECT_DIR="")  # the working directory
                self.assertEqual("deny", fallback["hookSpecificOutput"]["permissionDecision"])
                self.assertEqual({}, self.run_in(shell, command, attributed,
                                                 CLAUDE_PROJECT_DIR=str(self.root / "absent")))


class TheMcpjsonApproval(unittest.TestCase):
    def test_the_registered_server_is_approved_beside_the_users_names(self):
        merged = settings.merge('{"enabledMcpjsonServers": ["mine"]}', [], None, [], mcpjson=True)
        self.assertEqual(["mine", "quenching"], load(merged)["enabledMcpjsonServers"])
        self.assertTrue(merged.mcpjson)

    def test_an_approval_the_user_wrote_is_not_claimed(self):
        text = '{"enabledMcpjsonServers": ["quenching"]}'
        merged = settings.merge(text, [], None, [], mcpjson=True)
        self.assertEqual(text, merged.text)
        self.assertFalse(merged.mcpjson)

    def test_a_disabled_server_stays_off_with_a_warning(self):
        text = '{"disabledMcpjsonServers": ["quenching"]}'
        merged = settings.merge(text, [], None, [], mcpjson=True)
        self.assertEqual(text, merged.text)
        self.assertTrue(any("disabledMcpjsonServers" in w for w in merged.warnings))

    def test_removal_takes_out_only_what_the_deploy_wrote(self):
        text = '{"enabledMcpjsonServers": ["mine", "quenching"]}'
        self.assertEqual(text, settings.merge(text, [], None, [], mcpjson=False).text)
        out = settings.merge(text, [], None, [], mcpjson=False, mcpjson_recorded=True)
        self.assertEqual(["mine"], load(out)["enabledMcpjsonServers"])
        alone = settings.merge('{"enabledMcpjsonServers": ["quenching"]}', [], None, [],
                               mcpjson=False, mcpjson_recorded=True)
        self.assertEqual({}, load(alone))

    def test_a_list_that_is_not_a_list_refuses(self):
        with self.assertRaises(settings.SettingsRefusal):
            settings.merge('{"enabledMcpjsonServers": "quenching"}', [], None, [], mcpjson=True)


if __name__ == "__main__":
    unittest.main()
