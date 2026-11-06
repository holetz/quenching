"""The temp-root resolver: which candidate wins, why one is refused, and what it tells the human.

The filesystem itself is injected (`_mounts`, `_free_bytes`, `_dev_drives`), so every branch is
exercised on a machine that has neither a Windows Dev Drive nor a second tmpfs. The real machine's
own resolution is checked once, at the end, without assuming which candidate it lands on.
"""

from __future__ import annotations

import contextlib
import io
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from scripts.toolchain import tmproot  # noqa: E402

GIGABYTE = 2**30


class TempRootCase(unittest.TestCase):
    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.base = pathlib.Path(self._tmp.name)
        self.xdg = self.base / "runtime"
        self.xdg.mkdir()
        self.local = self.base / "local"
        self.local.mkdir()
        self._saved_tempdir = tempfile.tempdir

    def tearDown(self):
        tempfile.tempdir = self._saved_tempdir

    def mounts(self, *rows):
        return mock.patch.object(tmproot, "_mounts", return_value=list(rows))

    def room(self, size=2 * GIGABYTE):
        return mock.patch.object(tmproot, "_free_bytes", return_value=size)

    def dev_drives(self, *paths):
        return mock.patch.object(tmproot, "_dev_drives", return_value=[pathlib.Path(p) for p in paths])

    def test_the_explicit_override_wins_over_a_ram_candidate(self):
        with self.mounts((str(self.xdg), "tmpfs")), self.room():
            got = tmproot.resolve({tmproot.OVERRIDE: str(self.local),
                                   "XDG_RUNTIME_DIR": str(self.xdg)}, platform="linux")
        self.assertEqual(got.path, self.local)
        self.assertEqual(got.kind, "explicit")
        self.assertIsNone(got.notice)

    def test_an_explicit_override_that_cannot_be_used_fails_loudly(self):
        missing = self.base / "does-not-exist"
        with self.assertRaises(tmproot.TempRootError) as caught:
            tmproot.resolve({tmproot.OVERRIDE: str(missing)}, platform="linux")
        self.assertIn(tmproot.OVERRIDE, str(caught.exception))
        self.assertIn("does not exist", str(caught.exception))

    def test_xdg_runtime_dir_is_preferred_when_it_is_a_tmpfs_with_room(self):
        with self.mounts((str(self.xdg), "tmpfs"), ("/dev/shm", "tmpfs")), self.room():
            got = tmproot.resolve({"XDG_RUNTIME_DIR": str(self.xdg)}, platform="linux")
        self.assertEqual((got.path, got.kind, got.label), (self.xdg, "ram", "XDG_RUNTIME_DIR"))
        self.assertIsNone(got.notice)

    def test_a_disk_backed_xdg_runtime_dir_falls_through_to_dev_shm(self):
        with self.mounts((str(self.xdg), "ext4"), ("/dev/shm", "tmpfs")), self.room():
            got = tmproot.resolve({"XDG_RUNTIME_DIR": str(self.xdg)}, platform="linux")
        self.assertEqual(got.path, pathlib.Path("/dev/shm"))

    def test_a_tmpfs_without_room_is_refused(self):
        with self.mounts((str(self.xdg), "tmpfs"), ("/dev/shm", "tmpfs")), \
                mock.patch.object(tmproot, "_free_bytes", return_value=tmproot.MIN_FREE_BYTES - 1):
            got = tmproot.resolve({"XDG_RUNTIME_DIR": str(self.xdg)}, platform="linux")
        self.assertNotEqual(got.path, self.xdg)

    def test_no_ram_candidate_falls_back_to_disk_with_a_notice(self):
        system = pathlib.Path(tempfile.gettempdir())
        with self.mounts((str(self.xdg), "ext4"), ("/dev/shm", "ext4")):
            got = tmproot.resolve({"XDG_RUNTIME_DIR": str(self.xdg)}, platform="linux")
        self.assertEqual(got.path, system)
        self.assertEqual(got.kind, "disk")
        self.assertIn("NOTICE", got.notice)
        self.assertIn(str(system), got.notice)

    def test_a_windows_dev_drive_wins_over_local_app_data(self):
        drive = self.base / "devdrive"
        drive.mkdir()
        with self.dev_drives(drive), self.room():
            got = tmproot.resolve({"LOCALAPPDATA": str(self.local)}, platform="win32")
        self.assertEqual((got.path, got.label), (drive, "Dev Drive"))

    def test_local_app_data_inside_a_synced_folder_is_skipped(self):
        synced = self.base / "OneDrive" / "local"
        synced.mkdir(parents=True)
        with self.dev_drives():
            got = tmproot.resolve({"LOCALAPPDATA": str(synced)}, platform="win32")
        self.assertNotEqual(got.path, synced)
        self.assertIn("NOTICE", got.notice)

    def test_windows_local_app_data_outside_a_synced_folder_is_used(self):
        with self.dev_drives():
            got = tmproot.resolve({"LOCALAPPDATA": str(self.local)}, platform="win32")
        self.assertEqual((got.path, got.kind), (self.local, "disk"))
        self.assertIsNone(got.notice)

    def test_export_points_the_environment_and_tempfile_at_the_root(self):
        environ: dict[str, str] = {}
        tmproot.export(self.local, environ)
        self.assertEqual({key: environ[key] for key in tmproot.ENV_KEYS},
                         {key: str(self.local) for key in tmproot.ENV_KEYS})
        self.assertEqual(tempfile.tempdir, str(self.local))

    def test_apply_prints_the_notice_once(self):
        stream = io.StringIO()
        with self.mounts((str(self.xdg), "ext4"), ("/dev/shm", "ext4")):
            tmproot.apply({"XDG_RUNTIME_DIR": str(self.xdg)}, platform="linux", stream=stream)
        self.assertEqual(stream.getvalue().count("NOTICE"), 1)
        self.assertTrue(stream.getvalue().endswith("\n"))

    def test_the_cli_prints_a_writable_root(self):
        with contextlib.redirect_stdout(io.StringIO()) as out, \
                contextlib.redirect_stderr(io.StringIO()):
            code = tmproot.main([])
        self.assertEqual(code, 0)
        self.assertTrue(pathlib.Path(out.getvalue().strip()).is_dir())

    def test_the_cli_refuses_a_bad_override(self):
        with mock.patch.dict("os.environ", {tmproot.OVERRIDE: str(self.base / "nope")}):
            with contextlib.redirect_stderr(io.StringIO()) as err:
                self.assertEqual(tmproot.main([]), 2)
        self.assertIn(tmproot.OVERRIDE, err.getvalue())

    def test_this_machine_resolves_a_writable_root(self):
        got = tmproot.resolve()
        self.assertTrue(got.path.is_dir())
        self.assertTrue(tmproot._writable(got.path))


if __name__ == "__main__":
    unittest.main()
