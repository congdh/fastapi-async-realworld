# Implement notes step by step from scratch

## Features

-   [x] **Poetry**: Package management
-   [x] **FastAPI**: Modern, fast (high-performance) web framework for building APIs with Python
-   [x] **pytest**: Testing
-   [x] **npx**: Test API using Postman collection
-   [x] **isort**: Code formatting - sort imports
-   [x] **autoflake**: Code formatting - removes unused imports and unused variables
-   [x] **black**: Code formatting - The Uncompromising Code Formatter
-   [x] **flake8**: Code linting - Style enforcement
-   [x] **mypy**: Code linting - Static types
-   [x] **bandit**: Code linting - Security linting
-   [x] **safety**: Code linting - Checks installed dependencies for known security vulnerabilities
-   [x] **Git Pre-commit hooks**: Run checks automatically before git commits
-   [x] **Make**: Leverage muscle memory
-   [x] **Docker, docker-compose**: Packaging and deployment
-   [x] **postgres**: SQL database
-   [x] **Alembic**: Database migration
-   [x] **dbdiagram.io**: Design ER diagrams

## Project setup

### Dependency management with `Poetry`

```commandline
brew install poetry
poetry init
poetry install
poetry shell
```

> **_`Knowledge`_**
>
> -   Manage package dependency and virtual environment using `poetry` => Better than old solution using `virtualenvwrapper` + `pip`

### First API: FastAPI helloworld

Follow tutorial [FastAPI Bigger Applications - Multiple Files](https://fastapi.tiangolo.com/tutorial/bigger-applications/)

> Skip route `items` because need only simplest API for test configuration and environment

Run & test

```commandline
uvicorn app.main:app --reload
curl localhost:8000/api/users -v
```

Open docs <http://127.0.0.1:8000/docs>

> **_`Knowledge`_**
>
> -   FastAPI Helloworld

### First testcase: Testing with `pytest` (async)

Follow tutorial [Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/)

> **_`Knowledge`_**
>
> -   Async testing for FastAPI

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
>
> -   Code formatting with `black`, `isort`, `autoflake`

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
poetry add pydantic -E email
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
>
> -   Code linting with `flake8`, `mypy`

### Make to leverage muscle memory

Create Makefile contains below commands

-   poetry
-   clean
-   format
-   lint
-   test
-   default
-   run-dev
-   run

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
>
> -   Make to leverage muscle memory

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
>
> -   Security analysis static source code for python project by `bandit`

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
>
> -   Check vulnerability dependencies

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
>
> -   Run checks automatically before git commits

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

Open docs <http://127.0.0.1:80/docs>

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

## Database setup

Add postgres service into `docker-compose.yml`

```yaml
version: "3.8"

services:
  app:
    build: .
    ports:
      - 80:80
  db:
    image: postgres:12
    volumes:
      - app-db-data:/var/lib/postgresql/data/pgdata
    environment:
      - PGDATA=/var/lib/postgresql/data/pgdata
    ports:
      - "5432:5432"

volumes:
  app-db-data:
```

and start it

```commandline
docker-compose up db
```

## Postgres asynchronously

> Reference:
>
> -   [Developing and Testing an Asynchronous API with FastAPI and Pytest](https://testdriven.io/blog/fastapi-crud/)
> -   [Async SQL (Relational) Databases with FastAPI](https://fastapi.tiangolo.com/advanced/async-sql-databases/)
> -   [Using database with Starlette](https://www.starlette.io/database/)

```commandline
poetry add asyncpg psycopg2-binary databases
poetry add python-jose -E cryptography
poetry add passlib bcrypt
poetry add -D Faker
```

Notable package/class

-   **`db.py`** SQLAlchemy parts: Declare, configure database
-   **`schemas`** Pydantic models. Read, write data interface with API
-   **`crud`** CRUD utils, which have reusable functions to interact with the data in the database
-   **`core`** Core utils, which have function/variable to run app like config, secuirty ...
-   **api/deps.py** Dependency variable which used in API function

Difference between Asynchronous and Synchronous with SQL database

|                        | Asynchronous                                            | Synchronous                               |
| ---------------------- | ------------------------------------------------------- | ----------------------------------------- |
| Database models        | sqlalchemy.Table                                        | sqlalchemy.ext.declarative.as_declarative |
| Connect and disconnect | event handlers (startup & shutdown)                     | Don't care                                |
| ORM                    | Not support                                             | Support                                   |
| CRUD                   | databases.Database                                      | sqlalchemy.orm.Session                    |
| Test                   | database.connect() before & database.disconnect() after | Don't care                                |

> **_Note_**: This comparison only apply for [encode/databases](https://github.com/encode/databases) library

> **_`Knowledge`_**
>
> -   Async SQL database with `encode/databases`

## Test API using Postman collection with npx

Beside pytest, you can test api using Postman collection with npx (npm package executor). The postman collection and script file is stored in `postman` directory. Read more details [here](postman/README.md)

```bash
cd postman
APIURL=http://localhost:8000/api bash ./run-api-tests.sh
```

> **_`Knowledge`_**
>
> -   Test API using Postman collection with npx

## Database migration with Alembic

> Reference: [Database migrations](https://www.starlette.io/database/#migrations)

Add alembic package using poetry

```commandline
poetry add alembic
```

Init alembic

```commandline
alembic init alembic
```

that will create config file `alembic.ini` and directory `alembic`
In alembic.ini remove the following line:

```ini
sqlalchemy.url = driver://user:pass@localhost/dbname
```

In migrations/env.py, you need to set the 'sqlalchemy.url' configuration key, and the target_metadata variable

```python
# The Alembic Config object.
config = context.config

# Configure Alembic to use our DATABASE_URL and our table definitions...
import app
config.set_main_option('sqlalchemy.url', str(app.DATABASE_URL))
target_metadata = app.metadata

...
```

Then, create an initial revision:

```shell script
alembic revision --autogenerate -m "Create users table"
```

Running our first migration

```shell script
$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade  -> 8ebc5ea3592e, Create users table
```

## Test isolation

Install `sqlalchemy-utils` package

```shell script
 poetry add -D sqlalchemy-utils
```

In config file _`app/core/config.py`_, add `TESTING` config and route to test database when `TESTING` is set

```python
class Settings(BaseSettings):
    TESTING: bool = False
    # API_V1_STR: str = "/api/v1"
    SECRET_KEY: str = secrets.token_urlsafe(32)
    # 60 minutes * 24 hours * 8 days = 8 days
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8
    POSTGRES_SERVER: str = "127.0.0.1"
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "realworld"
    SQLALCHEMY_DATABASE_URI: Optional[PostgresDsn] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True)
    def assemble_db_connection(cls, v: Optional[str], values: Dict[str, Any]) -> Any:
        if isinstance(v, str):
            return v
        db_prefix = "test_" if values.get("TESTING") else ""
        return PostgresDsn.build(
            scheme="postgresql",
            user=values.get("POSTGRES_USER"),
            password=values.get("POSTGRES_PASSWORD"),
            host=values.get("POSTGRES_SERVER"),
            path=f"/{db_prefix}{values.get('POSTGRES_DB') or ''}",
        )
```

Then prepare test database before run testcase

```python
@pytest.fixture(scope="session", autouse=True)
def create_test_database():
    root_dir = pathlib.Path(__file__).absolute().parent.parent
    ini_file = root_dir.joinpath("alembic.ini").__str__()
    alembic_directory = root_dir.joinpath("alembic").__str__()
    url = settings.SQLALCHEMY_DATABASE_URI
    assert not database_exists(url), "Test database already exists. Aborting tests."
    create_database(url)  # Create the test database.

    config = Config(ini_file)  # Run the migrations.
    config.set_main_option("script_location", alembic_directory)
    command.upgrade(config, "head")
    yield  # Run the tests.
    drop_database(url)  # Drop the test database.
```

Note that you **_MUST_** set `TESTING` environment variable before import app package

```python
environ["TESTING"] = "True"

from app import schemas  # noqa: E402
...
```

> **_`Knowledge`_**
>
> -   Test isolation database
> -   Using alembic in code

## Profiles API

Create `followers_assoc` table using alembic

```python
followers_assoc = sqlalchemy.Table(
    "followers_assoc",
    metadata,
    Column("follower", Integer, ForeignKey("users.id"), nullable=False),
    Column("followed_by", Integer, ForeignKey("users.id"), nullable=False)
)
```

```shell script
alembic revision --autogenerate -m "Create followers_assoc table"
```

Create schema, crud, api route and testcase for Profile API

> **_`Knowledge`_**
>
> -   Using Callable with Depends

## Tags API

Create `tags` table using alembic

```python
tags = sqlalchemy.Table(
    "tags",
    metadata,
    Column("tag", String, primary_key=True, index=True),
)
```

```shell script
alembic revision --autogenerate -m "Create tags table"
```

Create crud, api route and testcase for Tags API

## Articles API

Install slugify package

```shell script
poetry add python-slugify
```

Design database diagram using [dbdiagram.io](https://dbdiagram.io)

```dbml
Table users as U {
  id int [pk, increment] // auto-increment
  email varchar
  username varchar
  bio text
  image varchar
}

Table follow_assoc{
  follower int [pk]
  follow_by int [pk]
}
Ref: follow_assoc.follower > users.id
Ref: follow_assoc.follow_by > users.id

Table articles {
  id int [pk, increment] // auto-increment
  slug varchar [not null, unique]
  title varchar
  description varchar
  body varchar
  author_id int
  created_at timestamp [not null]
  updated_at timestamp [not null]
}

Ref: articles.author_id > users.id

Table tags {
  tag varchar [pk]
}

Table tag_assoc {
  article_id int [pk]
  tag varchar [pk]


}

Ref: tag_assoc.article_id > articles.id
Ref: tag_assoc.tag > tags.tag

Table favoriter_assoc{
  user_id int [pk]
  article_id int [pk]
}
Ref: favoriter_assoc.user_id > users.id
Ref: favoriter_assoc.article_id > articles.id

Table comments{
  id int [pk, increment] // auto-increment
  body text
  author_id int
  article_id int
  created_at timestamp [not null]
  updated_at timestamp [not null]
}
Ref: comments.author_id > users.id
Ref: comments.article_id > articles.id

```

Create tables using alembic

```python
articles = sqlalchemy.Table(
    "articles",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("slug", String, unique=True),
    Column("title", String),
    Column("description", String),
    Column("body", String),
    Column("author_id", Integer, ForeignKey("users.id")),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)

tag_assoc = sqlalchemy.Table(
    "tag_assoc",
    metadata,
    Column("article_id", Integer, primary_key=True, index=True),
    Column("tag", ForeignKey("tags.tag"), primary_key=True),
)

favoriter_assoc = sqlalchemy.Table(
    "favoriter_assoc",
    metadata,
    Column("user_id", Integer, ForeignKey("users.id"), primary_key=True),
    Column("article_id", Integer, ForeignKey("articles.id"), primary_key=True),
)

comments = sqlalchemy.Table(
    "comments",
    metadata,
    Column("id", Integer, primary_key=True, index=True),
    Column("body", String),
    Column("author_id", Integer, ForeignKey("users.id")),
    Column("article_id", Integer, ForeignKey("articles.id")),
    Column(
        "created_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
    Column(
        "updated_at",
        TIMESTAMP(timezone=True),
        nullable=False,
        server_default=func.now(),
    ),
)
```

```shell script
alembic revision --autogenerate -m "Create articles, comments table"
```

Create crud, api route and testcase for Articles API

> **_`Knowledge`_**
>
> -   Design ER diagrams using dbdiagram.io => Simple, Painlessly
