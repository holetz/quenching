"""The repository's own tooling: helpers the gate and the test loop call.

Not part of the deployed plugin — `cq deploy` ships `quenching/assets/**` only — and watched by
`cq git audit` as a gate path, so a change here cannot silently weaken verification.

Run a module as `python -m scripts.toolchain.<module>`.
"""
