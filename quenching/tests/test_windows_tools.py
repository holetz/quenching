"""O desvio do `az` no Windows, dirigido em qualquer host por `os.name` e `which` mockados."""
import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest import mock

import _paths  # noqa: F401
from quenching.common import doctor, tools
from quenching.deploy import tree


class SpawnArgv(unittest.TestCase):
    def test_fora_do_windows_o_argv_e_identidade(self):
        with mock.patch.object(tools.os, "name", "posix"):
            self.assertEqual(tools.spawn_argv(["az", "version"]), ["az", "version"])

    def test_outra_ferramenta_no_windows_nao_muda(self):
        with mock.patch.object(tools.os, "name", "nt"), \
                mock.patch.object(tools.shutil, "which") as which:
            self.assertEqual(tools.spawn_argv(["gh", "pr", "list"]), ["gh", "pr", "list"])
        which.assert_not_called()

    def test_no_windows_o_az_vira_o_python_do_cli_com_o_argv_intacto(self):
        launcher = r"C:\AzureCLI\wbin\az.cmd"
        with mock.patch.object(tools.os, "name", "nt"), \
                mock.patch.object(tools.shutil, "which", return_value=launcher), \
                mock.patch.object(tools.os.path, "isfile", return_value=True):
            argv = tools.spawn_argv(["az", "repos", "pr", "create", "--title", "A & B %TEMP%"])
        self.assertEqual(argv, [r"C:\AzureCLI\python.exe", "-IBm", "azure.cli",
                                "repos", "pr", "create", "--title", "A & B %TEMP%"])

    def test_sem_lancador_o_argv_fica_como_esta(self):
        with mock.patch.object(tools.os, "name", "nt"), \
                mock.patch.object(tools.shutil, "which", return_value=None):
            self.assertEqual(tools.spawn_argv(["az", "version"]), ["az", "version"])

    def test_sem_o_python_ao_lado_do_lancador_o_argv_fica_como_esta(self):
        with mock.patch.object(tools.os, "name", "nt"), \
                mock.patch.object(tools.shutil, "which", return_value=r"C:\CLI\wbin\az.cmd"), \
                mock.patch.object(tools.os.path, "isfile", return_value=False):
            self.assertEqual(tools.spawn_argv(["az", "version"]), ["az", "version"])

    def test_argv_vazio_nao_quebra(self):
        with mock.patch.object(tools.os, "name", "nt"):
            self.assertEqual(tools.spawn_argv([]), [])


class Doctor(unittest.TestCase):
    def test_o_doctor_acha_o_az_pelo_mesmo_which_do_spawn(self):
        def which(name):
            return r"C:\AzureCLI\wbin\az.cmd" if name == "az" else None

        with mock.patch.object(doctor.shutil, "which", side_effect=which):
            report = doctor.inspect_environment(".", config={"data": {"backend": "azure-boards"}})
        self.assertIn("az", [item["name"] for item in report["requirements"]])
        self.assertTrue(next(item for item in report["requirements"] if item["name"] == "az")["found"])


@unittest.skipUnless(os.name == "nt", "o cmd.exe só existe no Windows")
class LauncherArgv(unittest.TestCase):
    """O `cq.cmd` gerado entrega um argv acentuado ao Python sem trocar a codificação."""

    STUB = ("import json, sys\n"
            "sys.stdout.write(json.dumps(sys.argv[1:]))\n"  # ensure_ascii: a saída não depende da página
            "sys.exit(3)\n")

    def _run(self, *args):
        with tempfile.TemporaryDirectory() as root:
            (Path(root) / "bin").mkdir()
            (Path(root) / "assets" / "bin").mkdir(parents=True)
            (Path(root) / "bin" / "cq.cmd").write_bytes(tree._VENDOR_CMD.encode())
            (Path(root) / "assets" / "bin" / "cq").write_text(self.STUB, encoding="utf-8")
            return subprocess.run([str(Path(root) / "bin" / "cq.cmd"), *args],
                                  capture_output=True, text=True, check=False)

    def test_o_argv_acentuado_chega_ao_cq_intacto(self):
        argv = ["não a do usuário", "ação"]
        done = self._run(*argv)
        self.assertEqual(json.loads(done.stdout), argv, done.stderr)

    def test_o_codigo_de_saida_do_cq_atravessa_o_lancador(self):
        self.assertEqual(self._run("x").returncode, 3)


if __name__ == "__main__":
    unittest.main()
