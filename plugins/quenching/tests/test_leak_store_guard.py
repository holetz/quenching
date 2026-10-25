"""Executable proofs for the leak guard on every specs store write.

Each backend runs its write primitive through `guard_store_write` before anything leaves the
process: paths are normalized, a generic or denylist hit refuses with `sp-leak` (exit 2) and
nothing is written. Against the previous document only the lines a write adds are judged, so a
legacy spec stays writable. The denylisted term is the test's own, in a temporary denylist."""
from __future__ import annotations

import os
import pathlib
import sys
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401 — must precede the `quenching` import
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from test_specs_git_backend import GitStoreFixture
from quenching.common import leak
from quenching.specs.backends import azure as az_mod
from quenching.specs.backends import github as gh_mod
from quenching.specs.backends.azure import AzureBoardsBackend
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.git import GitBackend
from quenching.specs.backends.github import GitHubBackend
from quenching.specs.backends.memory import MemoryBackend

HOME = "/home/alice"
TERM = "acme-corp"
DATABRICKS_HOST = "adb-" + "1234567890" + ".7.azure" + "databricks.net"


def spec(body: str) -> str:
    return f"---\ntitle: guard\n---\n\n## Problem\n\n{body}\n"


def no_transport(*_args, **_kwargs):
    raise AssertionError("a refused write reached the transport")


class GuardEnv(GitStoreFixture):
    """The git store fixture plus a fake `$HOME` and a denylist of the test's own."""

    def setUp(self):
        super().setUp()
        self.denylist = pathlib.Path(self.tmp, "denylist.txt")
        self.denylist.write_text(f"{TERM}\n", encoding="utf-8")
        patcher = mock.patch.dict(os.environ, {"HOME": HOME,
                                               leak.DENYLIST_ENV: str(self.denylist)})
        patcher.start()
        self.addCleanup(patcher.stop)

    def assertLeak(self, raised: BackendRefusal, label: str) -> None:
        self.assertEqual((raised.err["code"], raised.err["exit"]), ("sp-leak", 2))
        self.assertEqual(raised.err["findings"][0]["label"], label)
        self.assertIn("nothing was written", raised.err["message"])


class Memory(GuardEnv):
    def test_create_normalizes_paths_and_refuses_a_denylist_term(self):
        backend = MemoryBackend()
        backend.create_spec("plans", spec(f"see {HOME}/notes.md"))
        self.assertIn("see ~/notes.md", backend.docs[1][1])
        with self.assertRaises(BackendRefusal) as caught:
            backend.create_spec("plans", spec(f"org {TERM}"))
        self.assertLeak(caught.exception, "denylist:1")
        self.assertEqual(list(backend.docs), [1])

    def test_write_judges_only_the_lines_it_adds(self):
        backend = MemoryBackend()
        backend.docs[1] = ("plans", spec(f"legacy {TERM}"))
        info, _ = backend.read_spec(1)
        backend.write_spec(info, info["text"] + "a clean line\n")
        self.assertIn("a clean line", backend.docs[1][1])
        info, _ = backend.read_spec(1)
        before = backend.docs[1][1]
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_spec(info, info["text"] + f"host {DATABRICKS_HOST}\n")
        self.assertLeak(caught.exception, "azure-databricks-host")
        self.assertEqual(backend.docs[1][1], before)


class Git(GuardEnv):
    def test_a_refused_create_pushes_nothing(self):
        backend = GitBackend(self.clone("a"))
        with self.assertRaises(BackendRefusal) as caught:
            backend.create_spec("plans", spec(f"org {TERM}"))
        self.assertLeak(caught.exception, "denylist:1")
        self.assertEqual(self.remote_log_or_empty(), [])

    def test_write_keeps_the_legacy_line_and_refuses_a_new_one(self):
        self.denylist.write_text("# nothing yet\n", encoding="utf-8")
        backend = GitBackend(self.clone("a"))
        locator = backend.create_spec("plans", spec(f"legacy {TERM}"))
        self.denylist.write_text(f"{TERM}\n", encoding="utf-8")
        spec_id = int(locator.rsplit("/", 1)[1].removesuffix(".md"))
        path = locator.removeprefix("quenching:")
        info, _ = backend.read_spec(spec_id)
        backend.write_spec(info, info["text"] + "a clean line\n")
        self.assertIn("a clean line", self.remote_file(path))
        info, _ = backend.read_spec(spec_id)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_spec(info, info["text"] + f"another {TERM}\n")
        self.assertLeak(caught.exception, "denylist:1")
        self.assertNotIn("another", self.remote_file(path))

    def test_import_is_judged_whole(self):
        backend = GitBackend(self.clone("a"))
        with self.assertRaises(BackendRefusal) as caught:
            backend.import_specs([(7, "plans", spec(f"org {TERM}"))])
        self.assertLeak(caught.exception, "denylist:1")
        self.assertEqual(self.remote_log_or_empty(), [])

    def test_a_denylisted_commit_email_refuses_the_store_write(self):
        backend = GitBackend(self.clone("a"))
        with mock.patch.dict(os.environ, {"GIT_COMMITTER_EMAIL": f"dev@{TERM}.example"}):
            with self.assertRaises(BackendRefusal) as caught:
                backend.create_spec("plans", spec("clean"))
        self.assertLeak(caught.exception, "denylist:1")
        self.assertEqual(caught.exception.err["findings"][0]["where"],
                         "git var GIT_COMMITTER_IDENT")
        self.assertEqual(self.remote_log_or_empty(), [])

    def test_a_denylisted_email_refuses_before_the_card_is_created(self):
        backend = GitBackend(self.clone("a"))
        card = mock.Mock()
        card.create.side_effect = no_transport
        with mock.patch.object(GitBackend, "card", return_value=card), \
                mock.patch.dict(os.environ, {"GIT_AUTHOR_EMAIL": f"dev@{TERM}.example"}):
            with self.assertRaises(BackendRefusal) as caught:
                backend.create_spec("plans", spec("clean"))
        self.assertLeak(caught.exception, "denylist:1")
        card.create.assert_not_called()

    def remote_log_or_empty(self) -> list[str]:
        try:
            return self.remote_log()
        except AssertionError:
            return []


class Trackers(GuardEnv):
    def test_github_refuses_before_any_request(self):
        backend = GitHubBackend("owner/repo", self.tmp)
        info = {"id": 3, "text": spec("legacy"), "frontmatter": {}}
        with mock.patch.object(gh_mod, "_gh_run", side_effect=no_transport):
            for write in (lambda: backend.create_spec("plans", spec(f"org {TERM}")),
                          lambda: backend.write_spec(info, info["text"] + f"org {TERM}\n")):
                with self.assertRaises(BackendRefusal) as caught:
                    write()
                self.assertLeak(caught.exception, "denylist:1")

    def test_azure_refuses_before_any_request(self):
        backend = AzureBoardsBackend("org", "proj", {"plans": "Active", "archive": "Closed"},
                                     self.tmp)
        info = {"id": 3, "text": spec("legacy"), "frontmatter": {}}
        with mock.patch.object(az_mod, "_az_run", side_effect=no_transport), \
                mock.patch.object(az_mod, "announce_unproved"):
            for write in (lambda: backend.create_spec("plans", spec(f"host {DATABRICKS_HOST}")),
                          lambda: backend.write_spec(info, info["text"] + f"org {TERM}\n")):
                with self.assertRaises(BackendRefusal) as caught:
                    write()
                self.assertEqual(caught.exception.err["code"], "sp-leak")


if __name__ == "__main__":
    unittest.main()
