"""The Windows branch of the process-group helper, driven on any host by patching `os.name`."""
import subprocess
import unittest
from unittest import mock

import _paths  # noqa: F401
import importlib

probe = importlib.import_module("quenching.codex.probe")


class GroupKwargs(unittest.TestCase):
    def test_posix_starts_a_new_session(self):
        with mock.patch.object(probe.os, "name", "posix"):
            self.assertEqual(probe.group_kwargs(), {"start_new_session": True})

    def test_windows_starts_a_new_process_group(self):
        flag = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 512)
        with mock.patch.object(probe.os, "name", "nt"), \
                mock.patch.object(subprocess, "CREATE_NEW_PROCESS_GROUP", flag, create=True):
            self.assertEqual(probe.group_kwargs(), {"creationflags": flag})


class Stop(unittest.TestCase):
    def test_windows_kills_the_tree_with_taskkill_and_waits(self):
        process = mock.Mock(pid=4321)
        with mock.patch.object(probe.os, "name", "nt"), \
                mock.patch.object(probe.subprocess, "run") as run:
            probe.stop(process)
        run.assert_called_once()
        self.assertEqual(run.call_args.args[0], ["taskkill", "/F", "/T", "/PID", "4321"])
        process.wait.assert_called_once()

    def test_posix_kills_the_group(self):
        process = mock.Mock(pid=4321)
        with mock.patch.object(probe.os, "name", "posix"), \
                mock.patch.object(probe.os, "killpg", create=True) as killpg:
            probe.stop(process)
        killpg.assert_called_once_with(4321, probe.signal.SIGKILL)
        process.wait.assert_called_once()

    def test_posix_tolerates_a_gone_group(self):
        process = mock.Mock(pid=4321)
        with mock.patch.object(probe.os, "name", "posix"), \
                mock.patch.object(probe.os, "killpg", side_effect=ProcessLookupError, create=True):
            probe.stop(process)
        process.wait.assert_called_once()


if __name__ == "__main__":
    unittest.main()
