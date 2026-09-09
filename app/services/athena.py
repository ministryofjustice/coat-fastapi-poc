import asyncio
from typing import Any

import aioboto3  # type: ignore[import-untyped]

from app.core.config import settings
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


class AthenaService:
    def __init__(self) -> None:
        self.session = aioboto3.Session()
        self.region_name = settings.aws_region
        self.database = settings.athena_database
        self.workgroup = settings.athena_workgroup
        self.output_location = settings.athena_output_location

    async def start_query(self, client: Any, query: str) -> str:
        response = await client.start_query_execution(
            QueryString=query,
            QueryExecutionContext={"Database": self.database},
            ResultConfiguration={"OutputLocation": self.output_location},
            WorkGroup=self.workgroup,
        )
        return str(response["QueryExecutionId"])

    async def wait_for_query(self, client: Any, query_execution_id: str) -> None:
        while True:
            response = await client.get_query_execution(
                QueryExecutionId=query_execution_id
            )
            state = response["QueryExecution"]["Status"]["State"]

            if state == "SUCCEEDED":
                return

            if state in ("FAILED", "CANCELLED"):
                reason = response["QueryExecution"]["Status"].get(
                    "StateChangeReason", ""
                )
                raise RuntimeError(f"Athena query {state}: {reason}")

            await asyncio.sleep(2)

    async def get_results(
            self, client: Any, query_execution_id: str
        ) -> list[dict[str, Any]]:
        paginator = client.get_paginator("get_query_results")
        pages = paginator.paginate(QueryExecutionId=query_execution_id)

        columns: list[str] = []
        rows: list[dict[str, Any]] = []

        async for page in pages:
            if not columns:
                columns = [
                    col["Name"]
                    for col in page["ResultSet"]["ResultSetMetadata"]["ColumnInfo"]
                ]

            for row in page["ResultSet"]["Rows"]:
                values = [field.get("VarCharValue", "") for field in row["Data"]]
                rows.append(dict(zip(columns, values)))

        return rows[1:]  # first row is the header row, same as Node's .slice(1)

    async def run_query(self, query: str) -> list[dict[str, Any]]:
        async with self.session.client(
            "athena", region_name=self.region_name
        ) as client:
            query_execution_id = await self.start_query(client, query)
            await self.wait_for_query(client, query_execution_id)
            return await self.get_results(client, query_execution_id)

    async def get_daily_cost(
            self, params: DailyCostQueryParams
        ) -> list[dict[str, Any]]:
        query = build_daily_cost_query(params)
        return await self.run_query(query)
