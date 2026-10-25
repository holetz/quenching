"""The declared spec store and its credential source, offline: the `az`/`gh` calls are doubles and
no real organisation or repository is ever reached."""

import contextlib
import json
import os
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

try:
    import _paths  # noqa: F401  — must precede the `quenching` import; see its docstring
except ModuleNotFoundError:  # package-qualified unittest invocation from the repository root
    sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
    import _paths  # noqa: F401
from quenching.specs import store
from quenching.specs.backends.base import BackendRefusal

TOKEN = "s3cret-token-value-1234"


@contextlib.contextmanager
def workspace(repo_specs=None, user_specs=None, env=None):
    """A repository tree with `.claude/quenching.json` and a user-layer file, plus the env."""
    with tempfile.TemporaryDirectory() as tmp:
        repo = pathlib.Path(tmp, "repo")
        (repo / ".claude").mkdir(parents=True)
        if repo_specs is not None:
            (repo / ".claude" / "quenching.json").write_text(
                json.dumps({"backend": "git", "specs": repo_specs}), encoding="utf-8")
        else:
            (repo / ".claude" / "quenching.json").write_text("{}", encoding="utf-8")
        user = pathlib.Path(tmp, "user.json")
        if user_specs is not None:
            user.write_text(json.dumps({"specs": user_specs}), encoding="utf-8")
        patched = {"QUENCHING_USER_CONFIG": str(user), **(env or {})}
        with mock.patch.dict(os.environ, patched):
            yield str(repo)


def tree(path):
    return sorted((str(p.relative_to(path)), p.read_bytes()) for p in pathlib.Path(path).rglob("*")
                  if p.is_file())


class DeclaredStore(unittest.TestCase):
    def test_nothing_declared_is_empty(self):
        with workspace() as repo:
            self.assertEqual(({}, {}), store.declared_store(repo))

    def test_valid_declaration_normalises_a_bare_organisation(self):
        decl = {"store": {"azure": {"organization": "acme", "project": "Board"},
                          "github": {"repository": "acme/specs"}}}
        with workspace(decl) as repo:
            got, err = store.declared_store(repo)
        self.assertEqual({}, err)
        self.assertEqual({"organization": "https://dev.azure.com/acme", "project": "Board"},
                         got["azure"])
        self.assertEqual({"repository": "acme/specs"}, got["github"])

    def test_an_https_organisation_url_is_kept_without_the_trailing_slash(self):
        decl = {"store": {"azure": {"organization": "https://dev.azure.com/acme/",
                                    "project": "Board"}}}
        with workspace(decl) as repo:
            got, _ = store.declared_store(repo)
        self.assertEqual("https://dev.azure.com/acme", got["azure"]["organization"])

    def test_invalid_shapes_are_refused(self):
        cases = [
            ({"store": "x"}, "sp-store-invalid"),
            ({"store": {"azure": {"organization": "acme"}}}, "sp-store-invalid"),
            ({"store": {"azure": {"organization": "a b", "project": "p"}}}, "sp-store-invalid"),
            ({"store": {"github": {"repository": "no-slash"}}}, "sp-store-invalid"),
            ({"store": {"gitlab": {"repository": "a/b"}}}, "sp-store-unknown-key"),
            ({"store": {"github": {"repository": "a/b", "branch": "x"}}}, "sp-store-unknown-key"),
        ]
        for decl, code in cases:
            with self.subTest(decl=decl), workspace(decl) as repo:
                got, err = store.declared_store(repo)
                self.assertEqual({}, got)
                self.assertEqual((code, 2), (err["code"], err["exit"]))

    def test_a_secret_named_key_is_refused_without_echoing_its_value(self):
        for key in ("token", "pat", "password", "apiKey", "secret"):
            decl = {"store": {"azure": {"organization": "acme", "project": "p", key: TOKEN}}}
            with self.subTest(key=key), workspace(decl) as repo:
                _, err = store.declared_store(repo)
                self.assertEqual("sp-store-secret", err["code"])
                self.assertNotIn(TOKEN, json.dumps(err))

    def test_a_credential_block_in_the_repository_is_refused(self):
        decl = {"credential": {"github": {"source": "env", "env": "X"}}}
        with workspace(decl) as repo:
            _, err = store.declared_store(repo)
        self.assertEqual("sp-store-secret", err["code"])


class CredentialEnv(unittest.TestCase):
    def test_nothing_configured_inherits_the_environment(self):
        with workspace():
            self.assertEqual(({}, {}), store.credential_env("azure"))
            self.assertIsNone(store.subprocess_env("azure"))

    def test_env_source_maps_the_variable_onto_each_tools_token(self):
        user = {"credential": {"azure": {"source": "env", "env": "MY_AZ"},
                               "github": {"source": "env", "env": "MY_GH"}}}
        with workspace(user_specs=user, env={"MY_AZ": TOKEN, "MY_GH": TOKEN + "x"}):
            self.assertEqual({"AZURE_DEVOPS_EXT_PAT": TOKEN}, store.credential_env("azure")[0])
            self.assertEqual({"GH_TOKEN": TOKEN + "x"}, store.credential_env("github")[0])
            self.assertEqual(TOKEN, store.subprocess_env("azure")["AZURE_DEVOPS_EXT_PAT"])

    def test_login_source_expands_the_config_directory(self):
        user = {"credential": {"azure": {"source": "login", "configDir": "~/az-quenching"},
                               "github": {"source": "login"}}}
        with workspace(user_specs=user):
            self.assertEqual({"AZURE_CONFIG_DIR": os.path.expanduser("~/az-quenching")},
                             store.credential_env("azure")[0])
            self.assertEqual(({}, {}), store.credential_env("github"))

    def test_a_missing_variable_names_the_variable_only(self):
        user = {"credential": {"github": {"source": "env", "env": "ABSENT_VAR_X"}}}
        with workspace(user_specs=user):
            os.environ.pop("ABSENT_VAR_X", None)
            _, err = store.credential_env("github")
            self.assertEqual(("sp-credential-env-missing", "ABSENT_VAR_X"),
                             (err["code"], err["variable"]))
            with self.assertRaises(BackendRefusal):
                store.subprocess_env("github")

    def test_keyring_and_unknown_sources_are_refused_with_a_pointer_to_the_login(self):
        for source in ("keyring", "vault", None):
            user = {"credential": {"azure": {"source": source}}}
            with self.subTest(source=source), workspace(user_specs=user):
                _, err = store.credential_env("azure")
                self.assertEqual("sp-credential-source", err["code"])
                self.assertIn("login", err["message"])

    def test_a_bad_variable_name_is_refused_and_a_refusal_never_carries_the_token(self):
        user = {"credential": {"azure": {"source": "env", "env": "not a name"}}}
        with workspace(user_specs=user, env={"not a name": TOKEN}):
            _, err = store.credential_env("azure")
            self.assertEqual("sp-credential-source", err["code"])
            self.assertNotIn(TOKEN, json.dumps(err))

    def test_resolving_writes_nothing_into_the_repository(self):
        user = {"credential": {"azure": {"source": "env", "env": "MY_AZ"}}}
        decl = {"store": {"azure": {"organization": "acme", "project": "p"}}}
        with workspace(decl, user, {"MY_AZ": TOKEN}) as repo:
            before = tree(repo)
            store.declared_store(repo)
            store.subprocess_env("azure")
            self.assertEqual(before, tree(repo))
            self.assertNotIn(TOKEN.encode(), b"".join(data for _, data in tree(repo)))


class Wiring(unittest.TestCase):
    def test_declared_azure_skips_every_az_call(self):
        from quenching.specs.backends import azure
        decl = {"store": {"azure": {"organization": "acme", "project": "Board"}}}
        with workspace(decl) as repo, mock.patch("subprocess.run") as run:
            got, err = azure.resolve_azure_project(repo)
        self.assertEqual((("https://dev.azure.com/acme", "Board"), {}), (got, err))
        run.assert_not_called()

    def test_declared_github_skips_every_gh_call(self):
        from quenching.specs.backends import github
        decl = {"store": {"github": {"repository": "acme/specs"}}}
        with workspace(decl) as repo, mock.patch("subprocess.run") as run:
            got = github.resolve_github_repo(repo)
        self.assertEqual(("acme/specs", None, {}), got)
        run.assert_not_called()

    def test_a_refused_declaration_is_returned_not_raised(self):
        from quenching.specs.backends import azure, github
        decl = {"store": {"azure": {"organization": "a", "project": "p", "token": "x"}}}
        with workspace(decl) as repo, mock.patch("subprocess.run") as run:
            self.assertEqual("sp-store-secret", azure.resolve_azure_project(repo)[1]["code"])
            self.assertEqual("sp-store-secret", github.resolve_github_repo(repo)[2]["code"])
        run.assert_not_called()

    def test_nothing_declared_still_asks_az(self):
        from quenching.specs.backends import azure
        done = mock.Mock(returncode=1, stdout="", stderr="boom")
        with workspace() as repo, mock.patch("subprocess.run", return_value=done) as run:
            azure.resolve_azure_project(repo)
        self.assertEqual("devops", run.call_args.args[0][1])
        self.assertIsNone(run.call_args.kwargs["env"])

    def test_az_and_gh_receive_the_token_only_in_env(self):
        from quenching.specs.backends import azure, github
        user = {"credential": {"azure": {"source": "env", "env": "MY_AZ"},
                               "github": {"source": "env", "env": "MY_GH"}}}
        done = mock.Mock(returncode=0, stdout="{}", stderr="")
        with workspace(user_specs=user, env={"MY_AZ": TOKEN, "MY_GH": TOKEN}) as repo, \
                mock.patch("subprocess.run", return_value=done) as run:
            azure._az_run(repo, "devops", "configure", "--list")
            github._gh_run(repo, "repo", "view")
        for call in run.call_args_list:
            self.assertNotIn(TOKEN, " ".join(call.args[0]))
        self.assertEqual(TOKEN, run.call_args_list[0].kwargs["env"]["AZURE_DEVOPS_EXT_PAT"])
        self.assertEqual(TOKEN, run.call_args_list[1].kwargs["env"]["GH_TOKEN"])

    def test_env_missing_refuses_in_the_runner_and_base_stays_safe(self):
        from quenching.git import base
        from quenching.specs.backends import azure
        user = {"credential": {"azure": {"source": "env", "env": "MY_AZ"}}}
        with workspace(user_specs=user) as repo, \
                mock.patch.dict(os.environ, {}, clear=False), mock.patch("subprocess.run") as run:
            os.environ.pop("MY_AZ", None)
            with self.assertRaises(BackendRefusal) as ctx:
                azure._az_run(repo, "devops", "configure", "--list")
            self.assertEqual("sp-credential-env-missing", ctx.exception.err["code"])
            self.assertIsNone(base._is_host_default(repo, "azure-boards", "main"))
        run.assert_not_called()


if __name__ == "__main__":
    unittest.main()
