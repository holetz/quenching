"""`migrate --to github`, offline: the destination is an in-memory double that allocates its own
issue numbers and reads its blocked-by relations back as `predecessor_links`, the way the GitHub
backend does. No `gh` process, no network and no real repository is ever reached."""

import argparse
import contextlib
import io
import json
import sys
import pathlib
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.azure import azure_predecessor_ids
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import migrate as migrate_mod
from quenching.specs.commands.output import Emitter
from test_specs_migrate_azure import AzureDouble, GitSource, doc, front


class GitHubDouble(MemoryBackend):
    """Allocates issue numbers of its own and keeps the blocked-by relations apart from the
    document: set when an issue is created or written, read back by `predecessor_links`."""
    name = "github"

    def __init__(self, first_id=700, drop_links=False):
        super().__init__()
        self._next_id = first_id
        self.created = 0
        self.links = {}
        self.drop_links = drop_links

    def _link(self, spec_id, text):
        wanted = azure_predecessor_ids(parse_frontmatter(text), spec_id)
        self.links[spec_id] = [] if self.drop_links else wanted

    def create_spec(self, phase, text):
        self.created += 1
        locator = super().create_spec(phase, text)
        spec_id = int(locator.rsplit("/", 1)[1])
        self._link(spec_id, text)
        return f"https://github.com/owner/repo/issues/{spec_id}"

    def write_spec(self, info, text):
        super().write_spec(info, text)
        self._link(info["id"], text)

    def predecessor_links(self, spec_id):
        return sorted(self.links.get(int(spec_id), []))


class Migration(unittest.TestCase):
    def test_a_dry_run_reads_everything_and_creates_nothing(self):
        target = GitHubDouble()
        report = migrate_mod.migrate_to_github(front(), target, write=False)
        self.assertTrue(report["ok"], report)
        self.assertEqual("github", report["to"])
        self.assertEqual([20, 10, 30, 40], report["order"])
        self.assertEqual({"backend": "github"}, report["configChange"]["set"])
        self.assertEqual((0, {}), (target.created, report["idMap"]))

    def test_github_has_no_description_ceiling(self):
        source = front()
        source.docs[20] = ("plans", doc("Two") + "x" * migrate_mod.AZ_DESCRIPTION_MAX)
        report = migrate_mod.migrate_to_github(source, GitHubDouble(), write=True)
        self.assertTrue(report["ok"], report)
        self.assertEqual([], report["oversize"])

    def test_write_remaps_ids_and_proves_the_links_equal_depends_on(self):
        target = GitHubDouble()
        report = migrate_mod.migrate_to_github(front(), target, write=True)
        self.assertTrue(report["ok"], report)
        self.assertEqual(([], [], []),
                         (report["diffs"], report["mismatched"], report["unlinked"]))
        idmap = report["idMap"]
        self.assertTrue(all(v >= 700 for v in idmap.values()))
        self.assertEqual([idmap[20]], target.predecessor_links(idmap[10]))
        one, _ = target.read_spec(idmap[10])
        self.assertEqual([str(idmap[20])], one["frontmatter"]["dependsOn"])
        epic, _ = target.read_spec(idmap[40])
        self.assertIn(f"— spec: #{idmap[10]}", epic["text"])
        self.assertEqual("archive", target.docs[idmap[30]][0])

    def test_links_that_did_not_survive_fail_the_equality(self):
        report = migrate_mod.migrate_to_github(front(), GitHubDouble(drop_links=True),
                                               write=True)
        self.assertFalse(report["ok"])
        self.assertEqual([], report["mismatched"])
        self.assertEqual([10], report["unlinked"])

    def test_an_occupied_destination_refuses_naming_github(self):
        busy = GitHubDouble()
        busy.create_spec("plans", doc("Taken"))
        with self.assertRaises(BackendRefusal) as caught:
            migrate_mod.migrate_to_github(front(), busy, write=True)
        self.assertEqual("sp-migrate-target-not-empty", caught.exception.err["code"])
        self.assertIn("GitHub Issues", caught.exception.err["message"])
        self.assertEqual(1, busy.created)

    def test_a_spec_over_the_dependency_cap_blocks_the_dry_run_and_the_write(self):
        source = GitSource()
        preds = list(range(100, 100 + migrate_mod.GH_DEPENDENCY_LIMIT + 1))
        for n in preds:
            source.docs[n] = ("plans", doc(f"Pred {n}"))
        source.docs[10] = ("plans", doc("Waits", dependsOn="[" + ", ".join(map(str, preds)) + "]"))
        report = migrate_mod.migrate_to_github(source, GitHubDouble(), write=False)
        self.assertFalse(report["ok"])
        self.assertEqual(([], [10]), (report["unresolved"], report["overlinked"]))
        target = GitHubDouble()
        with self.assertRaises(BackendRefusal) as caught:
            migrate_mod.migrate_to_github(source, target, write=True)
        self.assertEqual("sp-migrate-dependency-limit", caught.exception.err["code"])
        self.assertEqual(0, target.created)

    def test_azure_keeps_its_report_without_a_dependency_cap(self):
        report = migrate_mod.migrate_to_azure(front(), AzureDouble(), write=False)
        self.assertNotIn("overlinked", report)

    def test_a_refusal_while_reading_back_keeps_the_id_map(self):
        target = GitHubDouble()

        def refuse(spec_id):
            raise BackendRefusal({"code": "sp-gh-transport", "message": "HTTP 503"})
        target.predecessor_links = refuse
        report = migrate_mod.migrate_to_github(front(), target, write=True)
        self.assertFalse(report["ok"])
        self.assertEqual(4, len(report["idMap"]))
        self.assertEqual(("verify", "sp-gh-transport"),
                         (report["failed"]["stage"], report["failed"]["code"]))

    def test_a_destination_without_predecessor_links_still_matches(self):
        report = migrate_mod.migrate_to_tracker(GitSource(), AzureDouble(),
                                                migrate_mod.GITHUB_PROFILE, write=True)
        self.assertTrue(report["ok"], report)


class Command(unittest.TestCase):
    def _run(self, *, backend="git", target=None, **flags):
        args = argparse.Namespace(**{"json": True, "to": "github", "write": False,
                                     "thin_open_cards": False, "dry_run": False, **flags})
        target = target or GitHubDouble()
        buf = io.StringIO()
        with mock.patch.object(migrate_mod, "load_config", lambda _r: {"backend": backend}), \
                mock.patch.object(migrate_mod, "open_git_backend", lambda _r: (front(), {})), \
                mock.patch.object(migrate_mod, "open_github_backend", lambda _r: (target, {})), \
                mock.patch.object(migrate_mod, "open_azure_backend",
                                  lambda _r: self.fail("the azure opener was reached")), \
                contextlib.redirect_stdout(buf):
            code = migrate_mod.cmd_migrate(args, ".", Emitter())
        return code, json.loads(buf.getvalue()), target

    def test_the_command_is_a_dry_run_by_default(self):
        code, payload, target = self._run()
        self.assertEqual(0, code)
        self.assertTrue(payload["dryRun"])
        self.assertEqual(0, target.created)

    def test_the_command_writes_with_write(self):
        code, payload, target = self._run(write=True)
        self.assertEqual(0, code, payload)
        self.assertEqual(4, target.created)
        self.assertEqual("github", payload["to"])

    def test_each_refusal_is_exit_2_with_its_code(self):
        code, payload, _ = self._run(backend="github")
        self.assertEqual((2, "sp-migrate-source-not-git"), (code, payload["code"]))
        self.assertIn("`--to github`", payload["message"])
        code, payload, _ = self._run(write=True, thin_open_cards=True)
        self.assertEqual((2, "sp-migrate-thin-git-only"), (code, payload["code"]))

    def test_the_cli_accepts_github_as_a_destination(self):
        from quenching.specs.commands.cli import build_parser
        self.assertEqual("github",
                         build_parser()[0].parse_args(["migrate", "--to", "github"]).to)


if __name__ == "__main__":
    unittest.main()
