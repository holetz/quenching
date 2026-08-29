"""`sk-unscoped-bash` reads the body its own remedy points at.

The finding used to say *"scope it to the commands the workflow runs, or state the reason in the
body"* while reading only `allowed-tools`. The second half of that remedy was unreachable: a body
that already stated the reason got the identical bytes as one nobody had looked at, so following
the advice changed nothing the check could see. That is the defect — not the warning, which is
correct in both cases, because the grant is the whole shell for the turn either way.

What the marker buys is a reader who can tell a deliberate grant from an unexamined one, and it is
a BOOLEAN on purpose: `marker_present` does not read the reason, judge it, or measure it. A check
that graded prose would be inventing a verdict it cannot support.

MUTATION PASS (2026-08-27, four mutations, each applied to `lint.py`, run, observed, reverted),
per `docs/standards/quality/selftest-mutation.md`. Run in both modes — this suite, and the
human `cq --root . components lint` arm over the real surface, where six bodies hold the grant and
none carries the marker:

| Mutation | Rule it attacks | This suite | Human arm |
| --- | --- | --- | --- |
| `marker_present` → always `True` | an unexamined grant is not priced | 6 failures | all six flip to the priced message |
| `marker_present` → always `False` | a stated reason IS observed | 3 failures | unchanged (none is priced) |
| drop the fence state | a quoted example does not price itself | 1 failure | unchanged (no body quotes it) |
| `startswith` → `in` | the marker is a line, not a mention | 1 failure | unchanged |

The human column is what makes the pass honest: three of the four mutations move nothing on the
real surface, so this fixture is their only witness — the same measurement
`selftest-mutation.md` §The third pass made about `named_by_bodies`.

The pass also graded the fixture, not only the code. `startswith` → `in` SURVIVED the first draft:
the near miss says `scoped` where the marker says `unrestricted`, so it contains no substring for
`in` to find, and `MENTIONED_BODY` had to be added to separate a line that IS the marker from a
sentence that names it. A rule with no case that fails without it is a rule nobody is holding.
"""

import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.commands.lint import (
    UNSCOPED_TOOLS,
    lint_command,
    marker_present,
    unscoped_marker,
)

TOOL = UNSCOPED_TOOLS[0]
MARKER = unscoped_marker(TOOL)
BASE = "/plugin"

PRICED_BODY = f"""\
# /qx:front:verb — does a thing

{MARKER} The workflow runs whatever the repo's own test command turns out to be, and that
is a fact about the target repository, not about this plugin.

Steps follow.
"""

UNPRICED_BODY = """\
# /qx:front:verb — does a thing

The workflow shells out. Steps follow.
"""

# `scoped` where the marker says `unrestricted`: the near miss that a substring test, or a
# reader skimming for the word "Why", would take for the real thing.
NEAR_MISS_BODY = """\
# /qx:front:verb — does a thing

**Why `Bash` is scoped here.** It is not — but this line is not the marker either.
"""

# The marker mid-sentence: prose ABOUT the marker, not a line that is one. A substring test
# takes this for the real thing, which is why the near miss above is not enough on its own —
# measured: with `startswith` relaxed to `in`, this is the only case that fails.
MENTIONED_BODY = f"""\
# /qx:front:verb — does a thing

A body that opens a line with {MARKER} prices its grant; this sentence only says so.
"""

FENCED_BODY = f"""\
# /qx:front:verb — does a thing

The mould shows what pricing looks like:

```markdown
{MARKER} The reason goes here.
```

This body quotes the marker; it does not write one.
"""


def command(body: str) -> dict:
    """One row of the shape `discover_commands` returns, holding the unscoped grant."""
    return {
        "command": "/front:verb",
        "path": f"{BASE}/commands/front/verb.md",
        "frontmatter": {"description": 'Trigger on "do the thing". Not for: anything else.',
                        "allowed-tools": f"Read, {TOOL}"},
        "anomalies": [],
        "hooks": {},
        "hooksParsed": True,
        "body": body,
        "bodyLines": len(body.splitlines()),
    }


def unscoped(body: str) -> dict:
    """The one `sk-unscoped-bash` finding for a body, which must always be present."""
    found = [f for f in lint_command(command(body), BASE) if f["code"] == "sk-unscoped-bash"]
    assert len(found) == 1, f"expected exactly one sk-unscoped-bash, got {len(found)}"
    return found[0]


class MarkerPredicate(unittest.TestCase):
    def test_a_line_opening_with_the_marker_prices_the_grant(self):
        """Kills: `marker_present` → always `False`."""
        self.assertTrue(marker_present(PRICED_BODY, TOOL))

    def test_a_body_that_says_nothing_does_not(self):
        """Kills: `marker_present` → always `True`."""
        self.assertFalse(marker_present(UNPRICED_BODY, TOOL))

    def test_a_near_miss_does_not(self):
        """Kills: any test looser than the literal line — a reader skimming for "Why".

        `scoped` for `unrestricted` is one word apart from the marker and means the opposite
        of what the grant is."""
        self.assertFalse(marker_present(NEAR_MISS_BODY, TOOL))

    def test_the_marker_mentioned_mid_line_does_not(self):
        """Kills: `startswith` → `in`.

        The marker is a LINE, not a mention. Prose explaining the convention names it in
        passing, and a body that explains pricing has not priced anything."""
        self.assertFalse(marker_present(MENTIONED_BODY, TOOL))

    def test_the_marker_quoted_inside_a_fence_does_not(self):
        """Kills: drop the fence state.

        This repo's own moulds show the marker in a fenced example. A body that demonstrates
        what pricing looks like has not priced anything."""
        self.assertFalse(marker_present(FENCED_BODY, TOOL))

    def test_the_marker_is_derived_from_the_tool_name(self):
        """The literal is parameterised, so a second unscoped tool gets its marker for free
        instead of silently sharing Bash's."""
        self.assertIn(f"`{TOOL}`", MARKER)
        self.assertNotEqual(unscoped_marker(TOOL), unscoped_marker("Write"))


class FindingShape(unittest.TestCase):
    """The finding is reported in BOTH cases — the grant is the whole shell either way, and a
    check that fell silent on a priced body would be trading a report for a marker."""

    def test_both_bodies_still_raise_the_finding_at_warn(self):
        for label, body in (("priced", PRICED_BODY), ("unpriced", UNPRICED_BODY)):
            with self.subTest(label):
                found = unscoped(body)
                self.assertEqual(found["severity"], "warn")
                self.assertEqual(found["tool"], TOOL)

    def test_priced_is_carried_as_data_not_only_as_prose(self):
        """A JSON consumer decides on the field, never by matching the message text."""
        self.assertTrue(unscoped(PRICED_BODY)["priced"])
        self.assertFalse(unscoped(UNPRICED_BODY)["priced"])

    def test_the_unpriced_message_carries_the_exact_marker_to_write(self):
        """The remedy has to be followable from the message alone — that is the whole defect
        this spec closes."""
        self.assertIn(MARKER, unscoped(UNPRICED_BODY)["message"])

    def test_the_priced_message_claims_presence_and_nothing_about_quality(self):
        message = unscoped(PRICED_BODY)["message"]
        self.assertIn("whole shell", message)
        self.assertNotIn(MARKER, message)


if __name__ == "__main__":
    unittest.main()
