from fastapi import APIRouter, Depends

from app.schemas.daily import DailyCostQueryParams, DailyCostResponse
from app.services.athena import AthenaService

router = APIRouter()


@router.get("/cloud-cost/daily", response_model=DailyCostResponse, response_model_exclude_none=True)
def get_daily_cost(params: DailyCostQueryParams = Depends()):
    athena_service = AthenaService()
    raw_rows = athena_service.get_daily_cost(params)

    return DailyCostResponse(
        account_name=params.account_name,
        results=raw_rows,
    )