# ![RealWorld Example App](logo.png)

> ### [FastAPI] codebase containing real world examples (CRUD, auth, advanced patterns, etc) that adheres to the [RealWorld](https://github.com/gothinkster/realworld) spec and API.


### [Demo](https://github.com/gothinkster/realworld)&nbsp;&nbsp;&nbsp;&nbsp;[RealWorld](https://github.com/gothinkster/realworld)


This codebase was created to demonstrate a fully fledged fullstack application built with **[FastAPI]** including CRUD operations, authentication, routing, pagination, and more.

We've gone to great lengths to adhere to the **[FastAPI]** community styleguides & best practices.

For more information on how to this works with other frontends/backends, head over to the [RealWorld](https://github.com/gothinkster/realworld) repo.


# How it works

> Describe the general architecture of your app here
```
.
├── Dockerfile
├── LICENSE
├── Makefile
├── app
│   ├── __init__.py
│   ├── api
│   │   ├── __init__.py
│   │   ├── api.py
│   │   └── routers
│   ├── core
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   ├── crud
│   │   ├── __init__.py
│   │   └── users.py
│   ├── db.py
│   ├── main.py
│   └── schemas
│       ├── __init__.py
│       └── user.py
├── docker-compose.yml
├── logo.png
├── notes.md
├── poetry.lock
├── postman
│   ├── Conduit.postman_collection.json
│   ├── README.md
│   ├── run-api-tests.sh
│   └── swagger.json
├── pyproject.toml
├── readme.md
├── setup.cfg
└── tests
    ├── __init__.py
    ├── api
    │   ├── __init__.py
    │   └── test_users.py
    └── conftest.py
```

# Getting started
First, start postgres database
```bash
docker-compose up -d db pgadmin
```
Then, bootstrap your environment with `poetry`
```
poetry install
poetry shell
```
Run application
```shell script
uvicorn app.main:app --reload
```

Test

```shell script
poetry run pytestpytest
```

Test coverage

```shell script
pytest --cov=app --cov-report=term-missing tests
```

Postman collection test

```shell script
alembic downgrade base
alembic upgrade head
APIURL=http://localhost:8000/api bash ./postman/run-api-tests.sh
```
