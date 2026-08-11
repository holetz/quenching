"""Put `assets/bin` on `sys.path` so the tests import `quenching.common.*` the way a pillar does.

`unittest discover -s tests` inserts the start directory — this one — at the head of `sys.path`
and nothing else, so a plain `import quenching.common...` from a test module cannot resolve. The
package is a PEP 420 namespace package with no `__init__.py` and none is to be added, so the fix
has to be a path entry rather than a package relationship: importing this module from a test adds
the one directory that makes `quenching` importable. Python caches it, so the two test modules pay
for it once.

Not named `test*.py`, therefore never collected as a test.
"""

import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin"))
