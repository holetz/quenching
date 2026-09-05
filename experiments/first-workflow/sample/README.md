# Disposable target sample

This directory is copied into a temporary target by `../run.sh`. It is not a repository-owned
knowledge bundle and is not installed into a user's home directory. The runner changes only the
temporary copy of `docs/glossary.md`, then lets `cq knowledge project --write` regenerate the
temporary `docs/assets/glossary-abbreviations.txt`.
