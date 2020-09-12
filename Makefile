.DEFAULT_GOAL = default

default: clean format lint coverage

.PHONY: clean
clean:
	@echo "remove all build, test, coverage and Python artifacts"
	rm -fr build dist .eggs *egg-info .tox/ .cache/ .pytest_cache/ docs/_build/ .coverage htmlcov +
	find . -name '*.egg-info' -exec rm -fr {} +
	find . -name '*.egg' -exec rm -f {} +
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '__pycache__' -exec rm -fr {} +

.PHONY: poetry
poetry:
	poetry install

.PHONY: format
format:
	# Sort imports one per line, so autoflake can remove unused imports
	poetry run isort --force-single-line-imports app tests
	poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
	poetry run black app tests
	poetry run isort app tests

.PHONY: lint
lint:
	poetry run mypy --show-error-codes app
	poetry run flake8
	poetry run bandit -r --ini setup.cfg

.PHONY: test
test:
	poetry run pytest

.PHONY: coverage
coverage:
	poetry run pytest --cov=app --cov-report=term-missing tests

.PHONY: run-dev
run-dev:
	poetry run uvicorn app.main:app --reload --lifespan on --workers 1 --host 0.0.0.0 --port 8080 --log-level debug

.PHONY: run
run:
	uvicorn app.main:app --lifespan on --workers 1 --host 0.0.0.0 --port 8080
