import pytest
from unittest.mock import AsyncMock
from app.services.athena import AthenaService


@pytest.mark.asyncio
async def test_start_query_returns_query_execution_id():
    """start_query returns the QueryExecutionId from the client's response"""
    service = AthenaService()
    client = AsyncMock()
    client.start_query_execution.return_value = {"QueryExecutionId": "random-test-id-54321"}

    result = await service.start_query(client, "SELECT 1", [])

    assert result == "random-test-id-54321"


@pytest.mark.asyncio
async def test_start_query_calls_client_with_correct_arguments():
    """Start_query passes query, execution_params, database, workgroup and output_location to the client"""
    service = AthenaService()
    client = AsyncMock()
    client.start_query_execution.return_value = {"QueryExecutionId": "abc-123"}

    await service.start_query(client, "SELECT 1", ["param1"])

    client.start_query_execution.assert_called_once_with(
        ExecutionParameters=["param1"],
        QueryString="SELECT 1",
        QueryExecutionContext={"Database": service.database},
        ResultConfiguration={"OutputLocation": service.output_location},
        WorkGroup=service.workgroup,
    )

@pytest.mark.asyncio
async def test_wait_for_query_returns_when_succeeded():
    """wait_for_query returns normally when the query state is SUCCEEDED"""
    service = AthenaService()
    client = AsyncMock()
    client.get_query_execution.return_value = {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}}

    await service.wait_for_query(client, "query-id-123")

    client.get_query_execution.assert_called_once_with(
        QueryExecutionId="query-id-123"
    )

@pytest.mark.asyncio
async def test_wait_for_query_returns_runtime_error_when_fails():
    """wait_for_query raises runtime error when the query state is failed"""
    service = AthenaService()
    client = AsyncMock()
    client.get_query_execution.return_value = {
        "QueryExecution": {"Status": {"State": "FAILED"}}
    }

    with pytest.raises(RuntimeError):
        await service.wait_for_query(client, "query-id-123")

@pytest.mark.asyncio
async def test_wait_for_query_raises_runtime_error_when_cancelled():
    """wait_for_query raises runtime error when the query state is cancelled"""
    service = AthenaService()
    client = AsyncMock()
    client.get_query_execution.return_value = {
        "QueryExecution": {"Status": {"State": "CANCELLED"}}
    }

    with pytest.raises(RuntimeError):
        await service.wait_for_query(client, "query-id-123")

@pytest.mark.asyncio
async def test_wait_for_query_polls_until_succeeded():
    """wait_for_query polls repeatedly until the query state is succeeded"""
    service = AthenaService()
    client = AsyncMock()
    client.get_query_execution.side_effect = [
        {"QueryExecution": {"Status": {"State": "RUNNING"}}},
        {"QueryExecution": {"Status": {"State": "SUCCEEDED"}}},
    ]

    await service.wait_for_query(client, "query-id-123")

    assert client.get_query_execution.call_count == 2