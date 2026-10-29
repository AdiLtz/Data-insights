"""Deterministic natural-language-to-SQL templates for the bundled schema."""

from __future__ import annotations

import re
import sqlite3
from pathlib import Path


class GenerationError(ValueError):
    """Raised when a question does not match a supported query template."""


def _literal(value: str) -> str:
    return "'" + value.replace("'", "''") + "'"


class SQLGenerator:
    """Generate transparent SQL from common employee/project questions."""

    def __init__(self, database_path: Path):
        self.database_path = database_path.expanduser().resolve()

    def _departments(self) -> list[str]:
        connection = sqlite3.connect(
            f"{self.database_path.as_uri()}?mode=ro",
            uri=True,
        )
        try:
            return [
                row[0]
                for row in connection.execute(
                    "SELECT department_name FROM departments ORDER BY department_name"
                )
            ]
        except sqlite3.Error as error:
            raise GenerationError(
                "Could not read the department list from the configured database."
            ) from error
        finally:
            connection.close()

    def generate(self, question: str) -> str:
        if not question or not question.strip():
            raise GenerationError("Enter a question first.")
        if len(question) > 1_000:
            raise GenerationError("Keep the question under 1,000 characters.")

        text = re.sub(r"\s+", " ", question.strip().lower())

        if re.search(r"\b(count|number of|how many)\b", text):
            if "employee" in text or "staff" in text:
                return "SELECT COUNT(*) AS employee_count FROM employees;"
            if "department" in text:
                return "SELECT COUNT(*) AS department_count FROM departments;"
            if "project" in text:
                return "SELECT COUNT(*) AS project_count FROM projects;"
            if "assignment" in text or "assigned" in text:
                return "SELECT COUNT(*) AS assignment_count FROM employee_projects;"

        department = next(
            (name for name in self._departments() if name.lower() in text),
            None,
        )
        if department and ("employee" in text or "staff" in text):
            return (
                "SELECT e.employee_id, e.first_name, e.last_name, e.email, "
                "e.job_title, d.department_name "
                "FROM employees AS e "
                "JOIN departments AS d ON d.department_id = e.department_id "
                f"WHERE d.department_name = {_literal(department)} "
                "ORDER BY e.last_name, e.first_name LIMIT 100;"
            )

        if "project" in text and any(
            word in text
            for word in ("member", "employee", "assigned", "assignment", "team")
        ):
            return (
                "SELECT p.project_name, e.employee_id, e.first_name, e.last_name, "
                "ep.project_role, ep.allocation_pct "
                "FROM employee_projects AS ep "
                "JOIN employees AS e ON e.employee_id = ep.employee_id "
                "JOIN projects AS p ON p.project_id = ep.project_id "
                "ORDER BY p.project_name, e.last_name LIMIT 200;"
            )

        if "department" in text and (
            "list" in text or "show" in text or "all" in text
        ):
            return (
                "SELECT department_id, department_name, location "
                "FROM departments ORDER BY department_name LIMIT 100;"
            )

        if ("project" in text or "projects" in text) and any(
            word in text for word in ("list", "show", "all")
        ):
            return (
                "SELECT project_id, project_name, start_date, end_date, status, budget "
                "FROM projects ORDER BY project_name LIMIT 100;"
            )

        if (
            "employee" in text
            or "staff" in text
            or re.search(r"\b(?:find|search for)\b", text)
        ):
            if any(word in text for word in ("list", "show", "all")):
                return (
                    "SELECT employee_id, first_name, last_name, email, job_title, "
                    "department_id, hire_date "
                    "FROM employees ORDER BY last_name, first_name LIMIT 100;"
                )
            name_match = re.search(
                r"\b(?:find|search for|show)\s+(?:employee\s+)?"
                r"([a-z][a-z'-]*(?:\s+[a-z][a-z'-]*)?)\b",
                text,
            )
            if name_match:
                name = name_match.group(1).strip()
                return (
                    "SELECT employee_id, first_name, last_name, email, job_title, "
                    "department_id "
                    "FROM employees "
                    f"WHERE first_name LIKE {_literal('%' + name + '%')} "
                    f"OR last_name LIKE {_literal('%' + name + '%')} "
                    "ORDER BY last_name, first_name LIMIT 100;"
                )

        raise GenerationError(
            "I couldn't map that question to a supported query. Try asking to "
            "count employees, list employees, show employees in a named department, "
            "list departments or projects, or show project assignments. You can "
            "also write or edit a SELECT query directly."
        )
