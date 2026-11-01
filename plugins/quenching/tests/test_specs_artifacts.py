"""The artifact capability: text stored beside the spec, read back through the same store.

The rule these tests exist for is that an artifact is a STORE WRITE and not a side file: it
must survive the pending ref, the replay onto a newer tip and the single-commit push exactly
as a document does. The cases that prove the second half live in `test_specs_git_backend` and
`test_specs_push`; this module owns the capability itself.
"""

import contextlib
import io
import json
import os
import pathlib
import subprocess
import sys
import unittest
from types import SimpleNamespace
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
import test_specs_git_backend as fixture
from test_specs_git_backend import GitStoreFixture
from quenching.specs import backends as backends_mod
from quenching.specs.backends import git as git_mod
from quenching.specs.commands import cli
from quenching.specs.backends.base import MAX_ARTIFACT_BYTES, BackendRefusal
from quenching.specs.backends.git import GitBackend
from quenching.specs.backends.github import GitHubBackend
from quenching.specs.backends.memory import MemoryBackend


def _seed(backend, count: int = 1) -> None:
    for n in range(1, count + 1):
        backend.create_spec("plans", f"---\ntitle: Spec {n}\n---\n\n"
                                     f"## Problem\n\nbody {n}\n")


class RoundTrip(GitStoreFixture):
    def test_write_read_list_and_remove(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        locator = backend.write_artifact(1, "handoff-2026-11-01-x.md", "the handoff\n")
        self.assertEqual("quenching:specs/artifacts/1/handoff-2026-11-01-x.md", locator)
        self.assertEqual("the handoff\n", backend.read_artifact(1, "handoff-2026-11-01-x.md"))
        self.assertEqual([{"spec": 1, "name": "handoff-2026-11-01-x.md",
                           "path": locator}], backend.list_artifacts(1))
        self.assertEqual([], backend.list_artifacts())
        backend.remove_artifact(1, "handoff-2026-11-01-x.md")
        self.assertEqual([], backend.list_artifacts(1))
        with self.assertRaises(BackendRefusal) as caught:
            backend.read_artifact(1, "handoff-2026-11-01-x.md")
        self.assertEqual("sp-artifact-unknown", caught.exception.err["code"])

    def test_a_standalone_artifact_lives_under_handoffs(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        locator = backend.write_artifact(None, "handoff-2026-11-01-x.md", "no spec\n")
        self.assertEqual("quenching:specs/artifacts/_handoffs/handoff-2026-11-01-x.md", locator)
        self.assertEqual("no spec\n", backend.read_artifact(None, "handoff-2026-11-01-x.md"))
        self.assertEqual([], backend.list_artifacts(1))
        self.assertEqual(["handoff-2026-11-01-x.md"],
                         [row["name"] for row in backend.list_artifacts()])

    def test_writing_the_same_name_replaces_it(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        backend.write_artifact(1, "h.md", "first\n")
        backend.write_artifact(1, "h.md", "second\n")
        self.assertEqual("second\n", backend.read_artifact(1, "h.md"))
        self.assertEqual(1, len(backend.list_artifacts(1)))

    def test_an_attached_artifact_needs_a_spec(self):
        backend = GitBackend(self.clone("a"))
        for call in (lambda: backend.write_artifact(99, "h.md", "text\n"),
                     lambda: backend.read_artifact(99, "h.md"),
                     lambda: backend.list_artifacts(99),
                     lambda: backend.remove_artifact(99, "h.md")):
            with self.assertRaises(BackendRefusal) as caught:
                call()
            self.assertEqual("sp-unknown-id", caught.exception.err["code"])


class Ownership(GitStoreFixture):
    """An artifact belongs to its spec at every point the store judges ownership."""

    def test_the_artifact_is_visible_to_a_second_reader_before_the_sync(self):
        path = self.clone("a")
        backend = GitBackend(path)
        _seed(backend)
        backend.write_artifact(1, "h.md", "pending text\n")
        self.assertEqual("pending text\n", GitBackend(path).read_artifact(1, "h.md"))

    def test_a_push_carries_the_document_and_its_artifact_in_one_commit(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        backend.write_artifact(1, "h.md", "handoff\n")
        backend.push()
        self.assertEqual("handoff\n", self.remote_file("specs/artifacts/1/h.md"))
        self.assertEqual("handoff\n", GitBackend(self.clone("b")).read_artifact(1, "h.md"))
        self.assertIsNone(backend.pending_state())

    def test_an_artifact_only_pending_is_reported_and_pushed(self):
        backend = GitBackend(self.clone("a"))
        backend.write_artifact(None, "h.md", "no spec\n")
        state = backend.pending_state()
        self.assertIsNotNone(state)
        self.assertEqual([], state["specs"])
        self.assertEqual(["_handoffs/h.md"], state["artifacts"])
        backend.push()
        self.assertEqual("no spec\n", self.remote_file("specs/artifacts/_handoffs/h.md"))
        self.assertIsNone(backend.pending_state())

    def test_both_sides_changing_one_artifact_conflicts_on_its_spec(self):
        first = GitBackend(self.clone("a"))
        _seed(first)
        first.push()
        second = GitBackend(self.clone("b"))
        second.write_artifact(1, "h.md", "theirs\n")
        first.write_artifact(1, "h.md", "mine\n")
        first.push()
        with self.assertRaises(BackendRefusal) as caught:
            second.push()
        self.assertEqual("sp-git-stale-write", caught.exception.err["code"])
        self.assertEqual([1], caught.exception.err["ids"])
        self.assertEqual("mine\n", self.remote_file("specs/artifacts/1/h.md"))

    def test_a_write_to_an_artifact_of_a_spec_the_remote_moved_refuses(self):
        path = self.clone("a")
        first = GitBackend(path)
        _seed(first, 2)
        first.push()
        info, _ = first.read_spec(1)
        first.write_spec(info, info["text"] + "\nlocal\n")     # the pending write that conflicts
        other = GitBackend(self.clone("b"))
        for spec_id in (1, 2):
            moved, _ = other.read_spec(spec_id)
            other.write_spec(moved, moved["text"] + "\nremote\n")
        other.push()
        with mock.patch.object(git_mod, "FETCH_TTL_S", 0):
            fresh = GitBackend(path)
            fresh.read_spec(2)
        with self.assertRaises(BackendRefusal) as caught:
            fresh.write_artifact(2, "h.md", "attached to the changed spec\n")
        self.assertEqual("sp-git-stale-write", caught.exception.err["code"])
        self.assertEqual([2], caught.exception.err["ids"])


class Preload(GitStoreFixture):
    """`list --lean` answers from the documents, never from the artifacts beside them."""

    def _binary_artifact(self, backend: GitBackend, path: str, name: str = "dump.bin") -> str:
        """A blob the API refuses to write — written the way a hand commit would."""
        raw = bytes(range(256)) * 4 + b"\xff\xfe\x00 not utf-8"
        run = subprocess.run(["git", "hash-object", "-w", "--stdin"], cwd=path, input=raw,
                             capture_output=True, check=True)
        sha = run.stdout.decode().strip()
        backend._store(lambda view: ({f"specs/artifacts/1/{name}": git_mod._Blob(sha)}, None),
                       f"artifact 1 {name}")
        return sha

    def test_a_lean_listing_decodes_the_documents_and_no_artifact(self):
        path = self.clone("a")
        backend = GitBackend(path)
        _seed(backend)
        backend.write_artifact(1, "big.log", "a line of the handoff\n" * 40_000)
        backend.push()
        artifact_blob = backend._view()["specs/artifacts/1/big.log"][0]
        document_blob = backend._view()["specs/1.md"][0]
        seen: list[str] = []
        real = GitBackend._texts

        def spy(this, blobs):
            seen.extend(blobs)
            return real(this, blobs)

        with mock.patch.object(GitBackend, "_texts", spy):
            rows = GitBackend(path).list_specs(lean=True)
        self.assertEqual([1], [row["id"] for row in rows])
        self.assertEqual("Spec 1", rows[0]["title"])
        self.assertIn(document_blob, seen)
        self.assertNotIn(artifact_blob, seen)

    def test_a_binary_artifact_neither_breaks_the_listing_nor_tracebacks_on_read(self):
        path = self.clone("a")
        backend = GitBackend(path)
        _seed(backend)
        backend.push()
        self._binary_artifact(backend, path)
        fresh = GitBackend(path)
        self.assertEqual([1], [row["id"] for row in fresh.list_specs(lean=True)])
        with self.assertRaises(BackendRefusal) as caught:
            GitBackend(path).read_artifact(1, "dump.bin")
        self.assertEqual("sp-artifact-binary", caught.exception.err["code"])


class Refusals(GitStoreFixture):
    def test_the_name_is_one_segment(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        for name in ("", "../x", "a/b", ".hidden", "x" * 121):
            with self.subTest(name=name):
                with self.assertRaises(BackendRefusal) as caught:
                    backend.write_artifact(1, name, "text\n")
                self.assertEqual("sp-artifact-name", caught.exception.err["code"])

    def test_the_size_cap_refuses_before_anything_is_written(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "big.md", "x" * (MAX_ARTIFACT_BYTES + 1))
        self.assertEqual("sp-artifact-too-large", caught.exception.err["code"])
        self.assertEqual([], backend.list_artifacts(1))

    def test_the_leak_guard_runs_on_the_artifact(self):
        backend = GitBackend(self.clone("a"))
        _seed(backend)
        # Assembled at run time: this file is scanned by the gate it is testing, and a
        # tax id written whole here would be the finding it is meant to catch.
        fake_tax_id = ".".join(["123", "456", "789"]) + "-" + "0" + "1"
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "h.md", f"cpf {fake_tax_id}\n")
        self.assertEqual("sp-leak", caught.exception.err["code"])
        self.assertEqual([], backend.list_artifacts(1))

    def test_a_backend_without_the_capability_refuses(self):
        backend = GitHubBackend("owner/repo", ".", types={}, open_issues=0)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "h.md", "text\n")
        self.assertEqual("sp-artifact-unsupported", caught.exception.err["code"])
        self.assertEqual("github", caught.exception.err["message"].split("'")[1])


class MemoryEquivalence(unittest.TestCase):
    def test_the_fake_answers_the_same_shape(self):
        backend = MemoryBackend()
        _seed(backend)
        locator = backend.write_artifact(1, "h.md", "text\n")
        self.assertEqual("memory://artifacts/1/h.md", locator)
        self.assertEqual("text\n", backend.read_artifact(1, "h.md"))
        self.assertEqual([{"spec": 1, "name": "h.md", "path": locator}],
                         backend.list_artifacts(1))
        backend.remove_artifact(1, "h.md")
        self.assertEqual([], backend.list_artifacts(1))

    def test_the_fake_refuses_an_unknown_spec_and_a_bad_name(self):
        backend = MemoryBackend()
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(7, "h.md", "text\n")
        self.assertEqual("sp-unknown-id", caught.exception.err["code"])
        _seed(backend)
        with self.assertRaises(BackendRefusal) as caught:
            backend.write_artifact(1, "a/b", "text\n")
        self.assertEqual("sp-artifact-name", caught.exception.err["code"])


class Cli(GitStoreFixture):
    """`cq specs artifact` end to end: the four verbs, the two body sources and the exit codes."""

    def setUp(self):
        super().setUp()
        self.path = self.clone("a")
        os.makedirs(os.path.join(self.path, ".claude"))
        with open(os.path.join(self.path, ".claude", "quenching.json"), "w") as handle:
            json.dump({"backend": "git"}, handle)
        backend = GitBackend(self.path)
        _seed(backend)
        backend.push()
        # A `cq` invocation is a NEW process: the store it opens must not inherit the instance
        # the push created (and the tip that instance memoized while the ref was still moving).
        git_mod._STORES.clear()
        backends_mod._BACKEND_CACHE.clear()

    def run_cli(self, *argv: str, stdin=None) -> tuple[int, str]:
        buf = io.StringIO()
        patcher = mock.patch.object(sys, "stdin", stdin) if stdin is not None else None
        if patcher:
            patcher.start()
            self.addCleanup(patcher.stop)
        with contextlib.redirect_stdout(buf):
            code = cli.main(["--root", self.path, *argv])
        return code, buf.getvalue()

    def test_write_from_stdin_then_list_read_and_rm(self):
        code, said = self.run_cli("artifact", "write", "--spec", "1", "--name", "h.md",
                                  stdin=io.StringIO("the handoff\n"))
        self.assertEqual(0, code, said)
        self.assertIn("quenching:specs/artifacts/1/h.md", said)
        code, said = self.run_cli("artifact", "list", "--spec", "1")
        self.assertEqual((0, "quenching:specs/artifacts/1/h.md"), (code, said.strip()))
        code, said = self.run_cli("artifact", "read", "--spec", "1", "--name", "h.md")
        self.assertEqual((0, "the handoff\n"), (code, said))
        code, said = self.run_cli("artifact", "rm", "--spec", "1", "--name", "h.md")
        self.assertEqual(0, code, said)
        self.assertIn("removed", said)
        code, said = self.run_cli("artifact", "list", "--spec", "1")
        self.assertEqual((0, "no artifact for spec 1"), (code, said.strip()))

    def test_write_from_a_file_and_read_it_back_into_another(self):
        source = os.path.join(self.tmp, "source.md")
        with open(source, "w", encoding="utf-8") as handle:
            handle.write("from a file\n")
        code, said = self.run_cli("artifact", "write", "--spec", "1", "--name", "h.md",
                                  "--from", source)
        self.assertEqual(0, code, said)
        dest = os.path.join(self.tmp, "dest.md")
        code, said = self.run_cli("artifact", "read", "--spec", "1", "--name", "h.md",
                                  "--out", dest)
        self.assertEqual(0, code, said)
        with open(dest, encoding="utf-8") as handle:
            self.assertEqual("from a file\n", handle.read())

    def test_json_carries_the_spec_name_locator_and_size(self):
        code, said = self.run_cli("artifact", "write", "--spec", "1", "--name", "h.md",
                                  "--json", stdin=io.StringIO("six\n"))
        self.assertEqual(0, code, said)
        wrote = json.loads(said)
        self.assertEqual((1, "h.md", "quenching:specs/artifacts/1/h.md", 4),
                         (wrote["spec"], wrote["name"], wrote["path"], wrote["bytes"]))
        code, said = self.run_cli("artifact", "read", "--spec", "1", "--name", "h.md", "--json")
        read = json.loads(said)
        self.assertEqual("six\n", read["text"])
        code, said = self.run_cli("artifact", "list", "--json")
        self.assertEqual({"count": 0, "artifacts": []},
                         {k: v for k, v in json.loads(said).items()
                          if k in ("count", "artifacts")})

    def test_a_standalone_artifact_needs_no_spec(self):
        code, said = self.run_cli("artifact", "write", "--name", "h.md", "--json",
                                  stdin=io.StringIO("no spec\n"))
        self.assertEqual(0, code, said)
        self.assertIsNone(json.loads(said)["spec"])
        code, said = self.run_cli("artifact", "list")
        self.assertEqual("quenching:specs/artifacts/_handoffs/h.md", said.strip())

    def test_every_refusal_exits_two_with_its_own_code(self):
        missing = os.path.join(self.tmp, "absent.md")
        binary = SimpleNamespace(buffer=io.BytesIO(b"\xff\xfe\x00"))
        cases = {
            "sp-artifact-verb": ("artifact", "--json"),
            "sp-artifact-unknown": ("artifact", "read", "--spec", "1", "--name", "nope.md",
                                    "--json"),
            "sp-unknown-id": ("artifact", "write", "--spec", "99", "--name", "h.md", "--json"),
            "sp-artifact-unreadable": ("artifact", "write", "--spec", "1", "--name", "h.md",
                                       "--from", missing, "--json"),
        }
        for code_name, argv in cases.items():
            with self.subTest(code=code_name):
                code, said = self.run_cli(*argv, stdin=io.StringIO("text\n"))
                self.assertEqual(2, code, said)
                self.assertEqual(code_name, json.loads(said)["code"])
        code, said = self.run_cli("artifact", "write", "--spec", "1", "--name", "h.md",
                                  "--json", stdin=binary)
        self.assertEqual((2, "sp-artifact-binary"), (code, json.loads(said)["code"]))
        code, said = self.run_cli("artifact", "write", "--spec", "1", "--name", "a/b", "--json",
                                  stdin=io.StringIO("text\n"))
        self.assertEqual((2, "sp-artifact-name"), (code, json.loads(said)["code"]))


if __name__ == "__main__":
    unittest.main()
