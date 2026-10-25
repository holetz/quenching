"""`migrate --to azure`, offline: the destination is an in-memory double that allocates its own
ids and keeps `tags`/`assignee`/`start`/`target` in native fields, the way Azure Boards does.
No `az` process, no network and no real organisation is ever reached."""

import sys
import pathlib
import unittest

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
import test_specs_backends as canonical
from quenching.common.frontmatter import parse_frontmatter
from quenching.specs.commands import migrate as migrate_mod
from quenching.specs.parse import derive_info
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


if __name__ == "__main__":
    unittest.main()
