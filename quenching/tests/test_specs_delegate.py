"""`cq specs delegate` — the delivery of an approved spec to the GitHub Copilot cloud agent:
the refusals that happen before any remote write, the deterministic briefing, and the one
client invocation (`gh agent-task create`) behind `--send`.

The store is the real git backend in a throwaway bare remote; `gh` is patched, so no network
and no cloud session is touched."""
from __future__ import annotations

import contextlib
import io
import json
import os
import pathlib
import sys
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401
except ModuleNotFoundError:
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401

import test_specs_git_backend as fixture
from test_specs_git_backend import GitStoreFixture, _sh
from quenching.specs import backends as backends_mod
from quenching.specs.backends import git as git_mod
from quenching.specs.backends.git import GitBackend
from quenching.specs.commands import cli, delegate

WORK = "plan/464-specs-delegaveis"
AGENT = "quenching-spec-runner"


def spec_text(*, approved=True, branch=True, tasks="""### 1. A secao

- [ ] 1.1 A primeira
- [x] 1.2 A segunda
"""):
    lines = ["---", "title: Specs delegáveis", "date: 2026-11-25"]
    if approved:
        lines.append("approved: {by: orchestrator-forced}")
    if branch:
        lines.append(f"branch: {{base: main, work: {WORK}}}")
    lines += ["---", "", "# Specs delegáveis", "", "## Problem", "", "Delegar.", "",
              "## Proposal", "", "- um", "", "## Out of Scope", "", "- nenhum", "",
              "## Impact", "",
              "### Standards this spec will write into docs/standards/", "",
              "- none — fixture", "",
              "### Product code this spec expects to touch", "",
              "- none — fixture", "",
              "### Process surface this spec expects to touch", "",
              "- none — fixture", "",
              "## Validation", "", "- none — fixture", "",
              "## Design", "", "- none — fixture", "",
              "## Alternatives Considered", "", "- none — fixture", "",
              "## Open Decisions", "", "- none — fixture", "",
              "## Risks", "", "- none — fixture", "",
              "## Handoff", "", "- none — fixture", "",
              "## Tasks", "", tasks]
    return "\n".join(lines) + "\n"


class Delegation(GitStoreFixture):
    def setUp(self):
        super().setUp()
        self.root = self.clone("work")
        self.configure()
        agent = pathlib.Path(self.root) / ".github/agents" / f"{AGENT}.agent.md"
        agent.parent.mkdir(parents=True, exist_ok=True)
        agent.write_text("---\nname: quenching-spec-runner\ndescription: fixture\n---\n", encoding="utf-8")
        self.backend = GitBackend(self.root)
        self.backend.create_spec("plans", spec_text(), spec_id=464)
        _sh(self.root, "branch", WORK, "origin/quenching")
        _sh(self.root, "push", "origin", f"{WORK}:refs/heads/{WORK}")
        # The fixture wrote through one backend; the CLI opens another, and the store
        # snapshot cache would otherwise answer from before the create.
        git_mod._STORES.clear()
        backends_mod._BACKEND_CACHE.clear()

    def configure(self, projections=("github",), card="github"):
        document = {"backend": "git"}
        shared = {}
        if projections is not None:
            shared["projections"] = list(projections)
        if shared:
            document["shared"] = shared
        if card is not None:
            document["card"] = {"provider": card}
        path = pathlib.Path(self.root) / ".agents/quenching.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(document), encoding="utf-8")

    def rewrite(self, text):
        info, _err = self.backend.read_spec(464)
        self.assertIsNotNone(info)
        self.backend.write_spec(info, text)
        git_mod._STORES.clear()
        backends_mod._BACKEND_CACHE.clear()

    def run_cli(self, *argv, provider="github"):
        out = io.StringIO()
        with mock.patch.object(delegate, "load_config",
                               return_value={"provider": provider, "card": {}}):
            with contextlib.redirect_stdout(out), contextlib.redirect_stderr(io.StringIO()):
                code = cli.main(["--root", self.root, *argv, "--json"])
        return code, json.loads(out.getvalue() or "{}")

    def test_the_brief_names_the_spec_the_branch_and_the_task_protocol(self):
        code, payload = self.run_cli("delegate", "464")
        self.assertEqual(0, code, payload)
        self.assertTrue(payload["ok"])
        self.assertFalse(payload["sent"])
        self.assertEqual(WORK, payload["work"])
        self.assertEqual("main", payload["base"])
        self.assertEqual(AGENT, payload["customAgent"])
        self.assertEqual({"open": 1, "total": 2}, payload["tasks"])
        brief = payload["brief"]
        self.assertIn("# Spec 464 — Specs delegáveis", brief)
        self.assertIn("cq specs show 464 --full", brief)
        self.assertIn(f"base is `{WORK}`", brief)
        self.assertIn("One task, one commit", brief)
        self.assertIn("--subject", brief)
        self.assertIn("SPEC/WORKTREE/STATE", brief)
        self.assertNotIn("Delegar.", brief)

    def test_send_hands_the_brief_to_gh_and_reports_the_task(self):
        seen = {}

        def fake(root, base, agent, brief):
            seen.update({"root": root, "base": base, "agent": agent, "brief": brief})
            return 0, "https://github.com/owner/repo/agent-sessions/abc", ""

        with mock.patch.object(delegate, "_gh_agent_task", side_effect=fake):
            code, payload = self.run_cli("delegate", "464", "--send")
        self.assertEqual(0, code, payload)
        self.assertTrue(payload["sent"])
        self.assertIn("agent-sessions/abc", payload["task"])
        self.assertEqual(WORK, seen["base"])
        self.assertEqual(AGENT, seen["agent"])
        self.assertEqual(self.root, seen["root"])
        self.assertIn("Spec 464", seen["brief"])

    def test_a_custom_agent_flag_is_used(self):
        other = pathlib.Path(self.root) / ".github/agents/other.agent.md"
        other.write_text("---\nname: other\n---\n", encoding="utf-8")
        code, payload = self.run_cli("delegate", "464", "--custom-agent", "other")
        self.assertEqual(0, code, payload)
        self.assertEqual("other", payload["customAgent"])

    def test_an_unapproved_spec_is_refused(self):
        self.rewrite(spec_text(approved=False))
        code, payload = self.run_cli("delegate", "464")
        self.assertEqual((2, "sp-delegate-approved"), (code, payload["code"]))

    def test_a_spec_without_the_branch_record_is_refused(self):
        self.rewrite(spec_text(branch=False))
        code, payload = self.run_cli("delegate", "464")
        self.assertEqual((2, "sp-delegate-branch"), (code, payload["code"]))
        self.assertIn("/quenching-git branch 464", payload["remedy"])

    def test_a_missing_projection_is_refused(self):
        self.configure(projections=None)
        code, payload = self.run_cli("delegate", "464")
        self.assertEqual((2, "sp-delegate-projection"), (code, payload["code"]))

    def test_a_non_github_provider_is_refused(self):
        code, payload = self.run_cli("delegate", "464", provider="azure-boards")
        self.assertEqual((2, "sp-delegate-provider"), (code, payload["code"]))

    def test_a_branch_missing_on_the_remote_is_refused(self):
        self.rewrite(spec_text().replace(WORK, "plan/464-never-pushed"))
        code, payload = self.run_cli("delegate", "464")
        self.assertEqual((2, "sp-delegate-remote"), (code, payload["code"]))
        self.assertEqual("plan/464-never-pushed", payload["work"])

    def test_a_missing_custom_agent_file_is_refused(self):
        self.configure()
        (pathlib.Path(self.root) / ".github/agents" / f"{AGENT}.agent.md").unlink()
        code, payload = self.run_cli("delegate", "464")
        self.assertEqual((2, "sp-delegate-agent"), (code, payload["code"]))

    def test_a_flat_slug_is_required(self):
        code, payload = self.run_cli("delegate", "464", "--custom-agent", "../other")
        self.assertEqual((2, "sp-delegate-agent"), (code, payload["code"]))

    def test_a_missing_gh_is_refused(self):
        with mock.patch.object(delegate.shutil, "which", return_value=None):
            code, payload = self.run_cli("delegate", "464", "--send")
        self.assertEqual((2, "sp-delegate-gh"), (code, payload["code"]))

    def test_a_gh_failure_is_a_refusal_with_its_output(self):
        with mock.patch.object(delegate, "_gh_agent_task", return_value=(1, "", "boom")):
            code, payload = self.run_cli("delegate", "464", "--send")
        self.assertEqual((2, "sp-delegate-gh"), (code, payload["code"]))
        self.assertIn("boom", payload["message"])

    def test_an_unknown_spec_is_refused(self):
        code, payload = self.run_cli("delegate", "999")
        self.assertFalse(payload["ok"])
        self.assertIn(payload["code"], ("sp-unknown-id", "sp-spec-unknown", "sp-no-spec"))


class TheBrief(unittest.TestCase):
    def test_it_is_deterministic_and_counts_open_tasks(self):
        info = {"id": 7, "frontmatter": {"title": "T"},
                "tasks": [{"checked": False}, {"checked": True}]}
        one = delegate.delegation_brief(info, "plan/7-x", "main", 1)
        two = delegate.delegation_brief(info, "plan/7-x", "main", 1)
        self.assertEqual(one, two)
        self.assertIn("1 open task(s)", one)
        self.assertIn("plan/7-x", one)
