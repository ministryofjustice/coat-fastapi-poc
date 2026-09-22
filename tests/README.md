# Tests

Test suite for `coat-fastapi-poc`

> Runs from the project root (`testpaths` is configured in `pyproject.toml`, so no need to `cd` into `tests/`)

## Structure

Tests mirror the `app/` folder structure. Each source file gets a matching `test_*.py` file, one level deep under `v1/`.


```
tests/
├── __init__.py
├── conftest.py
└── v1
    ├── __init__.py
    ├── api
    │   ├── __init__.py
    │   └── test_daily.py
    ├── schemas
    │   ├── __init__.py
    │   └── test_daily.py
    └── services
        ├── __init__.py
        ├── test_athena.py
        └── query_builder
            ├── __init__.py
            ├── test_daily.py
            └── test_escape_literal.py
```