"""The card layer and `migrate --to git`, offline: a bare repository is the remote, the card
client is a recorder (backend rules) or `gh`/`az` themselves are mocked at their runner
(transport rules). Nothing here reaches a network, and no real tracker is ever written."""

import argparse
import contextlib
import io
import json
import pathlib
import sys
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
import test_specs_backends as canonical
from test_specs_git_backend import GitStoreFixture, _sh
from quenching.specs import cards
from quenching.specs.backends import azure as az_mod
from quenching.specs.backends import github as gh_mod
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.git import GitBackend
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import create as create_mod
from quenching.specs.commands import migrate as migrate_mod
from quenching.specs.commands.output import Emitter
from quenching.specs.parse import derive_info
from quenching.specs.parse.edit import upsert_section
from quenching.specs.parse.fields import set_frontmatter_record


class FakeCard(cards.CardClient):
    """Records every request; allocates numbers from `next_number` like a tracker would."""
    provider = "fake"

    def __init__(self, next_number=900, fail_updates=False):
        self.calls = []
        self.next_number = next_number
        self.fail_updates = fail_updates
        self.items = {}

    def create(self, state):
        number, self.next_number = self.next_number, self.next_number + 1
        self.calls.append(("create", number, state))
        return number

    def update(self, number, state):
        self.calls.append(("update", number, state))
        if self.fail_updates:
            raise BackendRefusal({"code": "sp-gh-api-error", "exit": 2, "message": "HTTP 503"})

    def read(self, number):
        return self.items[number]

    def verbs(self):
        return [c[0] for c in self.calls]


def _doc_with_tasks(title="Alpha"):
    doc = canonical._case_doc(title)
    info = derive_info({"phase": "plans"}, doc)
    doc, _ = upsert_section(info, "Problem", "## Problem\n\nWhy this exists.\n\nSecond paragraph.\n")
    info = derive_info({"phase": "plans"}, doc)
    doc, _ = upsert_section(info, "Tasks", "## Tasks\n\n- [ ] 1.1 first\n- [ ] 1.2 second\n")
    return doc


class CardCreation(GitStoreFixture):
    def test_the_card_is_created_first_and_its_number_is_the_spec_id(self):
        fake = FakeCard(next_number=777)
        backend = GitBackend(self.clone("a"), card=fake)
        locator = backend.create_spec("plans", _doc_with_tasks())
        self.assertEqual("quenching:specs/777.md", locator)
        self.assertEqual(["create"], fake.verbs())
        self.assertEqual("Why this exists.", fake.calls[0][2]["summary"])
        self.assertEqual(_doc_with_tasks(), self.remote_file("specs/777.md"))
        self.assertEqual("778\n", self.remote_file("specs/.next-id"))

    def test_a_card_failure_at_create_writes_no_spec(self):
        fake = FakeCard()
        fake.create = mock.Mock(side_effect=BackendRefusal(
            {"code": "sp-gh-api-error", "exit": 2, "message": "HTTP 401"}))
        backend = GitBackend(self.clone("a"), card=fake)
        with self.assertRaises(BackendRefusal):
            backend.create_spec("plans", _doc_with_tasks())
        self.assertEqual([], backend.list_specs())

    def test_a_taken_id_names_the_orphan_card(self):
        fake = FakeCard(next_number=1)
        backend = GitBackend(self.clone("a"), card=None)
        backend.create_spec("plans", _doc_with_tasks())
        backend = GitBackend(self.clone("b"), card=fake)
        with self.assertRaises(BackendRefusal) as caught:
            backend.create_spec("plans", _doc_with_tasks("Beta"))
        self.assertIn("orphan", caught.exception.err["message"])

    def test_without_a_provider_the_counter_allocates_and_no_card_exists(self):
        backend = GitBackend(self.clone("a"), card=None)
        self.assertEqual("quenching:specs/1.md", backend.create_spec("plans", _doc_with_tasks()))

    def test_adoption_keeps_the_number_and_rewrites_the_card_once(self):
        fake = FakeCard()
        fake.items[5] = {"title": "Human issue", "body": "The human's own words.",
                         "closed": False}
        backend = GitBackend(self.clone("a"), card=fake)
        text = canonical._case_doc("Adopted")
        self.assertEqual("quenching:specs/5.md", backend.create_spec("plans", text, card=5))
        self.assertEqual(["update"], fake.verbs())
        self.assertEqual(5, fake.calls[0][1])

    def test_new_card_turns_the_issue_body_into_problem(self):
        fake = FakeCard()
        fake.items[5] = {"title": "Human issue", "body": "The human's own words.",
                         "closed": False}
        path = self.clone("a")
        backend = GitBackend(path, card=fake)
        args = argparse.Namespace(name="Adopted", title=None, verification=None, subject=None,
                                  type=None, tags=None, complexity=None, card=5, json=True)
        buf = io.StringIO()
        with mock.patch.object(create_mod, "open_backend", lambda _r: (backend, {})), \
                mock.patch.object(create_mod.sys, "stdin", io.StringIO("")), \
                contextlib.redirect_stdout(buf):
            code = create_mod.cmd_new(args, path, Emitter())
        self.assertEqual(0, code, buf.getvalue())
        self.assertEqual(5, json.loads(buf.getvalue())["id"])
        info, _ = backend.read_spec(5)
        self.assertIn("The human's own words.", info["sections"]["Problem"]["body"])
        self.assertEqual(["update"], fake.verbs())

    def test_new_card_refuses_on_a_tracker_backend(self):
        args = argparse.Namespace(name="X", title=None, verification=None, subject=None,
                                  type=None, tags=None, complexity=None, card=5, json=True)
        buf = io.StringIO()
        with mock.patch.object(create_mod, "open_backend",
                               lambda _r: (MemoryBackend(), {})), \
                mock.patch.object(create_mod.sys, "stdin", io.StringIO("")), \
                contextlib.redirect_stdout(buf):
            code = create_mod.cmd_new(args, self.tmp, Emitter())
        self.assertEqual(2, code)
        self.assertEqual("sp-card-unsupported", json.loads(buf.getvalue())["code"])


class CardTransitions(GitStoreFixture):
    def _spec(self):
        fake = FakeCard(next_number=10)
        backend = GitBackend(self.clone("a"), card=fake)
        backend.create_spec("plans", _doc_with_tasks())
        fake.calls.clear()
        return backend, fake

    def test_ticks_after_the_stage_moved_and_section_edits_make_no_card_call(self):
        backend, fake = self._spec()
        info, _ = backend.read_spec(10)
        # The FIRST tick moves the derived stage to `executing` (`spec:built`): the start of
        # construction is a lifecycle transition, so it costs exactly one request.
        backend.write_spec(info, info["text"].replace("- [ ] 1.1 first", "- [x] 1.1 first"))
        self.assertEqual(["update"], fake.verbs())
        self.assertEqual(["spec:built"], fake.calls[0][2]["labels"])
        fake.calls.clear()
        info, _ = backend.read_spec(10)
        backend.write_spec(info, info["text"].replace("- [ ] 1.2 second", "- [x] 1.2 second"))
        info, _ = backend.read_spec(10)
        edited, _ = upsert_section(info, "Problem", "## Problem\n\nRewritten entirely.\n")
        backend.write_spec(info, edited)
        self.assertEqual([], fake.calls)
        self.assertEqual(3, len([c for c in self.remote_log() if "write 10" in c]))

    def test_a_record_is_one_card_request_carrying_the_label_and_progress(self):
        backend, fake = self._spec()
        info, _ = backend.read_spec(10)
        approved = set_frontmatter_record(info["text"], "approved",
                                          {"by": "human", "date": "2026-01-02"})
        backend.write_spec(info, approved)
        self.assertEqual(["update"], fake.verbs())
        state = fake.calls[0][2]
        self.assertIn("spec:approved", state["labels"])
        self.assertEqual((0, 2), (state["checked"], state["total"]))
        self.assertFalse(state["closed"])

    def test_archive_is_one_request_that_closes_the_card(self):
        backend, fake = self._spec()
        info, _ = backend.read_spec(10)
        backend.write_spec(info, info["text"] + "\n<!-- outcome stamp -->\n")
        self.assertEqual([], fake.calls)
        info, _ = backend.read_spec(10)
        backend.move_spec(info, "archive")
        self.assertEqual(["update"], fake.verbs())
        self.assertTrue(fake.calls[0][2]["closed"])
        info, _ = backend.read_spec(10)
        backend.move_spec(info, "plans")
        self.assertFalse(fake.calls[-1][2]["closed"])

    def test_a_title_change_is_a_transition(self):
        backend, fake = self._spec()
        info, _ = backend.read_spec(10)
        backend.write_spec(info, info["text"].replace("title: Alpha", "title: Beta"))
        self.assertEqual(["update"], fake.verbs())
        self.assertEqual("Beta", fake.calls[0][2]["title"])

    def test_a_card_failure_is_loud_and_never_rolls_the_spec_back(self):
        backend, fake = self._spec()
        fake.fail_updates = True
        info, _ = backend.read_spec(10)
        approved = set_frontmatter_record(info["text"], "approved",
                                          {"by": "human", "date": "2026-01-02"})
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_spec(info, approved)
        self.assertEqual("sp-card-failed", caught.exception.err["code"])
        self.assertIn("not rolled back", caught.exception.err["message"])
        self.assertEqual(approved, self.remote_file("specs/10.md"))

    def test_a_batch_costs_one_request_per_changed_spec(self):
        fake = FakeCard(next_number=20)
        backend = GitBackend(self.clone("a"), card=fake)
        for title in ("A", "B", "C"):
            backend.create_spec("plans", _doc_with_tasks(title))
        fake.calls.clear()
        infos = [backend.read_spec(n)[0] for n in (20, 21, 22)]
        backend.write_specs([
            (infos[0], set_frontmatter_record(infos[0]["text"], "priority", {"level": "high"})),
            (infos[1], infos[1]["text"] + "\n<!-- note -->\n"),
            (infos[2], set_frontmatter_record(infos[2]["text"], "priority", {"level": "low"}))])
        self.assertEqual([20, 22], [c[1] for c in fake.calls])
        self.assertEqual(1, len([c for c in self.remote_log() if c.endswith("write 20 21 22")]))


class CardConfiguration(GitStoreFixture):
    def test_the_default_is_none_unless_the_remote_is_github(self):
        path = self.clone("a")
        self.assertEqual("none", cards.card_settings({}, path)["provider"])
        with mock.patch("quenching.specs.config.detect_provider",
                        return_value=("github", "github.com")):
            self.assertEqual("github", cards.card_settings({}, path)["provider"])
            self.assertEqual("none", cards.card_settings(
                {"card": {"provider": "none"}}, path)["provider"])
        self.assertEqual("azure-boards", cards.card_settings(
            {"card": {"provider": "azure-boards", "at": "capture"}}, path)["provider"])

    def test_the_branch_config_declares_the_card(self):
        from quenching.specs import config as config_mod
        path = self.clone("a")
        import os
        os.makedirs(os.path.join(path, ".claude"), exist_ok=True)
        with open(os.path.join(path, ".claude", "quenching.json"), "w", encoding="utf-8") as fh:
            json.dump({"backend": "git"}, fh)
        GitBackend(self.clone("b"), card=None).write_config(
            {"card": {"provider": "azure-boards", "at": "capture"}})
        self.assertEqual({"provider": "azure-boards", "at": "capture"},
                         config_mod.load_config(path)["card"])


class GitHubTransport(unittest.TestCase):
    def _run(self, calls, reply):
        def fake(cwd, *argv, stdin=None):
            calls.append({"argv": list(argv), "payload": json.loads(stdin) if stdin else None})
            return 0, json.dumps(reply), "", 1
        return mock.patch.object(gh_mod, "_gh_run", fake)

    def _state(self, phase="plans", **extra):
        doc = _doc_with_tasks()
        if phase == "archive":
            doc = set_frontmatter_record(doc, "approved", {"by": "human", "date": "2026-01-02"})
        info = derive_info({"id": 31, "phase": phase}, doc)
        return {**cards.card_state(info), **extra}

    def test_create_is_one_post_with_the_thin_body(self):
        calls = []
        with self._run(calls, {"number": 31}):
            number = cards.GitHubCard("o/r", ".").create(self._state())
        self.assertEqual(31, number)
        self.assertEqual(1, len(calls))
        self.assertEqual(["api", "-X", "POST", "repos/o/r/issues"], calls[0]["argv"][:4])
        body = calls[0]["payload"]["body"]
        self.assertTrue(body.startswith(cards.CARD_MARKER))
        self.assertIn("Tasks 0/2", body)
        self.assertIn("https://github.com/o/r/tree/quenching/specs", body)
        self.assertNotIn("quenching-spec", body)

    def test_update_is_one_patch_with_state_labels_and_the_file_link(self):
        calls = []
        with self._run(calls, {"number": 31}):
            cards.GitHubCard("o/r", ".").update(31, self._state("archive"))
        self.assertEqual(1, len(calls))
        payload = calls[0]["payload"]
        self.assertEqual("closed", payload["state"])
        self.assertIn("spec:approved", payload["labels"])
        self.assertIn("https://github.com/o/r/blob/quenching/specs/archive/31.md",
                      payload["body"])

    def test_adopting_a_pull_request_is_refused(self):
        calls = []
        with self._run(calls, {"number": 3, "pull_request": {}}):
            with self.assertRaises(BackendRefusal) as caught:
                cards.GitHubCard("o/r", ".").read(3)
        self.assertEqual("sp-card-not-an-issue", caught.exception.err["code"])


class AzureTransport(unittest.TestCase):
    def _run(self, calls, reply):
        def fake(cwd, *argv, stdin=None):
            calls.append(list(argv))
            return 0, json.dumps(reply), ""
        return mock.patch.object(az_mod, "_az_run", fake)

    def _client(self):
        return cards.AzureCard("https://dev.azure.com/org", "TI", ".",
                               placement={"areaPath": "TI\\Area", "iterationPath": "TI\\Sprint"},
                               states={"plans": "Active", "archive": "Closed"})

    def _state(self, phase="plans"):
        return cards.card_state(derive_info({"id": 8, "phase": phase}, _doc_with_tasks()))

    def test_create_uses_the_boards_cli_with_placement_and_never_az_rest(self):
        calls = []
        with self._run(calls, {"id": 8}):
            self.assertEqual(8, self._client().create(self._state()))
        self.assertEqual(1, len(calls))
        argv = calls[0]
        self.assertEqual(["boards", "work-item", "create"], argv[:3])
        self.assertNotIn("rest", argv)
        self.assertEqual("TI\\Area", argv[argv.index("--area") + 1])
        self.assertEqual("TI\\Sprint", argv[argv.index("--iteration") + 1])
        description = argv[argv.index("--description") + 1]
        self.assertIn("quenching-card", description)
        self.assertIn("branch quenching", description)

    def test_a_transition_is_one_update_with_the_declared_state(self):
        calls = []
        with self._run(calls, {"id": 8}):
            self._client().update(8, self._state("archive"))
        self.assertEqual(1, len(calls))
        argv = calls[0]
        self.assertEqual(["boards", "work-item", "update"], argv[:3])
        self.assertNotIn("rest", argv)
        self.assertEqual("Closed", argv[argv.index("--state") + 1])
        self.assertEqual("TI\\Area", argv[argv.index("--area") + 1])


class Migration(GitStoreFixture):
    class NativeSource(MemoryBackend):
        """A tracker-shaped source: tags and assignee are native fields, not in the text."""
        name = "github"

        def read_spec(self, spec_id):
            info, err = super().read_spec(spec_id)
            if info and info["id"] == 1:
                info["frontmatter"]["tags"] = ["alpha", "beta"]
                info["frontmatter"]["assignee"] = "ana"
            return info, err

    def _source(self):
        source = self.NativeSource()
        source.create_spec("plans", _doc_with_tasks("One"))
        source.create_spec("plans", _doc_with_tasks("Two"))
        source.create_spec("archive", canonical._case_doc("Old"))
        source.docs[5] = ("plans", _doc_with_tasks("Five"))
        return source

    def _target(self):
        return GitBackend(self.clone("target"), card=None)

    def test_a_dry_run_reads_everything_and_writes_nothing(self):
        target = self._target()
        report = migrate_mod.migrate(self._source(), target, {"subjects": {"s": {}}},
                                     write=False)
        self.assertTrue(report["ok"], report)
        self.assertEqual((4, 3, 1), (report["count"], report["open"], report["closed"]))
        self.assertEqual({"backend": "git"}, report["configChange"]["set"])
        self.assertEqual({"provider": "github", "at": "capture"}, report["configChange"]["card"])
        self.assertEqual([], target.list_specs())
        self.assertEqual("", _sh(self.remote, "branch", "--list", "quenching").strip())

    def test_write_is_one_commit_with_the_same_ids_and_the_config(self):
        target = self._target()
        source = self._source()
        report = migrate_mod.migrate(source, target, {"subjects": {"s": {"name": "S"}},
                                                      "hooks": {"x": 1}}, write=True)
        self.assertTrue(report["ok"], report)
        self.assertEqual([], report["diffs"])
        self.assertEqual(["[skip ci] specs: import 4 specs"], self.remote_log())
        listing = {r["id"]: r["phase"] for r in target.list_specs()}
        self.assertEqual({1: "plans", 2: "plans", 3: "archive", 5: "plans"}, listing)
        self.assertIn("specs/archive/3.md",
                      _sh(self.remote, "ls-tree", "-r", "--name-only", "quenching"))
        branch_config = json.loads(self.remote_file("quenching.json"))["specs"]
        self.assertEqual({"name": "S"}, branch_config["subjects"]["s"])
        self.assertNotIn("hooks", branch_config)
        self.assertEqual("github", branch_config["card"]["provider"])
        self.assertEqual("6\n", self.remote_file("specs/.next-id"))

    def test_native_fields_are_reassembled_into_the_frontmatter(self):
        target = self._target()
        migrate_mod.migrate(self._source(), target, {}, write=True)
        text = self.remote_file("specs/1.md")
        self.assertIn('tags: ["alpha", "beta"]', text)
        self.assertIn("assignee: ana", text)
        info, _ = target.read_spec(1)
        self.assertEqual(["alpha", "beta"], info["frontmatter"]["tags"])
        self.assertEqual(self.remote_file("specs/2.md"), _doc_with_tasks("Two"))

    def test_a_rerun_is_idempotent_and_a_conflict_refuses_the_batch(self):
        target = self._target()
        source = self._source()
        migrate_mod.migrate(source, target, {}, write=True)
        migrate_mod.migrate(source, target, {}, write=True)
        self.assertEqual(1, len(self.remote_log()))
        source.docs[2] = ("plans", _doc_with_tasks("Changed"))
        with self.assertRaises(BackendRefusal) as caught:
            migrate_mod.migrate(source, target, {}, write=True)
        self.assertEqual("sp-git-id-taken", caught.exception.err["code"])
        self.assertEqual(1, len(self.remote_log()))

    def test_equality_reports_the_differences_it_finds(self):
        source = self._source()
        infos, _ = migrate_mod.read_front(source)
        other = [dict(i) for i in infos]
        other[0] = derive_info(other[0], other[0]["text"].replace("title: One", "title: Uno"))
        self.assertEqual([{"id": 1, "kind": "differs", "fields": ["title"]}],
                         migrate_mod.diff_fronts(infos, other))
        self.assertEqual([{"id": 3, "kind": "missing-in-target"}],
                         migrate_mod.diff_fronts(infos, infos[:-1]))

    def test_thin_open_cards_rewrites_only_open_items(self):
        fake = FakeCard()
        target = self._target()
        report = migrate_mod.migrate(self._source(), target, {}, write=True, thin_cards=True,
                                     card_client=fake)
        self.assertTrue(report["ok"], report)
        self.assertEqual([1, 2, 5], sorted(c[1] for c in fake.calls))
        self.assertNotIn(3, [c[1] for c in fake.calls])
        self.assertEqual({"plans"}, {c[2]["phase"] for c in fake.calls})

    def test_a_card_failure_is_reported_after_the_commit_landed(self):
        fake = FakeCard(fail_updates=True)
        target = self._target()
        report = migrate_mod.migrate(self._source(), target, {}, write=True, thin_cards=True,
                                     card_client=fake)
        self.assertFalse(report["ok"])
        self.assertEqual(3, len(report["cardErrors"]))
        self.assertEqual(4, len(target.list_specs()))

    def _cmd(self, **flags):
        args = argparse.Namespace(json=True, to="git", write=False, thin_open_cards=False,
                                  dry_run=False, **flags)
        buf = io.StringIO()
        path = self.clone("cmd")
        target = GitBackend(path, card=None)
        with mock.patch.object(migrate_mod, "open_backend", lambda _r: (self._source(), {})), \
                mock.patch.object(migrate_mod, "open_git_backend", lambda _r: (target, {})), \
                contextlib.redirect_stdout(buf):
            code = migrate_mod.cmd_migrate(args, path, Emitter())
        return code, json.loads(buf.getvalue())

    def test_the_command_is_a_dry_run_by_default(self):
        code, payload = self._cmd()
        self.assertEqual(0, code)
        self.assertTrue(payload["dryRun"])
        self.assertEqual("", _sh(self.remote, "branch", "--list", "quenching").strip())

    def test_the_command_writes_with_write(self):
        args = argparse.Namespace(json=True, to="git", write=True, thin_open_cards=False,
                                  dry_run=False)
        path = self.clone("cmd2")
        target = GitBackend(path, card=None)
        buf = io.StringIO()
        with mock.patch.object(migrate_mod, "open_backend", lambda _r: (self._source(), {})), \
                mock.patch.object(migrate_mod, "open_git_backend", lambda _r: (target, {})), \
                contextlib.redirect_stdout(buf):
            code = migrate_mod.cmd_migrate(args, path, Emitter())
        self.assertEqual(0, code, buf.getvalue())
        self.assertFalse(json.loads(buf.getvalue())["dryRun"])
        self.assertEqual(4, len(target.list_specs()))

    def test_thinning_without_write_and_a_missing_destination_refuse(self):
        buf = io.StringIO()
        args = argparse.Namespace(json=True, to="git", write=False, thin_open_cards=True,
                                  dry_run=False)
        with contextlib.redirect_stdout(buf):
            self.assertEqual(2, migrate_mod.cmd_migrate(args, self.tmp, Emitter()))
        self.assertEqual("sp-migrate-thin-needs-write", json.loads(buf.getvalue())["code"])
        buf = io.StringIO()
        args = argparse.Namespace(json=True, to=None, write=False, thin_open_cards=False,
                                  dry_run=False)
        with contextlib.redirect_stdout(buf):
            self.assertEqual(2, migrate_mod.cmd_migrate(args, self.tmp, Emitter()))
        self.assertEqual("sp-local-backend-removed", json.loads(buf.getvalue())["code"])


if __name__ == "__main__":
    unittest.main()
