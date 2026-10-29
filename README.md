# Employee Management Database

Database schema and sample data for a basic employee management system. The
design supports departments, employees, projects, and employee-project
assignments.

See [ARCHITECTURE.md](./ARCHITECTURE.md) for the architecture and component
diagrams, data flows, security, observability, exception handling, and testing
strategies.

## InsightSQL application

InsightSQL is a local web app for asking questions about the bundled employee
database, reviewing generated SQL, and viewing results and recent query
history. It uses only Python's standard library; no package installation or
external AI API key is required. Natural-language conversion uses deterministic
templates for common employee, department, project, and assignment questions.
Unsupported questions receive suggestions, and SQL can be edited directly.

Requirements: Python 3.11 or newer. From the repository directory, start it
with:

```powershell
python app.py
```

Open [http://127.0.0.1:8000](http://127.0.0.1:8000). If your database is
elsewhere, specify it explicitly:

```powershell
python app.py --db "D:\path\to\employee_management.db" --port 8000
```

Stop the server with `Ctrl+C`. By default, InsightSQL reads
`employee_management.db` in this repository. It does not create or modify the
data database. If the file is absent, create it using the SQLite scripts above.

### InsightSQL safety and limits

- The server binds to the local machine by default and refuses non-local bind
  addresses. Do not expose it to a network without adding authentication and
  deployment hardening.
- The data database is opened in SQLite read-only mode. The application allows
  one `SELECT` statement only, restricts reads to the four application tables,
  and uses SQLite's authorizer as a second enforcement layer.
- Queries have a three-second execution limit, a 10,000-character SQL limit,
  and return at most 500 rows or 2 MB of results.
- Recent questions, SQL, and outcomes are stored locally in the ignored
  `.insightsql_history.db` file. Delete that file to remove local query history.
- The initial natural-language generator supports common count/list questions,
  employees in a named department, employee name search, and project
  assignments. Inspect generated SQL before running it; unsupported questions
  are not sent to an external service.

Run the test suite from the repository root with:

```powershell
python -m unittest discover -s tests -v
```

## Database contents

| Table | Purpose |
|---|---|
| `departments` | Department names and locations |
| `employees` | Employee details, department membership, and optional manager |
| `projects` | Project details, dates, status, and budget |
| `employee_projects` | Employee-to-project assignments, roles, and allocation |

`departments` has a one-to-many relationship with `employees`. Employees may
report to another employee through the self-referencing `manager_id`. Employees
and projects have a many-to-many relationship represented by
`employee_projects`, whose composite primary key is `(employee_id, project_id)`.

The sample data contains 5 departments, 20 employees, 10 projects, and 30
employee-project assignments.

## Files

| File | Description |
|---|---|
| [`schema.sql`](./schema.sql) | PostgreSQL table definitions and indexes |
| [`seed.sql`](./seed.sql) | PostgreSQL sample data |
| [`sqlite_schema.sql`](./sqlite_schema.sql) | SQLite table definitions and indexes |
| [`sqlite_seed.sql`](./sqlite_seed.sql) | SQLite sample data |
| [`app.py`](./app.py) | InsightSQL local application entry point |
| [`insightsql/`](./insightsql/) | SQL generation, validation, execution, history, and HTTP API |
| [`static/`](./static/) | InsightSQL browser interface |
| [`tests/`](./tests/) | Standard-library unit and integration tests |

## PostgreSQL

Create or connect to an empty PostgreSQL database, then run the schema followed
by the seed data:

```sh
psql -d employee_management -f schema.sql
psql -d employee_management -f seed.sql
```

Replace `employee_management` with the name of your database. The seed script
runs its inserts in a transaction and displays the resulting row counts.

## SQLite

From this directory, create and populate a database with the SQLite CLI:

```sh
sqlite3 employee_management.db
```

At the `sqlite>` prompt, run:

```sql
.read sqlite_schema.sql
.read sqlite_seed.sql
.quit
```

The SQLite scripts enable foreign-key checks. Since SQLite applies this setting
per connection, enable it for other connections that need foreign-key
enforcement:

```sql
PRAGMA foreign_keys = ON;
```

## Constraints and notes

- IDs are explicit in the sample data; the scripts do not rely on generated
  identity values.
- Department and project names, and employee emails, must be unique.
- Salary and project budget cannot be negative.
- Project end dates cannot precede start dates.
- Assignment allocation must be greater than 0 and no more than 100 percent.
- Allocation is validated per assignment; combined allocation across an
  employee's projects is not constrained by these scripts.