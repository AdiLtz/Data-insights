"""Read-only SQLite query execution."""

from __future__ import annotations

import json
import sqlite3
import time
from pathlib import Path

from .sql_guard import sqlite_authorizer, validate_select


MAX_ROWS = 500
MAX_RESULT_BYTES = 2_000_000
QUERY_TIMEOUT_SECONDS = 3.0
ALLOWED_TABLES = ("departments", "employees", "projects", "employee_projects")


class QueryExecutionError(RuntimeError):
    """A safe, user-displayable query execution failure."""


class ReadOnlyDatabase:
    def __init__(self, path: Path):
        self.path = path.expanduser().resolve()
        if not self.path.is_file():
            raise FileNotFoundError(f"SQLite database not found: {self.path}")

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(
            f"{self.path.as_uri()}?mode=ro",
            uri=True,
            timeout=2.0,
        )
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA query_only = ON")
        connection.execute("PRAGMA trusted_schema = OFF")

        limits = (
            (sqlite3.SQLITE_LIMIT_LENGTH, 1_000_000),
            (sqlite3.SQLITE_LIMIT_SQL_LENGTH, 10_000),
            (sqlite3.SQLITE_LIMIT_COLUMN, 100),
            (sqlite3.SQLITE_LIMIT_COMPOUND_SELECT, 20),
            (sqlite3.SQLITE_LIMIT_EXPR_DEPTH, 100),
            (sqlite3.SQLITE_LIMIT_ATTACHED, 0),
            (sqlite3.SQLITE_LIMIT_VDBE_OP, 100_000),
        )
        for category, value in limits:
            connection.setlimit(category, value)
        connection.set_authorizer(sqlite_authorizer)
        return connection

    def execute(self, sql: str) -> dict[str, object]:
        safe_sql = validate_select(sql)
        connection = self._connect()
        deadline = time.monotonic() + QUERY_TIMEOUT_SECONDS
        connection.set_progress_handler(
            lambda: int(time.monotonic() > deadline),
            1_000,
        )

        try:
            cursor = connection.execute(safe_sql)
            columns = [description[0] for description in cursor.description or ()]
            formatted_rows: list[dict[str, object]] = []
            result_bytes = 0
            truncated = False
            for row_number in range(MAX_ROWS + 1):
                row = cursor.fetchone()
                if row is None:
                    break
                if row_number == MAX_ROWS:
                    truncated = True
                    break
                formatted_row = {
                    key: value.hex() if isinstance(value, bytes) else value
                    for key, value in dict(row).items()
                }
                row_bytes = len(
                    json.dumps(formatted_row, ensure_ascii=False).encode("utf-8")
                )
                if result_bytes + row_bytes > MAX_RESULT_BYTES:
                    truncated = True
                    break
                result_bytes += row_bytes
                formatted_rows.append(formatted_row)
            return {
                "columns": columns,
                "rows": formatted_rows,
                "row_count": len(formatted_rows),
                "truncated": truncated,
            }
        except sqlite3.Error as error:
            message = str(error)
            if (
                "not authorized" in message.lower()
                or "authorization denied" in message.lower()
            ):
                raise QueryExecutionError(
                    "This query attempted an operation that is not permitted. "
                    "Only read-only SELECT queries on application tables are allowed."
                ) from error
            if "interrupted" in message.lower():
                raise QueryExecutionError(
                    "The query took too long. Try narrowing the request or adding a filter."
                ) from error
            raise QueryExecutionError(
                f"SQLite could not run this query: {message}"
            ) from error
        finally:
            connection.close()

    def schema_context(self) -> list[dict[str, object]]:
        connection = self._connect()
        try:
            connection.set_authorizer(None)
            tables: list[dict[str, object]] = []
            for table in ALLOWED_TABLES:
                columns = connection.execute(
                    f"PRAGMA table_info({table})"
                ).fetchall()
                tables.append(
                    {
                        "name": table,
                        "columns": [column["name"] for column in columns],
                    }
                )
            return tables
        finally:
            connection.close()
