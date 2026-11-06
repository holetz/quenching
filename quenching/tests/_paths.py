"""Put `assets/bin` on `sys.path` so the tests import `quenching.common.*` the way a pillar does.

`unittest discover -s tests` inserts the start directory — this one — at the head of `sys.path`
and nothing else, so a plain `import quenching.common...` from a test module cannot resolve. The
package is a PEP 420 namespace package with no `__init__.py` and none is to be added, so the fix
has to be a path entry rather than a package relationship: importing this module from a test adds
the one directory that makes `quenching` importable. Python caches it, so the two test modules pay
for it once.

It also points `$QUENCHING_DENYLIST_FILE` at an empty file, so no test reads the machine's private
denylist: a test that needs denylist terms writes a fixture of its own.

**The temp root.** A run that did not come through the gate (`scripts/verify_repo.sh`) resolves one
here, through the same `scripts.toolchain.tmproot` the gate calls, and points `TMPDIR`/`TEMP`/`TMP`
at a per-run directory under it so workers, `git` children and every `tempfile` call share it. The
gate's own directory is adopted untouched: it exports :data:`tmproot.GATE_MARKER`, because it owns
the trap that removes it. This is the module every test imports first, so it runs before `tempfile`
caches its answer.

`repository_config` resolves this repository's own configuration the way the tool does: the
generic `.agents/quenching.json` first, then the legacy `.claude/quenching.json`.

**Git isolation.** Every `git` this suite starts reads this run's configuration and nothing of the
machine's: `GIT_CONFIG_GLOBAL` points at a file written under this run's temp root, the system file is
skipped, and the repository's own settings still win. Without it a developer's hooks,
`commit.gpgsign`, `init.defaultBranch` or `diff.external` leaks into a test; with it, a test that
needs a different value sets it on the repository it creates. Identity deliberately stays out of the
file: the suite sets `user.name`/`user.email` per repository, and a command-scope value would hide
what `test_identity_allowlist` is exercising.

Not named `test*.py`, therefore never collected as a test.
"""

import atexit
import os
import pathlib
import shutil
import sys
import tempfile

_REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))  # `scripts.toolchain` resolves however the suite was started
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent / "assets" / "bin"))

from scripts.toolchain import tmproot  # noqa: E402

# Throwaway repositories do not need durability, and a suite that ran one `fsync` per loose object
# measured 1,146 sync calls in the whole tree. The settings live in a *global file* of this run, not
# in `GIT_CONFIG_COUNT` pairs: command-scope configuration outranks a repository's own, and two
# tests set `core.autocrlf`/`init.defaultBranch` locally and read the value back. A global file is
# overridden by the repository, which is the precedence a test expects.
_GIT_CONFIG = """[core]
\tfsync = none
\tfsyncMethod = batch
[gc]
\tauto = 0
[init]
\tdefaultBranch = main
[commit]
\tgpgsign = false
[tag]
\tgpgsign = false
"""
if os.environ.get(tmproot.GATE_MARKER):
    _run_root = pathlib.Path(os.environ[tmproot.GATE_MARKER])
else:
    _resolution = tmproot.resolve()
    if _resolution.notice:
        print(_resolution.notice, file=sys.stderr, flush=True)
    _run_root = pathlib.Path(tempfile.mkdtemp(prefix=f"quenching-tests-{os.getpid()}-",
                                              dir=_resolution.path))
    atexit.register(shutil.rmtree, str(_run_root), True)
    tmproot.export(_run_root)

# Under the run root, so the gate's trap or this module's own atexit removes it with everything
# else the run wrote. It is written after the root resolves for exactly that reason.
_git_config = pathlib.Path(tempfile.mkdtemp(prefix="quenching-gitconfig-", dir=_run_root), "gitconfig")
_git_config.write_text(_GIT_CONFIG, encoding="utf-8")
os.environ["GIT_CONFIG_GLOBAL"] = str(_git_config)
os.environ["GIT_CONFIG_NOSYSTEM"] = "1"
# A caller's command-scope pairs would outrank the file and every repository's own config.
for _key in [key for key in os.environ
             if key == "GIT_CONFIG_COUNT" or key.startswith(("GIT_CONFIG_KEY_", "GIT_CONFIG_VALUE_"))]:
    del os.environ[_key]

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
