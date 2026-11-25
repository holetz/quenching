"""`quenching.common.access`: the family derivation and the per-client declarations."""

import json
import os
import pathlib
import subprocess
import sys
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common import access


def _git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True, text=True,
                   env={**os.environ, "GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@e",
                        "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@e"})


class FamilyTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "proj")
        _git("init", "-q", self.repo, cwd=self.tmp)

    def test_primary_is_the_checkout_root(self):
        self.assertEqual(os.path.realpath(self.repo),
                         os.path.realpath(access.primary(self.repo)[0]))

    def test_a_slot_resolves_to_the_primary(self):
        _git("commit", "-q", "--allow-empty", "-m", "base", cwd=self.repo)
        slot = os.path.join(self.tmp, "proj-slot-1")
        _git("worktree", "add", "-q", slot, "-b", "plan/x", cwd=self.repo)
        self.assertEqual(os.path.realpath(self.repo),
                         os.path.realpath(access.primary(slot)[0]))

    def test_no_git_names_the_reason(self):
        outside = os.path.join(self.tmp, "plain")
        os.makedirs(outside)
        self.assertEqual((None, "not a git checkout"), access.primary(outside))

    def test_patterns_use_the_home_prefix_when_under_it(self):
        home = os.path.join(self.tmp, "home")
        root = os.path.join(home, "src", "proj")
        self.assertEqual(["~/src/proj-slot-*", "~/src/proj.*"], access.patterns(root, home))

    def test_patterns_stay_absolute_outside_the_home(self):
        home = os.path.join(self.tmp, "home")
        root = os.path.join(self.tmp, "src", "proj")
        self.assertEqual([root + "-slot-*", root + ".*"], access.patterns(root, home))


class DeclarationsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "proj")
        os.makedirs(self.repo)

    def test_claude_rules_name_the_bash_entry_and_the_family(self):
        rules = access.claude_rules(self.repo, "/home/user")
        self.assertIn("Bash(.agents/quenching/bin/cq:*)", rules)
        self.assertIn("Read(//" + self.repo.lstrip("/") + "-slot-*/**)", rules)
        self.assertIn("Edit(//" + self.repo.lstrip("/") + ".*/**)", rules)
        self.assertIn("Write(//" + self.repo.lstrip("/") + "-slot-*/**)", rules)

    def test_claude_rules_keep_the_home_form(self):
        root = "/home/user/src/proj"
        self.assertIn("Read(~/src/proj-slot-*/**)", access.claude_rules(root, "/home/user"))

    def test_vscode_block_approves_the_entry_and_stops_the_write_block(self):
        block = access.vscode_block()
        self.assertEqual("never", block[access.BLOCK_WRITES])
        self.assertEqual({True}, set(block[access.AUTO_APPROVE].values()))
        snippet = access.vscode_snippet()
        self.assertIn("chat.tools.terminal.autoApprove", snippet)
        self.assertIn("blockDetectedFileWrites", snippet)

    def test_copilot_invocation_lists_existing_siblings_only(self):
        os.makedirs(os.path.join(self.tmp, "proj-slot-1"))
        os.makedirs(os.path.join(self.tmp, "proj.worktrees"))
        os.makedirs(os.path.join(self.tmp, "proj-slot-2"))
        invocation = access.copilot_invocation(self.repo)
        self.assertIn('--add-dir "' + os.path.join(self.tmp, "proj-slot-1") + '"', invocation)
        self.assertIn('--add-dir "' + os.path.join(self.tmp, "proj.worktrees") + '"', invocation)
        self.assertNotIn('"' + self.tmp + '"', invocation)


class ReportTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.mkdtemp()
        self.repo = os.path.join(self.tmp, "proj")
        _git("init", "-q", self.repo, cwd=self.tmp)
        os.makedirs(os.path.join(self.tmp, "proj-slot-1"))
        self.home = os.path.join(self.tmp, "home")
        os.makedirs(self.home)

    def write(self, rel, document):
        path = os.path.join(self.repo, rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(document, handle)

    def complete(self):
        home = self.home
        # The report derives the family from the real repo, so the artifacts must name it.
        patterns = access.patterns(self.repo, home)
        rules = access.claude_rules(self.repo, home)
        self.write(access.OPENCODE, {"permission": {
            "external_directory": {pattern: "allow" for pattern in patterns},
            "bash": {pattern: "allow" for pattern in access.OPENCODE_BASH}}})
        self.write(access.CLAUDE, {"permissions": {"allow": rules}})
        self.write(access.VSCODE, access.vscode_block())

    def test_a_complete_target_reports_complete(self):
        self.complete()
        value = access.report(self.repo)
        self.assertTrue(value["complete"], value)
        self.assertEqual("present", value["family"]["state"])
        self.assertEqual("complete", access.summary(value).split(" — ")[0][len("access: "):])

    def test_a_missing_artifact_is_named_per_client(self):
        value = access.report(self.repo)
        self.assertFalse(value["complete"])
        self.assertEqual("absent", value["opencode"]["state"])
        self.assertEqual("absent", value["claude"]["state"])
        self.assertEqual("absent", value["vscode"]["state"])
        self.assertIn("opencode", access.summary(value))

    def test_a_stale_pattern_is_reported_with_its_remedy(self):
        self.complete()
        path = os.path.join(self.repo, access.OPENCODE)
        with open(path, encoding="utf-8") as handle:
            document = json.load(handle)
        document["permission"]["external_directory"] = {
            "/nonexistent/old/quenching-slot-*": "allow",
            "/nonexistent/old/quenching.*": "allow"}
        with open(path, "w", encoding="utf-8") as handle:
            json.dump(document, handle)
        value = access.report(self.repo)
        self.assertEqual(2, len(value["opencode"]["stalePatterns"]))
        self.assertIn("stale", access.summary(value))

    def test_a_jsonc_vscode_file_is_read(self):
        path = os.path.join(self.repo, access.VSCODE)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w", encoding="utf-8") as handle:
            handle.write("{\n  // comment\n  \"chat.tools.terminal.blockDetectedFileWrites\": "
                         "\"never\",\n}")
        self.assertEqual("present", access.report(self.repo)["vscode"]["state"])

    def test_human_prints_the_block_and_the_invocation(self):
        self.complete()
        text = access.human(access.report(self.repo))
        self.assertIn("chat.tools.terminal.autoApprove", text)
        self.assertIn("copilot --add-dir", text)

    def test_outside_a_git_repository_the_family_is_absent(self):
        plain = os.path.join(self.tmp, "plain")
        os.makedirs(plain)
        value = access.report(plain)
        self.assertEqual("absent", value["family"]["state"])
        self.assertFalse(value["complete"])
        self.assertIn("no family", access.summary(value))


if __name__ == "__main__":
    unittest.main()
