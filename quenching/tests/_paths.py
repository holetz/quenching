"""Put `assets/bin` on `sys.path` so the tests import `quenching.common.*` the way a pillar does.

`unittest discover -s tests` inserts the start directory — this one — at the head of `sys.path`
and nothing else, so a plain `import quenching.common...` from a test module cannot resolve. The
package is a PEP 420 namespace package with no `__init__.py` and none is to be added, so the fix
has to be a path entry rather than a package relationship: importing this module from a test adds
the one directory that makes `quenching` importable. Python caches it, so the two test modules pay
for it once.

It also points `$QUENCHING_DENYLIST_FILE` at an empty file, so no test reads the machine's private
denylist: a test that needs denylist terms writes a fixture of its own.

`repository_config` resolves this repository's own configuration the way the tool does: the
generic `.agents/quenching.json` first, then the legacy `.claude/quenching.json`.

Not named `test*.py`, therefore never collected as a test.
"""

import atexit
import os
import pathlib
import shutil
import sys
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin"))

_denylist_dir = tempfile.mkdtemp(prefix="quenching-test-denylist-")
atexit.register(shutil.rmtree, _denylist_dir, True)
_empty_denylist = pathlib.Path(_denylist_dir, "denylist.txt")
_empty_denylist.write_text("", encoding="utf-8")
os.environ["QUENCHING_DENYLIST_FILE"] = str(_empty_denylist)


def repository_config(root):
    """The repository's own configuration file: the generic home first, then the legacy one."""
    for home in (".agents", ".claude"):
        path = pathlib.Path(root) / home / "quenching.json"
        if path.is_file():
            return path
    raise FileNotFoundError(f"no .agents/quenching.json or .claude/quenching.json under {root}")
