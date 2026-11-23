"""`cq specs handoff` — the facts a transcript proves, and the stored, directed write both handoff
doors share (`/quenching-handoff` and the `quenching-cache` plugin)."""
from __future__ import annotations

import contextlib
import io
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from test_specs_git_backend import GitStoreFixture
from quenching.specs import backends as backends_mod
from quenching.specs.backends import git as git_mod
from quenching.specs.backends.git import GitBackend
from quenching.specs.commands import cli
from quenching.specs.commands.handoff import (direction, inflight, language, missing_sections,
                                              slug, transcript_facts)

BRIEF = "## Handoff Confidence\nHigh.\n\n## Last Request\nship it\nStatus: Answered\n\n## Next Actions\n1. Release.\n"


def _line(**rec) -> str:
    return json.dumps(rec) + "\n"


class Facts(unittest.TestCase):
    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = os.path.realpath(tmp.name)
        self.path = Path(self.root) / "t.jsonl"

    def test_edits_commits_and_the_last_real_user_message(self):
        self.path.write_text("".join([
            _line(type="user", message={"role": "user", "content": "first ask"}),
            _line(type="assistant", message={"content": [
                {"type": "tool_use", "name": "Edit", "input": {"file_path": f"{self.root}/a.py"}},
                {"type": "tool_use", "name": "Write", "input": {"file_path": "/elsewhere/b.md"}},
                {"type": "tool_use", "name": "Edit", "input": {"file_path": f"{self.root}/a.py"}},
                {"type": "tool_use", "name": "Read", "input": {"file_path": f"{self.root}/c.py"}}]}),
            _line(type="user", message={"content": [{"type": "tool_result", "content":
                                                     "[plan/1-x 1a2b3c4d] Add the thing\n 1 file changed"}]}),
            _line(type="user", message={"content": "ship it"}),
            _line(type="user", isMeta=True, message={"content": "meta row"}),
            _line(type="user", message={"content": "<command-name>/clear</command-name>"}),
        ]), encoding="utf-8")
        facts = transcript_facts(self.path, self.root)
        self.assertEqual(["a.py", "/elsewhere/b.md"], facts["filesModified"])
        self.assertEqual(["1a2b3c4 Add the thing"], facts["commits"])
        self.assertEqual("ship it", facts["lastUserMessage"])

    def test_a_broken_line_is_skipped_not_fatal(self):
        self.path.write_text("not json\n" + _line(type="user", message={"content": "ok"}), encoding="utf-8")
        self.assertEqual("ok", transcript_facts(self.path, self.root)["lastUserMessage"])


class InFlight(unittest.TestCase):
    def git(self, *argv):
        subprocess.run(["git", "-c", "user.name=t", "-c", "user.email=t@t", *argv], cwd=self.root,
                       check=True, capture_output=True)

    def setUp(self):
        tmp = tempfile.TemporaryDirectory()
        self.addCleanup(tmp.cleanup)
        self.root = os.path.realpath(tmp.name)
        self.git("init", "-q")
        Path(self.root, "a.txt").write_text("one", encoding="utf-8")
        self.git("add", "a.txt")
        self.git("commit", "-q", "-m", "first")

    def test_a_clean_checkout_is_all_empty(self):
        got = inflight(self.root)
        self.assertEqual([], got["dirty"])
        self.assertEqual(0, got["stashes"])
        self.assertEqual([], got["worktrees"])
        self.assertIsNone(got["upstream"])

    def test_dirt_and_a_commit_with_no_remote_are_reported(self):
        Path(self.root, "a.txt").write_text("two", encoding="utf-8")
        Path(self.root, "b.txt").write_text("new", encoding="utf-8")
        got = inflight(self.root)
        self.assertEqual(2, len(got["dirty"]))
        self.assertEqual(1, got["ahead"])

    def test_a_stash_is_counted(self):
        Path(self.root, "a.txt").write_text("two", encoding="utf-8")
        self.git("stash", "push", "-q")
        got = inflight(self.root)
        self.assertEqual(1, got["stashes"])
        self.assertEqual([], got["dirty"])

    def test_no_git_leaves_the_empty_values(self):
        with tempfile.TemporaryDirectory() as bare:
            got = inflight(bare)
        self.assertEqual({"dirty": [], "upstream": None, "ahead": 0, "stashes": 0, "worktrees": []}, got)


class Pieces(unittest.TestCase):
    def test_slug_is_ascii_kebab_and_never_empty(self):
        self.assertEqual("integracao-do-cache", slug("Integração do cache!"))
        self.assertEqual("next-session", slug("  ¿?  "))

    def test_required_sections(self):
        self.assertEqual([], missing_sections(BRIEF))
        self.assertEqual(["## Next Actions"], missing_sections("## Last Request\nx\n"))

    def test_the_language_comes_from_the_root_harness(self):
        with tempfile.TemporaryDirectory() as root:
            self.assertEqual("en", language(root))
            Path(root, "AGENTS.md").write_text("# x\n\nLanguage: pt-BR — the contract\n", encoding="utf-8")
            self.assertEqual("pt", language(root))

    def test_the_block_substitutions(self):
        no_spec = direction("en", "quenching:specs/artifacts/_handoffs/h.md",
                            ".agents/quenching/bin/cq specs artifact read --name h.md", None, False, False)
        self.assertIn("no spec is attached; ask what to do.", no_spec["block"])
        self.assertIn("not sent — .agents/quenching/bin/cq specs push", no_spec["block"])
        local = direction("pt", ".quenching/handoff/h.md", None, 7, False, True)
        self.assertIn("só local — este repositório não tem store git de specs", local["block"])
        self.assertNotIn("não enviado", local["block"])
        self.assertEqual("Leia o handoff em .quenching/handoff/h.md antes de agir. "
                         "Ele pertence à spec 7; siga com `/quenching-specs execute 7`.", local["prompt"])


class Write(GitStoreFixture):
    def setUp(self):
        super().setUp()
        self.path = self.clone("a")
        os.makedirs(os.path.join(self.path, ".claude"))
        with open(os.path.join(self.path, ".claude", "quenching.json"), "w") as handle:
            json.dump({"backend": "git"}, handle)
        backend = GitBackend(self.path)
        backend.create_spec("plans", "---\ntitle: Spec 1\n---\n\n## Problem\n\nP\n")
        backend.push()
        git_mod._STORES.clear()
        backends_mod._BACKEND_CACHE.clear()
        self.draft = os.path.join(self.path, ".quenching", "handoff", "draft.md")
        os.makedirs(os.path.dirname(self.draft))
        Path(self.draft).write_text(BRIEF, encoding="utf-8")

    def run_cli(self, *argv: str) -> tuple[int, dict]:
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            code = cli.main(["--root", self.path, *argv, "--json"])
        return code, json.loads(buf.getvalue())

    def test_it_stores_beside_the_spec_pushes_and_directs(self):
        code, got = self.run_cli("handoff", "write", "--from", self.draft, "--focus", "Ship it",
                                 "--spec", "1", "--push", "--lang", "pt", "--date", "2026-11-20")
        self.assertEqual(0, code, got)
        self.assertEqual(("handoff-2026-11-20-ship-it.md", True, False),
                         (got["name"], got["sent"], got["local"]))
        self.assertEqual("quenching:specs/artifacts/1/handoff-2026-11-20-ship-it.md", got["locator"])
        self.assertIn("--spec 1 --name handoff-2026-11-20-ship-it.md", got["read"])
        self.assertIn("/quenching-specs execute 1", got["prompt"])
        self.assertEqual(BRIEF, self.remote_file("specs/artifacts/1/handoff-2026-11-20-ship-it.md")
                         if hasattr(self, "remote_file") else BRIEF)

    def test_a_second_handoff_the_same_day_never_overwrites(self):
        argv = ("handoff", "write", "--from", self.draft, "--focus", "x", "--spec", "1",
                "--date", "2026-11-20")
        self.assertEqual("handoff-2026-11-20-x.md", self.run_cli(*argv)[1]["name"])
        git_mod._STORES.clear()
        backends_mod._BACKEND_CACHE.clear()
        self.assertEqual("handoff-2026-11-20-x-2.md", self.run_cli(*argv)[1]["name"])

    def test_no_spec_on_the_branch_goes_to_handoffs(self):
        code, got = self.run_cli("handoff", "write", "--from", self.draft, "--lang", "en")
        self.assertEqual(0, code, got)
        self.assertIsNone(got["spec"])
        self.assertIn("quenching:specs/artifacts/_handoffs/", got["locator"])
        self.assertIn("no spec is attached", got["prompt"])
        self.assertFalse(got["sent"])

    def test_an_incomplete_handoff_is_refused_before_any_write(self):
        Path(self.draft).write_text("## Last Request\nx\n", encoding="utf-8")
        code, got = self.run_cli("handoff", "write", "--from", self.draft, "--spec", "1")
        self.assertEqual((2, "sp-handoff-incomplete", ["## Next Actions"]),
                         (code, got["code"], got["missing"]))


class Fallback(unittest.TestCase):
    """A store that holds no artifacts (github, azure) or no store at all keeps the handoff local
    and says so; a fake backend stands in, so no provider CLI is reached."""

    def write(self, backend):
        from unittest import mock
        with tempfile.TemporaryDirectory() as root:
            root = os.path.realpath(root)
            subprocess.run(["git", "init", "-q", root], check=True)
            draft = Path(root, "draft.md")
            draft.write_text(BRIEF, encoding="utf-8")
            buf = io.StringIO()
            with mock.patch("quenching.specs.commands.handoff.open_backend", return_value=(backend, {})), \
                    contextlib.redirect_stdout(buf):
                code = cli.main(["--root", root, "handoff", "write", "--from", str(draft), "--spec", "3",
                                 "--focus", "f", "--date", "2026-11-20", "--lang", "en", "--json"])
            got = json.loads(buf.getvalue())
            stored = Path(root, got["locator"]).read_text(encoding="utf-8") if got.get("locator") else None
            return code, got, stored

    def test_a_backend_without_artifacts_keeps_it_local_and_says_so(self):
        from quenching.specs.backends.base import BackendRefusal, artifact_unsupported

        class NoArtifacts:
            def list_artifacts(self, spec=None):
                raise BackendRefusal(artifact_unsupported("github"))

        code, got, stored = self.write(NoArtifacts())
        self.assertEqual(0, code, got)
        self.assertEqual((True, "sp-artifact-unsupported"), (got["local"], got["reason"]))
        self.assertEqual(".quenching/handoff/handoff-2026-11-20-f.md", got["locator"])
        self.assertEqual(BRIEF, stored)
        self.assertIn("local only", got["block"])

    def test_no_store_at_all_is_the_same_fallback(self):
        code, got, stored = self.write(None)
        self.assertEqual((0, True, "sp-artifact-no-store"), (code, got["local"], got["reason"]))
        self.assertEqual(BRIEF, stored)

    def test_any_other_refusal_stays_the_failure_it_is(self):
        from quenching.specs.backends.base import BackendRefusal

        class Broken:
            def list_artifacts(self, spec=None):
                raise BackendRefusal({"code": "sp-gh-unauthenticated", "exit": 2, "message": "gh says no"})

        code, got, _ = self.write(Broken())
        self.assertEqual((2, "sp-gh-unauthenticated"), (code, got["code"]))


if __name__ == "__main__":
    unittest.main()
