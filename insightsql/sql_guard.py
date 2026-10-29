"""Read-only SQL validation and SQLite authorizer policy."""

from __future__ import annotations

import sqlite3


ALLOWED_TABLES = frozenset(
    {"departments", "employees", "projects", "employee_projects"}
)
BLOCKED_FUNCTIONS = frozenset({"load_extension", "readfile", "writefile"})


class SQLValidationError(ValueError):
    """Raised when a query is not a single read-only SELECT statement."""


def _significant_tokens(sql: str) -> list[str]:
    """Tokenize enough SQL syntax to identify statement boundaries and roots."""
    tokens: list[str] = []
    index = 0
    length = len(sql)

    while index < length:
        char = sql[index]
        if char.isspace():
            index += 1
            continue
        if sql.startswith("--", index):
            newline = sql.find("\n", index + 2)
            index = length if newline == -1 else newline + 1
            continue
        if sql.startswith("/*", index):
            end = sql.find("*/", index + 2)
            if end == -1:
                raise SQLValidationError("SQL contains an unfinished comment.")
            index = end + 2
            continue
        if char in ("'", '"', "`"):
            quote = char
            index += 1
            while index < length:
                if sql[index] == quote:
                    if index + 1 < length and sql[index + 1] == quote:
                        index += 2
                        continue
                    index += 1
                    break
                index += 1
            else:
                raise SQLValidationError("SQL contains an unfinished quoted value.")
            tokens.append("VALUE")
            continue
        if char == "[":
            end = sql.find("]", index + 1)
            if end == -1:
                raise SQLValidationError("SQL contains an unfinished identifier.")
            tokens.append("IDENTIFIER")
            index = end + 1
            continue
        if char == ";":
            tokens.append(";")
            index += 1
            continue
        if char.isalpha() or char == "_":
            end = index + 1
            while end < length and (sql[end].isalnum() or sql[end] in "_$"):
                end += 1
            tokens.append(sql[index:end].upper())
            index = end
            continue
        tokens.append(char)
        index += 1

    return tokens


def validate_select(sql: str) -> str:
    """Allow one SELECT or SELECT-producing WITH statement only."""
    if not isinstance(sql, str) or not sql.strip():
        raise SQLValidationError("Enter a SELECT query to run.")
    if len(sql) > 10_000:
        raise SQLValidationError("The SQL query is too long (maximum 10,000 characters).")

    tokens = _significant_tokens(sql)
    if not tokens or tokens[0] not in {"SELECT", "WITH"}:
        raise SQLValidationError("Only SELECT queries are allowed.")

    semicolons = [index for index, token in enumerate(tokens) if token == ";"]
    if len(semicolons) > 1 or (
        semicolons and semicolons[0] != len(tokens) - 1
    ):
        raise SQLValidationError("Run one SQL statement at a time.")

    return sql.strip().rstrip(";").strip()


def sqlite_authorizer(
    action: int,
    argument1: str | None,
    argument2: str | None,
    database_name: str | None,
    trigger_name: str | None,
) -> int:
    """Allow SELECT reads from application tables and deny all other actions."""
    del database_name, trigger_name

    if action in {
        sqlite3.SQLITE_SELECT,
        sqlite3.SQLITE_RECURSIVE,
    }:
        return sqlite3.SQLITE_OK

    if action == sqlite3.SQLITE_READ:
        if argument1 in ALLOWED_TABLES:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    if action == sqlite3.SQLITE_FUNCTION:
        function_name = (argument2 or argument1 or "").lower()
        if function_name not in BLOCKED_FUNCTIONS:
            return sqlite3.SQLITE_OK
        return sqlite3.SQLITE_DENY

    return sqlite3.SQLITE_DENY
