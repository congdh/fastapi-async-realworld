# Implement notes step by step from scratch

> Tham khảo template [Full Stack FastAPI PostgreSQL](https://github.com/tiangolo/full-stack-fastapi-postgresql)

## Features

- [x] **Poetry**: Package management
- [x] **pytest**: Testing

## Project setup
### Poetry
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

### First testcase: Testing with pytest (async)
Follow tutorial [Async Tests](https://fastapi.tiangolo.com/advanced/async-tests/)

> **_`Knowledge`_**
> - Async testing for FastAPI