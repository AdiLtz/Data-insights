# Employee Management Database

Database schema and sample data for a basic employee management system. The
design supports departments, employees, projects, and employee-project
assignments.

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