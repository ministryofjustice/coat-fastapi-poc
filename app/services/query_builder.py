from app.schemas.daily import DailyCostQueryParams

# Allowlist: query param name -> real SQL column name.
# This is the ONLY set of columns that can ever appear in SELECT/GROUP BY/WHERE.
DAILY_COST_DIMENSION_COLUMNS = {
    "account_name": "account_name",
    "region": "product_region_code",
    "environment": "environment",
    "business_unit": "business_unit",
    "application": "tag_application",
    "namespace": "tag_namespace",
    "service_area": "tag_service_area",
    "owner": "tag_owner",
    "product_name": "product_name",
}


def _escape_literal(value: str) -> str:
    """Escape single quotes for safe inclusion in a SQL string literal."""
    return value.replace("'", "''")


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
        where_conditions.append(f"{column_name} = '{_escape_literal(value)}'")

    where_clause = " AND ".join(where_conditions)

    return (
        f"SELECT {select_clause}\n"
        f"FROM fct_daily_cost\n"
        f"WHERE {where_clause}\n"
        f"GROUP BY {group_by_clause}\n"
        f"ORDER BY usage_date;"
    )
