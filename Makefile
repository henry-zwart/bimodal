MAKEFLAGS += --warn-undefined-variables
SHELL = /bin/bash -o pipefail
.DEFAULT_GOAL := all
SOURCES = src tests

.PHONY: all  ## Check everything that will be done in CI
all: sync lint typecheck test

.PHONY: test  ## Run all the tests with coverage.
test:
	poetry run py.test --cov=src tests -v

.PHONY: testfailed  ## Run tests that failed last time.
testfailed:
	poetry run py.test tests -v --last-failed

.PHONY: pre  ## Run precommit
pre:
	poetry run pre-commit run -a

.PHONY: covrep ## Run tests and generate a coverage report, skipping the type-checker integration tests
covrep: test
	@echo "building coverage html"
	@poetry run coverage html

.PHONY: format  ## format all sources
format:
	poetry run ruff $(SOURCES) --fix
	poetry run black $(SOURCES)

.PHONY: lint  ## lint all sources
lint:
	poetry run ruff $(SOURCES)
	poetry run black $(SOURCES) --check --diff

.PHONY: typecheck  ## Run mypy for typechecking
typecheck:
	poetry run mypy src/ tests/

.PHONY: sync  ## Synchronize packages and data.
sync:
	poetry install --sync --with dvc
	poetry run dvc pull

.PHONY: clean  ## Clean all the things!
clean:
	rm -rf .eggs
	rm -rf .pytest_cache
	rm -rf build
	rm -rf tmp
	rm -rf var
	rm -rf src/*.egg-info
	rm -rf build
	rm -rf var
	rm -rf tags
	rm -rf __pycache__

.PHONY: help  ## Display this message
help:
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
