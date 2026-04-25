.PHONY: validate validate-ci test check

audit:
	uv run pip-audit


lint:
	uv run ruff check . --fix
	uv run ruff format .
	uv run ruff format . --check
	uv run mypy .

check:
	uv lock --check
	uv run ruff check .
	uv run ruff format . --check
	uv run mypy .


test:
	uv run pytest


test-coverage:
	uv run pytest \
		--cov=src \
		--cov-report=term-missing  \
    	--cov-report=xml


validate: lint test-coverage


validate-ci: audit check test-coverage
