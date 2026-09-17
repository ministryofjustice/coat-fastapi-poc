from app.schemas.daily import DailyCostQueryParams
from app.services.query_builder.cloud_cost.daily_cost_columns import (
    DAILY_COST_DIMENSION_COLUMNS,
)
from app.services.query_builder.escape_literal import escape_literal


def build_daily_cost_query(params: DailyCostQueryParams) -> tuple[str, list[str]]:
    """Builds the SQL query and execution parameters for the /daily endpoint.

    Returns a (query, execution_params) pair rather than a single SQL string.
    The query text uses `?` placeholders for every user supplied value; the
    actual values are returned separately in execution_params, in the same
    order the `?`s appear. Athena substitutes these into the query text
    server-side but still parses the result as SQL. An unquoted/unescaped
    value can be reinterpreted as syntax. Each string
    value is therefore quoted and escaped via escape_literal before being
    added to execution_params.

    Column/dimension names are NOT parameters and they come from
    DAILY_COST_DIMENSION_COLUMNS, a fixed allowlist, and are safe to build
    directly into the query string since they never come from user input
    """
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

    where_conditions: list[str] = []
    execution_params: list[str] = []

    where_conditions.append("usage_date BETWEEN ? AND ?")
    # Athena requires an explicit CAST for typed comparisons even when the
    # value is passed as an execution parameter- without it, '?' binds as a
    # plain string and the DATE comparison won't work as intended
    execution_params.append(f"CAST('{params.start_usage_date.isoformat()}' AS DATE)")
    execution_params.append(f"CAST('{params.end_usage_date.isoformat()}' AS DATE)")

    for column_name, value in selected_dimensions:
        where_conditions.append(f"{column_name} = ?")
        # value must be quoted AND escaped, same as a manually-built literal -
        # Athena substitutes this text into the query and still parses it as
        # SQL, it doesn't bind it opaquely (see docstring above)
        execution_params.append(f"'{escape_literal(value)}'")

    where_clause = " AND ".join(where_conditions)

    query = (
        f"SELECT {select_clause}\n"
        f"FROM fct_daily_cost\n"
        f"WHERE {where_clause}\n"
        f"GROUP BY {group_by_clause}\n"
        f"ORDER BY usage_date;"
    )

    return query, execution_params
