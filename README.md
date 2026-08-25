coat-fastapi-poc/
├── app/
│   ├── __init__.py
│   ├── main.py              # creates FastAPI() app, includes routers
│   ├── api/
│   │   ├── __init__.py
│   │   └── v1/
│   │       ├── __init__.py
│   │       ├── router.py    # assembles all v1 sub-routers
│   │       └── endpoints/
│   │           ├── __init__.py
│   │           └── daily.py # /cloud-cost/daily route + logic
│   ├── core/
│   │   ├── __init__.py
│   │   └── config.py        # settings (env vars, AWS profile, Athena db name etc.)
│   ├── models/
│   │   ├── __init__.py
│   │   └── daily.py         # Pydantic response/request models for /daily
│   └── services/
│       ├── __init__.py
│       └── athena.py        # Athena query client/wrapper (real query logic lives here)
├── tests/
│   ├── __init__.py
│   └── test_daily.py
├── .env.example
├── .gitignore
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
└── README.md