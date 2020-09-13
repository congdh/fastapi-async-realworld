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
> **_`Knowledge`_**
> - Security analysis static source code for python project by `bandit`

### Code linting: Checks your installed dependencies for known security vulnerabilitie with `safety`
Install package
```commandline
poetry add -D safety
```
Lets run safety
```commandline
safety check
```
> **_`Knowledge`_**
> - Check vulnerability dependencies

### Git Pre-commit hooks: Run checks automatically before git commits
Install package
```commandline
poetry add -D pre-commit
pre-commit install
```
Create file `.pre-commit-config.yaml` with content
```yaml
repos:
  - repo: https://github.com/myint/autoflake
    rev: v1.4
    hooks:
      - id: autoflake
        name: autoflake
        entry: autoflake
        language: python
        'types': [ python ]
        require_serial: true
  - repo: https://github.com/ambv/black
    rev: stable
    hooks:
      - id: black
  - repo: https://github.com/pycqa/isort
    rev: 5.5.2
    hooks:
      - id: isort
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v0.782
    hooks:
      - id: mypy
        files: ^app/
        entry: mypy --show-error-codes --no-warn-unused-ignores --follow-imports silent app
        pass_filenames: false
        additional_dependencies:
          - 'pydantic'
          - 'sqlalchemy-stubs'
  - repo: https://gitlab.com/PyCQA/flake8
    rev: 3.8.3
    hooks:
      - id: flake8
        name: flake8
        description: '`flake8` is a command-line utility for enforcing style consistency across Python projects.'
        entry: flake8
        language: python
        types: [ python ]
        require_serial: true
  - repo: https://github.com/PyCQA/bandit
    rev: 1.6.2
    hooks:
      - id: bandit
        args: ["-x", "tests"]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v2.5.0
    hooks:
      - id: check-added-large-files
      - id: check-docstring-first
      - id: debug-statements
      - id: end-of-file-fixer
      - id: trailing-whitespace
      - id: check-ast
      - id: check-builtin-literals
      - id: detect-private-key
      - id: mixed-line-ending
```
Test with command
```commandline
poetry run pre-commit run --all-file
```

> **_`Knowledge`_**
> - Run checks automatically before git commits

### Deployment with docker
#### Dockerfile
Follow tutorial [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/).

Then, install install packages with poetry in Dockerfile using example [Using Poetry](https://github.com/tiangolo/uvicorn-gunicorn-fastapi-docker#using-poetry)
Dockerfile
```dockerfile
FROM tiangolo/uvicorn-gunicorn-fastapi:python3.8

# Install Poetry
RUN curl -sSL https://raw.githubusercontent.com/python-poetry/poetry/master/get-poetry.py | POETRY_HOME=/opt/poetry python && \
    cd /usr/local/bin && \
    ln -s /opt/poetry/bin/poetry && \
    poetry config virtualenvs.create false

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /app/


RUN poetry install --no-root --no-dev

COPY ./app /app/app
```
Build image and run container
```commandline
docker build -t myimage .
docker run -d --name mycontainer -p 80:80 myimage
```
Test
```shell script
curl localhost:80/api/users | jq
```
Open docs http://127.0.0.1:80/docs

#### Docker compose
Create `docker-compose.yml`
```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - 80:80
```
Lets run
```commandline
docker-compose up
```
And test
Test
```shell script
curl localhost:80/api/users | jq
```
