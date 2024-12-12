SHELL := bash

.PHONY: install
install:
	uv sync --all-extras --dev

.PHONY: test
test: install
	uv run pytest -vv

.PHONY: lint
lint: install
	uv lock --check
	uv run ruff check .
	uv run ruff format . --check

.PHONY: format
format: install
	uv run ruff check . --fix
	uv run ruff format .

.PHONY: clean
clean:
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete
