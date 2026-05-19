.DEFAULT_GOAL := help

PYTHON ?= python3
PIP ?= $(PYTHON) -m pip

.PHONY: help install lint lint-python lint-markdown test docs build-docs clean

help: ## Show this help
	@echo "myforge-vault-1111 — make targets:"
	@awk 'BEGIN {FS = ":.*## "} /^[a-zA-Z_-]+:.*?## / {printf "  \033[36m%-20s\033[0m %s\n", $$1, $$2}' $(MAKEFILE_LIST)

install: ## Install Python deps (mkdocs + lint/test tools)
	$(PIP) install -r requirements.txt
	$(PIP) install -r requirements-dev.txt

lint: lint-python lint-markdown ## Run all linters (Python + Markdown)

lint-python: ## Ruff-check all Python files in the repo
	ruff check --exclude site --exclude .git .

lint-markdown: ## markdownlint-cli2 on 11-wiki, 07-Decisions, 06-Audits (lax preset)
	@command -v markdownlint-cli2 >/dev/null 2>&1 || { echo "Install: npm i -g markdownlint-cli2@0.13.0"; exit 1; }
	markdownlint-cli2 "11-wiki/**/*.md" "07-Decisions/**/*.md" "06-Audits/**/*.md" || true

test: ## Run pytest regression suite (fast markers only)
	@if [ -d .vault-eval/regression ]; then \
		pytest .vault-eval/regression -m fast -v --tb=short; \
	else \
		echo ".vault-eval/regression/ not present — skipping."; \
	fi

docs: ## Serve docs locally (mkdocs serve)
	mkdocs serve

build-docs: ## Strict-build the docs site (catches broken refs)
	mkdocs build --strict

clean: ## Remove caches and built site
	find . -type d -name "__pycache__" -prune -exec rm -rf {} +
	find . -type d -name ".pytest_cache" -prune -exec rm -rf {} +
	rm -rf site _ci_site
