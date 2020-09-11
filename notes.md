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