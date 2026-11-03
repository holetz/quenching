"""The composition verbs, offline: `link add|remove`, the `epic add` alias, the renamed
findings and the many-to-many rules. The memory fake is enough — no store is under test."""
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
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import epic as epic_cmd
from quenching.specs.commands import validate as validate_cmd
from quenching.specs.commands.output import Emitter
from quenching.specs.parse.epics import parse_items
from quenching.specs.parse.fields import set_frontmatter_key


def doc(title="Spec", fm="", tasks="## Tasks\n\n"):
    return f"---\ntitle: {title}\ndate: 2026-01-01\n{fm}---\n\n## Problem\n\nx\n\n" + tasks


def run(fn, backend, **kw):
    args = argparse.Namespace(json=True, **kw)
    buf = io.StringIO()
    with contextlib.ExitStack() as stack:
        for mod in (epic_cmd, validate_cmd):
            stack.enter_context(mock.patch.object(mod, "open_backend",
                                                  return_value=(backend, {})))
        stack.enter_context(contextlib.redirect_stdout(buf))
        code = fn(args, tempfile.gettempdir(), Emitter())
    text = buf.getvalue().strip()
    return code, (json.loads(text) if text else {})


def link(backend, composite, member, **kw):
    kw.setdefault("after", None)
    kw.setdefault("group", None)
    kw.setdefault("label", None)
    return run(epic_cmd.cmd_epic, backend, link_cmd="add", epic=composite, spec=member, **kw)


def remove(backend, composite, member):
    return run(epic_cmd.cmd_epic, backend, link_cmd="remove", epic=composite, spec=member)


class LinkCommands(unittest.TestCase):
    def setUp(self):
        self.b = MemoryBackend()
        self.b.create_spec("plans", doc("Composite"))                 # 1
        self.b.create_spec("plans", doc("Other"))                     # 2
        self.b.create_spec("plans", doc("Member one"))                # 3
        self.b.create_spec("plans", doc("Member two"))                # 4

    def labels(self, composite=1):
        return [i["label"] for i in parse_items(self.b.read_spec(composite)[0])]

    def test_link_add_is_the_verb_and_epic_add_is_an_alias(self):
        code, got = link(self.b, 1, 3, group="Wave 1")
        self.assertEqual((0, "S1"), (code, got["label"]), got)
        code, got = run(epic_cmd.cmd_epic, self.b, epic_cmd="add", epic=1, spec=4,
                        after="S1", group="Wave 2", label=None, move=False)
        self.assertEqual((0, "S2"), (code, got["label"]), got)
        self.assertEqual(["S1", "S2"], self.labels())
        text = self.b.read_spec(1)[0]["text"]
        self.assertIn("- [ ] S1 Member one — spec: #3", text)
        self.assertIn("- [ ] S2 Member two — spec: #4 — after: S1", text)

    def test_link_add_is_idempotent(self):
        link(self.b, 1, 3)
        before = self.b.read_spec(1)[0]["text"]
        code, got = link(self.b, 1, 3)
        self.assertEqual((0, False), (code, got["changed"]))
        self.assertEqual(before, self.b.read_spec(1)[0]["text"])

    def test_a_member_may_belong_to_several_composites_and_move_is_a_no_op(self):
        link(self.b, 1, 3)
        link(self.b, 2, 3)
        self.assertEqual(["S1"], self.labels(1))
        self.assertEqual(["S1"], self.labels(2))
        code, got = run(epic_cmd.cmd_epic, self.b, epic_cmd="add", epic=2, spec=4,
                        after=None, group=None, label=None, move=True)
        self.assertEqual(0, code, got)
        self.assertEqual(["S1"], self.labels(1))
        self.assertEqual(["S1", "S2"], self.labels(2))

    def test_remove_refuses_a_dependent_and_then_removes(self):
        link(self.b, 1, 3)
        link(self.b, 1, 4, after="S1")
        code, got = remove(self.b, 1, 3)
        self.assertEqual((2, "sp-epic-move-dependents"), (code, got["code"]))
        self.assertEqual(["S1", "S2"], self.labels())
        code, got = remove(self.b, 1, 4)
        self.assertEqual((0, True), (code, got["changed"]))
        self.assertEqual(["S1"], self.labels())
        code, got = remove(self.b, 1, 4)
        self.assertEqual((0, False), (code, got["changed"]))

    def test_validate_allows_nesting_and_reports_the_renamed_codes(self):
        self.b.create_spec("plans", doc("Child",
                                        tasks="## Tasks\n\n- [ ] S1 Leaf — spec: #3\n"))  # 5
        link(self.b, 1, 5)                                            # 1 -> child 5 -> 3
        _, got = run(validate_cmd.cmd_validate, self.b, spec=None, phase=None, by_code=False)
        codes = {f["code"] for f in got["findings"]}
        self.assertNotIn("sp-link-nested", codes)
        self.assertNotIn("sp-link-missing-member", codes)
        info, _ = self.b.read_spec(3)
        self.b.write_spec(info, set_frontmatter_key(info["text"], "epic", "1"))
        _, got = run(validate_cmd.cmd_validate, self.b, spec=None, phase=None, by_code=False)
        self.assertIn("sp-epic-key-deprecated", {f["code"] for f in got["findings"]})
        info, _ = self.b.read_spec(1)
        self.b.write_spec(info, info["text"] + "- [ ] S9 Ghost — spec: #900\n")
        _, got = run(validate_cmd.cmd_validate, self.b, spec=None, phase=None, by_code=False)
        self.assertIn("sp-link-missing-member", {f["code"] for f in got["findings"]})

    def test_a_cross_document_cycle_is_a_finding(self):
        link(self.b, 1, 2)
        link(self.b, 2, 1)
        _, got = run(validate_cmd.cmd_validate, self.b, spec=None, phase=None, by_code=False)
        cycles = [f for f in got["findings"] if f["code"] == "sp-link-member-cycle"]
        self.assertEqual(1, len(cycles))
        self.assertEqual(["1", "2", "1"], cycles[0]["cycle"])
        self.assertFalse(got["ok"])


if __name__ == "__main__":
    unittest.main()
