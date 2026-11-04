"""The pure merge of quenching's hooks and `attribution` into `.claude/settings.json`."""

import json
import pathlib
import sys
import unittest

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin"))

from quenching.deploy import settings  # noqa: E402

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
        self.assertIn('"$CLAUDE_PROJECT_DIR/.agents/quenching/assets/hooks/deny-claude-coauthor.sh"',
                      entry["hooks"][0]["command"])
        self.assertTrue(entry["hooks"][0]["command"].startswith("test -f "))
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
        own = {"type": "command", "command": settings.hook_command("deny-claude-coauthor"), "timeout": 5}
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
        self.assertIn("deny-claude-coauthor", commands[0])

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


if __name__ == "__main__":
    unittest.main()
