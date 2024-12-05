SHELL := bash

.PHONY: install
install:
	poetry install

.PHONY: test
test:
	poetry run pytest -vv

.PHONY: lint
lint:
	poetry check --lock
	poetry run ruff check .
	poetry run ruff format . --check

.PHONY: format
format:
	poetry run ruff check . --fix
	poetry run ruff format .

.PHONY: clean
clean:
	@find . -iname '*.pyc' -delete
	@find . -iname '*.pyo' -delete
	@find . -iname '*~' -delete
	@find . -iname '*.swp' -delete
	@find . -iname '__pycache__' -delete
