from datetime import date
from app.schemas.daily import DailyCostQueryParams
from app.services.query_builder.cloud_cost.daily import build_daily_cost_query

def test_build_daily_cost_query_with_one_dimension():
    """One selected dimension appears in SELECT, GROUP BY, WHERE, and execution_params"""
    params = DailyCostQueryParams(
        start_usage_date=date(2025, 12, 1),
        end_usage_date=date(2025, 12, 10),
        account_name="LAA",
    )

    query, execution_params = build_daily_cost_query(params)

    assert "account_name" in query
    assert "WHERE usage_date BETWEEN ? AND ?" in query
    assert "account_name = ?" in query
    assert "GROUP BY account_name, usage_date" in query
    assert "LIMIT 100;" in query
    assert execution_params == [
        "CAST('2025-12-01' AS DATE)",
        "CAST('2025-12-10' AS DATE)",
        "'LAA'",
    ]


def test_build_daily_cost_query_with_multiple_dimension():
    """Multiple selected dimension appears in SELECT, GROUP BY, WHERE, and execution_params"""
    params = DailyCostQueryParams(
        start_usage_date=date(2025, 12, 1),
        end_usage_date=date(2025, 12, 10),
        account_name="LAA",
        region="eu-west-2",
    )

    query, execution_params = build_daily_cost_query(params)

    assert "account_name" in query
    assert "WHERE usage_date BETWEEN ? AND ?" in query
    assert "account_name = ?" in query
    assert "product_region_code = ?" in query
    assert "GROUP BY account_name, product_region_code, usage_date" in query
    assert "LIMIT 100;" in query
    assert execution_params == [
        "CAST('2025-12-01' AS DATE)",
        "CAST('2025-12-10' AS DATE)",
        "'LAA'",
        "'eu-west-2'",
    ]

def test_build_daily_cost_query_with_dimension_contains_single_quote():
    """Single quote is doubled anywhere in the dimension via escape literal"""
    params = DailyCostQueryParams(
        start_usage_date=date(2025, 12, 1),
        end_usage_date=date(2025, 12, 10),
        account_name="O'Brien's Team",
        region="eu-west-2",
    )

    query, execution_params = build_daily_cost_query(params)

    assert "account_name" in query
    assert "WHERE usage_date BETWEEN ? AND ?" in query
    assert "account_name = ?" in query
    assert "product_region_code = ?" in query
    assert "GROUP BY account_name, product_region_code, usage_date" in query
    assert "LIMIT 100;" in query
    assert execution_params == [
        "CAST('2025-12-01' AS DATE)",
        "CAST('2025-12-10' AS DATE)",
        "'O''Brien''s Team'",
        "'eu-west-2'",
    ]

def test_build_daily_cost_query_with_custom_limit():
    """A custom limit value is reflected in the LIMIT clause"""
    params = DailyCostQueryParams(
        start_usage_date=date(2025, 12, 1),
        end_usage_date=date(2025, 12, 10),
        account_name="LAA",
        limit=500,
    )

    query, execution_params = build_daily_cost_query(params)

    assert "LIMIT 500;" in query