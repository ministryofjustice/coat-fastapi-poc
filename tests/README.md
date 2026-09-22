


####

Test tree:

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