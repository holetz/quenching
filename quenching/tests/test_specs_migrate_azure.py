"""`migrate --to azure`, offline: the destination is an in-memory double that allocates its own
ids and keeps `tags`/`assignee`/`start`/`target` in native fields, the way Azure Boards does.
No `az` process, no network and no real organisation is ever reached."""

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
import test_specs_backends as canonical
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.memory import MemoryBackend
from quenching.specs.commands import migrate as migrate_mod
from quenching.specs.commands.output import Emitter
from quenching.specs.parse import FIELD_KEYS, derive_info, strip_frontmatter_keys
from quenching.specs.parse.fields import set_frontmatter_key


def doc(title, **keys):
    text = canonical._case_doc(title)
    for key, value in keys.items():
        text = set_frontmatter_key(text, key, value)
    return text


def epic_doc(*members):
    items = "\n".join(f"- [ ] S{n} Member {m} — spec: #{m}" for n, m in enumerate(members, 1))
    text = set_frontmatter_key(canonical._case_doc("Epic"), "workItemType", "epic")
    return text.rstrip("\n") + "\n\n## Tasks\n\n### 1. Wave\n\n" + items + "\n"


class Ordering(unittest.TestCase):
    def test_dependencies_come_first_and_ties_follow_the_source_id(self):
        items = [(1, "plans", doc("a", dependsOn="[3]")), (2, "plans", doc("b")),
                 (3, "plans", doc("c", dependsOn="[2]")), (4, "archive", doc("d"))]
        order, unresolved = migrate_mod.azure_order(items)
        self.assertEqual([2, 3, 1, 4], order)
        self.assertEqual([], unresolved)

    def test_non_numeric_dependencies_are_not_this_stores_and_are_ignored(self):
        items = [(1, "plans", doc("a", dependsOn='[other-slug, "x/y#4"]'))]
        self.assertEqual(([1], []), migrate_mod.azure_order(items))

    def test_a_missing_id_a_self_wait_a_cycle_and_a_lost_member_are_unresolved(self):
        items = [(1, "plans", doc("a", dependsOn="[99]")), (2, "plans", doc("b", dependsOn="[2]")),
                 (3, "plans", doc("c", dependsOn="[4]")), (4, "plans", doc("d", dependsOn="[3]")),
                 (5, "plans", epic_doc(1, 77))]
        _, unresolved = migrate_mod.azure_order(items)
        kinds = sorted((u["id"], u["kind"]) for u in unresolved)
        self.assertEqual([(1, "missing"), (2, "self"), (3, "cycle"), (4, "cycle"),
                          (5, "missing-member")], kinds)


class Remap(unittest.TestCase):
    def test_depends_on_moves_onto_the_new_ids_and_keeps_foreign_ones(self):
        text = doc("a", dependsOn='[1, 2, other-slug]')
        out = migrate_mod.remap_text(text, {1: 101, 2: 102})
        self.assertEqual(["101", "102", "other-slug"],
                         parse_frontmatter(out)["dependsOn"])

    def test_a_text_with_nothing_to_remap_is_returned_unchanged(self):
        text = doc("a")
        self.assertIs(text, migrate_mod.remap_text(text, {1: 101}))

    def test_epic_members_are_remapped_only_when_asked_and_prose_is_untouched(self):
        text = epic_doc(1, 2).replace("## Tasks", "Mentions #1 in prose.\n\n## Tasks")
        early = migrate_mod.remap_text(text, {1: 101, 2: 102}, members=False)
        self.assertEqual(text, early)
        late = migrate_mod.remap_text(text, {1: 101, 2: 102})
        self.assertIn("— spec: #101", late)
        self.assertIn("— spec: #102", late)
        self.assertIn("Mentions #1 in prose.", late)

    def test_a_new_id_is_never_remapped_twice(self):
        text = epic_doc(1, 2)
        out = migrate_mod.remap_text(text, {1: 2, 2: 3})
        self.assertIn("Member 1 — spec: #2", out)
        self.assertIn("Member 2 — spec: #3", out)


class Equality(unittest.TestCase):
    def _info(self, text, **native):
        info = derive_info({"id": 9, "phase": "plans"}, migrate_mod.strip_frontmatter_keys(
            text, migrate_mod.FIELD_KEYS))
        info["frontmatter"].update(native)
        return info

    def test_native_fields_are_compared_as_values_not_as_text(self):
        expected = doc("a", tags='["x", "y"]', assignee="ana")
        self.assertTrue(migrate_mod.document_matches(
            expected, self._info(expected, tags=["x", "y"], assignee="ana")))

    def test_a_changed_native_value_or_body_is_a_difference(self):
        expected = doc("a", tags='["x"]')
        self.assertFalse(migrate_mod.document_matches(expected, self._info(expected, tags=["z"])))
        self.assertFalse(migrate_mod.document_matches(
            expected, self._info(expected + "\nextra line\n", tags=["x"])))


class GitSource(MemoryBackend):
    name = "git"


class AzureDouble(MemoryBackend):
    """Allocates its own ids and keeps the four native fields apart from the document."""
    name = "azure-boards"

    def __init__(self, first_id=5000, fail_on=None, mangle=False):
        super().__init__()
        self._next_id = first_id
        self.native = {}
        self.created = 0
        self.fail_on = fail_on
        self.mangle = mangle

    def _keep(self, spec_id, text):
        fm = parse_frontmatter(text)
        self.native[spec_id] = {k: fm[k] for k in FIELD_KEYS if k in fm}

    def create_spec(self, phase, text):
        self.created += 1
        if self.created == self.fail_on:
            raise BackendRefusal({"code": "sp-az-api-error", "exit": 2, "message": "HTTP 503"})
        body = strip_frontmatter_keys(text, FIELD_KEYS)
        locator = super().create_spec(phase, body + ("tampered\n" if self.mangle else ""))
        spec_id = int(locator.rsplit("/", 1)[1])
        self._keep(spec_id, text)
        return f"https://example.invalid/org/proj/_workitems/edit/{spec_id}"

    def read_spec(self, spec_id):
        info, err = super().read_spec(spec_id)
        if info:
            info["frontmatter"].update(self.native.get(info["id"], {}))
        return info, err

    def write_spec(self, info, text):
        super().write_spec(info, strip_frontmatter_keys(text, FIELD_KEYS))
        self._keep(info["id"], text)


def front():
    source = GitSource()
    source.docs[10] = ("plans", doc("One", dependsOn="[20]", tags='["alpha", "beta"]',
                                    assignee="ana"))
    source.docs[20] = ("plans", doc("Two"))
    source.docs[30] = ("archive", doc("Old"))
    source.docs[40] = ("plans", epic_doc(10, 20))
    return source


class Migration(unittest.TestCase):
    def test_a_dry_run_reads_everything_and_creates_nothing(self):
        target = AzureDouble()
        report = migrate_mod.migrate_to_azure(front(), target, write=False)
        self.assertTrue(report["ok"], report)
        self.assertEqual((4, 3, 1), (report["count"], report["open"], report["closed"]))
        self.assertEqual([20, 10, 30, 40], report["order"])
        self.assertEqual({"backend": "azure-boards"}, report["configChange"]["set"])
        self.assertEqual(0, target.created)
        self.assertEqual({}, report["idMap"])

    def test_a_dry_run_reports_what_a_write_would_refuse(self):
        source = front()
        source.docs[50] = ("plans", doc("Five", dependsOn="[99]"))
        report = migrate_mod.migrate_to_azure(source, AzureDouble(), write=False)
        self.assertFalse(report["ok"])
        self.assertEqual([{"id": 50, "kind": "missing", "ref": 99}], report["unresolved"])
        busy = AzureDouble()
        busy.create_spec("plans", doc("Taken"))
        report = migrate_mod.migrate_to_azure(front(), busy, write=False)
        self.assertEqual((False, 1), (report["ok"], report["occupied"]))

    def test_write_creates_one_item_per_spec_and_proves_the_equality(self):
        target = AzureDouble()
        report = migrate_mod.migrate_to_azure(front(), target, write=True)
        self.assertTrue(report["ok"], report)
        self.assertEqual([], report["diffs"])
        self.assertTrue(report["identical"])
        idmap = report["idMap"]
        self.assertEqual({10, 20, 30, 40}, set(idmap))
        self.assertTrue(all(v >= 5000 for v in idmap.values()))
        self.assertEqual({"plans": 3, "archive": 1},
                         {p: sum(1 for ph, _ in target.docs.values() if ph == p)
                          for p in ("plans", "archive")})
        self.assertEqual("archive", target.docs[idmap[30]][0])

    def test_references_are_remapped_and_native_fields_travel(self):
        target = AzureDouble()
        idmap = migrate_mod.migrate_to_azure(front(), target, write=True)["idMap"]
        one, _ = target.read_spec(idmap[10])
        self.assertEqual([str(idmap[20])], one["frontmatter"]["dependsOn"])
        self.assertEqual(["alpha", "beta"], one["frontmatter"]["tags"])
        self.assertEqual("ana", one["frontmatter"]["assignee"])
        epic, _ = target.read_spec(idmap[40])
        self.assertIn(f"— spec: #{idmap[10]}", epic["text"])
        self.assertIn(f"— spec: #{idmap[20]}", epic["text"])
        self.assertNotIn("— spec: #10", epic["text"])

    def test_an_occupied_destination_refuses_before_creating(self):
        busy = AzureDouble()
        busy.create_spec("plans", doc("Taken"))
        with self.assertRaises(BackendRefusal) as caught:
            migrate_mod.migrate_to_azure(front(), busy, write=True)
        self.assertEqual("sp-migrate-target-not-empty", caught.exception.err["code"])
        self.assertEqual(1, busy.created)

    def test_unresolved_references_refuse_before_creating(self):
        source = front()
        source.docs[50] = ("plans", doc("Five", dependsOn="[99]"))
        target = AzureDouble()
        with self.assertRaises(BackendRefusal) as caught:
            migrate_mod.migrate_to_azure(source, target, write=True)
        self.assertEqual("sp-migrate-unresolved-references", caught.exception.err["code"])
        self.assertEqual(0, target.created)

    def test_a_document_over_the_ceiling_refuses_before_creating(self):
        source = front()
        source.docs[20] = ("plans", doc("Two") + "x" * migrate_mod.AZ_DESCRIPTION_MAX)
        target = AzureDouble()
        with self.assertRaises(BackendRefusal) as caught:
            migrate_mod.migrate_to_azure(source, target, write=True)
        self.assertEqual("sp-migrate-description-ceiling", caught.exception.err["code"])
        self.assertEqual(0, target.created)

    def test_a_failure_midway_reports_what_was_created_and_stops(self):
        target = AzureDouble(fail_on=3)
        report = migrate_mod.migrate_to_azure(front(), target, write=True)
        self.assertFalse(report["ok"])
        self.assertEqual({20, 10}, set(report["idMap"]))
        self.assertEqual({"id": 30, "code": "sp-az-api-error", "message": "HTTP 503"},
                         report["failed"])
        self.assertEqual(2, len(target.docs))

    def test_the_equality_names_a_document_that_did_not_survive(self):
        report = migrate_mod.migrate_to_azure(front(), AzureDouble(mangle=True), write=True)
        self.assertFalse(report["ok"])
        self.assertFalse(report["identical"])
        # the epic is rewritten by `write_spec` after the batch, which restores its body
        self.assertEqual({10, 20, 30}, set(report["mismatched"]))


class Command(unittest.TestCase):
    def _run(self, *, backend="git", target=None, **flags):
        args = argparse.Namespace(**{"json": True, "to": "azure", "write": False,
                                     "thin_open_cards": False, "dry_run": False, **flags})
        target = target or AzureDouble()
        buf = io.StringIO()
        with mock.patch.object(migrate_mod, "load_config", lambda _r: {"backend": backend}), \
                mock.patch.object(migrate_mod, "open_git_backend", lambda _r: (front(), {})), \
                mock.patch.object(migrate_mod, "open_azure_backend", lambda _r: (target, {})), \
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
        self.assertFalse(payload["dryRun"])
        self.assertEqual(4, target.created)

    def test_each_refusal_is_exit_2_with_its_code(self):
        code, payload, _ = self._run(backend="github")
        self.assertEqual((2, "sp-migrate-source-not-git"), (code, payload["code"]))
        code, payload, _ = self._run(write=True, thin_open_cards=True)
        self.assertEqual((2, "sp-migrate-thin-git-only"), (code, payload["code"]))
        busy = AzureDouble()
        busy.create_spec("plans", doc("Taken"))
        code, payload, _ = self._run(write=True, target=busy)
        self.assertEqual((2, "sp-migrate-target-not-empty"), (code, payload["code"]))

    def test_the_cli_accepts_azure_as_a_destination(self):
        from quenching.specs.commands.cli import build_parser
        self.assertEqual("azure", build_parser()[0].parse_args(["migrate", "--to", "azure"]).to)


if __name__ == "__main__":
    unittest.main()
