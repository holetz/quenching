# Documentation-site scripts for the claude-quenching plugin.
# All targets run through `uv` against the pinned toolchain in pyproject.toml/uv.lock.

.DEFAULT_GOAL := help
.PHONY: help docs-install docs-serve docs-build docs-deploy docs-update

help: ## List the available scripts
	@grep -E '^[a-zA-Z0-9_-]+:.*?## .*$$' $(MAKEFILE_LIST) \
		| awk 'BEGIN{FS=":.*?## "}{printf "  \033[36m%-14s\033[0m %s\n", $$1, $$2}'

docs-install: ## Sync the docs toolchain into .venv (creates it if missing)
	uv sync

docs-serve: docs-install ## Serve the docs locally with live reload (http://127.0.0.1:8000)
	uv run mkdocs serve

docs-build: docs-install ## Build the static site into ./site (strict: fails on broken refs)
	uv run mkdocs build --strict

docs-deploy: docs-install ## Publish to GitHub Pages (pushes the gh-pages branch)
	uv run mkdocs gh-deploy --force

docs-update: ## Upgrade the pinned docs dependencies, then re-sync
	uv lock --upgrade
	uv sync
