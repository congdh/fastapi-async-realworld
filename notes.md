# Implement notes step by step from scratch

> Tham khảo template [Full Stack FastAPI PostgreSQL](https://github.com/tiangolo/full-stack-fastapi-postgresql)

## Features

- [x] **Poetry**: Package management
- [x] **pytest**: Testing

## Project setup
### Dependency management with `Poetry`
```commandline
brew install poetry
poetry init
poetry install
poetry shell
```
> **_`Knowledge`_**
> - Manage package dependency and virtual environment using `poetry` => Better than old solution using `virtualenvwrapper` + `pip`

## First API: FastAPI helloworld
Follow tutorial [FastAPI Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/)
> Skip route `items` because need only simplest API for test configuration and environment

Run & test
```commandline
uvicorn app.main:app --reload
curl localhost:8000/api/users -v
```
Open docs http://127.0.0.1:8000/docs

> **_`Knowledge`_**
> - FastAPI Helloworld

### First testcase: Testing with `pytest` (async)
Follow tutorial [Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/)

> **_`Knowledge`_**
> - Async testing for FastAPI

### Code formatting with `black`, `isort`, `autoflake`
Let's install them using `poetry` as development dependencies so they don't clutter a deployment
```commandline
poetry add -D --allow-prereleases black
poetry add -D isort
poetry add -D autoflake
```
Create a setup.cfg file and add this config:
```ini
[isort]
multi_line_output=3
include_trailing_comma=True
force_grid_wrap=0
use_parentheses=True
line_length=88
```
Check code format with black and isort
```commandline
poetry run black . --check
poetry run isort . --diff
poetry run autoflake -c -r .
```

Enforce format for code
```shell script
echo "Sort imports one per line, so autoflake can remove unused imports"
poetry run isort --recursive  --force-single-line-imports --apply app tests
poetry run autoflake --remove-all-unused-imports --recursive --remove-unused-variables --in-place app --exclude=__init__.py
poetry run black app tests
poetry run isort --recursive --apply app tests
```
> **_`Knowledge`_**
> - Code formatting with `black`, `isort`, `autoflake`

### Code linting: Style enforcement with `flake8`
Install package
```commandline
poetry add -D flake8
```
Add this config to setup.cfg:
```ini
[flake8]
ignore = E203, E266, E501, W503
max-line-length = 88
max-complexity = 18
select = B,C,E,F,W,T4
```
Now can run `flake8`
```commandline
poetry run flake8
```
### Code linting: Static types with mypy
Install package
```commandline
poetry add pydantic
poetry add -D mypy sqlalchemy-stubs
```
Add this to setup.cfg
```ini
[mypy]
plugins = pydantic.mypy, sqlmypy
follow_imports = silent
strict_optional = True
warn_redundant_casts = True
warn_unused_ignores = True
disallow_any_generics = True
check_untyped_defs = True
;no_implicit_reexport = True

# for strict mypy: (this is the tricky one :-))
disallow_untyped_defs = True

[pydantic-mypy]
init_forbid_extra = True
init_typed = True
warn_required_dynamic_aliases = True
warn_untyped_fields = True
```
Now can run `mypy`
```commandline
poetry run mypy --show-error-codes app
```

> **_`Knowledge`_**
> - Code linting with `flake8`, `mypy`

### Make to leverage muscle memory
Create Makefile contains below commands
- poetry
- clean
- format
- lint
- test
- default
- run-dev
- run

```makefile
.DEFAULT_GOAL = default

default: poetry clean format lint coverage

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
```

Lets run make command with option you want

```commandline
make format
make lint
make
```

> **_`Knowledge`_**
> - Make to leverage muscle memory

### Code linting: Security linting with `bandit`
Install package
```commandline
poetry add -D bandit
```
Add this to setup.cfg
```ini
[bandit]
exclude: /tests
targets: .
```
Lets run bandit
```commandline
bandit -r --ini setup.cfg
```
