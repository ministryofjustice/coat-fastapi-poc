from botocore.exceptions import BotoCoreError, ClientError
from fastapi import FastAPI, Request
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.api.v1.router import router as v1_router

app = FastAPI(title="COAT API (FastAPI POC)")


@app.exception_handler(ValidationError)
async def pydantic_validation_exception_handler(request: Request, exc: ValidationError):
    """Bad input from the client e.g. missing required params, invalid
    dates, or failing our custom 'at least one categorical param' rule.
    Returns 422 (Unprocessable Entity) - the standard 'your request was
    malformed' status. jsonable_encoder handles non-JSON-native types
    (like date objects) that Pydantic embeds in its error details."""
    return JSONResponse(
        status_code=422,
        content=jsonable_encoder({"detail": exc.errors()}),
    )


@app.exception_handler(RuntimeError)
async def athena_runtime_error_handler(request: Request, exc: RuntimeError):
    """The Athena query itself failed or was cancelled after successfully
    starting - e.g. bad SQL, a timeout, or Athena-side query failure.
    This is OUR service raising it deliberately (see AthenaService.wait_for_query),
    not a network/auth problem. Returns 500 (Internal Server Error) since
    the request was valid but we couldn't fulfil it."""
    return JSONResponse(
        status_code=500,
        content={"error": "Failed to retrieve cloud cost data", "details": str(exc)},
    )


@app.exception_handler(BotoCoreError)
@app.exception_handler(ClientError)
async def aws_error_handler(request: Request, exc: Exception):
    """AWS/boto3-level failure before or outside our own logic - e.g. missing
    or expired credentials (NoCredentialsError), network/connectivity issues
    (BotoCoreError family), or AWS itself rejecting the call (access denied,
    throttling - ClientError family). Returns 502 (Bad Gateway) rather than 500,
    since this signals 'we're fine, but an upstream service we depend on failed',
    which is more precise for monitoring/alerting than a generic 500."""
    return JSONResponse(
        status_code=502,
        content={"error": "AWS service error", "details": str(exc)},
    )


@app.get("/health")
def health_check():
    """Basic liveness check - deliberately has no dependency on athena/AWS,
    so it can confirm the service itself is up even if AWS is unreachable."""
    return {"status": "ok"}


app.include_router(v1_router)