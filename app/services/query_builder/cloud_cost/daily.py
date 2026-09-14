from app.schemas.daily import DailyCostQueryParams
from app.services.query_builder.cloud_cost.daily_cost_columns import (
    DAILY_COST_DIMENSION_COLUMNS,
)
from app.services.query_builder.escape_literal import escape_literal


def build_daily_cost_query(params: DailyCostQueryParams) -> str:
    selected_dimensions = []

    for param_name, column_name in DAILY_COST_DIMENSION_COLUMNS.items():
        value = getattr(params, param_name)
        if value is not None:
            selected_dimensions.append((column_name, value))

    select_columns = [col for col, _ in selected_dimensions]
    select_clause = ", ".join(
        select_columns + ["usage_date", "SUM(daily_cost) AS total_daily_cost"]
    )
    group_by_clause = ", ".join(select_columns + ["usage_date"])

    where_conditions = [
        f"usage_date BETWEEN DATE '{params.start_usage_date.isoformat()}' "
        f"AND DATE '{params.end_usage_date.isoformat()}'"
    ]
    for column_name, value in selected_dimensions:
        where_conditions.append(f"{column_name} = '{escape_literal(value)}'")

    where_clause = " AND ".join(where_conditions)

    return (
        f"SELECT {select_clause}\n"
        f"FROM fct_daily_cost\n"
        f"WHERE {where_clause}\n"
        f"GROUP BY {group_by_clause}\n"
        f"ORDER BY usage_date;"
    )
