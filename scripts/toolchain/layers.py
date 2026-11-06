"""Apply the `integration` marker to the modules whose tests drive git and subprocesses.

The heavy layer is named here, once, and applied at collection time by a plugin. Two alternatives
do not work in this repository: a `pytestmark` assignment would make every one of those modules
`import pytest`, which `test_suite.py::test_no_external_imports` refuses (the suite is stdlib plus
first-party); and a `conftest.py` is the surface `pf-fat-conftest` watches.

Load it with `-p scripts.toolchain.layers` — `scripts.toolchain.test` does. A plain `pytest` run
without the flag collects everything, which is the safe direction: a marker that fails to apply can
only make a run bigger, never silently smaller.
"""

from __future__ import annotations

import pathlib

INTEGRATION_MODULES = frozenset({
    "test_deploy.py",
    "test_git.py",
    "test_run_evals.py",
    "test_specs_epics.py",
    "test_specs_git_backend.py",
    "test_specs_portal.py",
})


def pytest_collection_modifyitems(config, items):
    """Mark every item of a listed module; the file name is the unit, not the test function."""
    import pytest

    for item in items:
        if pathlib.Path(str(item.path)).name in INTEGRATION_MODULES:
            item.add_marker(pytest.mark.integration)
