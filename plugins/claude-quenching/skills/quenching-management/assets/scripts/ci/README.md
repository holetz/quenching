# scripts/ci — build & deploy

Scripts that **generate the deployable artifact** and validate it: build entrypoint,
YAML/manifest generation from the source, CI lint/format, deploy. **Within** the
lint/CI scope.

**"X defines Y" rule:** the source (Python/config) defines the artifact (YAML/manifest),
which is **generated and never edited by hand**. The scripts here are the end that
**generates**; the generated output is protected by code (it crosses the generated-file
protection hook).

> Replace/add the real modules and register each one in the map at
> [../README.md](../README.md). Remove this folder if the repo has no build of its own.
