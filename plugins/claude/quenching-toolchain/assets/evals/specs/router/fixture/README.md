# Eval fixture — specs/create

A near-empty repository for the `/quenching-specs:specs:create` suite. `setup.sh` turns it into a
spec store: it declares the git backend in `.claude/quenching.json` and wires a local bare
repository as `origin`, so `cq specs new` writes onto the `quenching` branch without a network.
