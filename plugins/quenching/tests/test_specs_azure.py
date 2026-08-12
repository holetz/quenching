"""The `azure-boards` backend's vocabulary: work-item type resolution, tags/board state,
the `az` transport's refusal shapes, and the consolidated PATCH — migrated from the pre-refactor
specs script's `_failures()` selftest suites, run against `quenching.specs.*` rather than the script.

Every case, fixture and `why` below is carried over verbatim from its `_failures()` — the
translation is the assertion, not the data.
"""

import os
import tempfile
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.specs.backends.azure import (
    AZ_DESCRIPTION_MAX,
    AZ_MISSING,
    AZ_SPEC_TYPE,
    AzureBoardsBackend,
    az_refusal,
    azure_artifact_url,
    azure_comparable_fields,
    azure_native_fields,
    azure_patch_body,
    azure_patch_culprit,
    azure_query_wiql,
    azure_restore_trailing_newline,
)
from quenching.specs.backends.base import BackendRefusal
from quenching.specs.backends.github import GitHubBackend
from quenching.specs.config import (azure_workitemtype_retirement, resolve_type_key,
                                    resolve_work_item_type)
from quenching.specs.parse import (
    FIELD_KEYS,
    board_state_of,
    declared_tags,
    reconcile_label_set,
    strip_frontmatter_keys,
    tags_outside_catalog,
)
from quenching.specs.schema import capture_form

# The one `azureStates` mapping every case below constructs a backend against — none of
# these cases exercises state resolution itself, so the mapping only needs to satisfy the
# constructor.
AZ_STATES = {"plans": "Active", "archive": "Closed"}


def _case_doc(slug: str = "alpha") -> str:
    # A FIXED date, never `today()`: it is the fact the case asserts travels intact through
    # each store, and one computed at call time would compare equal to itself no matter what
    # either backend did with it.
    return (capture_form().replace("<SLUG>", slug).replace("<TITLE>", "Alpha")
            .replace("<DATE>", "2026-01-01").replace("<VERIFICATION>", "per-task"))


def _type_argv(argv: list[str]) -> str | None:
    """The value `--type` was given in one recorded `az` call, or None if it was never
    passed — the one check `AzureCreateType`'s two cases both make."""
    return argv[argv.index("--type") + 1] if "--type" in argv else None


class WorkItemTypeResolution(unittest.TestCase):
    """`resolve_work_item_type` against one case per link in its own chain."""

    INCIDENTE = {"description": "d", "azure": "Bug"}
    TAREFA = {"description": "d", "azure": "Task", "default": True}
    GITHUB_ONLY = {"description": "d", "github": "Incident"}

    CASES = (
        ({"workItemTypes": {"incidente": INCIDENTE}}, "incidente",
         "an explicit key with an azure name resolves it", "Bug"),
        ({"workItemTypes": {"incidente": INCIDENTE, "tarefa": TAREFA}}, None,
         "no explicit key falls back to the default entry", "Task"),
        ({"workItemTypes": {"incidente": GITHUB_ONLY}}, "incidente",
         "an explicit key with no azure name falls through to the floor", AZ_SPEC_TYPE),
        ({"workItemTypes": {"tarefa": GITHUB_ONLY}}, None,
         "a default entry with no azure name falls through to the floor", AZ_SPEC_TYPE),
        ({}, None, "nothing declared falls through to the floor", AZ_SPEC_TYPE),
    )

    def test_each_link_in_the_chain(self):
        for cfg, key, label, want in self.CASES:
            with self.subTest(case=label):
                self.assertEqual(resolve_work_item_type(cfg, key), want)


class TypeKeyResolution(unittest.TestCase):
    """`resolve_type_key` against the two refusals `## Design` shares with `--subject`, and
    the one non-refusal that keeps `--type` optional."""

    INCIDENTE = {"description": "d", "azure": "Bug"}

    CASES = (
        ({"workItemTypes": {}}, None, "no key asked is not a refusal", None, None),
        ({"workItemTypes": {}}, "incidente",
         "an explicit key against nothing declared refuses", None, "sp-type-unknown"),
        ({"workItemTypes": {"incidente": INCIDENTE}}, "incidente",
         "an explicit key that exists resolves it", "incidente", None),
        ({"workItemTypes": {"incidente": INCIDENTE}}, "ghost",
         "a declared key that does not exist refuses", None, "sp-type-unknown"),
    )

    def test_each_case_resolves_or_refuses_as_declared(self):
        for cfg, key, label, want_key, want_code in self.CASES:
            with self.subTest(case=label):
                got, err = resolve_type_key(cfg, key)
                self.assertEqual(got, want_key)
                self.assertEqual(err.get("code"), want_code)


class AzureWorkItemTypeRetirement(unittest.TestCase):
    """One case per branch: nothing declared, declared beside a catalog that already
    resolves, and declared as the only entry that would have answered."""

    TAREFA = {"description": "d", "azure": "Task", "default": True}

    CASES = (
        ({"azurePlacement": {}}, None, "nothing declared is not a finding"),
        ({"azurePlacement": {"workItemType": "Issue"}, "workItemTypes": {"tarefa": TAREFA}},
         "sp-az-workitemtype-retired-unused",
         "declared beside a catalog that resolves is dead configuration"),
        ({"azurePlacement": {"workItemType": "Issue"}}, "sp-az-workitemtype-only-answer",
         "declared as the only answer refuses"),
    )

    def test_each_branch_names_its_own_code(self):
        for cfg, want_code, label in self.CASES:
            with self.subTest(case=label):
                got = azure_workitemtype_retirement(cfg, None)
                code = got["code"] if got else None
                self.assertEqual(code, want_code)


class BoardState(unittest.TestCase):
    """The three-way precedence, each rung checked against the other two: `archived`
    outranks `reviewed`, `reviewed` outranks the derived stage, and the derived stage is
    the floor."""

    CASES = (
        ({"phase": "archive", "frontmatter": {"reviewed": {"date": "x"}}, "stage": "executing"},
         "archived", "archived outranks reviewed"),
        ({"phase": "plans", "frontmatter": {"reviewed": {"date": "x"}}, "stage": "executing"},
         "reviewed", "reviewed outranks the derived stage"),
        ({"phase": "plans", "frontmatter": {}, "stage": "executing"},
         "executing", "the derived stage is the floor"),
    )

    def test_the_precedence(self):
        for info, want, label in self.CASES:
            with self.subTest(case=label):
                self.assertEqual(board_state_of(info), want)


class TagCatalog(unittest.TestCase):
    """`tags_outside_catalog` — the one flag and the two ways nothing is flagged."""

    CASES = (
        ([], {"a": "d"}, [], "no tags, nothing to flag"),
        (["a", "b"], {"a": "d"}, ["b"], "one outside the catalog"),
        (["a"], {}, [], "no catalog declared flags nothing"),
    )

    def test_each_case(self):
        for tags, catalog, want, label in self.CASES:
            with self.subTest(case=label):
                self.assertEqual(tags_outside_catalog(tags, catalog), want)


class AzRefusal(unittest.TestCase):
    """Every `az` failure must arrive as its own exit-2 refusal, carrying the remedy that
    fixes THAT failure — never a traceback, and never the wrong remedy stated confidently.

    Self-contained: no network and no `az`. Asserted against the literal streams the CLI
    produces, because the split into remedies is made on what it said."""

    # (label, az exit, stdout, stderr, expected code). `az` reports almost everything as
    # exit 1 and explains in stderr, so these are the literal stderr shapes its 2.6x
    # releases produce — a reworded release breaks the check rather than the refusal.
    CASES = (
        ("no binary on PATH", AZ_MISSING, "", "", "sp-az-missing"),
        ("the azure-devops extension is not installed", 2, "",
         "ERROR: 'boards' is not in the 'az' command group. Run `az extension add --name "
         "azure-devops`.\n", "sp-az-extension-missing"),
        ("nobody logged in", 1, "",
         "ERROR: Before you can run Azure DevOps commands, you need to run the login command "
         "(az login if using AAD/MSA identity...).\n", "sp-az-unauthenticated"),
        ("an identity without access", 1, "",
         "ERROR: TF400813: The user 'x' is not authorized to access this resource.\n",
         "sp-az-unauthenticated"),
        ("a work item that is not there", 1, "",
         "ERROR: TF401232: Work item 4242 does not exist, or you do not have permissions to "
         "read it.\n", "sp-az-api-error"),
        # Captured VERBATIM from az 2.88 on 2026-08-01, by running `az boards query` in a
        # checkout with no defaults configured. It is the failure a first-time user actually
        # hits, and it is not an API error: nothing was asked of Azure DevOps at all.
        ("no organization configured", 1, "",
         "ERROR: --organization must be specified. The value should be the URI of your Azure "
         "DevOps organization, for example: https://dev.azure.com/MyOrganization/. You can set "
         "a default value by running: az devops configure --defaults "
         "organization=https://dev.azure.com/MyOrganization/.\n", "sp-az-no-project"),
        # A fifth outcome, `code == 0`: this org's `az boards work-item show/create/update`
        # never legitimately prints nothing on success, so an empty response is a cut-short
        # transport failure rather than a shape to accept.
        ("az exits 0 with empty stdout on a single-item call", 0, "", "", "sp-az-empty-response"),
        # The PATCH endpoint's own two, which `az boards work-item update` never produced.
        ("a format op sent without its own value", 1, "",
         "ERROR: VS403319: The type changed without a value for field System.Description.\n",
         "sp-az-format-uncoupled"),
        ("a column value the process refuses", 1, "",
         "ERROR: TF401320: Rule Error for field WEF_a_Kanban.Column. Error code: "
         "AllowedValues.\n", "sp-az-rule-error"),
    )

    def test_every_shape_names_its_own_code_and_is_always_exit_2_with_a_message(self):
        for label, code, out, err, want in self.CASES:
            with self.subTest(case=label):
                got = az_refusal("reading a spec", code, out, err)
                self.assertEqual(got.get("code"), want)
                self.assertEqual(got.get("exit"), 2, "every refusal is 2")
                self.assertTrue(str(got.get("message", "")).strip(),
                                "refused with an empty message")


class AzureQueryWiql(unittest.TestCase):
    """The literal-project-name fix and the two optional scopes, pure and self-contained."""

    CASES = (
        ("Proj", None, None,
         "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'Proj'"),
        ("Proj", "Proj\\Area", None,
         "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'Proj' AND "
         "[System.AreaPath] = 'Proj\\Area'"),
        ("Proj", None, "quenching-spec",
         "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'Proj' AND "
         "[System.Tags] CONTAINS 'quenching-spec'"),
        ("Proj", "Proj\\Area", "quenching-spec",
         "SELECT [System.Id] FROM WorkItems WHERE [System.TeamProject] = 'Proj' AND "
         "[System.AreaPath] = 'Proj\\Area' AND [System.Tags] CONTAINS 'quenching-spec'"),
    )

    def test_the_query_built_for_each_scope(self):
        for project, area, tag, want in self.CASES:
            with self.subTest(project=project, area=area, tag=tag):
                got = azure_query_wiql(project, area, tag)
                self.assertEqual(got, want)

    def test_the_project_is_never_the_at_project_macro(self):
        # Measured on this org (az 2.89.0 + azure-devops 1.0.6): the macro resolves to
        # nothing and the query exits 0 with byte-empty stdout AND stderr — identical to a
        # query that legitimately matches zero work items.
        for project, area, tag, _ in self.CASES:
            with self.subTest(project=project, area=area, tag=tag):
                self.assertNotIn("@project", azure_query_wiql(project, area, tag))


class AzureNativeField(unittest.TestCase):
    """The one rule that must never regress: the discovery tag survives every write, tagged
    or not — plus the ordinary cases, so a future edit cannot fix the alarming one by
    breaking the boring ones."""

    CASES = (
        ({}, "quenching-spec", {"System.Tags": "quenching-spec"}, None,
         "no tags at all still writes the discovery tag alone"),
        ({"tags": ["Vertical: Risco"]}, "quenching-spec",
         {"System.Tags": "Vertical: Risco; quenching-spec"}, None,
         "a declared tag is joined with the discovery tag, never instead of it"),
        ({"tags": ["quenching-spec"]}, "quenching-spec",
         {"System.Tags": "quenching-spec"}, None,
         "the discovery tag is never duplicated when already declared"),
        ({"start": "2026-01-01", "target": "2026-02-01"}, "quenching-spec",
         {"System.Tags": "quenching-spec",
          "Microsoft.VSTS.Scheduling.StartDate": "2026-01-01",
          "Microsoft.VSTS.Scheduling.TargetDate": "2026-02-01"}, None,
         "both scheduling dates become their own field"),
        ({"assignee": "Someone"}, None, {}, "Someone",
         "no discovery tag declared writes no System.Tags at all"),
    )

    def test_each_case(self):
        for fm, tag, want_fields, want_assignee, label in self.CASES:
            with self.subTest(case=label):
                fields, assignee = azure_native_fields(fm, tag)
                self.assertEqual(fields, want_fields)
                self.assertEqual(assignee, want_assignee)


class FieldStrip(unittest.TestCase):
    """`strip_frontmatter_keys` drops exactly the four stored keys and nothing else — the
    WRITE half of the same round trip `AzureNativeField` checks the pairs for."""

    TEXT = ("---\nslug: x\ntitle: X\ndate: 2026-01-01\nverification: per-section\n"
           'tags: ["a", "b"]\nassignee: someone\nstart: 2026-01-01\ntarget: 2026-02-01\n'
           "---\n\n# X\n")

    def test_azure_strips_the_four_native_keys_and_keeps_the_rest(self):
        got = strip_frontmatter_keys(self.TEXT, FIELD_KEYS)
        for key in FIELD_KEYS:
            with self.subTest(dropped=key):
                self.assertNotIn(f"{key}:", got)
        for kept in ("slug: x", "title: X", "date: 2026-01-01", "verification: per-section"):
            with self.subTest(kept=kept):
                self.assertIn(kept, got)

    def test_github_strips_only_tags_and_assignee(self):
        # `github` strips only `tags`/`assignee` — `start`/`target` have no native
        # counterpart on an issue and stay in the document, exactly as `date:` already does.
        got = strip_frontmatter_keys(self.TEXT, GitHubBackend.GH_STORED_KEYS)
        for key in ("tags", "assignee"):
            with self.subTest(dropped=key):
                self.assertNotIn(f"{key}:", got)
        for kept in ("start: 2026-01-01", "target: 2026-02-01"):
            with self.subTest(kept=kept):
                self.assertIn(kept, got,
                             "no native counterpart exists to reassemble it from")


class AzurePatch(unittest.TestCase):
    """The consolidated write's two halves: which op a rejection names, and which ops a
    diff against the item as read actually emits."""

    # (label, ops' paths, what az said, the op expected to be named).
    CULPRIT_CASES = (
        ("a rejected column value names its own field",
         ("/fields/System.Title", "/fields/WEF_a_Kanban.Column"),
         "TF401320: Rule Error for field WEF_a_Kanban.Column: value not allowed",
         "/fields/WEF_a_Kanban.Column"),
        ("the type error names the format op, never a field",
         ("/fields/System.Title", "/multilineFieldsFormat/System.Description"),
         "400 The type changed without a value",
         "/multilineFieldsFormat/System.Description"),
        ("a relation op is never guessed at from a hyphen",
         ("/relations/-",), "VS402323: some-rule-failed for this work item", None),
        ("a message naming nothing names no op",
         ("/fields/System.Title",), "TF400813: the user is not authorized", None),
    )

    # The exact shape `_work_item_url` builds — org AND project, then the API's own
    # spelling of a work item. Written out here rather than derived, so a fixture that
    # stops matching what the code produces is visible in the diff.
    PARENT = (788243, "https://dev.azure.com/o/proj/_apis/wit/workItems/788243")

    # (label, current, desired, markdown, parent, expected op paths in order).
    PATCH_CASES = (
        ("nothing changed emits nothing",
         {"System.Title": "t", "System.Description": "d"},
         {"System.Title": "t", "System.Description": "d"}, False, None, ()),
        ("one changed field is one op",
         {"System.Title": "t", "System.Description": "d"},
         {"System.Title": "t2", "System.Description": "d"}, False, None,
         ("/fields/System.Title",)),
        ("a field the item does not carry yet is an op",
         {"System.Title": "t"}, {"System.Title": "t", "System.Tags": "spec"}, False, None,
         ("/fields/System.Tags",)),
        ("markdown rides with the description it needs",
         {"System.Description": "d"}, {"System.Description": "d2"}, True, None,
         ("/fields/System.Description", "/multilineFieldsFormat/System.Description")),
        ("markdown is never emitted alone",
         {"System.Title": "t", "System.Description": "d"},
         {"System.Title": "t2", "System.Description": "d"}, True, None,
         ("/fields/System.Title",)),
        ("an unlinked parent is a relation op",
         {"System.Title": "t"}, {"System.Title": "t"}, False, PARENT, ("/relations/-",)),
        ("a parent already linked emits nothing",
         {"System.Title": "t", "System.Parent": 788243}, {"System.Title": "t"}, False,
         PARENT, ()),
        # The two fields whose read shape is not their write shape. Fed through
        # `azure_comparable_fields` first, an unchanged assignee and an unchanged date must
        # vanish from the patch exactly like any other unchanged field.
        ("an identity object equals the UPN it was written from",
         azure_comparable_fields({"System.AssignedTo": {"uniqueName": "a@b.c",
                                                        "displayName": "A B"}}),
         {"System.AssignedTo": "a@b.c"}, False, None, ()),
        ("a datetime equals the date it was written from",
         azure_comparable_fields({"Microsoft.VSTS.Scheduling.StartDate":
                                  "2026-01-01T03:00:00Z"}),
         {"Microsoft.VSTS.Scheduling.StartDate": "2026-01-01"}, False, None, ()),
    )

    def test_azure_patch_culprit_names_the_right_op_or_none(self):
        for label, paths, said, want in self.CULPRIT_CASES:
            with self.subTest(case=label):
                ops = [{"op": "add", "path": p, "value": "v"} for p in paths]
                self.assertEqual(azure_patch_culprit(ops, said), want)

    def test_azure_patch_body_emits_only_the_ops_that_change_something(self):
        for label, current, desired, markdown, parent, want in self.PATCH_CASES:
            with self.subTest(case=label):
                ops = azure_patch_body(current, desired, markdown=markdown, parent=parent)
                self.assertEqual(tuple(o["path"] for o in ops), want)
                for op in ops:
                    if op["path"] == "/relations/-":
                        self.assertFalse(op["value"]["url"].isdigit(),
                                        "the relation carries a bare id, not a work-item url")


class AzureTrailingNewline(unittest.TestCase):
    """The one case that matters (a stripped newline restored) and the two it must leave
    alone (already-terminated, and genuinely empty)."""

    CASES = (("x", "x\n"), ("x\n", "x\n"), ("", ""))

    def test_each_case(self):
        for given, want in self.CASES:
            with self.subTest(given=given):
                self.assertEqual(azure_restore_trailing_newline(given), want)


class AzureDescriptionCeiling(unittest.TestCase):
    """The measured ceiling refuses BEFORE any call is made — self-contained, since only
    the over-ceiling path never reaches `az`; the under-ceiling path is what a real cycle
    exercises."""

    def test_over_ceiling_refuses_with_the_named_code_and_exit_2(self):
        az = AzureBoardsBackend("org", "proj", AZ_STATES, ".")
        with self.assertRaises(BackendRefusal) as ctx:
            az._az_patch("testing", 1, [{"op": "add", "path": "/fields/System.Description",
                                        "value": "x" * (AZ_DESCRIPTION_MAX + 1)}])
        self.assertEqual(ctx.exception.err.get("code"), "sp-az-description-too-large")
        self.assertEqual(ctx.exception.err.get("exit"), 2)


class AzureNativeFieldsRead(unittest.TestCase):
    """`AzureBoardsBackend._native_fields`, over fake `System.AssignedTo` shapes — no
    network. The one rule measured on this org (task 6.1): `uniqueName` (the UPN), never
    `displayName` — `--assigned-to` refuses a display name outright, so reading one back
    would read a value this backend could never write again."""

    CASES = (
        ({"fields": {"System.AssignedTo": {"displayName": "Israel Holetz",
                                           "uniqueName": "israel@x.com"}}},
         "israel@x.com", "uniqueName wins over displayName"),
        ({"fields": {"System.AssignedTo": {"displayName": "Israel Holetz"}}},
         "Israel Holetz", "no uniqueName falls back to displayName"),
        ({"fields": {}}, None, "no assignee at all reassembles nothing"),
    )

    def test_each_case(self):
        az = AzureBoardsBackend("org", "proj", AZ_STATES, ".", discovery_tag="quenching-spec")
        for item, want, label in self.CASES:
            with self.subTest(case=label):
                self.assertEqual(az._native_fields(item).get("assignee"), want)


class AzureBoardFieldType(unittest.TestCase):
    """`_resolve_board_field`'s process-local cache, keyed by TYPE — `board_findings` loops
    the whole listing in one process, and a spec born under a different type from the last
    one resolved must never answer with the other's field, which a single `self._board_field`
    string (rather than a dict) once did."""

    def test_two_types_resolve_to_different_fields_and_the_process_cache_holds(self):
        # `XDG_CACHE_HOME` redirected to a throwaway directory: `_resolve_board_field` also
        # writes the CROSS-process cache, and this proves the per-type key without ever
        # touching the real one at `~/.cache/quenching/azure/`.
        with tempfile.TemporaryDirectory() as tmp:
            old_xdg = os.environ.get("XDG_CACHE_HOME")
            os.environ["XDG_CACHE_HOME"] = tmp
            try:
                az = AzureBoardsBackend("test-org-4-2", "test-proj-4-2", AZ_STATES, ".",
                                        team="Diretoria Risco")
                boards = {
                    "1": {"allowedMappings": {"x": ["Bug"]},
                         "fields": {"columnField": {
                             "referenceName": "WEF_bugs_Kanban.Column"}}},
                    "2": {"allowedMappings": {"x": ["User Story"]},
                         "fields": {"columnField": {
                             "referenceName": "WEF_stories_Kanban.Column"}}},
                }
                az._az_raw = lambda action, *argv, expect="object": (
                    boards[next(a for a in argv if a.startswith("id="))[3:]]
                    if any(a.startswith("id=") for a in argv)
                    else {"value": [{"id": "1", "name": "Bugs"},
                                    {"id": "2", "name": "Stories"}]})
                bug_field = az._resolve_board_field("Bug")
                story_field = az._resolve_board_field("User Story")
                self.assertNotEqual(bug_field, story_field,
                                   "two different types resolved to the same board field")
                self.assertEqual(az._resolve_board_field("Bug"), bug_field,
                                "re-resolving the same type did not hit the process cache")
            finally:
                if old_xdg is None:
                    os.environ.pop("XDG_CACHE_HOME", None)
                else:
                    os.environ["XDG_CACHE_HOME"] = old_xdg


class AzureCreateType(unittest.TestCase):
    """`create_spec`'s `--type` argv — the resolved chain, never `self.work_item_type`, the
    single per-repo default that only `_board_field_for_read`'s optimisation still reads."""

    @staticmethod
    def _stubbed(**kwargs) -> tuple[AzureBoardsBackend, list]:
        """A backend whose `az` calls are recorded rather than shelled out — `create_spec`'s
        argv is the only thing either case reads."""
        az = AzureBoardsBackend("org", "proj", AZ_STATES, ".", area_path="Proj\\Area", **kwargs)
        calls: list[list[str]] = []
        az._az = lambda action, *argv, expect="object": (calls.append(list(argv)) or {"id": 1})
        az._az_patch = lambda action, item_id, ops: None
        return az, calls

    def test_a_resolved_type_key_reaches_type_argv(self):
        incidente = {"description": "d", "azure": "Bug"}
        az, calls = self._stubbed(types={"incidente": incidente})
        doc = _case_doc("alpha")
        close = doc.index("\n---\n")
        typed = doc[:close] + "\nworkItemType: incidente" + doc[close:]
        az.create_spec("plans", "alpha.md", typed)
        self.assertEqual(_type_argv(calls[-1]), "Bug")

    def test_no_declared_type_falls_through_to_az_spec_type(self):
        az, calls = self._stubbed()
        az.create_spec("plans", "beta.md", _case_doc("beta"))
        self.assertEqual(_type_argv(calls[-1]), AZ_SPEC_TYPE)


class DeclaredTag(unittest.TestCase):
    """Both halves of the reserved prefix: a rendered name and the discovery tag are
    filtered out, and an ordinary tag that merely CONTAINS the prefix is not."""

    CASES = (
        (["a", "spec:built", "quenching-spec"], "quenching-spec", ["a"],
         "the rendering and the discovery tag are both the tool's, never the spec's"),
        (["a", "b"], None, ["a", "b"], "no discovery tag declared filters only the prefix"),
        (["not-spec:built"], None, ["not-spec:built"],
         "the prefix is a PREFIX — a name merely containing it is the spec's own"),
        ([], "quenching-spec", [], "nothing declared filters to nothing"),
    )

    def test_each_case(self):
        for names, tag, want, label in self.CASES:
            with self.subTest(case=label):
                self.assertEqual(declared_tags(names, tag), want)


class LabelReconciliation(unittest.TestCase):
    """`reconcile_label_set` against the cases that decide whether it may ship: a label
    outside the `spec:` prefix survives untouched — a human's own label is never this
    tool's to touch — a stale `spec:` label a stage regression left behind is dropped, and
    one the document newly earns is added, all in the one pass a PATCH can afford."""

    CASES = {
        "foreign label survives, spec: labels replaced": (
            ["bug", "spec:ranked"], ["spec:ranked", "spec:approved"],
            ["bug", "spec:ranked", "spec:approved"]),
        "stale spec: label dropped": (
            ["spec:ranked", "spec:built"], ["spec:ranked"],
            ["spec:ranked"]),
        "nothing under the prefix is a no-op": (
            ["help wanted"], [], ["help wanted"]),
        "every spec: label sheds when the document sheds every record": (
            ["spec:ranked", "spec:approved"], [], []),
    }

    def test_each_case(self):
        for label, (current, desired, want) in self.CASES.items():
            with self.subTest(case=label):
                self.assertEqual(reconcile_label_set(current, desired), want)


class ResolveRepoIds(unittest.TestCase):
    """`_resolve_repo_ids` — resolved once, cached cross-process like the project's own name,
    and a name that does not resolve refuses rather than silently skipping the link."""

    def _isolated_cache(self):
        tmp = tempfile.TemporaryDirectory()
        old_xdg = os.environ.get("XDG_CACHE_HOME")
        os.environ["XDG_CACHE_HOME"] = tmp.name
        self.addCleanup(tmp.cleanup)
        if old_xdg is None:
            self.addCleanup(os.environ.pop, "XDG_CACHE_HOME", None)
        else:
            self.addCleanup(os.environ.__setitem__, "XDG_CACHE_HOME", old_xdg)

    def test_resolves_and_caches_the_pair(self):
        self._isolated_cache()
        az = AzureBoardsBackend("test-org-5-1", "test-proj-5-1", AZ_STATES, ".",
                                repository="the-repo")
        calls = []
        az._az_raw = lambda action, *argv, expect="object": (
            calls.append(argv) or {"id": "R1", "project": {"id": "P1"}})
        self.assertEqual(az._resolve_repo_ids(), ("P1", "R1"))
        self.assertEqual(len(calls), 1)
        # A second call hits the cross-process cache — no second `az` call.
        self.assertEqual(az._resolve_repo_ids(), ("P1", "R1"))
        self.assertEqual(len(calls), 1, "re-resolving the same repository called `az` again")

    def test_an_unresolvable_repository_refuses_rather_than_skipping_silently(self):
        self._isolated_cache()
        az = AzureBoardsBackend("test-org-5-1b", "test-proj-5-1b", AZ_STATES, ".",
                                repository="nonesuch")
        az._az_raw = lambda action, *argv, expect="object": {}
        with self.assertRaises(BackendRefusal) as ctx:
            az._resolve_repo_ids()
        self.assertEqual(ctx.exception.err.get("code"), "sp-az-repo-unresolved")


class ArtifactUrl(unittest.TestCase):
    """`azure_artifact_url` — the fixed vstfs encoding, one scheme per kind. `pr` is not a
    kind this function admits at all (## Design): the `PullRequestId` scheme names an Azure
    Repos pull request, and this plugin's `pr`/`merge.pr` records always name a `github` one."""

    def test_branch_gets_the_ref_scheme_and_the_gb_prefix(self):
        self.assertEqual(azure_artifact_url("branch", "P", "R", "plan/alpha"),
                         "vstfs:///Git/Ref/P%2FR%2FGBplan/alpha")

    def test_commit_gets_the_commit_scheme_and_no_prefix(self):
        self.assertEqual(azure_artifact_url("commit", "P", "R", "abc123"),
                         "vstfs:///Git/Commit/P%2FR%2Fabc123")

    def test_pr_is_not_an_admitted_kind(self):
        with self.assertRaises(KeyError):
            azure_artifact_url("pr", "P", "R", "1")


class LinkNewArtifacts(unittest.TestCase):
    """`_link_new_artifacts` — attempted only for what THIS write actually changed, diffed
    against the pre-write `info` every caller already hands `write_spec`. No network: `_git`
    is stubbed at the module level, and `_link_artifact`'s own `az` call is recorded rather
    than shelled out."""

    def _stubbed(self, grep_hits: dict[str, str]):
        az = AzureBoardsBackend("test-org-5-2", "test-proj-5-2", AZ_STATES, ".",
                                repository="the-repo")
        az._resolve_repo_ids = lambda: ("P1", "R1")
        linked: list[tuple[str, str]] = []
        az._az_patch = lambda action, item_id, ops: (
            linked.append((ops[0]["value"]["url"], action)) or None)
        import quenching.specs.backends.azure as azure_module
        real_git = azure_module._git
        azure_module._git = lambda cwd, *argv: grep_hits.get(argv[argv.index("--grep") + 1], "")
        self.addCleanup(setattr, azure_module, "_git", real_git)
        return az, linked

    def test_a_newly_stamped_branch_is_linked_once(self):
        az, linked = self._stubbed({})
        old = {"frontmatter": {"branch": None}, "tasks": []}
        fresh = {"frontmatter": {"branch": {"base": "develop", "work": "plan/alpha"}},
                "tasks": []}
        az._link_new_artifacts(1, old, fresh)
        self.assertEqual(len(linked), 1)
        self.assertIn("GBplan/alpha", linked[0][0])

    def test_an_unchanged_branch_is_never_relinked(self):
        az, linked = self._stubbed({})
        same = {"branch": {"base": "develop", "work": "plan/alpha"}}
        az._link_new_artifacts(1, {"frontmatter": same, "tasks": []},
                               {"frontmatter": same, "tasks": []})
        self.assertEqual(linked, [])

    def test_a_newly_recorded_task_subject_resolves_and_links_its_commit(self):
        subject = "plan/alpha: 1.1 Do the thing"
        az, linked = self._stubbed({subject: "deadbeef" * 5})
        old = {"frontmatter": {}, "tasks": [{"id": "1.1", "subject": None}]}
        fresh = {"frontmatter": {}, "tasks": [{"id": "1.1", "subject": subject}]}
        az._link_new_artifacts(1, old, fresh)
        self.assertEqual(len(linked), 1)
        self.assertIn("deadbeef" * 5, linked[0][0])

    def test_a_subject_that_does_not_resolve_in_this_checkout_links_nothing(self):
        subject = "plan/alpha: 1.1 Do the thing"
        az, linked = self._stubbed({})   # `_git` returns "" — nothing resolves
        old = {"frontmatter": {}, "tasks": [{"id": "1.1", "subject": None}]}
        fresh = {"frontmatter": {}, "tasks": [{"id": "1.1", "subject": subject}]}
        az._link_new_artifacts(1, old, fresh)
        self.assertEqual(linked, [])

    def test_no_repository_declared_means_write_spec_never_calls_this_at_all(self):
        # `write_spec` itself gates on `self.repository` before calling `_link_new_artifacts`
        # — proved here as the constructor default, the property every other case in this
        # class relies on `repository="the-repo"` to opt out of.
        az = AzureBoardsBackend("test-org-5-2b", "test-proj-5-2b", AZ_STATES, ".")
        self.assertIsNone(az.repository)


if __name__ == "__main__":
    unittest.main()
