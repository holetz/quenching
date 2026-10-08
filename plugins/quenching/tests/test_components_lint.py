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

import contextlib
import io
import json
import pathlib
import tempfile
import unittest
from types import SimpleNamespace

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.commands.lint import (
    UNSCOPED_TOOLS,
    _numbered_steps,
    _agent_grant_findings,
    _cq_call_findings,
    _step_criteria,
    cmd_lint,
    lint_agents,
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


def strict_findings(frontmatter: str) -> list[dict]:
    """Run the command lint against a real frontmatter file, preserving source syntax."""
    with tempfile.TemporaryDirectory() as tmp:
        path = pathlib.Path(tmp) / "command.md"
        path.write_text(f"---\n{frontmatter}\n---\n\nbody\n", encoding="utf-8")
        item = command("body\n")
        item["path"] = str(path)
        return [f for f in lint_command(item, BASE) if f["code"] == "sk-frontmatter-strict"]


class StrictFrontmatter(unittest.TestCase):
    def test_a_folded_scalar_swallowing_a_known_key_reports_the_key_and_line(self):
        found = strict_findings("description: >-\n  Trigger prose\n argument-hint: [input]\nallowed-tools: Read")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["key"], "argument-hint")
        self.assertEqual(found[0]["line"], 4)
        self.assertIn("align", found[0]["remedy"])

    def test_an_unquoted_nested_flow_sequence_reports_a_flat_or_quoted_remedy(self):
        found = strict_findings("description: trigger\nargument-hint: [ref [mainline]]")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["kind"], "nested-flow-sequence")
        self.assertIn("quote", found[0]["remedy"])

    def test_an_unquoted_plain_scalar_with_colon_space_reports_a_safe_form(self):
        found = strict_findings("description: Use when: this is explicit\nallowed-tools: Read")
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["kind"], "plain-colon-space")
        self.assertIn(">-", found[0]["remedy"])

    def test_the_plugin_command_surface_has_no_lint_errors(self):
        plugin_root = pathlib.Path(__file__).resolve().parent.parent
        output = io.StringIO()
        with contextlib.redirect_stdout(output):
            status = cmd_lint(SimpleNamespace(path=None, json=True), str(plugin_root))
        payload = json.loads(output.getvalue())
        errors = [f for f in payload["findings"] if f["severity"] == "error"]
        self.assertEqual(errors, [])  # first: a red gate names the finding, not just the status
        self.assertEqual(status, 0)
        self.assertEqual(payload["commandCount"], 58)


class StepCriterion(unittest.TestCase):
    def test_child_headings_under_workflow_are_steps_without_numbers(self):
        body = ("## Workflow\n\n### Probe\n\nRead the payload.\n\n"
                "### Report\n\nWrite the report.\n\n**Done when:** report exists.\n")
        self.assertEqual(_numbered_steps(body), ["### Probe", "### Report"])
        self.assertEqual(_step_criteria(body), (2, 1))

    def test_a_top_level_bullet_sequence_under_steps_is_operational(self):
        body = "## Steps\n\n- Probe the front.\n- Report the result.\n"
        self.assertEqual(_numbered_steps(body), ["- Probe the front.", "- Report the result."])

    def test_narrative_bullets_and_a_lone_bullet_are_not_steps(self):
        self.assertEqual(_numbered_steps("## Notes\n\n- A narrative note.\n- Another note.\n"), [])
        self.assertEqual(_numbered_steps("## Workflow\n\n- One sentence of context.\n"), [])


class GateAndGrantLint(unittest.TestCase):
    def _findings(self, body: str, allowed: str) -> list[dict]:
        item = command(body)
        item["frontmatter"]["allowed-tools"] = allowed
        return lint_command(item, BASE)

    def test_a_confirmation_gate_without_ask_user_question_is_an_error(self):
        found = [f for f in self._findings(
            "Present the plan. Wait for the user's confirmation before writing.", "Read, Write")
                 if f["code"] == "sk-prose-gate"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["severity"], "error")
        self.assertIn("AskUserQuestion", found[0]["remedy"])

    def test_a_fenced_git_call_without_a_matching_grant_is_an_error(self):
        found = [f for f in self._findings("```bash\ngit add -- file\n```",
                                            "Read, Bash(git status:*)")
                 if f["code"] == "sk-grant-gap"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["tool"], "git add")
        self.assertEqual(found[0]["line"], 2)
        self.assertIn("Bash(git add:*)", found[0]["remedy"])

    def test_historical_or_negative_confirmation_prose_is_not_a_gate(self):
        bodies = (
            "A previous run waited for confirmation; this report only describes it.",
            "Never ask for confirmation here; the operation is read-only.",
        )
        for body in bodies:
            with self.subTest(body=body):
                self.assertNotIn("sk-prose-gate",
                                 {f["code"] for f in self._findings(body, "Read")})


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


class BodySizeBudgetTests(unittest.TestCase):
    def _codes(self, body: str) -> set[str]:
        return {f["code"] for f in lint_command(command(body), BASE)}

    def test_a_body_over_the_budget_warns(self):
        found = [f for f in lint_command(command("x" * 13000), BASE) if f["code"] == "sk-body-size"]
        self.assertEqual(len(found), 1)
        self.assertEqual(found[0]["severity"], "warn")

    def test_a_body_under_the_budget_is_silent(self):
        self.assertNotIn("sk-body-size", self._codes("x" * 1000))

    def test_a_justified_opt_out_line_silences_it(self):
        body = "<!-- body-size: justified — one atomic procedure -->\n" + "x" * 13000
        self.assertNotIn("sk-body-size", self._codes(body))

    def test_the_budget_counts_bytes_not_characters(self):
        self.assertIn("sk-body-size", self._codes("é" * 7000))


class CqCallsAgainstTheParsers(unittest.TestCase):
    """A `cq` call in prose is checked against the pillar's real argparse, in commands and agents."""

    WHERE = {"command": "agent:x", "path": "agents/x.md"}

    def _codes(self, body):
        return [f["code"] for f in _cq_call_findings(body, self.WHERE)]

    def test_a_missing_required_option_is_a_flag_finding(self):
        found = _cq_call_findings("run `cq specs task --check 1.1` first", self.WHERE)
        self.assertEqual([f["code"] for f in found], ["sk-cq-flag"])
        self.assertEqual(found[0]["severity"], "error")
        self.assertEqual(found[0]["line"], 1)
        self.assertIn("--spec", found[0]["message"])

    def test_show_and_parallel_without_an_id_are_flag_findings(self):
        for call in ("cq specs show --task 1.1", "cq specs parallel --json"):
            found = _cq_call_findings(f"```bash\n{call}\n```\n", self.WHERE)
            self.assertEqual([f["code"] for f in found], ["sk-cq-flag"], call)
            self.assertIn("--spec", found[0]["message"])

    def test_show_and_parallel_with_an_id_are_clean(self):
        body = "```bash\ncq specs show 12 --task 1.1\ncq specs parallel --spec 12\ncq specs status\n```\n"
        self.assertEqual(self._codes(body), [])

    def test_an_unknown_flag_is_a_flag_finding(self):
        self.assertEqual(self._codes("`cq specs show --spec <id> --nope`"), ["sk-cq-flag"])

    def test_an_unknown_verb_is_named(self):
        found = _cq_call_findings("`cq specs bogus`", self.WHERE)
        self.assertEqual([f["code"] for f in found], ["sk-cq-unknown-verb"])
        self.assertIn("bogus", found[0]["message"])

    def test_a_correct_call_is_clean_inline_and_fenced(self):
        body = "`cq specs show --spec <id> --json`\n\n```bash\ncq --root . specs status --spec 1\n```\n"
        self.assertEqual(self._codes(body), [])

    def test_a_negated_line_is_ignored(self):
        self.assertEqual(self._codes("never run `cq specs bogus`"), [])

    def test_no_before_another_noun_negates_nothing(self):
        self.assertEqual(self._codes("When no reviewer answered `cq specs bogus` it stamps."), ["sk-cq-unknown-verb"])

    def test_never_skip_is_a_double_negation_that_requires_the_call(self):
        self.assertEqual(self._codes("Never skip `cq specs bogus` once done."), ["sk-cq-unknown-verb"])

    def test_do_not_skip_is_a_double_negation_that_requires_the_call(self):
        self.assertEqual(self._codes("Do not skip `cq specs bogus` once done."), ["sk-cq-unknown-verb"])

    def test_no_right_before_the_span_still_negates(self):
        for line in ("there is no `cq specs bogus` grant", "it is no longer `cq specs bogus`"):
            self.assertEqual(self._codes(line), [], line)

    def test_no_longer_before_a_verb_negates(self):
        for line in ("Do that, no longer call `cq specs bogus` here", "we no longer run `cq specs bogus`"):
            self.assertEqual(self._codes(line), [], line)

    def test_no_more_before_a_verb_negates(self):
        for line in ("we no more run `cq specs bogus`", "it will no more call `cq specs bogus`"):
            self.assertEqual(self._codes(line), [], line)

    def test_a_bare_skip_still_negates(self):
        self.assertEqual(self._codes("the runner skips `cq specs bogus`"), [])

    def test_a_span_that_only_names_the_verb_cites_it(self):
        self.assertEqual(self._codes("the tick is `cq specs task --check`"), [])

    def test_a_fenced_call_continued_with_a_backslash_is_one_call(self):
        body = "```bash\ncq specs show \\\n  --spec 1\n```\n"
        self.assertEqual(self._codes(body), [])


class AgentGrantGap(unittest.TestCase):
    WHERE = {"command": "agent:x", "path": "agents/x.md"}

    def test_a_cq_call_without_its_grant_is_a_gap(self):
        found = _agent_grant_findings("run `cq specs record 1 branch`", "Read, Bash(cq specs show:*)",
                                      self.WHERE)
        self.assertEqual([f["code"] for f in found], ["sk-agent-grant-gap"])
        self.assertEqual(found[0]["tool"], "cq specs record")

    def test_a_granted_call_and_an_unscoped_bash_are_clean(self):
        body = "`cq specs show --spec 1` and `git log -3`"
        self.assertEqual(_agent_grant_findings(body, "Bash(cq specs show:*), Bash(git log:*)",
                                               self.WHERE), [])
        self.assertEqual(_agent_grant_findings(body, "Bash, Read", self.WHERE), [])

    def test_a_line_that_says_the_agent_does_not_run_the_verb_is_clean(self):
        for body in ("The steward does not run `cq specs record`.",
                     "It skips the command's `cq specs record` stamp.",
                     "It cannot call `cq specs record`."):
            self.assertEqual(_agent_grant_findings(body, "Read", self.WHERE), [], body)

    def test_a_real_call_on_a_line_with_a_loose_negation_is_still_a_gap(self):
        for body in ("It runs `cq specs record 1 branch` without asking.",
                     "It skips the check. Then run `cq specs record 1 branch`.",
                     "Never mind: run `cq specs record 1 branch`."):
            found = _agent_grant_findings(body, "Read", self.WHERE)
            self.assertEqual([f["code"] for f in found], ["sk-agent-grant-gap"], body)

    def test_negation_is_adjacent_wrapped_lines_and_abbreviations_included(self):
        for body in ("The steward never\n`cq specs record`s anything.",
                     "Never run task 3.1's `cq specs record` yourself.",
                     "Never stamp a record, e.g. `cq specs record 1 pr`.",
                     "It holds no `cq specs record` grant."):
            self.assertEqual(_agent_grant_findings(body, "Read", self.WHERE), [], body)
        for body in ("Without a PR yet, open it with `gh pr create --base main`.",
                     "When the store cannot answer, retry `cq specs record 1 pr`."):
            found = _agent_grant_findings(body, "Read", self.WHERE)
            self.assertEqual([f["code"] for f in found], ["sk-agent-grant-gap"], body)

    def test_an_option_before_the_verb_falls_outside_the_grant(self):
        for tools, body in (("Bash(cq specs show:*)", "`cq --root <wt> specs show --spec 1 --full`"),
                            ("Bash(cq specs show:*)", "`cq specs --root <wt> show --spec 1`"),
                            ("Bash(git status:*)", "`git -C <wt> status --porcelain`")):
            found = _agent_grant_findings(body, tools, self.WHERE)
            self.assertEqual([f["code"] for f in found], ["sk-agent-grant-gap"], body)
            self.assertIn("option before its verb", found[0]["message"], body)

    def test_an_option_after_the_verb_stays_inside_the_grant(self):
        for tools, body in (("Bash(cq specs show:*)", "`cq specs show --spec 1 --full`"),
                            ("Bash(git status:*)", "`git status --porcelain`")):
            self.assertEqual(_agent_grant_findings(body, tools, self.WHERE), [], body)

    def test_a_missing_grant_and_a_displaced_option_on_one_verb_are_both_reported(self):
        body = "`cq --root <wt> specs show --spec 1` and `cq specs show --spec 2`"
        self.assertEqual(len(_agent_grant_findings(body, "Bash(cq specs show:*)", self.WHERE)), 1)
        body = "`cq --root <wt> specs show --spec 1` and `cq specs record 1 pr`"
        self.assertEqual(len(_agent_grant_findings(body, "Bash(cq specs show:*)", self.WHERE)), 2)

    def test_lint_agents_reads_the_agents_folder(self):
        with tempfile.TemporaryDirectory() as root:
            agents = pathlib.Path(root, "agents")
            agents.mkdir()
            (agents / "a.md").write_text(
                "---\nname: a\ntools: Read, Bash(cq specs task:*)\n---\n"
                "Run `cq specs task --check 1.1` then `cq specs record 1 branch`.\n", encoding="utf-8")
            codes = sorted(f["code"] for f in lint_agents(root, root))
        self.assertEqual(codes, ["sk-agent-grant-gap", "sk-cq-flag"])

    def test_a_bash_pattern_in_disallowed_tools_is_an_error(self):
        with tempfile.TemporaryDirectory() as root:
            agents = pathlib.Path(root, "agents")
            agents.mkdir()
            (agents / "a.md").write_text(
                "---\nname: a\ntools: Bash(echo:*), Read\ndisallowedTools: Bash(x:*), Write\n---\nBody.\n",
                encoding="utf-8")
            (agents / "b.md").write_text(
                "---\nname: b\ntools: Bash(echo:*)\ndisallowedTools: Write\n---\nBody.\n",
                encoding="utf-8")
            found = lint_agents(root, root)
        self.assertEqual([(f["code"], f["command"]) for f in found],
                         [("sk-agent-disallowed-bash", "agent:a")])


if __name__ == "__main__":
    unittest.main()
