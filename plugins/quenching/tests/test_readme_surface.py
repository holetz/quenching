"""The README's command manual must list exactly the commands that exist in `commands/`.

The manual is a hand-written second copy of what `commands/**/*.md` already says, and a hand-written
copy of a surface assembled at session start drifts every time the surface moves. That is not a
hypothetical: the section carried thirteen `###` blocks naming skills the plugin retired, listed
`/communications:teams:create` — an invented example nobody ever shipped — and omitted three real
commands, while its own heading claimed a count written from memory.

An inventory like this only earns its place when the count is a property of the structure rather
than a sentence, and when a machine holds the lockstep. The assertion lives here, in the suite, and
not as a line in CLAUDE.md's verification block: that block already runs `unittest discover -s
tests`, so this costs the harness no new line, and a set comparison names the command that drifted
where a shell `diff` of two substitutions can only say that something did.

The manual's span is `## The <n> commands` through `## Install`, so the count written into that
heading is free to change without touching this test, and a front documented in its own `## `
section inside that span — as the `specs` flow is — still counts as listed.
"""

import pathlib
import re
import unittest

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
COMMANDS = PLUGIN_ROOT / "commands"
README = PLUGIN_ROOT / "README.md"

MANUAL_OPENS = re.compile(r"^## The .* commands\s*$", re.MULTILINE)
MANUAL_CLOSES = re.compile(r"^## Install\s*$", re.MULTILINE)
INVOCABLE = re.compile(r"`(/[a-z][a-z:-]*)`")
EXPECTED_COMMAND_COUNT = 47


def _commands_on_disk() -> set[str]:
    """`commands/knowledge/add.md` is `/quenching:knowledge:add` — the path IS the identity."""
    return {"/quenching:" + path.relative_to(COMMANDS).with_suffix("").as_posix().replace("/", ":")
            for path in COMMANDS.rglob("*.md")}


def _manual_span(text: str) -> str:
    opens = MANUAL_OPENS.search(text)
    if opens is None:
        raise AssertionError("README.md carries no `## The <n> commands` heading")
    rest = text[opens.end():]
    closes = MANUAL_CLOSES.search(rest)
    return rest if closes is None else rest[:closes.start()]


class ReadmeManualMatchesTheSurface(unittest.TestCase):

    def test_the_manual_lists_exactly_the_commands_on_disk(self):
        listed = set(INVOCABLE.findall(_manual_span(README.read_text(encoding="utf-8"))))
        on_disk = _commands_on_disk()
        self.assertEqual(len(on_disk), EXPECTED_COMMAND_COUNT,
                         "surface count changed; update the catalog and this assertion")
        self.assertEqual(on_disk - listed, set(), "commands on disk the README manual never lists")
        self.assertEqual(listed - on_disk, set(), "commands the README manual names that do not exist")

    def test_the_check_can_fail(self):
        """A green that could not go red is not evidence — so prove this one discriminates.

        Over a synthetic manual, not the real one: this must hold whether or not README.md happens
        to be correct today, and reading the real file would make the proof depend on the very
        thing the other test is asserting.
        """
        real = sorted(_commands_on_disk())[0]
        fake = "/quenching:" + "invented:command"
        synthetic = (f"## The 2 commands\n\n"
                     f"| command | what it does |\n"
                     f"| `{fake}` | a command nobody ships |\n\n"
                     f"## Install\n\n`{real}` — outside the manual's span, so it does not count.\n")

        listed = set(INVOCABLE.findall(_manual_span(synthetic)))
        self.assertEqual(listed, {fake})
        self.assertIn(real, _commands_on_disk() - listed)
        self.assertIn(fake, listed - _commands_on_disk())

    def test_the_span_stops_at_install_and_not_at_an_inner_heading(self):
        span = _manual_span("## The 9 commands\n\nkept\n\n## The specs flow\n\nalso kept\n"
                            "\n## Install\n\ndropped\n")
        self.assertIn("kept", span)
        self.assertIn("also kept", span)
        self.assertNotIn("dropped", span)
