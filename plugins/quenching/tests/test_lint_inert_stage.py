"""The five rules `named_by_bodies` and `sk-inert-stage` decide, each with a case that dies
when that rule is broken — the successor to the five synthetic `/docs:*` cases the retired
components `selftest` carried.

Why a synthetic corpus rather than the golden. The golden captures the REAL plugin surface, and
on that surface no command carrying `disable-model-invocation: true` is reached by name from any
body, so `sk-inert-stage` — the only finding `named_by_bodies` can produce — never fires. The
mutation pass recorded in `.knowledge/standards/quality/selftest-mutation.md` §The third pass
measured the consequence: of the seven mutations the retired selftest killed, five survived the
suite that replaced it, three of them while demonstrably moving the predicate's return. A rule
whose only witness is a finding the corpus cannot raise has no witness at all.

So the corpus here is built to sit ON the threshold the real surface stays clear of: every
typed-only command below is one caller away from being inert, which is what makes each arm of
the predicate observable in isolation. It is fixture data, not a sample of the surface — the
real one is measured by `test_golden.py` and `test_lint_scaling.py`, which answer different
questions (findings byte-for-byte, and cost curve).
"""

import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.commands.lint import lint_command, named_by_bodies

PREFIX = "qx"
BASE = "/plugin"

# A description with no quoted trigger and no `Not for:` boundary. Both routing codes fire on
# it — WHEN the description is resident. Shared by the typed-only and the routable case below
# so the only difference between them is `disable-model-invocation`, which is the whole point:
# the residency gate, not the prose, has to be what separates their findings.
UNROUTABLE_DESCRIPTION = "Does a thing to the tree and reports what it did."

# One citation per paragraph, and the paragraphs matter: `SKILL_TOOL_WINDOW` reads a line
# TOGETHER WITH its neighbours, so a "Skill tool" mention one line away would put the registry
# citation inside the adjacent arm's reach too — and a corpus where both arms answer for the
# same name cannot tell which one was deleted. Measured: a first draft that wrapped "the Skill
# / tool actually takes" onto the line under the registry citation let `drop the registry arm`
# survive the whole suite.
CONDUCTOR_BODY = """\
Stage 1 hands off to `qx:stage:registry`, in the bare registry form.

Stage 2 chains into /qx:stage:adjacent through the Skill tool.

Stage 3 is documented for a reader as /qx:stage:slashed — a citation, not a call.
"""

# Its own name, in the registry form, inside its own body — a body that documents what it
# itself does. Without the self-reference guard this reads as a command reaching itself.
SELF_NAMING_BODY = "This command, `qx:stage:selfnamed`, rewrites the tree in place.\n"


def command(name: str, body: str = "", *, typed_only: bool = False,
            description: str = "Trigger on \"do the thing\". Not for: anything else.") -> dict:
    """One row of the shape `discover_commands` returns, with only the keys `lint_command`
    reads. Built by hand rather than written to a tmpdir: the rules under test are decided
    from the parsed row, so a filesystem round-trip would add a second thing that can fail."""
    frontmatter = {"description": description}
    if typed_only:
        frontmatter["disable-model-invocation"] = "true"
    return {
        "command": name,
        "path": f"{BASE}/commands/{name.lstrip('/').replace(':', '/')}.md",
        "frontmatter": frontmatter,
        "anomalies": [],
        "hooks": {},
        "hooksParsed": True,
        "body": body,
        "bodyLines": len(body.splitlines()),
    }


CONDUCTOR = command("/routed:conductor", CONDUCTOR_BODY)
SURFACE = [
    CONDUCTOR,
    command("/stage:registry", typed_only=True),
    command("/stage:adjacent", typed_only=True),
    command("/stage:slashed", typed_only=True),
    command("/stage:selfnamed", SELF_NAMING_BODY, typed_only=True),
]


def codes(cmd: dict, named_by: set[str] | None = None) -> list[str]:
    return [f["code"] for f in lint_command(cmd, BASE, named_by)]


class NamedByBodies(unittest.TestCase):
    """Each test names the mutation it kills — that is the claim being made about it."""

    def setUp(self):
        self.reached = named_by_bodies(SURFACE, PREFIX)

    def test_the_registry_form_reaches_a_command(self):
        """Kills: drop the registry arm."""
        self.assertEqual(self.reached.get("/stage:registry"), {"/routed:conductor"})

    def test_a_name_beside_a_skill_tool_line_reaches_a_command(self):
        """Kills: drop the Skill-tool arm.

        The name is written `/qx:stage:adjacent` — the leading slash that disqualifies the
        registry form is not a disqualifier here, which is what makes this a second arm rather
        than a looser spelling of the first."""
        self.assertEqual(self.reached.get("/stage:adjacent"), {"/routed:conductor"})

    def test_a_leading_slash_away_from_a_skill_tool_line_reaches_nothing(self):
        """Kills: drop the leading-slash exclusion.

        `/qx:stage:slashed` appears in the same body as the two hits above and is a citation
        for a human, not a call. Both arms have to decline it: the registry arm on the slash,
        the adjacent arm because no Skill-tool line is within a line of it."""
        self.assertNotIn("/stage:slashed", self.reached)

    def test_a_body_naming_itself_does_not_reach_itself(self):
        """Kills: drop the self-reference guard."""
        self.assertNotIn("/stage:selfnamed", self.reached)

    def test_only_the_names_the_bodies_carry_are_reached(self):
        """The union is the wider read, not an open one: a predicate that returned every
        command would satisfy three of the four assertions above."""
        self.assertEqual(set(self.reached), {"/stage:registry", "/stage:adjacent"})


class InertStage(unittest.TestCase):
    def test_a_typed_only_command_reached_by_name_is_reported_inert(self):
        self.assertIn("sk-inert-stage",
                      codes(command("/stage:registry", typed_only=True), {"/routed:conductor"}))

    def test_the_same_command_no_caller_reaches_is_not(self):
        """Kills: ungate `sk-inert-stage` from the caller set.

        `disable-model-invocation: true` is a legitimate state — it is how a stage says the
        human types it. The defect is only ever the pair: typed-only AND named by a body."""
        typed_only = command("/stage:registry", typed_only=True)
        self.assertNotIn("sk-inert-stage", codes(typed_only, None))
        self.assertNotIn("sk-inert-stage", codes(typed_only, set()))


class ResidencyGate(unittest.TestCase):
    """`description_is_resident` scopes the two routing codes. Neither the real surface nor the
    golden raises them, so both directions of the gate need a case here."""

    def test_a_resident_description_with_no_trigger_and_no_boundary_raises_both(self):
        """Kills: `description_is_resident` → always `False`."""
        found = codes(command("/routed:bare", description=UNROUTABLE_DESCRIPTION))
        self.assertIn("sk-trigger-position", found)
        self.assertIn("sk-no-boundary", found)

    def test_the_same_description_on_a_typed_only_command_raises_neither(self):
        """Kills: `description_is_resident` → always `True`.

        Nothing routes from a description that is not in context, so judging its routing prose
        is `lint` reporting a defect the command cannot have."""
        found = codes(command("/stage:bare", description=UNROUTABLE_DESCRIPTION,
                              typed_only=True))
        self.assertNotIn("sk-trigger-position", found)
        self.assertNotIn("sk-no-boundary", found)


if __name__ == "__main__":
    unittest.main()
