import asyncio
from pathlib import Path

from app.db.query_loader import load_query
from app.repositories.base_repository import BaseRepository


class FakeSession:
    async def execute(self, statement, parameters):
        return statement.text, parameters


def test_load_query_reads_service_sql_file() -> None:
    query = load_query("health", "database_time")

    assert query == "SELECT NOW() AS database_time;"


def test_load_query_rejects_path_traversal() -> None:
    try:
        load_query("health", "../secrets")
    except ValueError as error:
        assert "invalid SQL query name" in str(error)
    else:
        raise AssertionError("path traversal must be rejected")


def test_repository_load_query_wraps_sql_loader() -> None:
    repository = BaseRepository()

    assert repository.load_query("health", "database_time") == "SELECT NOW() AS database_time;"


def test_repository_execute_query_hides_sql_execution_syntax() -> None:
    result = asyncio.run(
        BaseRepository().execute_query(
            FakeSession(),
            "health",
            "database_time",
        )
    )

    assert result == ("SELECT NOW() AS database_time;", {})
