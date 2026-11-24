"""The OpenCode extras the deploy merges into `opencode.json`: the subagent depth and the
`external_directory` allows for the slots and the store, and the global `experimental` read."""

import json
import os
import pathlib
import sys
import tempfile
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PLUGIN_ROOT / "assets" / "bin"))

from quenching.deploy import mcpfiles  # noqa: E402

ARGV = ["python3", ".agents/quenching/assets/bin/cq", "mcp"]
PATTERNS = ["~/p/repo-slot-*", "~/p/repo.*"]
EXTRAS = {"subagentDepth": mcpfiles.SUBAGENT_DEPTH, "externalDirectory": PATTERNS}


def merge(text, extras=EXTRAS):
    out = mcpfiles.merged(mcpfiles.OPENCODE, text, ARGV, extras)
    return None if out is None else json.loads(out)


class TheOpencodeExtras(unittest.TestCase):
    def test_an_empty_file_gets_the_depth_and_both_allows(self):
        doc = merge(None)
        self.assertEqual(4, doc["experimental"]["subagent_depth"])
        self.assertEqual({p: "allow" for p in PATTERNS}, doc["permission"]["external_directory"])
        self.assertIn("quenching", doc["mcp"])

    def test_a_higher_project_depth_and_the_other_keys_survive(self):
        doc = merge(json.dumps({"experimental": {"subagent_depth": 6, "todo": True},
                                "permission": {"edit": "ask",
                                               "external_directory": {"*": "ask"}}}))
        self.assertEqual({"subagent_depth": 6, "todo": True}, doc["experimental"])
        self.assertEqual("ask", doc["permission"]["edit"])
        self.assertEqual("ask", doc["permission"]["external_directory"]["*"])
        self.assertEqual("allow", doc["permission"]["external_directory"][PATTERNS[0]])

    def test_a_lower_project_depth_is_raised(self):
        doc = merge(json.dumps({"experimental": {"subagent_depth": 2}}))
        self.assertEqual(4, doc["experimental"]["subagent_depth"])

    def test_no_depth_leaves_experimental_alone(self):
        doc = merge(None, {"subagentDepth": None, "externalDirectory": PATTERNS})
        self.assertNotIn("experimental", doc)

    def test_a_permission_that_is_not_an_object_refuses_the_merge(self):
        self.assertIsNone(merge(json.dumps({"permission": "allow"})))
        self.assertIsNone(merge(json.dumps({"experimental": []})))

    def test_removal_takes_out_only_what_still_holds_the_written_value(self):
        written = mcpfiles.merged(mcpfiles.OPENCODE, json.dumps({"theme": "dark"}), ARGV, EXTRAS)
        doc = json.loads(written)
        doc["permission"]["external_directory"][PATTERNS[1]] = "deny"
        out = json.loads(mcpfiles.removed(mcpfiles.OPENCODE, json.dumps(doc), EXTRAS))
        self.assertNotIn("experimental", out)
        self.assertEqual({PATTERNS[1]: "deny"}, out["permission"]["external_directory"])
        self.assertEqual("dark", out["theme"])

    def test_removal_of_everything_the_deploy_wrote_empties_the_file(self):
        written = mcpfiles.merged(mcpfiles.OPENCODE, None, ARGV, EXTRAS)
        self.assertEqual("", mcpfiles.removed(mcpfiles.OPENCODE, written, EXTRAS))

    def test_strip_keeps_the_mcp_entry(self):
        written = mcpfiles.merged(mcpfiles.OPENCODE, None, ARGV, EXTRAS)
        doc = json.loads(mcpfiles.opencode_strip(written, EXTRAS))
        self.assertEqual({"$schema", "mcp"}, set(doc))


class TheRecordIsOnlyWhatWasWritten(unittest.TestCase):
    def test_an_empty_file_records_the_depth_and_both_allows(self):
        self.assertEqual({"subagentDepth": 4, "externalDirectory": PATTERNS},
                         mcpfiles.written_extras(None, EXTRAS))

    def test_a_user_depth_equal_or_higher_is_not_recorded(self):
        for value in (4, 6):
            text = json.dumps({"experimental": {"subagent_depth": value}})
            self.assertIsNone(mcpfiles.written_extras(text, EXTRAS)["subagentDepth"])

    def test_a_lower_user_depth_is_raised_and_recorded(self):
        text = json.dumps({"experimental": {"subagent_depth": 2}})
        self.assertEqual(4, mcpfiles.written_extras(text, EXTRAS)["subagentDepth"])

    def test_an_allow_the_user_already_had_is_not_recorded(self):
        text = json.dumps({"permission": {"external_directory": {PATTERNS[0]: "allow"}}})
        self.assertEqual([PATTERNS[1]], mcpfiles.written_extras(text, EXTRAS)["externalDirectory"])

    def test_removal_keeps_the_depth_and_the_allow_the_user_already_had(self):
        user = json.dumps({"experimental": {"subagent_depth": 4},
                           "permission": {"external_directory": {PATTERNS[0]: "allow"}}})
        written = mcpfiles.merged(mcpfiles.OPENCODE, user, ARGV, EXTRAS)
        recorded = mcpfiles.written_extras(user, EXTRAS)
        out = json.loads(mcpfiles.removed(mcpfiles.OPENCODE, written, recorded))
        self.assertEqual(4, out["experimental"]["subagent_depth"])
        self.assertEqual({PATTERNS[0]: "allow"}, out["permission"]["external_directory"])
        self.assertNotIn("mcp", out)


class ThePatterns(unittest.TestCase):
    def test_the_slots_and_the_store_are_siblings_of_the_primary(self):
        self.assertEqual(["/srv/p/repo-slot-*", "/srv/p/repo.*"],
                         mcpfiles.external_patterns("/srv/p/repo", "/home/u"))

    def test_a_primary_under_home_is_written_with_a_tilde(self):
        self.assertEqual(["~/p/repo-slot-*", "~/p/repo.*"],
                         mcpfiles.external_patterns("/home/u/p/repo", "/home/u/"))


class TheGlobalExperimental(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.home = pathlib.Path(tmp.name)
        (self.home / "opencode").mkdir()
        self.env = {"XDG_CONFIG_HOME": str(self.home)}

    def write(self, text, name="opencode.jsonc"):
        (self.home / "opencode" / name).write_text(text, encoding="utf-8")

    def test_jsonc_comments_and_trailing_commas_are_read(self):
        self.write('{\n  // a note\n  "url": "http://x//y",\n  /* block */\n'
                   '  "experimental": {"todo": true, "subagent_depth": 5,},\n}\n')
        found, unreadable = mcpfiles.global_experimental(self.env)
        self.assertEqual([], unreadable)
        self.assertEqual(["subagent_depth", "todo"], list(found.values())[0])

    def test_a_global_key_the_project_lacks_is_hidden(self):
        self.write('{"experimental": {"todo": true, "subagent_depth": 5}}')
        hidden, _ = mcpfiles.hidden_by_depth(None, self.env)
        self.assertEqual([["todo"]], list(hidden.values()))

    def test_a_global_depth_alone_hides_nothing(self):
        self.write('{"experimental": {"subagent_depth": 5}}')
        self.assertEqual(({}, []), mcpfiles.hidden_by_depth(None, self.env))

    def test_a_key_the_project_already_carries_hides_nothing(self):
        self.write('{"experimental": {"todo": true}}')
        project = json.dumps({"experimental": {"todo": False}})
        self.assertEqual(({}, []), mcpfiles.hidden_by_depth(project, self.env))

    def test_an_unreadable_global_is_reported(self):
        self.write("{ not json")
        hidden, unreadable = mcpfiles.hidden_by_depth(None, self.env)
        self.assertEqual({}, hidden)
        self.assertEqual(1, len(unreadable))

    def test_opencode_config_comes_first(self):
        custom = self.home / "custom.json"
        custom.write_text('{"experimental": {"todo": true}}', encoding="utf-8")
        paths = mcpfiles.global_config_paths({**self.env, "OPENCODE_CONFIG": str(custom)})
        self.assertEqual(str(custom), paths[0])
        self.assertEqual(os.path.join(str(self.home), "opencode", "opencode.json"), paths[1])


if __name__ == "__main__":
    unittest.main()


class TheVitrineReadsTheSameGlobals(unittest.TestCase):
    def test_the_plugin_lists_the_deploys_global_names_in_order(self):
        source = (PLUGIN_ROOT.parent / "integrations" / "opencode-vitrine" / "src" / "warnings.ts").read_text(encoding="utf-8")
        import re
        match = re.search(r"GLOBAL_NAMES = \[([^\]]*)\]", source)
        self.assertIsNotNone(match)
        self.assertEqual(list(mcpfiles.GLOBAL_NAMES), re.findall(r'"([^"]+)"', match.group(1)))
        self.assertIn("OPENCODE_CONFIG", source)
