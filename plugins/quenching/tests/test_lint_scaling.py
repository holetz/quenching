"""`named_by_bodies` must cost the summed size of the command bodies, never the square of how
many commands there are.

The predicate decides which commands another command's body reaches BY NAME, and it used to do
it with one regex per (caller, target) pair — 34 commands meant 1,122 whole-body searches, and
the ~250-command surface `route-commands-without-always-on-descriptions` committed to would have
meant ~62,000. Measured before the rewrite: 27 commands in 185 ms, the same corpus duplicated 10×
in 20.2 s — a 109× rise for a 10× corpus, which is the shape of n².

A wall-clock assertion is the only honest way to hold that. Counting regex compilations or body
scans would assert the *shape* of today's implementation, which is exactly what the next rewrite
is entitled to change; the contract is the cost curve, not the technique. What makes it safe to
assert is that the check is a RATIO of two runs in the same process on the same machine — machine
speed, interpreter version and load cancel out of it, so nothing here is tuned to a laptop.

The ceiling is deliberately far from both sides it separates. Linear measures ~7-10× (the rewrite,
this tree), quadratic ~97-109× (the original). At 30× a run has to be three times worse than
linear before it fails, and three times better than quadratic to pass — no regression that matters
can fit in that gap, and no scheduler hiccup can cross it.
"""

import pathlib
import time
import unittest

import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
from quenching.components.commands.lint import named_by_bodies
from quenching.components.surface import COMMANDS_DIR, discover_commands

PLUGIN_ROOT = pathlib.Path(__file__).resolve().parent.parent
FACTOR = 10                 # the synthetic corpus, as a multiple of the real one
RATIO_CEILING = 30.0        # between linear (~10×) and quadratic (~100×)
PREFIX = "quenching"
BEST_OF = 3                 # the fastest run of each corpus; a slow one is noise, never signal


def multiply(commands: list[dict], factor: int) -> list[dict]:
    """`factor` copies of the corpus, every command after the first copy renamed with a suffix.

    Suffixing rather than generating bodies keeps the synthetic corpus made of REAL command
    prose — the same method `## Design` measured with. Copy 0 keeps the original names, so every
    cross-reference the real bodies contain still resolves and the predicate has real work to do
    rather than an empty answer computed quickly.
    """
    return [dict(cmd, command=cmd["command"] if copy == 0 else f"{cmd['command']}-x{copy}")
            for copy in range(factor)
            for cmd in commands]


def fastest(commands: list[dict]) -> float:
    """Seconds of the quickest of `BEST_OF` runs over `commands`."""
    def once() -> float:
        start = time.perf_counter()
        named_by_bodies(commands, PREFIX)
        return time.perf_counter() - start
    return min(once() for _ in range(BEST_OF))


class NamedByBodiesScales(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.real = discover_commands(str(PLUGIN_ROOT / COMMANDS_DIR))

    def test_the_real_corpus_is_not_empty(self):
        """A corpus of zero commands would make every assertion below pass in no time at all."""
        self.assertGreater(len(self.real), 1, "the plugin's own commands/ tree read as empty")

    def test_ten_times_the_corpus_costs_far_less_than_a_hundred_times_the_time(self):
        big = multiply(self.real, FACTOR)
        self.assertEqual(len(big), len(self.real) * FACTOR)

        ratio = fastest(big) / fastest(self.real)
        self.assertLess(
            ratio, RATIO_CEILING,
            f"{FACTOR}x the commands cost {ratio:.1f}x the time — linear is ~{FACTOR}x and "
            f"quadratic ~{FACTOR ** 2}x, so this is the n-squared shape the generic-form-plus-set "
            "rewrite removed coming back")

    def test_the_synthetic_corpus_answers_the_same_question(self):
        """The 10× corpus is not one the predicate can answer trivially.

        Without this, an implementation that returned `{}` would pass the timing assertion above
        by doing nothing, which is the cheapest way to look linear. The suffixed copies keep the
        real bodies, so every name the real corpus resolves is still resolved in the big one —
        by MORE callers, since each of the ten copies of a caller names the same copy-0 target.
        """
        real = named_by_bodies(self.real, PREFIX)
        self.assertTrue(real, "the real corpus names nothing — the measurement proves nothing")

        big = named_by_bodies(multiply(self.real, FACTOR), PREFIX)
        for name, callers in real.items():
            self.assertLessEqual(callers, big.get(name, set()),
                                 f"{name}: the {FACTOR}x corpus lost a caller the real one found")


if __name__ == "__main__":
    unittest.main()
