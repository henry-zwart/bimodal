MAKEFLAGS += --warn-undefined-variables
SHELL = /bin/bash -o pipefail
SOURCES = python/src tests

.PHONY: test  ## Run all the tests with coverage.
test:
	poetry run py.test --cov=python/src tests -v

.PHONY: testfailed  ## Run tests that failed last time.
testfailed:
	poetry run py.test tests -v --last-failed

.PHONY: pre  ## Run precommit
pre:
	poetry run pre-commit run -a

.PHONY: help  ## Display this message
help:
	@grep -E \
		'^.PHONY: .*?## .*$$' $(MAKEFILE_LIST) | \
		sort | \
		awk 'BEGIN {FS = ".PHONY: |## "}; {printf "\033[36m%-19s\033[0m %s\n", $$2, $$3}'
