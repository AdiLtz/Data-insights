"""Small local query-history store."""

from __future__ import annotations

import sqlite3
from pathlib import Path


class QueryHistory:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with sqlite3.connect(self.path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS query_history (
                    history_id INTEGER PRIMARY KEY,
                    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%fZ', 'now')),
                    question TEXT NOT NULL,
                    sql_text TEXT NOT NULL,
                    status TEXT NOT NULL,
                    row_count INTEGER,
                    error TEXT
                )
                """
            )

    def add(
        self,
        question: str,
        sql_text: str,
        status: str,
        row_count: int | None,
        error: str | None,
    ) -> None:
        with sqlite3.connect(self.path, timeout=2.0) as connection:
            connection.execute(
                """
                INSERT INTO query_history (question, sql_text, status, row_count, error)
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    question[:1_000],
                    sql_text[:10_000],
                    status,
                    row_count,
                    error[:500] if error else None,
                ),
            )
            connection.execute(
                """
                DELETE FROM query_history
                WHERE history_id NOT IN (
                    SELECT history_id FROM query_history
                    ORDER BY history_id DESC LIMIT 100
                )
                """
            )

    def recent(self, limit: int = 50) -> list[dict[str, object]]:
        with sqlite3.connect(self.path, timeout=2.0) as connection:
            connection.row_factory = sqlite3.Row
            rows = connection.execute(
                """
                SELECT history_id, created_at, question, sql_text,
                       status, row_count, error
                FROM query_history
                ORDER BY history_id DESC
                LIMIT ?
                """,
                (min(max(limit, 1), 100),),
            ).fetchall()
        return [dict(row) for row in rows]
