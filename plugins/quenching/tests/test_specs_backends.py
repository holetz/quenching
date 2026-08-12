"""The `github` transport, the hybrid serialisation both external backends share, the specs
worktree lock, and the meta-suites that keep `files`/`memory`/`github`/`azure-boards` honest
against each other.

Migrated out of the pre-refactor specs script's selftest, which held forty-three
`_failures() -> list[str]`
functions aggregated by hand with no framework underneath them. This file carries the eleven
bound to GitHub, the hybrid wire format, the worktree lock, and cross-backend equivalence — the
fixtures each suite built for itself (the canonical case table, a spec document, a marker) travel
with it unchanged, so a failure here still names which case broke, the way the aggregated list
used to."""
import argparse
import contextlib
import io
import json
import os
import socket
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.azure import AzureBoardsBackend
from quenching.specs.backends.base import BackendRefusal, SpecBackend
from quenching.specs.backends.files import FilesBackend
from quenching.specs.backends.github import (GH_MISSING, GH_NOT_AUTHENTICATED, GitHubBackend,
                                             gh_refusal)
from quenching.specs.backends.hybrid import (GH_BODY_MAX, GH_PART_MAX, HYBRID_TITLE_MAX,
                                             hybrid_join, hybrid_project, hybrid_short_title,
                                             hybrid_split, hybrid_title_join, hybrid_title_split,
                                             hybrid_unwrap, hybrid_unwrap_part, hybrid_wrap,
                                             hybrid_wrap_part)
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands.next import _candidate
from quenching.specs.commands.validate import merge_record_finding, validate_spec
from quenching.specs.config import (BACKENDS, DEFAULT_SPECS_BRANCH, UNPROVED_BACKENDS,
                                    _UNPROVED_ANNOUNCED, announce_unproved, is_root_too_high)
from quenching.specs.parse import FIELD_KEYS, derive_labels
from quenching.specs.parse.edit import upsert_section
from quenching.specs.parse.fields import (legacy_marker_fold, set_frontmatter_key,
                                          set_frontmatter_record)
from quenching.specs.parse.records import spec_records
from quenching.specs.parse.tasks import parse_tasks, task_progress
from quenching.specs.schema import capture_form, load_schema
from quenching.specs.worktree import (SPECS_WORKTREE_DIR, SpecsLock, _holder_is_gone,
                                      command_writes, resolve_files_root, specs_worktree_path)


def _case_doc(slug: str = "alpha") -> str:
    # A FIXED date, never `today()`: it is the fact the case asserts travels intact through
    # each store, and one computed at call time would compare equal to itself no matter what
    # either backend did with it.
    return (capture_form().replace("<SLUG>", slug).replace("<TITLE>", "Alpha")
            .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))


# --------------------------------------------------------------------------- #
# gh_refusal — the classifier, asserted against gh's real output
# --------------------------------------------------------------------------- #
# (label, gh exit, stdout, stderr, expected code) — the literal streams `gh` 2.97 produces,
# captured by running it. Every one is exit 2: a refusal, never a finding.
GH_REFUSAL_CASES = (
    ("no binary on PATH", GH_MISSING, "", "", "sp-gh-missing"),
    ("no host authenticated", GH_NOT_AUTHENTICATED, "",
     "To get started with GitHub CLI, please run:  gh auth login\n",
     "sp-gh-unauthenticated"),
    ("a revoked token", 1, '{"message":"Bad credentials","status":"401"}',
     "gh: Bad credentials (HTTP 401)\n", "sp-gh-unauthenticated"),
    ("a repository that is not there", 1, '{"message":"Not Found","status":"404"}',
     "gh: Not Found (HTTP 404)\n", "sp-gh-api-error"),
    ("rate limited", 1,
     '{"message":"API rate limit exceeded for user ID 1.","status":"403"}',
     "gh: API rate limit exceeded (HTTP 403)\n", "sp-gh-api-error"),
)


class GhRefusal(unittest.TestCase):
    """`gh_refusal`, asserted against gh's real output, and the two marker round trips it
    guards on the way past.

    THE ONE THING THIS BACKEND PROMISES BEFORE IT PROMISES ANYTHING ELSE is that no failure
    reaches a human as a traceback and that each one arrives with the remedy that fixes it.
    That promise is decided by string matching on another program's stderr, so the cases hold
    the literal streams rather than a paraphrase of them — a `gh` release that reworded one
    line would break it silently otherwise.

    Self-contained: no network, no `gh`, no repository."""

    DOC = "---\ntitle: Alpha\n---\n\n## Problem\n\nUm problema.\n"

    def test_every_case_classifies_as_an_exit_2_refusal_with_a_message(self):
        for label, code, out, err, want in GH_REFUSAL_CASES:
            with self.subTest(case=label):
                got = gh_refusal("reading a spec", code, out, err)
                self.assertEqual(got.get("code"), want)
                self.assertEqual(got.get("exit"), 2)
                self.assertTrue(str(got.get("message") or "").strip())

    def test_missing_binary_and_unauthenticated_name_gh_auth_login(self):
        # A missing binary or a missing login that did not name the remedy would leave the
        # reader installing the CLI and stopping there.
        for code in (GH_MISSING, GH_NOT_AUTHENTICATED):
            with self.subTest(code=code):
                msg = gh_refusal("reading a spec", code, "", "")["message"]
                self.assertIn("gh auth login", msg)

    def test_comment_marker_round_trip_survives_gh_and_its_crlf(self):
        for label, body in (("as written", hybrid_wrap("alpha.md", self.DOC)),
                            ("as GitHub returns it",
                             hybrid_wrap("alpha.md", self.DOC).replace("\n", "\r\n"))):
            with self.subTest(case=label):
                self.assertEqual(hybrid_unwrap(body), ("alpha.md", self.DOC, 1))

    def test_a_marker_with_no_parts_reads_as_a_single_part_document(self):
        # A marker written WITHOUT `parts=` is the form every spec but a spilled one is stored
        # in, and the form every issue already in a repository carries.
        self.assertEqual(hybrid_unwrap("<!-- quenching-spec: x.md -->\n" + self.DOC)[2], 1)

    def test_an_issue_with_no_marker_is_not_read_as_a_spec(self):
        self.assertEqual(hybrid_unwrap("An ordinary bug report.\n"), ("", "", 0))

    def test_div_marker_round_trip_survives_az_and_its_own_normalisation(self):
        # `azure-boards`'s own marker (task 6.1): a comment does not survive
        # `System.Description`, a `display:none` div does. Round-tripped as written, and as
        # the org's own `az` gives it back — the `style` attribute gets a trailing `;` and the
        # marker text a trailing space, measured on the real board.
        for label, body in (
            ("as written", hybrid_wrap("alpha.md", self.DOC, fmt="div")),
            ("as az returns it",
             '<div style="display:none;">quenching-spec: alpha.md </div>\n' + self.DOC),
        ):
            with self.subTest(case=label):
                self.assertEqual(hybrid_unwrap(body), ("alpha.md", self.DOC, 1))


# --------------------------------------------------------------------------- #
# GitHubBackend._native_fields
# --------------------------------------------------------------------------- #
GH_NATIVE_FIELD_CASES = (
    ({}, {}, "no labels and no assignees reassembles nothing"),
    ({"labels": [{"name": "bug"}, {"name": "Vertical: Risco"}]},
     {"tags": ["bug", "Vertical: Risco"]}, "every label becomes a tag, in order"),
    ({"assignees": [{"login": "holetz"}, {"login": "second"}]},
     {"assignee": "holetz"},
     "only the FIRST assignee is reflected — the canonical field is singular"),
    ({"labels": [{"name": "bug"}], "assignees": [{"login": "holetz"}]},
     {"tags": ["bug"], "assignee": "holetz"}, "both together"),
)


class GithubNativeFields(unittest.TestCase):
    """`GitHubBackend._native_fields`, over fake issue payloads shaped exactly like the REST
    API's own (`labels: [{name}, …]`, `assignees: [{login}, …]`) — no network, no repository."""

    def test_reassembles_tags_and_assignee_from_labels_and_assignees(self):
        gh = GitHubBackend("owner/repo", ".")
        for issue, want, label in GH_NATIVE_FIELD_CASES:
            with self.subTest(case=label):
                self.assertEqual(gh._native_fields(issue), want)


# --------------------------------------------------------------------------- #
# create_spec's `type` projection
# --------------------------------------------------------------------------- #
class GithubCreateType(unittest.TestCase):
    """`create_spec`'s `type` projection — `_set_type` (`gh issue edit`), never a field on
    the create payload: MEASURED live that the REST create silently drops an invalid `type`
    instead of refusing, which is why `_set_type` is its own porcelain call rather than a JSON
    key. Three branches: a resolved name reaches `_set_type`, no key declared calls it not at
    all, and a key with no `github` translation calls it not at all either but says why on
    stderr — never a refusal, since an entry may exist for one backend only."""

    def setUp(self):
        self.gh = GitHubBackend("owner/repo", ".", types={"incidente": "Bug"})
        self.gh._api = lambda action, *argv, stdin=None: {"number": 1, "html_url": "x"}
        self.applied: list[tuple[int, str]] = []
        self.gh._set_type = lambda number, name: self.applied.append((number, name))

    def test_a_resolved_work_item_type_reaches_set_type(self):
        doc = _case_doc()
        close = doc.index("\n---\n")
        typed = doc[:close] + "\nworkItemType: incidente" + doc[close:]
        self.gh.create_spec("plans", "alpha.md", typed)
        self.assertEqual(self.applied, [(1, "Bug")])

    def test_no_declared_work_item_type_calls_set_type_not_at_all(self):
        self.gh.create_spec("plans", "beta.md", _case_doc())
        self.assertEqual(self.applied, [])

    def test_a_type_with_no_github_translation_advises_on_stderr_and_calls_nothing(self):
        doc = _case_doc()
        close = doc.index("\n---\n")
        untranslated = doc[:close] + "\nworkItemType: tarefa" + doc[close:]
        stderr = io.StringIO()
        with contextlib.redirect_stderr(stderr):
            self.gh.create_spec("plans", "gamma.md", untranslated)
        self.assertEqual(self.applied, [])
        self.assertIn("tarefa", stderr.getvalue())

    def test_set_type_on_an_impossible_cwd_raises_a_backend_refusal_that_exits_2(self):
        # Unmocked: a `cwd` that cannot exist makes `_gh_run` fail exactly as a real `gh`
        # refusal would, self-contained and with no network — proving the raise reaches the
        # caller as `BackendRefusal`, classified by the same `gh_refusal` every other
        # transport failure already is.
        broken = GitHubBackend("owner/repo", "/does/not/exist")
        with self.assertRaises(BackendRefusal) as ctx:
            broken._set_type(1, "Bug")
        self.assertEqual(ctx.exception.err.get("exit"), 2)


# --------------------------------------------------------------------------- #
# the GitHub issue body ceiling
# --------------------------------------------------------------------------- #
class GhBodyCeiling(unittest.TestCase):
    """A body over the ceiling refuses BEFORE any call is made — proved with a transport that
    records every call it is asked to make and fails the check if it was asked at all.

    No network and no `gh`: the point is not that GitHub says no, it is that this backend
    never gives it the chance."""

    def setUp(self):
        self.backend = GitHubBackend("owner/repo", os.getcwd())
        self.calls: list[str] = []
        self.backend._api = lambda action, *argv, stdin=None: self.calls.append(action)

    def test_an_oversized_body_refuses_and_makes_no_call(self):
        with self.assertRaises(BackendRefusal) as ctx:
            self.backend._write_api("creating an issue", "POST", "repos/owner/repo/issues",
                                    {"title": "x", "body": "a" * (GH_BODY_MAX + 1)})
        self.assertEqual(ctx.exception.err.get("code"), "sp-gh-body-too-large")
        self.assertEqual(ctx.exception.err.get("exit"), 2)
        self.assertEqual(self.calls, [])

    def test_a_body_exactly_at_the_ceiling_is_accepted_the_ceiling_is_inclusive(self):
        self.backend._write_api("creating an issue", "POST", "repos/owner/repo/issues",
                                {"title": "x", "body": "a" * GH_BODY_MAX})
        self.assertEqual(len(self.calls), 1)


# --------------------------------------------------------------------------- #
# the hybrid serialisation both external backends share
# --------------------------------------------------------------------------- #
# The fields `parse_tasks` derives, minus the ones a rebuild reproduces only because the
# document does: `lineno`/`blockEndLineno`/`metaInsertAt`/`metaIndent`/`subjectLineno`/
# `commitLineno` are POSITIONS. They are covered by the byte-for-byte equality checks
# elsewhere in this class — a document that comes back identical necessarily reparses to the
# same line numbers — so this tuple stays what it is: the semantic comparison that names WHICH
# task drifted when the stricter check has already said the document did.
HYBRID_TASK_SEMANTIC_KEYS = ("id", "state", "checked", "blocked", "reason", "text", "parallel",
                             "files", "pattern", "verify", "subject", "commit")


class HybridSerialization(unittest.TestCase):
    """The one obligation `spec-backend.md` puts on an external backend: it reassembles the
    canonical document on read, BYTE FOR BYTE.

    It used to be a hard claim, because `## Tasks` was stored apart from the rest and the
    document had to be rebuilt from an anchored pile of blocks. With the whole document in one
    body the claim is nearly free — which is most of why the mapping was retired — and what is
    left to prove is the part that is still real:

    - a document under the ceiling is ONE part, stored and returned unchanged;
    - a document over it splits, and the parts JOIN BACK to exactly what went in;
    - both survive the CRLF a tracker really stores bodies with, applied per part, because
      that is how the parts come back — separately, each normalised on its own;
    - `parse_tasks` reads the same tasks out the other end, since that shared derivation is the
      only thing that ever decides a task is checked or blocked.

    The fixture stays grouped under `### N.` headings with a line of prose inside `## Tasks`. It
    was written for the loss that motivated it — the shell used to empty that section, and 47 of
    this repository's 66 specs came back a structure short with no error anywhere — and it stays
    because a split is still free to cut through a group heading.

    Self-contained: no network, no `gh`."""

    DOC = ("---\ntitle: Alpha\nverification: per-task\n---\n\n"
          "## Problem\n\nAlgo.\n\n"
          "## Tasks\n\n"
          "### 1. Primeiro grupo\n\n"
          "Uma linha de prosa dentro de `## Tasks`, que tambem tem de voltar.\n\n"
          "- [ ] 1.1 primeira\n      files: a.py, b.py\n      verify: pytest\n"
          "- [x] 1.2 segunda\n\n"
          "### 2. Segundo grupo\n\n"
          "- [!] 2.1 terceira — blocked: esperando review\n\n"
          "- [ ] [P] quarta sem id\n\n"
          "## Outcome\n\n")

    # THE FIXTURE IS THE SHAPE OF A REAL DOCUMENT, not a minimal one. Three properties, each
    # from a way this repository's own specs really look: an accented title, because the
    # harness language is pt-BR and an accent is where a title projection loses bytes if it
    # ever re-encodes; `### N.` groups with prose inside `## Tasks`, because 49 of 68 specs
    # carry groups and that is precisely the structure the retired sub-issue mapping dropped;
    # and task metadata lines, because they are what a split is most likely to cut through.
    CANONICAL = (
        "---\nslug: alpha\ntitle: Avaliar o fluxo de criação de specs\ndate: 2026-01-01\n"
        "verification: per-section\n---\n\n"
        "# Avaliar o fluxo de criação de specs\n\n"
        "## Problem\n\nO documento não volta como entrou.\n\n"
        "## Tasks\n\n"
        "### 1. Primeiro grupo\n\n"
        "Uma linha de prosa dentro de `## Tasks`, que também tem de voltar.\n\n"
        "- [ ] 1.1 primeira\n      files: a.py, b.py\n      verify: pytest\n"
        "- [x] 1.2 segunda\n\n"
        "### 2. Segundo grupo\n\n"
        "- [!] 2.1 terceira — blocked: esperando revisão\n\n"
        "## Outcome\n\n")

    # The same document over GitHub's 65,536 ceiling. This is the case the title projection
    # makes newly interesting: the frontmatter and the `# <TITLE>` heading it removes both
    # live in the HEAD chunk, which is exactly the chunk a spill cuts. Two of this
    # repository's specs are over the ceiling as whole documents, one of them an active plan.
    BIG = CANONICAL.replace(
        "## Outcome\n\n",
        "### 3. Grupo grande\n\n"
        + "".join(f"- [ ] 3.{i} tarefa com acentuação — número {i}\n"
                  for i in range(1, 2600))
        + "\n## Outcome\n\n")

    def _store(self, chunks: list[tuple[str, bool]]) -> str:
        """What comes back after a store-and-reload, with each part CRLF'd on its own."""
        wrapped = [hybrid_wrap("alpha.md", chunks[0][0], len(chunks))] + [
            hybrid_wrap_part(i, len(chunks), c, eol)
            for i, (c, eol) in enumerate(chunks[1:], start=2)]
        stored = [w.replace("\n", "\r\n") for w in wrapped]
        _, head, parts = hybrid_unwrap(stored[0])
        self.assertEqual(parts, len(chunks),
                         "the marker declared a different part count than the document has "
                         "— a reader would stop early or ask for one too many")
        back = [(head, False)]
        for body in stored[1:]:
            index, chunk, eol = hybrid_unwrap_part(body)
            self.assertTrue(index, "a continuation comment did not read back as one")
            back.append((chunk, eol))
        return hybrid_join(back)

    def test_a_one_part_document_round_trips_byte_for_byte(self):
        # ONE PART — the case every spec in this repository but two takes.
        whole = hybrid_split(self.DOC, GH_PART_MAX)
        self.assertEqual(len(whole), 1)
        self.assertEqual(self._store(whole), self.DOC)

    def test_a_spilled_document_joins_back_byte_for_byte(self):
        # MANY PARTS, forced with a ceiling small enough that this fixture spills. A real
        # spill is a 70 KB document and would make the check unreadable; what a split has to
        # survive is the same either way, and a small ceiling exercises MORE boundaries per
        # character, including cuts that land inside a group and inside a task's own metadata
        # block.
        spilled = hybrid_split(self.DOC, 90)
        self.assertGreaterEqual(len(spilled), 3,
                                "a 90-character ceiling did not exercise the multi-part path")
        for chunk, _ in spilled:
            self.assertLessEqual(len(chunk), 90,
                                 "a chunk came back over the ceiling it was split to")
        self.assertEqual(self._store(spilled), self.DOC)

    def test_a_line_longer_than_one_part_survives_the_split_without_hanging(self):
        # The pathological single line longer than a whole part. It must not hang and it must
        # not lose a byte; nothing in this repository takes this branch, and a split that
        # could not make progress would take it as an infinite loop rather than as an error.
        long_line = "x" * 250 + "\n"
        cut = hybrid_split(long_line, 90)
        self.assertEqual(hybrid_join(cut), long_line)

    def test_a_rebuilt_document_reparses_to_the_same_tasks(self):
        # A part joined back must reparse to the same tasks — the shared derivation is the
        # only thing that reads state, so this is what "identical" means to every caller
        # downstream.
        tasks = parse_tasks(self.DOC)
        tasks2 = parse_tasks(self._store(hybrid_split(self.DOC, 90)))
        self.assertEqual(len(tasks2), len(tasks))
        for before, after in zip(tasks, tasks2):
            with self.subTest(task=before["id"] or before["index"]):
                b = {k: before[k] for k in HYBRID_TASK_SEMANTIC_KEYS}
                a = {k: after[k] for k in HYBRID_TASK_SEMANTIC_KEYS}
                self.assertEqual(a, b)

    def test_an_ordinary_comment_is_not_read_as_a_continuation_part(self):
        # A comment a human left on a spec issue is not a document part. The reverse of the
        # marker rule one level up: a repo's issues belong to its humans, and a backend that
        # read every comment as its own storage would splice a note into the middle of the
        # spec.
        index, _, _ = hybrid_unwrap_part("Concordo, mas a task 2.1 depende da 1.2.\n")
        self.assertFalse(index)

    def test_hybrid_short_title_cuts_on_a_word_boundary_and_marks_the_cut(self):
        # THE TITLE IS CUT, THE DOCUMENT IS NOT. The tracker caps a title; the body is the
        # only half `parse_tasks` ever reads. This repository's own longest task line is 946
        # characters, so the cut is exercised on a length it really carries.
        long_text = "9.9 " + " ".join(f"palavra{i:03d}" for i in range(120))
        short = hybrid_short_title(long_text)
        self.assertLessEqual(len(short), HYBRID_TITLE_MAX)
        self.assertTrue(short.endswith("…"))
        self.assertTrue(long_text.startswith(short[:-1].rstrip()),
                        "a cut title is not a prefix of the line it came from")

    def test_hybrid_short_title_leaves_a_title_that_already_fits_untouched(self):
        self.assertEqual(hybrid_short_title("9.9 curta"), "9.9 curta")

    def test_the_big_fixture_actually_crosses_the_github_body_ceiling(self):
        self.assertGreater(len(self.BIG), GH_BODY_MAX,
                           "the over-ceiling fixture does not reach the ceiling it exists "
                           "to cross")

    def test_title_projection_removes_the_duplicated_title_and_is_reversible(self):
        # THE TITLE PROJECTION, on the shape `new` actually stamps. What the store holds must
        # carry neither `title:` nor the `# <TITLE>` heading, and putting the native title
        # back must return the document byte for byte — the same obligation the body is held
        # to, on the one field that is no longer inside it.
        proj = hybrid_title_split(self.CANONICAL)
        self.assertIsNotNone(
            proj, "the capture form's own shape was refused by the title projection — every "
                  "spec `new` creates would be stored with a duplicated title")
        stored, native = proj
        self.assertNotIn("title:", stored)
        self.assertNotIn(f"# {native}", stored)
        self.assertEqual(native, str(parse_frontmatter(self.CANONICAL).get("title", "")).strip())
        self.assertEqual(hybrid_title_join(stored, native), self.CANONICAL)

    def test_title_projection_refuses_a_document_outside_the_capture_shape(self):
        # A document the projection REFUSES is stored whole, and a read must not then graft a
        # second title onto it. `DOC` is exactly that shape: no `slug:`, no heading.
        self.assertIsNone(hybrid_title_split(self.DOC))
        self.assertEqual(hybrid_title_join(self.DOC, "whatever the tracker says"), self.DOC)

    def test_round_trip_is_identical_across_github_and_azure_boards_ceilings(self):
        # THE SAME ROUND TRIP, AGAINST BOTH EXTERNAL BACKENDS — each with the ceiling it
        # really passes to `hybrid_split`: `github` splits at GH_PART_MAX, `azure-boards`
        # hands None and gets one chunk. Two stores that serialise a title differently is the
        # drift `spec-backend.md` forbids, and it is cheap to refute here: the projection, the
        # wrap, the split and the reassembly are the whole write path, and none of it needs a
        # network.
        for backend_name, ceiling in (("github", GH_PART_MAX), ("azure-boards", None)):
            for label, source in (("one part", self.CANONICAL), ("over the ceiling", self.BIG)):
                with self.subTest(backend=backend_name, doc=label):
                    stored, native = hybrid_project("alpha", source)
                    self.assertEqual(native,
                                     str(parse_frontmatter(source).get("title", "")).strip())
                    self.assertNotIn("title:", stored.split("\n---\n", 1)[0])
                    rebuilt = hybrid_title_join(self._store(hybrid_split(stored, ceiling)),
                                               native)
                    self.assertEqual(rebuilt, source)

    def test_a_quoted_title_is_refused_by_the_projection(self):
        # A QUOTED title is refused, and this one was found by the corpus rather than by
        # reasoning. `title: "…"` parses to the same string with the quotes gone, so a rebuild
        # from the value writes an unquoted line and the document comes back two characters
        # short — 4 of this repository's 73 specs quote their title, and all four failed the
        # byte-for-byte round trip before the raw line was checked instead of the parsed value.
        quoted = self.CANONICAL.replace(
            "title: Avaliar o fluxo de criação de specs\n",
            'title: "Avaliar o fluxo de criação de specs"\n', 1)
        self.assertIsNone(hybrid_title_split(quoted))

    def test_a_title_over_the_trackers_ceiling_is_refused(self):
        # A title the tracker would cut is refused, because a cut title is now a renamed spec.
        long_title = ("---\nslug: alpha\ntitle: " + "t" * (HYBRID_TITLE_MAX + 1) +
                     "\ndate: 2026-01-01\n---\n\n# " + "t" * (HYBRID_TITLE_MAX + 1) +
                     "\n\n## Problem\n\nAlgo.\n")
        self.assertIsNone(hybrid_title_split(long_title))

    def test_the_marker_fold_moves_the_capture_date_out_of_the_basename(self):
        # The marker fold is the only thing that moves a capture date out of a basename.
        folded = legacy_marker_fold("2026-07-25-alpha.md", self.CANONICAL)
        self.assertIsNotNone(folded)
        self.assertEqual(folded[0], "alpha.md")
        # The basename's copy is never allowed to win over a `date:` the document already
        # declares.
        self.assertEqual(str(parse_frontmatter(folded[1]).get("date", "")), "2026-01-01")

    def test_the_marker_fold_carries_the_basenames_date_when_the_document_has_none(self):
        # The prefix is the only copy of the capture date, so dropping it without moving it
        # would lose it outright.
        undated = self.CANONICAL.replace("date: 2026-01-01\n", "", 1)
        folded = legacy_marker_fold("2026-07-25-alpha.md", undated)
        self.assertIsNotNone(folded)
        self.assertEqual(str(parse_frontmatter(folded[1]).get("date", "")), "2026-07-25")

    def test_the_marker_fold_does_not_fire_on_an_already_folded_basename(self):
        undated = self.CANONICAL.replace("date: 2026-01-01\n", "", 1)
        self.assertIsNone(legacy_marker_fold("alpha.md", undated))


# --------------------------------------------------------------------------- #
# backend_equivalence — files and memory over the SAME canonical case list
# --------------------------------------------------------------------------- #
def _listing(b: SpecBackend) -> list[dict]:
    """A listing minus `path` — the one field the locator is allowed to differ on."""
    return [{k: v for k, v in s.items() if k != "path"} for s in b.list_specs()]


def _observable(info: dict | None) -> dict:
    """One spec's info minus the two fields a backend is SUPPOSED to disagree on.

    `path` is the locator — a filesystem path here, a URL there — and `text` is echoed back
    verbatim from what was written, so neither can distinguish a correct backend from a
    broken one. Everything else must match exactly, including the derived stage."""
    if info is None:
        return {}
    return {k: v for k, v in info.items() if k not in ("path", "text")}


def _case_create(b: SpecBackend) -> list[dict]:
    b.create_spec("plans", "alpha.md", _case_doc())
    return _listing(b)


def _case_date(b: SpecBackend) -> str:
    """The capture date, read back out of whatever the store did with the document.

    It used to ride in the basename, so `_listing` alone proved it survived. Now it is a
    frontmatter field, and the only thing that proves a backend did not drop, rewrite or
    recompute it is asking for it after a round trip."""
    info, _ = b.read_spec("alpha")
    return (info or {}).get("date", "")


def _case_validate(b: SpecBackend) -> list[dict]:
    """Every finding for the one spec in the store — the READER, not just the store.

    The cases above prove a backend can hand back the document it was given. This proves the
    shared code ASKS it for one: a `validate_spec` that reaches around the interface to
    `read_text(s["path"])` gets nothing from a `memory://` locator and reports a well-formed
    document as missing every required key, while `files` reports the real findings."""
    return validate_spec(b, b.list_specs()[0])


def _case_front(b: SpecBackend) -> dict:
    """One ranked candidate — the same trap on the other disk reader.

    `_candidate` off the path ranks a `memory://` spec as an empty one with no tasks and no
    priority, which is exactly what `/quenching:specs:continue` was handed against GitHub. `heads` and
    `current` are pinned empty so the case asserts the READ and never the repository it
    happens to run in.

    IT MUST RUN ON AN AUTHORED DOCUMENT, which is why it is ordered last rather than beside
    the other read case in `BACKEND_CASES`. Measured on the fresh capture form this case
    PASSED with the reader fully broken: every field it compares collapses to the same value
    from an empty document. A fixture that cannot tell the two apart is a case that asserts
    nothing, and the only reason this one is known to discriminate is that reverting the
    reader was tried against it."""
    c = _candidate(b, b.list_specs("plans")[0], load_schema(), set(), None, "")
    return {k: v for k, v in c.items() if k != "path"}


def _case_type(b: SpecBackend) -> str | None:
    """`workItemType:`, inserted into a fresh capture form exactly the way `cmd_new --type`
    inserts it — never `set_frontmatter_key`, which would misrepresent a key FIXED at
    creation as one of the four mutable STATE fields `_case_field` already covers.

    A second spec (`beta`), never `alpha`: the key is resolved once at `new` and never
    rewritten, so there is no round trip to prove beyond create-then-read."""
    doc = _case_doc("beta")
    close = doc.index("\n---\n")
    doc = doc[:close] + "\nworkItemType: incidente" + doc[close:]
    b.create_spec("plans", "beta.md", doc)
    info, _ = b.read_spec("beta")
    return (info or {}).get("frontmatter", {}).get("workItemType")


def _case_write(b: SpecBackend) -> dict:
    info, _ = b.read_spec("alpha")
    block, _ = upsert_section(info, "Problem", "## Problem\n\nUm problema.\n")
    b.write_spec(info, block)
    return _observable(b.read_spec("alpha")[0])


def _case_task(b: SpecBackend) -> dict:
    info, _ = b.read_spec("alpha")
    block, _ = upsert_section(info, "Tasks", "## Tasks\n\n- [x] 1.1 feito\n")
    b.write_spec(info, block)
    info, _ = b.read_spec("alpha")
    return {"progress": task_progress(info["tasks"]), "stage": info["stage"]}


def _case_record(b: SpecBackend) -> dict:
    info, _ = b.read_spec("alpha")
    b.write_spec(info, set_frontmatter_record(
        info["text"], "priority", {"level": "1", "criticality": "high"}))
    info, _ = b.read_spec("alpha")
    return spec_records(info["frontmatter"])


def _case_field(b: SpecBackend) -> dict:
    """The four STATE keys, round-tripped through `write_spec` — the SAME mechanism
    `_case_write` already proves for a section body, applied to `set_frontmatter_key`
    instead. Never a record: `_case_record` is what proves those, separately."""
    info, _ = b.read_spec("alpha")
    text = info["text"]
    for key, value in (("tags", '["a", "b"]'), ("assignee", "someone"),
                       ("start", "2026-01-01"), ("target", "2026-02-01")):
        text = set_frontmatter_key(text, key, value)
    b.write_spec(info, text)
    info, _ = b.read_spec("alpha")
    return {k: info["frontmatter"].get(k) for k in FIELD_KEYS}


def _case_move(b: SpecBackend) -> dict:
    info, _ = b.read_spec("alpha")
    b.move_spec(info, "archive")
    return _observable(b.read_spec("alpha")[0])


def _case_labels(b: SpecBackend) -> list[str]:
    """`derive_labels` off the same document through both stores — proves the calculation
    reads only `info`, never anything backend-specific, same as every case above it."""
    info, _ = b.read_spec("alpha")
    return derive_labels(info)


BACKEND_CASES = (
    ("list an empty store", lambda b: _listing(b)),
    ("create, then list", lambda b: _case_create(b)),
    ("read what was created", lambda b: _observable(b.read_spec("alpha")[0])),
    ("read an unknown slug", lambda b: b.read_spec("nope")[1]),
    ("validate what was created", lambda b: _case_validate(b)),
    ("the capture date survives the store", lambda b: _case_date(b)),
    ("write a section, then re-read", lambda b: _case_write(b)),
    ("tick a task", lambda b: _case_task(b)),
    ("stamp a record, then re-read", lambda b: _case_record(b)),
    ("set tags/assignee/start/target, then re-read", lambda b: _case_field(b)),
    ("derive labels off the stamped record", lambda b: _case_labels(b)),
    # AFTER the five cases that author the document, never on the fresh capture form. See
    # `_case_front`: on a capture form the case passes with the reader broken.
    ("rank the front", lambda b: _case_front(b)),
    ("create with workItemType, then re-read", lambda b: _case_type(b)),
    ("move to archive", lambda b: _case_move(b)),
    ("list after the move", lambda b: _listing(b)),
)


class BackendEquivalence(unittest.TestCase):
    """Run the canonical case list against `files` and against `memory`, and name every case
    where they disagree.

    THIS IS THE PROOF OF THE CENTRAL CLAIM. "Every backend behaves identically" is the
    sentence the whole configurable-backend design rests on, and a sentence nobody checks is
    a wish. Two backends sharing nothing but the interface — one on real files in a temp
    directory, one in a dict — must produce byte-identical results for every case but the
    locator.

    THE CASES RUN IN ORDER AND SHARE STATE, on purpose: each backend accumulates the same
    document through the same sequence of writes, so a case failing here can cascade into the
    ones after it exactly as it would in a real backend that started disagreeing partway
    through a build.

    Self-contained: `tempfile` is stdlib and the documents come from the embedded template,
    so this runs on an installed copy with no assets beside it."""

    def test_every_canonical_case_agrees_between_files_and_memory(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = os.path.join(tmp, ".specs")
            os.makedirs(os.path.join(root, "plans"))
            os.makedirs(os.path.join(root, "archive"))
            files: SpecBackend = FilesBackend(root)
            memory: SpecBackend = MemoryBackend()
            for label, case in BACKEND_CASES:
                with self.subTest(case=label):
                    got_f, got_m = case(files), case(memory)
                    self.assertEqual(
                        json.dumps(got_f, sort_keys=True, default=str),
                        json.dumps(got_m, sort_keys=True, default=str))


# --------------------------------------------------------------------------- #
# backend_completeness — every declared backend implements all five primitives
# --------------------------------------------------------------------------- #
SPEC_PRIMITIVES = ("list_specs", "read_spec", "write_spec", "create_spec", "move_spec")


class BackendCompleteness(unittest.TestCase):
    """Every declared backend implements all five primitives — none left inherited.

    THIS IS WHAT `azure-boards` HAS INSTEAD OF END-TO-END PROOF. `## Out of Scope` accepts
    shipping it without a real Azure DevOps project to exercise, and `BackendEquivalence`
    cannot cover it: that check runs the canonical cases against two backends, and running
    them here would mean a network. What CAN be checked without a network is the failure a
    half-written backend actually takes — a primitive left inheriting the base class's
    `NotImplementedError`, which reaches a human as a traceback rather than as a refusal,
    breaking the one promise every external backend makes.

    Self-contained: reads the classes, calls nothing."""

    def test_no_backend_inherits_a_primitive_from_the_abstract_base(self):
        for cls in (FilesBackend, MemoryBackend, GitHubBackend, AzureBoardsBackend):
            for primitive in SPEC_PRIMITIVES:
                with self.subTest(backend=cls.__name__, primitive=primitive):
                    self.assertIsNot(getattr(cls, primitive, None),
                                     getattr(SpecBackend, primitive),
                                     f"{cls.__name__} inherits `{primitive}` — it would raise "
                                     f"NotImplementedError as a traceback")

    def test_every_backend_names_itself(self):
        for cls in (FilesBackend, MemoryBackend, GitHubBackend, AzureBoardsBackend):
            with self.subTest(backend=cls.__name__):
                self.assertNotEqual(getattr(cls, "name", "abstract"), "abstract",
                                    f"{cls.__name__} never named itself — `name` is what a "
                                    f"refusal and every report call it")


# --------------------------------------------------------------------------- #
# the unproved-backend warning
# --------------------------------------------------------------------------- #
class UnprovedBackend(unittest.TestCase):
    """The unproved-backend warning says its piece once, on stderr, and only for a backend
    that is actually declared unproved.

    Three ways this decision could ship broken, and all three are silent. A name misspelled
    in `UNPROVED_BACKENDS` matches no backend, so the warning never fires and the caveat is
    dead code that reads as coverage. A warning that repeats is the per-operation noise the
    decision rejected, arriving anyway. A warning on stdout breaks the `--json` parse of
    every caller, which is a worse failure than the one it was warning about.

    Self-contained: no network, no `az`, and the process-level flag is restored so the check
    cannot change what a later command prints."""

    def setUp(self):
        self._held = set(_UNPROVED_ANNOUNCED)
        _UNPROVED_ANNOUNCED.clear()
        self.addCleanup(self._restore)

    def _restore(self):
        _UNPROVED_ANNOUNCED.clear()
        _UNPROVED_ANNOUNCED.update(self._held)

    def test_every_declared_unproved_backend_is_a_real_backend(self):
        for name in UNPROVED_BACKENDS:
            with self.subTest(backend=name):
                self.assertIn(name, BACKENDS,
                              "a name declared unproved and not a backend can never warn")

    def test_the_warning_fires_only_for_an_unproved_backend_once_and_on_stderr(self):
        for name, want in [(b, b in UNPROVED_BACKENDS) for b in BACKENDS]:
            with self.subTest(backend=name):
                err, out = io.StringIO(), io.StringIO()
                with contextlib.redirect_stderr(err), contextlib.redirect_stdout(out):
                    announce_unproved(name)
                    announce_unproved(name)
                said = err.getvalue().strip()
                self.assertEqual(bool(said), want)
                self.assertLessEqual(said.count("warning:"), 1,
                                     "warned twice in one process — the decision is one line "
                                     "per process, not one per operation")
                self.assertEqual(out.getvalue(), "",
                                 "wrote to stdout, which is the `--json` payload")


# --------------------------------------------------------------------------- #
# resolve_files_root — the shapes that must answer without reaching for git
# --------------------------------------------------------------------------- #
class FilesRoot(unittest.TestCase):
    """The shapes `resolve_files_root` must answer without reaching for git.

    Every one of them is a case where creating a worktree would be WRONG, and the cost of
    getting it wrong is not a bad answer but a branch and a checkout appearing in someone's
    repository. Self-contained — a temp directory and pure path arithmetic, so this runs on an
    installed copy with no repository staged."""

    CFG = {"specsBranch": DEFAULT_SPECS_BRANCH}

    def test_a_populated_workspace_resolves_to_itself(self):
        # A `/.specs/` holding phase folders in the code tree is the PRE-MIGRATION store and
        # stays authoritative until a human moves it.
        with tempfile.TemporaryDirectory() as tmp:
            populated = os.path.join(tmp, ".specs")
            os.makedirs(os.path.join(populated, "plans"))
            got, err = resolve_files_root(populated, self.CFG)
        self.assertEqual(got, populated)
        self.assertEqual(err, {})

    def test_a_workspace_already_inside_the_worktree_dir_resolves_to_itself(self):
        # Nothing nests a worktree in a worktree; the specs branch is already the tree
        # underfoot.
        with tempfile.TemporaryDirectory() as tmp:
            nested = os.path.join(tmp, SPECS_WORKTREE_DIR, "specs", ".specs")
            os.makedirs(nested)
            got, err = resolve_files_root(nested, self.CFG)
        self.assertEqual(got, nested)
        self.assertEqual(err, {})

    def test_a_namespaced_branch_does_not_deepen_the_worktree_path(self):
        want = os.path.join("/repo", SPECS_WORKTREE_DIR, "quenching-specs")
        self.assertEqual(specs_worktree_path("/repo", "quenching/specs"), want)


class RootTooHigh(unittest.TestCase):
    """`is_root_too_high` — the structural test behind `sp-root-too-high`. Pure path
    arithmetic, so it runs on an installed copy with no repository staged."""

    def test_a_container_with_a_phased_specs_child_is_too_high(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, ".specs", "plans"))
            self.assertTrue(is_root_too_high(tmp))

    def test_a_root_that_is_already_the_workspace_is_not_too_high(self):
        # Even with a foreign `.specs/` nested deeper somewhere inside it — `root` already
        # qualifying as the workspace short-circuits before that nested directory is looked at.
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "plans"))
            os.makedirs(os.path.join(tmp, "somewhere", ".specs", "plans"))
            self.assertFalse(is_root_too_high(tmp))

    def test_a_fresh_empty_directory_is_not_too_high(self):
        with tempfile.TemporaryDirectory() as tmp:
            self.assertFalse(is_root_too_high(tmp))

    def test_an_unrelated_path_with_no_specs_at_all_is_not_too_high(self):
        with tempfile.TemporaryDirectory() as tmp:
            os.makedirs(os.path.join(tmp, "src"))
            self.assertFalse(is_root_too_high(tmp))


# --------------------------------------------------------------------------- #
# the specs worktree lock
# --------------------------------------------------------------------------- #
class Lock(unittest.TestCase):
    """The lock's invariants, checked rather than asserted in prose.

    The direction that is asserted here is the DANGEROUS one: a lock that is taken while
    someone holds it, or a holder judged gone on evidence that does not prove it, silently
    loses a human's edit. Both are decidable with no repository and no second process.

    The opposite direction — a genuinely dead holder being reclaimed — needs a pid that is
    provably dead, and the only cheap way to get one is a process that just exited, whose pid
    the operating system may reuse. A selftest that fails once a month teaches people to
    ignore it, so that direction is exercised in a disposable repository and NOT here."""

    def test_a_free_lock_is_acquired_and_leaves_a_lock_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "specs.lock")
            lock = SpecsLock(path, label="task alpha")
            self.assertEqual(lock.acquire(wait=0.0), {})
            self.assertTrue(os.path.isfile(path),
                            "acquiring left no lock file, so nothing marks the worktree as held")
            lock.release()

    def test_a_held_lock_refuses_a_second_acquisition_and_names_the_real_holder(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "specs.lock")
            first = SpecsLock(path, label="task alpha")
            self.assertEqual(first.acquire(wait=0.0), {})
            second = SpecsLock(path, label="promote alpha")
            err = second.acquire(wait=0.0)
            self.assertEqual(err.get("code"), "sp-specs-locked",
                             "two writers in one worktree is the whole failure this prevents")
            self.assertEqual(err.get("exit"), 2)
            self.assertEqual(str(err.get("holder", {}).get("pid")), str(os.getpid()))
            first.release()

    def test_releasing_frees_the_lock_file_for_the_next_writer(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "specs.lock")
            first = SpecsLock(path, label="task alpha")
            first.acquire(wait=0.0)
            first.release()
            self.assertFalse(os.path.exists(path),
                             "releasing left the lock file behind, which wedges the next writer")
            second = SpecsLock(path, label="promote alpha")
            self.assertEqual(second.acquire(wait=0.0), {})
            second.release()

    def test_this_very_process_is_never_judged_gone(self):
        live = {"pid": os.getpid(), "host": socket.gethostname()}
        self.assertFalse(_holder_is_gone(live), "the liveness proof is inverted")

    def test_a_holder_on_another_host_is_never_reclaimed(self):
        # A pid does not travel — another host is unknowable, never reclaimed.
        self.assertFalse(_holder_is_gone({"pid": 1, "host": "a-host-that-is-not-this-one"}))

    def test_a_holder_with_no_usable_pid_is_never_reclaimed(self):
        # Absence of evidence is not proof of death.
        self.assertFalse(_holder_is_gone({"host": socket.gethostname()}))
        self.assertFalse(_holder_is_gone({"pid": 0, "host": socket.gethostname()}))

    def test_command_writes_classifies_every_flag_gated_subcommand_by_the_invocation(self):
        # The four FLAG-GATED subcommands are asserted as pairs — the same subcommand reads
        # or writes depending on the invocation, which is the whole reason `command_writes`
        # takes `args` rather than a name.
        cases = (
            ("section", argparse.Namespace(cmd="section", write=True, spec="x"),
             argparse.Namespace(cmd="section", write=False, spec="x")),
            ("record", argparse.Namespace(cmd="record", set=["complexity=high"], spec="x"),
             argparse.Namespace(cmd="record", set=None, spec="x")),
            ("verification", argparse.Namespace(cmd="verification", policy="per-task", spec="x"),
             argparse.Namespace(cmd="verification", policy=None, spec="x")),
            ("promote", argparse.Namespace(cmd="promote", dry_run=False, spec="x"),
             argparse.Namespace(cmd="promote", dry_run=True, spec="x")),
        )
        for label, writes, reads in cases:
            with self.subTest(cmd=label):
                self.assertTrue(command_writes(writes),
                                f"`{label}` classified as a reader while writing — it would "
                                f"take no lock and overwrite whoever holds one")
                self.assertFalse(command_writes(reads),
                                 f"`{label}` classified as a writer while only reading — the "
                                 f"lock follows the invocation, not the subcommand")

    def test_command_writes_is_true_for_every_unconditional_writer(self):
        for cmd in ("new", "task", "discover"):
            with self.subTest(cmd=cmd):
                self.assertTrue(command_writes(argparse.Namespace(cmd=cmd, spec="x")),
                                f"`{cmd}` takes no writer lock, but it modifies a spec")

    def test_command_writes_is_false_for_every_reader(self):
        for cmd in ("list", "status", "show", "next", "parallel", "validate", "config",
                   "doctor", "selftest"):
            with self.subTest(cmd=cmd):
                self.assertFalse(command_writes(argparse.Namespace(cmd=cmd)),
                                 f"`{cmd}` takes the writer lock, but it only reads")


# --------------------------------------------------------------------------- #
# the `pr:` rules on a `merge:` record
# --------------------------------------------------------------------------- #
class MergePr(unittest.TestCase):
    """The two `pr:` rules `merge_record_finding` must get right: a local conclusion with no
    `pr:` stays valid (most conclusions have no remote), and `pr:` under a strategy `gh pr
    merge` cannot perform is flagged rather than silently accepted."""

    def test_a_local_conclusion_with_no_pr_is_not_flagged(self):
        local = {"strategy": "merge-commit", "subject": "plan/a: merge (merge-commit)"}
        self.assertIsNone(merge_record_finding({"merge": local}, "plans/a.md", "a"))

    def test_pr_set_under_a_strategy_with_no_gh_pr_merge_equivalent_is_flagged(self):
        ff_with_pr = {"strategy": "fast-forward", "subject": "none — fast-forward",
                     "pr": "https://github.com/o/r/pull/1"}
        finding = merge_record_finding({"merge": ff_with_pr}, "plans/a.md", "a")
        self.assertIsNotNone(finding)
        self.assertEqual(finding.get("code"), "sp-bad-merge")


if __name__ == "__main__":
    unittest.main()
