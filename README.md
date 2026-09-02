# COAT FastAPI POC

Proof of Concept API for retrieving cloud cost data.

## Prerequisites (for dev)

- [uv](https://docs.astral.sh/uv/) for dependency management
- Docker, to run this in a container
- AWS SSO access to the `modernisation-platform-sandbox` profile, with
  permissions to query Athena in `coat-development`

## Running locally

### Option 1: plain uv

Make sure you have an active AWS SSO session first:

```bash
aws sso login --profile modernisation-platform-sandbox
export AWS_PROFILE=modernisation-platform-sandbox
```

Then install dependencies and run the app:

```bash
uv sync
uv run fastapi dev app/main.py
```

The API will be available at `http://localhost:8000`. Swagger/API docs are at
`http://localhost:8000/docs`.

### Option 2: Run Docker to check container, via Makefile

```bash
make run
```

This builds the image and starts the container, mounting your `~/.aws`
folder into the container so it can use your existing SSO session. The API
will be available at `http://localhost:3000`.

Other Makefile targets:

```bash
make build   # build the image only
make stop    # stop the running container
make shell   # open a shell inside the running container
make health  # curl the /health endpoint
```

## Project structure

```
app/
├── main.py                — creates the app, registers global exception
│                             handlers, defines /health
├── api/v1/
│   ├── router.py           — collects all v1 endpoint routers
│   └── endpoints/
│       └── daily.py        — GET /api/v1/cloud-cost/daily
├── core/
│   └── config.py           — env-driven settings (region, database, etc.)
├── schemas/
│   └── daily.py             — Pydantic request/response shapes for /daily
└── services/
    └── athena.py            — AthenaService, query builder, boto3 calls (for now before moving to aioboto3)
```


## Linting & type checking

This repo uses `ruff` for linting/import sorting and `mypy` for static type
checking, both configured in `pyproject.toml`.

```bash
uv run ruff check .    # lint
uv run ruff format .   # auto-format
uv run mypy            # type check
```

Both are wired into GitHub Actions and run on every push and pull request.

Note: `app/services/athena.py` is currently exempted from mypy via a scoped
override in `pyproject.toml`. This is deliberate, as that file is being
rewritten to use `aioboto3` (see ticket #1072), so it isn't worth fully
type-annotating the current sync `boto3` version now.