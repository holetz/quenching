"""Epics, offline: a spec whose `## Tasks` items are member specs.

The derivation is pure, so the same scenarios run against the memory fake and against the git
store fixture (a bare remote and clones) — and must observe the same thing. Nothing here reaches
a network or the repository under test."""
import argparse
import contextlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from test_specs_git_backend import GitStoreFixture
from quenching.specs.backends.git import GitBackend
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import epic as epic_cmd
from quenching.specs.commands import next as next_cmd
from quenching.specs.commands import promote as promote_cmd
from quenching.specs.commands import read as read_cmd
from quenching.specs.commands import task as task_cmd
from quenching.specs.commands import validate as validate_cmd
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.epics import derive_epic, find_cycle, parse_items
from quenching.specs.parse.fields import set_frontmatter_key

EPIC_ID = 1


def doc(title, fm="", body="## Problem\n\nSomething to solve.\n"):
    return f"---\ntitle: {title}\ndate: 2026-10-07\n{fm}---\n\n{body}"


def epic_doc(body="## Problem\n\nThe program.\n\n## Tasks\n\n"):
    return doc("The program", "workItemType: epic\n", body)


def run(fn, backend, **kw):
    """One command, its `--json` payload and exit code, through `backend`."""
    args = argparse.Namespace(json=True, **kw)
    buf = io.StringIO()
    with contextlib.ExitStack() as stack:
        for mod in (epic_cmd, next_cmd, promote_cmd, read_cmd, task_cmd, validate_cmd):
            stack.enter_context(mock.patch.object(mod, "open_backend",
                                                  return_value=(backend, {})))
        stack.enter_context(contextlib.redirect_stdout(buf))
        code = fn(args, tempfile.gettempdir(), Emitter())
    text = buf.getvalue().strip()
    return code, (json.loads(text) if text else {})


def add(backend, member, **kw):
    kw.setdefault("after", None)
    kw.setdefault("group", None)
    kw.setdefault("label", None)
    return run(epic_cmd.cmd_epic, backend, epic_cmd="add", epic=EPIC_ID, spec=member, **kw)


def archive(backend, spec_id, outcome="done"):
    info, _ = backend.read_spec(spec_id)
    backend.write_spec(info, set_frontmatter_key(info["text"], "outcome", outcome))
    info, _ = backend.read_spec(spec_id)
    backend.move_spec(info, "archive")


def ready_labels(backend):
    code, got = run(next_cmd.cmd_next, backend, epic=EPIC_ID, spec=None, front=False, limit=None)
    assert code == 0, got
    return [r["label"] for r in got["ready"]]


class Scenarios:
    """Mixed into a backend-specific TestCase: `self.backend` is the store under test."""

    def diamond(self):
        """Epic 1; members 2..5 as S1..S4 — S1, then S2 and S3 in parallel, then S4."""
        b = self.backend
        b.create_spec("plans", epic_doc())
        for n in range(1, 6):
            b.create_spec("plans", doc(f"Member {n}", "approved: 2026-10-07\n"))
        self.assertEqual(0, add(b, 2, group="Wave 1")[0])
        self.assertEqual(0, add(b, 3, after="S1", group="Wave 2")[0])
        self.assertEqual(0, add(b, 4, after="S1", group="Wave 2")[0])
        self.assertEqual(0, add(b, 5, after="S2,S3", group="Wave 3")[0])
        return b

    def test_add_writes_the_items_in_their_groups_and_the_epic_key_on_the_member(self):
        b = self.diamond()
        epic, _ = b.read_spec(EPIC_ID)
        self.assertIn("### 1. Wave 1\n- [ ] S1 Member 1 — spec: #2\n", epic["text"])
        self.assertIn("- [ ] S4 Member 4 — spec: #5 — after: S2,S3", epic["text"])
        self.assertEqual([("S1", 1, []), ("S2", 2, ["S1"]), ("S3", 2, ["S1"]),
                          ("S4", 3, ["S2", "S3"])],
                         [(i["label"], i["group"], i["after"]) for i in parse_items(epic)])
        member, _ = b.read_spec(5)
        self.assertEqual("1", str(member["frontmatter"]["epic"]))

    def test_a_second_item_joins_an_existing_group(self):
        b = self.diamond()
        self.assertEqual(0, add(b, 6, group="wave 2")[0])
        epic, _ = b.read_spec(EPIC_ID)
        self.assertEqual([2, 2, 2], [i["group"] for i in parse_items(epic) if i["group"] == 2])
        self.assertEqual("S5", parse_items(epic)[3]["label"])
        self.assertEqual(3, len([h for h in epic["text"].splitlines() if h.startswith("### ")]))

    def test_the_diamond_only_ever_offers_what_is_ready(self):
        b = self.diamond()
        self.assertEqual(["S1"], ready_labels(b))
        archive(b, 2)
        self.assertEqual(["S2", "S3"], ready_labels(b))
        archive(b, 3)
        self.assertEqual(["S3"], ready_labels(b))      # S4 still waits on S3
        archive(b, 4)
        self.assertEqual(["S4"], ready_labels(b))
        archive(b, 5)
        self.assertEqual([], ready_labels(b))

    def test_item_state_is_derived_and_the_epic_is_never_written(self):
        b = self.diamond()
        before = b.read_spec(EPIC_ID)[0]["text"]
        archive(b, 2)
        archive(b, 3)
        self.assertEqual(before, b.read_spec(EPIC_ID)[0]["text"])
        _, got = run(read_cmd.cmd_status, b, epic=EPIC_ID, spec=None)
        self.assertEqual({"done": 2, "total": 4, "blocked": 0, "ready": 1}, got["progress"])
        self.assertEqual([("1. Wave 1", 1, 1), ("2. Wave 2", 1, 2), ("3. Wave 3", 0, 1)],
                         [(g["title"], g["done"], g["total"]) for g in got["groups"]])
        self.assertEqual(["S3", "S4"], got["criticalPath"])

    def test_the_critical_path_is_the_longest_chain_left(self):
        b = self.diamond()
        _, got = run(read_cmd.cmd_status, b, epic=EPIC_ID, spec=None)
        path = got["criticalPath"]
        self.assertEqual((3, "S1", "S4"), (len(path), path[0], path[-1]))

    def test_a_blocked_member_blocks_its_item_and_holds_back_its_dependents(self):
        b = self.diamond()
        archive(b, 2)
        info, _ = b.read_spec(3)
        b.write_spec(info, info["text"] + "\n## Tasks\n\n- [!] 1 Wait — blocked: no access\n")
        self.assertEqual(["S3"], ready_labels(b))
        _, got = run(read_cmd.cmd_status, b, epic=EPIC_ID, spec=None)
        self.assertEqual(["S2"], [x["label"] for x in got["blocked"]])
        self.assertEqual(["no access"], got["blocked"][0]["reasons"])
        self.assertEqual("waiting", {i["label"]: i["status"] for i in got["items"]}["S4"])

    def test_an_abandoned_member_never_unblocks_its_dependents(self):
        b = self.diamond()
        archive(b, 2, outcome="abandoned")
        self.assertEqual([], ready_labels(b))
        _, got = run(read_cmd.cmd_status, b, epic=EPIC_ID, spec=None)
        self.assertEqual(["dropped"], [x["status"] for x in got["blocked"]])

    def archive_with_pr(self, spec_id, state):
        b = self.backend
        info, _ = b.read_spec(spec_id)
        text = set_frontmatter_key(info["text"], "pr", "{number: 77, url: u, date: 2026-10-07}")
        b.write_spec(info, text)
        archive(b, spec_id)
        return {str(spec_id): state} if state else {}

    def status_with(self, states):
        spy = mock.Mock(return_value=states)
        with mock.patch.object(epic_cmd, "pr_states", spy):
            got = run(read_cmd.cmd_status, self.backend, epic=EPIC_ID, spec=None)[1]
        self.assert_asked_from_the_root(spy)
        return got

    def assert_asked_from_the_root(self, spy):
        """The PR lookup must carry `--root`, or it reads the cwd's repository instead."""
        spy.assert_called()
        for call in spy.call_args_list:
            self.assertEqual(tempfile.gettempdir(), call.args[1] if len(call.args) > 1
                             else call.kwargs.get("root"))

    def test_an_archived_member_whose_pr_is_open_is_unmerged_and_holds_its_dependents(self):
        self.diamond()
        states = self.archive_with_pr(2, "OPEN")
        got = self.status_with(states)
        by = {i["label"]: i["status"] for i in got["items"]}
        self.assertEqual(("unmerged", "waiting"), (by["S1"], by["S2"]))
        self.assertEqual(0, got["progress"]["done"])
        self.assertEqual(["PR #77 is OPEN"], got["blocked"][0]["reasons"])
        self.assertEqual("S1", got["criticalPath"][0])

    def test_a_merged_pr_or_no_pr_keeps_the_member_done(self):
        b = self.diamond()
        merged = self.archive_with_pr(2, "MERGED")      # S1: merged
        archive(b, 3)                                   # S2: no `pr:` record at all
        got = self.status_with(merged)
        self.assertEqual(["done", "done"], [i["status"] for i in got["items"][:2]])

    def test_an_unreadable_pr_is_unverified_and_holds_its_dependents(self):
        self.diamond()
        states = self.archive_with_pr(2, None)          # `pr:` present, the lookup failed
        got = self.status_with(states)
        by = {i["label"]: i["status"] for i in got["items"]}
        self.assertEqual(("unverified", "waiting"), (by["S1"], by["S2"]))
        self.assertEqual(0, got["progress"]["done"])
        self.assertEqual(["PR #77 state could not be read"], got["blocked"][0]["reasons"])

    def test_a_member_that_is_not_ready_is_not_offered(self):
        b = self.backend
        b.create_spec("plans", epic_doc())
        b.create_spec("plans", doc("Captured only"))        # no `approved:`, no ready sections
        add(b, 2)
        self.assertEqual([], ready_labels(b))

    def test_next_orders_by_priority_and_honours_limit(self):
        b = self.backend
        b.create_spec("plans", epic_doc())
        for n, level in ((1, 3), (2, 1), (3, 2)):
            b.create_spec("plans", doc(f"M{n}", "approved: yes\n"
                                       f"priority: {{level: {level}, criticality: high}}\n"))
            add(b, n + 1)
        self.assertEqual(["S2", "S3", "S1"], ready_labels(b))
        _, got = run(next_cmd.cmd_next, b, epic=EPIC_ID, spec=None, front=False, limit=2)
        self.assertEqual(["S2", "S3"], [r["label"] for r in got["ready"]])
        self.assertEqual(3, got["readyTotal"])

    def test_add_refuses_a_bad_target(self):
        b = self.diamond()
        b.create_spec("plans", epic_doc())
        self.assertEqual("sp-epic-member-taken", self._refusal(b, member=2, epic_id=7))
        self.assertEqual("sp-epic-unknown-dependency", self._refusal(b, member=6, after="S9"))
        self.assertEqual("sp-epic-bad-label", self._refusal(b, member=6, label="S1"))
        self.assertEqual("sp-epic-not-an-epic", self._refusal(b, member=6, epic_id=2))
        self.assertEqual("sp-unknown-id", self._refusal(b, member=99))

    def _refusal(self, b, member, epic_id=EPIC_ID, **kw):
        kw.setdefault("after", None)
        kw.setdefault("group", None)
        kw.setdefault("label", None)
        code, got = run(epic_cmd.cmd_epic, b, epic_cmd="add", epic=epic_id, spec=member, **kw)
        self.assertEqual(2, code)
        return got["code"]

    def test_add_is_idempotent_and_repairs_a_missing_back_reference(self):
        b = self.diamond()
        before = b.read_spec(EPIC_ID)[0]["text"]
        self.assertFalse(add(b, 2)[1]["changed"])
        info, _ = b.read_spec(5)
        b.write_spec(info, info["text"].replace("epic: 1\n", ""))
        self.assertTrue(add(b, 5)[1]["changed"])
        self.assertEqual(before, b.read_spec(EPIC_ID)[0]["text"])
        self.assertEqual("1", str(b.read_spec(5)[0]["frontmatter"]["epic"]))

    def test_task_refuses_to_tick_an_epic_item(self):
        b = self.diamond()
        for flag in ("check", "uncheck", "block", "descope"):
            kw = dict(spec=EPIC_ID, check=None, uncheck=None, block=None, descope=None,
                      reason="r", subject=None, commit=None)
            kw[flag] = "S1"
            code, got = run(task_cmd.cmd_task, b, **kw)
            self.assertEqual((2, "sp-epic-derived-task"), (code, got["code"]))

    def test_validate_is_clean_for_a_consistent_epic(self):
        b = self.diamond()
        _, got = run(validate_cmd.cmd_validate, b, spec=None, phase=None, by_code=False)
        self.assertEqual([], [f for f in got["findings"] if f["code"].startswith("sp-epic")])

    def test_validate_flags_divergence_missing_members_and_cycles(self):
        b = self.diamond()
        info, _ = b.read_spec(3)                                  # the member loses its key
        b.write_spec(info, info["text"].replace("epic: 1\n", "epic: 77\n"))
        info, _ = b.read_spec(EPIC_ID)                             # a ghost and a cycle
        text = info["text"].replace("- [ ] S1 Member 1 — spec: #2",
                                    "- [ ] S1 Member 1 — spec: #2 — after: S4")
        b.write_spec(info, text + "- [ ] S9 Ghost — spec: #900\n")
        _, got = run(validate_cmd.cmd_validate, b, spec=None, phase=None, by_code=False)
        codes = {f["code"] for f in got["findings"] if f["code"].startswith("sp-epic")}
        self.assertEqual({"sp-epic-divergent", "sp-epic-missing-member", "sp-epic-cycle",
                          "sp-epic-orphan"}, codes)
        self.assertFalse(got["ok"])

    def test_a_narrowed_validate_still_sees_the_members_side(self):
        b = self.diamond()
        info, _ = b.read_spec(4)
        b.write_spec(info, set_frontmatter_key(info["text"], "epic", "1234"))
        _, got = run(validate_cmd.cmd_validate, b, spec="4", phase=None, by_code=False)
        self.assertEqual(["sp-epic-orphan"],
                         [f["code"] for f in got["findings"] if f["code"].startswith("sp-epic")])

    def test_an_epic_archives_as_done_only_when_every_member_is(self):
        b = self.diamond()
        epic_body = ("## Proposal\n\nx\n\n## Out of Scope\n\n- none — x\n"
                     "## Validation\n\nx\n\n## Design\n\nx\n\n## Outcome\n\nx\n")
        info, _ = b.read_spec(EPIC_ID)
        b.write_spec(info, info["text"] + epic_body)
        kw = dict(spec=EPIC_ID, to=None, outcome="done", force=False, dry_run=True)
        code, got = run(promote_cmd.cmd_promote, b, **kw)
        self.assertEqual((2, "sp-open-tasks"), (code, got.get("code")))
        self.assertEqual(4, got["open"])

    def test_an_epic_is_not_archived_as_done_while_a_member_pr_is_not_merged(self):
        b = self.diamond()
        for n in (3, 4, 5):
            archive(b, n)
        states = self.archive_with_pr(2, "OPEN")
        epic_body = ("## Proposal\n\nx\n\n## Out of Scope\n\n- none — x\n"
                     "## Validation\n\nx\n\n## Design\n\nx\n\n## Outcome\n\nx\n")
        info, _ = b.read_spec(EPIC_ID)
        b.write_spec(info, info["text"] + epic_body)
        kw = dict(spec=EPIC_ID, to=None, outcome="done", force=False, dry_run=True)
        spy = mock.Mock(return_value=states)
        with mock.patch.object(promote_cmd, "pr_states", spy):
            code, got = run(promote_cmd.cmd_promote, b, **kw)
        self.assert_asked_from_the_root(spy)
        self.assertEqual((2, "sp-open-tasks"), (code, got.get("code")))
        self.assertEqual("unmerged", got["openTasks"][0]["state"])


class MemoryEpics(Scenarios, unittest.TestCase):
    def setUp(self):
        self.backend = MemoryBackend()


class GitStoreEpics(Scenarios, GitStoreFixture):
    def setUp(self):
        super().setUp()
        self.backend = GitBackend(self.clone("a"))

    def test_adding_a_member_is_one_commit_for_both_documents(self):
        b = self.backend
        b.create_spec("plans", epic_doc())
        b.create_spec("plans", doc("Member", "approved: yes\n"))
        add(b, 2)
        self.assertEqual("[skip ci] specs: write 1 2", self.remote_log()[0])

    def test_a_status_reads_every_member_from_one_snapshot(self):
        self.diamond()
        fresh = GitBackend(self.clone("b"))
        calls = []
        real = fresh._snapshot
        with mock.patch.object(fresh, "_snapshot",
                               side_effect=lambda tip: calls.append(tip) or real(tip)):
            run(read_cmd.cmd_status, fresh, epic=EPIC_ID, spec=None)
        self.assertEqual(2, len(calls))      # the epic, then ALL four members at once


class PureDerivation(unittest.TestCase):
    def test_cycle_is_found_and_reported_as_a_path(self):
        items = [{"label": "A", "after": ["C"]}, {"label": "B", "after": ["A"]},
                 {"label": "C", "after": ["B"]}, {"label": "D", "after": []}]
        cycle = find_cycle(items)
        self.assertEqual(cycle[0], cycle[-1])
        self.assertEqual({"A", "B", "C"}, set(cycle))
        self.assertIsNone(find_cycle([{"label": "A", "after": []},
                                      {"label": "B", "after": ["A", "Z"]}]))

    def test_a_cyclic_epic_offers_nothing_and_has_no_critical_path(self):
        b = MemoryBackend()
        b.create_spec("plans", epic_doc(
            "## Tasks\n\n- [ ] S1 One — spec: #2 — after: S2\n- [ ] S2 Two — spec: #3 — after: S1\n"))
        for n in (1, 2):
            b.create_spec("plans", doc(f"M{n}", "approved: yes\nepic: 1\n"))
        info, _ = b.read_spec(1)
        got = derive_epic(info, b.read_specs([2, 3]))
        self.assertEqual([], got["ready"])
        self.assertEqual([], got["criticalPath"])
        self.assertIsNotNone(got["cycle"])

    def test_a_ticked_box_in_the_epic_is_a_finding_and_never_state(self):
        b = MemoryBackend()
        b.create_spec("plans", epic_doc("## Tasks\n\n- [x] S1 One — spec: #2\n"))
        b.create_spec("plans", doc("M", "approved: yes\nepic: 1\n"))
        info, _ = b.read_spec(1)
        got = derive_epic(info, b.read_specs([2]))
        self.assertEqual("ready", got["items"][0]["status"])
        _, report = run(validate_cmd.cmd_validate, b, spec=None, phase=None, by_code=False)
        self.assertIn("sp-epic-manual-tick", {f["code"] for f in report["findings"]})


class InsertItemGroupNumbering(unittest.TestCase):
    """One test per vector of `insert_item` naming a new group: the number is added once."""
    LINE = "- [ ] S1 Member — spec: #2"

    def info(self, body):
        b = MemoryBackend()
        b.create_spec("plans", epic_doc(body))
        return b.read_spec(EPIC_ID)[0]

    def heads(self, info, group):
        text = epic_cmd.insert_item(info, self.LINE, group)
        return [h for h in text.splitlines() if h.startswith("### ")], text

    def test_absent_tasks_a_bare_label_is_numbered(self):
        heads, text = self.heads(self.info("## Problem\n\nThe program.\n"), "Onda 1 — x")
        self.assertEqual(["### 1. Onda 1 — x"], heads)
        self.assertIn(self.LINE, text)

    def test_absent_tasks_a_label_with_its_number_is_used_as_is(self):
        heads, _ = self.heads(self.info("## Problem\n\nThe program.\n"), "1. Onda 1 — x")
        self.assertEqual(["### 1. Onda 1 — x"], heads)

    def test_empty_tasks_a_bare_label_is_numbered(self):
        self.assertEqual(["### 1. Onda 1"], self.heads(self.info(
            "## Problem\n\nThe program.\n\n## Tasks\n\n"), "Onda 1")[0])

    def test_empty_tasks_a_label_with_its_number_is_used_as_is(self):
        self.assertEqual(["### 1. Onda 1"], self.heads(self.info(
            "## Problem\n\nThe program.\n\n## Tasks\n\n"), "1. Onda 1")[0])

    def test_no_group_writes_no_heading(self):
        for body in ("## Problem\n\nThe program.\n", "## Problem\n\nX.\n\n## Tasks\n\n"):
            heads, text = self.heads(self.info(body), None)
            self.assertEqual([], heads)
            self.assertIn(self.LINE, text)

    def test_a_new_group_after_existing_ones_gets_the_next_number_once(self):
        body = "## Problem\n\nX.\n\n## Tasks\n\n### 1. A\n- [ ] S0 Old — spec: #3\n"
        self.assertEqual(["### 1. A", "### 2. B"], self.heads(self.info(body), "B")[0])
        self.assertEqual(["### 1. A", "### 2. B"], self.heads(self.info(body), "2. B")[0])


class PrStatesTarget(unittest.TestCase):
    def member(self, rec):
        return {"phase": "archive", "frontmatter": {"pr": rec}}

    def call(self, rec, root):
        seen = {}

        def fake(cmd, **kw):
            seen.update(cmd=cmd, **kw)
            return mock.Mock(returncode=0, stdout="MERGED\n")
        with mock.patch.object(epic_cmd.subprocess, "run", side_effect=fake):
            got = epic_cmd.pr_states({"7": self.member(rec)}, root)
        return got, seen

    def test_the_lookup_runs_from_the_named_root(self):
        got, seen = self.call({"number": 5, "url": "u"}, "/some/repo")
        self.assertEqual({"7": "MERGED"}, got)
        self.assertEqual("/some/repo", seen["cwd"])
        self.assertEqual("5", seen["cmd"][3])

    def test_a_recorded_url_names_the_repository_itself(self):
        url = "https://github.com/o/r/pull/5"
        _, seen = self.call({"number": 5, "url": url}, "/some/repo")
        self.assertEqual(url, seen["cmd"][3])


if __name__ == "__main__":
    unittest.main()
