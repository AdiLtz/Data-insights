-- PostgreSQL schema for the employee management system.
-- Apply to an empty database before running seed.sql.

CREATE TABLE departments (
    department_id   BIGINT PRIMARY KEY,
    department_name VARCHAR(100) NOT NULL UNIQUE,
    location        VARCHAR(100) NOT NULL
);

CREATE TABLE employees (
    employee_id   BIGINT PRIMARY KEY,
    department_id BIGINT NOT NULL
        REFERENCES departments (department_id) ON DELETE RESTRICT,
    manager_id    BIGINT
        REFERENCES employees (employee_id) ON DELETE SET NULL,
    first_name    VARCHAR(100) NOT NULL,
    last_name     VARCHAR(100) NOT NULL,
    email         VARCHAR(254) NOT NULL UNIQUE,
    job_title     VARCHAR(100) NOT NULL,
    hire_date     DATE NOT NULL,
    salary        NUMERIC(12, 2) NOT NULL CHECK (salary >= 0)
);

CREATE TABLE projects (
    project_id   BIGINT PRIMARY KEY,
    project_name VARCHAR(150) NOT NULL UNIQUE,
    start_date   DATE NOT NULL,
    end_date     DATE,
    status       VARCHAR(20) NOT NULL
        CHECK (status IN ('planned', 'active', 'completed', 'on_hold')),
    budget       NUMERIC(14, 2) NOT NULL CHECK (budget >= 0),
    CHECK (end_date IS NULL OR end_date >= start_date)
);

CREATE TABLE employee_projects (
    employee_id    BIGINT NOT NULL
        REFERENCES employees (employee_id) ON DELETE CASCADE,
    project_id     BIGINT NOT NULL
        REFERENCES projects (project_id) ON DELETE CASCADE,
    assigned_on    DATE NOT NULL,
    project_role   VARCHAR(100) NOT NULL,
    allocation_pct NUMERIC(5, 2) NOT NULL
        CHECK (allocation_pct > 0 AND allocation_pct <= 100),
    PRIMARY KEY (employee_id, project_id)
);

CREATE INDEX idx_employees_department_id
    ON employees (department_id);

CREATE INDEX idx_employees_manager_id
    ON employees (manager_id);

CREATE INDEX idx_employee_projects_project_id
    ON employee_projects (project_id, employee_id);
