"""`scripts/verify_repo.sh` pins the timezone before anything runs, so every tier of the gate
renders dates the same way on a laptop, in an agent session and in CI."""

import pathlib
import re
import unittest

SCRIPT = pathlib.Path(__file__).resolve().parent.parent.parent / "scripts" / "verify_repo.sh"


class TheGateEnvironment(unittest.TestCase):
    def test_tz_is_exported_as_utc_before_the_first_check(self):
        text = SCRIPT.read_text(encoding="utf-8")
        pin = re.search(r"^export TZ=UTC$", text, re.M)
        self.assertIsNotNone(pin, "verify_repo.sh no longer exports TZ=UTC")
        self.assertLess(pin.start(), text.index("pytest_args="))
        self.assertLess(pin.start(), text.index("run_check \""))


if __name__ == "__main__":
    unittest.main()
