from __future__ import annotations

import sqlite3
import tempfile
import unittest
from pathlib import Path

from insightsql.database import QueryExecutionError, ReadOnlyDatabase
from insightsql.generator import GenerationError, SQLGenerator
from insightsql.history import QueryHistory
from insightsql.sql_guard import SQLValidationError, validate_select


ROOT = Path(__file__).resolve().parents[1]


class SQLGuardTests(unittest.TestCase):
    def test_select_and_with_select_are_allowed(self) -> None:
        self.assertEqual(validate_select(" SELECT 1; "), "SELECT 1")
        self.assertTrue(validate_select("WITH c AS (SELECT 1) SELECT * FROM c"))

    def test_write_and_non_select_roots_are_rejected(self) -> None:
        for sql in (
            "DELETE FROM employees",
            "UPDATE employees SET salary = 0",
            "INSERT INTO departments VALUES (9, 'x', 'y')",
            "DROP TABLE employees",
            "ALTER TABLE employees ADD COLUMN x",
            "TRUNCATE employees",
            "PRAGMA table_info(employees)",
            "EXPLAIN SELECT * FROM employees",
        ):
            with self.subTest(sql=sql), self.assertRaises(SQLValidationError):
                validate_select(sql)

    def test_multiple_statements_are_rejected(self) -> None:
        with self.assertRaises(SQLValidationError):
            validate_select("SELECT 1; SELECT 2")

    def test_semicolon_in_string_is_not_statement_separator(self) -> None:
        self.assertEqual(
            validate_select("SELECT '; DROP TABLE employees'"),
            "SELECT '; DROP TABLE employees'",
        )


class ApplicationServiceTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp_dir = tempfile.TemporaryDirectory()
        self.directory = Path(self.temp_dir.name)
        self.database_path = self.directory / "fixture.db"
        with sqlite3.connect(self.database_path) as connection:
            connection.executescript((ROOT / "sqlite_schema.sql").read_text())
            connection.executescript((ROOT / "sqlite_seed.sql").read_text())
        self.database = ReadOnlyDatabase(self.database_path)

    def tearDown(self) -> None:
        self.temp_dir.cleanup()

    def test_read_query_returns_expected_sample_count(self) -> None:
        result = self.database.execute("SELECT COUNT(*) AS total FROM employees")
        self.assertEqual(result["rows"], [{"total": 20}])

    def test_schema_context_lists_only_application_tables(self) -> None:
        tables = self.database.schema_context()
        self.assertEqual(
            {table["name"] for table in tables},
            {"departments", "employees", "projects", "employee_projects"},
        )

    def test_authorizer_blocks_write_inside_with_clause(self) -> None:
        with self.assertRaises(QueryExecutionError):
            self.database.execute(
                "WITH candidate AS (SELECT 1001 AS id) "
                "DELETE FROM employees "
                "WHERE employee_id = (SELECT id FROM candidate)"
            )

    def test_database_file_remains_read_only(self) -> None:
        with self.assertRaises((SQLValidationError, QueryExecutionError)):
            self.database.execute("SELECT load_extension('extension')")
        with sqlite3.connect(self.database_path) as connection:
            self.assertEqual(
                connection.execute("SELECT COUNT(*) FROM employees").fetchone()[0],
                20,
            )

    def test_generator_handles_department_query(self) -> None:
        sql = SQLGenerator(self.database_path).generate(
            "Show employees in Engineering"
        )
        self.assertIn("department_name = 'Engineering'", sql)
        self.assertEqual(
            self.database.execute(sql)["row_count"],
            4,
        )

    def test_generator_handles_project_assignment_query(self) -> None:
        sql = SQLGenerator(self.database_path).generate("Show project assignments")
        self.assertIn("FROM employee_projects AS ep", sql)
        self.assertEqual(self.database.execute(sql)["row_count"], 30)

    def test_generator_handles_employee_name_search(self) -> None:
        sql = SQLGenerator(self.database_path).generate("Find Aarav")
        self.assertIn("first_name LIKE '%aarav%'", sql)
        self.assertEqual(self.database.execute(sql)["row_count"], 1)

    def test_generator_explains_unsupported_questions(self) -> None:
        with self.assertRaises(GenerationError):
            SQLGenerator(self.database_path).generate("What is the weather?")

    def test_history_is_persistent_and_bounded(self) -> None:
        history = QueryHistory(self.directory / "history.sqlite")
        for index in range(105):
            history.add(
                f"Question {index}",
                "SELECT COUNT(*) FROM employees",
                "success",
                1,
                None,
            )
        entries = history.recent()
        self.assertEqual(len(entries), 100)
        self.assertEqual(entries[0]["question"], "Question 104")
        self.assertEqual(entries[0]["status"], "success")


if __name__ == "__main__":
    unittest.main()
