from fastapi import APIRouter, Depends

from app.schemas.daily import DailyCostQueryParams, DailyCostResponse, DailyCostRow
from app.services.athena import AthenaService

router = APIRouter()


@router.get(
    "/cloud-cost/daily", 
    response_model=DailyCostResponse, 
    response_model_exclude_none=True,
)
def get_daily_cost(params: DailyCostQueryParams = Depends()) -> DailyCostResponse:
    athena_service = AthenaService()
    raw_rows = athena_service.get_daily_cost(params)
    rows = [DailyCostRow(**row) for row in raw_rows]

    return DailyCostResponse(
        account_name=params.account_name,
        results=rows,
    )