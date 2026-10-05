from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.daily import DailyCostQueryParams


def test_daily_cost_query_params_constracts_with_one_categorical_field():
    """Query is successfull when at least one categorical field is set"""
    params = DailyCostQueryParams(
        start_usage_date=date(2025, 12, 5),
        end_usage_date=date(2025, 12, 10),
        account_name="LAA",
    )

    assert params.account_name == "LAA"


def test_daily_cost_query_params_raises_error_when_no_categorical_field_set():
    """Raises ValidationError when no categorical field is set"""
    # params = DailyCostQueryParams(
    #     start_usage_date=date(2025, 12, 5),
    #     end_usage_date=date(2025, 12, 10),
    # )

    with pytest.raises(ValidationError, match="At least one categorical parameter"):
        DailyCostQueryParams(
            start_usage_date=date(2025, 12, 5),
            end_usage_date=date(2025, 12, 10),
    )