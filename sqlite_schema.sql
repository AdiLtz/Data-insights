-- SQLite schema for the employee management system.
-- Apply to an empty database before running sqlite_seed.sql.
-- Foreign-key enforcement is per connection; enable it in the client too.

PRAGMA foreign_keys = ON;

CREATE TABLE departments (
    department_id   INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL UNIQUE,
    location        TEXT NOT NULL
);

CREATE TABLE employees (
    employee_id   INTEGER PRIMARY KEY,
    department_id INTEGER NOT NULL
        REFERENCES departments (department_id) ON DELETE RESTRICT,
    manager_id    INTEGER
        REFERENCES employees (employee_id) ON DELETE SET NULL,
    first_name    TEXT NOT NULL,
    last_name     TEXT NOT NULL,
    email         TEXT NOT NULL UNIQUE,
    job_title     TEXT NOT NULL,
    hire_date     TEXT NOT NULL,
    salary        NUMERIC NOT NULL CHECK (salary >= 0)
);

CREATE TABLE projects (
    project_id   INTEGER PRIMARY KEY,
    project_name TEXT NOT NULL UNIQUE,
    start_date   TEXT NOT NULL,
    end_date     TEXT,
    status       TEXT NOT NULL
        CHECK (status IN ('planned', 'active', 'completed', 'on_hold')),
    budget       NUMERIC NOT NULL CHECK (budget >= 0),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE employee_projects (
    employee_id    INTEGER NOT NULL
        REFERENCES employees (employee_id) ON DELETE CASCADE,
    project_id     INTEGER NOT NULL
        REFERENCES projects (project_id) ON DELETE CASCADE,
    assigned_on    TEXT NOT NULL,
    project_role   TEXT NOT NULL,
    allocation_pct NUMERIC NOT NULL
        CHECK (allocation_pct > 0 AND allocation_pct <= 100),
    PRIMARY KEY (employee_id, project_id)
);

CREATE INDEX idx_employees_department_id
    ON employees (department_id);

CREATE INDEX idx_employees_manager_id
    ON employees (manager_id);

CREATE INDEX idx_employee_projects_project_id
    ON employee_projects (project_id, employee_id);
