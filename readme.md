# ![RealWorld Example App](logo.png)

> ### [FastAPI] codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://github.com/gothinkster/realworld)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged fullstack application built with **[FastAPI]** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **[FastAPI]** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.


# How it works

The application uses FastAPI web framework for building APIs with:

- [x] **Pydantic**: Data modeling
- [x] **postgres**: SQL database
- [x] **encode/databases**: Connect to database using `async` and `await`
- [x] **Alembic**: Database migration
- [x] **Docker, docker-compose**: Packaging and deployment
- [x] **Poetry**: Package management
- [x] **pytest**: Testing
- [x] **npx**: Test API using Postman collection
- [x] **black, autoflake, isort**: Code formatting
- [x] **mypy, flake8**: Code linting
- [x] **bandit**: Security linting
- [x] **safety**: Checks installed dependencies for known security vulnerabilities
- [x] **Git Pre-commit hooks**: Run checks automatically before git commits
- [x] **Make**: Leverage muscle memory
- [x] **dbdiagram.io**: Design ER diagrams

Project structure

```
.
├── Dockerfile
├── LICENSE
├── Makefile
├── alembic                 - Migration scripts
│   ├── env.py
│   ├── script.py.mako
│   └── versions
├── alembic.ini
├── app
│   ├── __init__.py
│   ├── api                 - API routers & business logic
│   ├── core                - Core functions/variables to run app
│   ├── crud                - CRUD operations
│   ├── db.py               - Declare, config database
│   ├── debug_server.py     - Debug in IDE with reload
│   ├── main.py
│   └── schemas             - Data modeling
├── docker-compose.yml
├── notes.md
├── postman                 - Postman collection for testing
├── pyproject.toml
├── readme.md
├── setup.cfg
└── tests                   - Test folder
    ├── __init__.py
    ├── alembic.ini
    ├── api
    ├── conftest.py
    └── utils
```

# Getting started
First, start postgres database
```bash
docker-compose up -d db pgadmin
```
Then, bootstrap your environment with `poetry`
```
make poetry
```
Run application
```shell script
uvicorn app.main:app --reload
```

# Running Tests

Run full test suite

```shell script
poetry run pytest
```

Run test coverage

```shell script
pytest --cov=app --cov-report=term-missing tests
```

Postman collection test

```shell script
alembic downgrade base
alembic upgrade head
APIURL=http://localhost:8000/api bash ./postman/run-api-tests.sh
```

# Deployment

# Migrations
