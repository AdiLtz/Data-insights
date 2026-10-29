-- Employee Management System database design
-- Database: PostgreSQL
--
-- Table distribution:
--   departments       One row per department; one-to-many with employees.
--   employees         One row per employee; belongs to a department and may
--                     report to another employee.
--   projects          One row per project.
--   employee_projects Resolves the many-to-many relationship between
--                     employees and projects; stores assignment details.
--
-- Primary keys:
--   departments       department_id
--   employees         employee_id
--   projects          project_id
--   employee_projects (employee_id, project_id)
--
-- Foreign keys:
--   employees.department_id            -> departments.department_id
--   employees.manager_id               -> employees.employee_id
--   employee_projects.employee_id      -> employees.employee_id
--   employee_projects.project_id       -> projects.project_id
--
-- ER diagram (Mermaid):
-- erDiagram
--     DEPARTMENTS ||--o{ EMPLOYEES : contains
--     EMPLOYEES o|--o{ EMPLOYEES : manages
--     EMPLOYEES ||--o{ EMPLOYEE_PROJECTS : assigned_to
--     PROJECTS ||--o{ EMPLOYEE_PROJECTS : includes
--
--     DEPARTMENTS {
--         bigint department_id PK
--         varchar department_name UK
--         varchar location
--     }
--     EMPLOYEES {
--         bigint employee_id PK
--         bigint department_id FK
--         bigint manager_id FK
--         varchar first_name
--         varchar last_name
--         varchar email UK
--         varchar job_title
--         date hire_date
--         numeric salary
--     }
--     PROJECTS {
--         bigint project_id PK
--         varchar project_name UK
--         date start_date
--         date end_date
--         varchar status
--         numeric budget
--     }
--     EMPLOYEE_PROJECTS {
--         bigint employee_id PK, FK
--         bigint project_id PK, FK
--         date assigned_on
--         varchar project_role
--         numeric allocation_pct
--     }
--
-- Run this script in an empty database. It creates 5 departments, 20
-- employees, 10 projects, and 30 employee-project assignments.

BEGIN;

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

INSERT INTO departments (department_id, department_name, location) VALUES
    (1, 'Engineering', 'Bengaluru'),
    (2, 'Human Resources', 'Bengaluru'),
    (3, 'Finance', 'Mumbai'),
    (4, 'Sales', 'Delhi'),
    (5, 'Operations', 'Hyderabad');

-- Each department has one manager and three employees.
INSERT INTO employees (
    employee_id, department_id, manager_id, first_name, last_name,
    email, job_title, hire_date, salary
) VALUES
    (1001, 1, NULL, 'Aarav', 'Sharma', 'aarav.sharma@example.com',
     'Engineering Manager', '2020-03-16', 125000.00),
    (1002, 1, 1001, 'Diya', 'Patel', 'diya.patel@example.com',
     'Senior Software Engineer', '2021-06-07', 98000.00),
    (1003, 1, 1001, 'Ishaan', 'Rao', 'ishaan.rao@example.com',
     'Software Engineer', '2022-01-10', 78000.00),
    (1004, 1, 1001, 'Meera', 'Nair', 'meera.nair@example.com',
     'QA Engineer', '2023-04-03', 72000.00),

    (1005, 2, NULL, 'Ananya', 'Iyer', 'ananya.iyer@example.com',
     'HR Manager', '2019-08-12', 110000.00),
    (1006, 2, 1005, 'Kabir', 'Mehta', 'kabir.mehta@example.com',
     'Recruiter', '2021-02-15', 68000.00),
    (1007, 2, 1005, 'Sara', 'Khan', 'sara.khan@example.com',
     'HR Business Partner', '2022-09-05', 75000.00),
    (1008, 2, 1005, 'Vihaan', 'Das', 'vihaan.das@example.com',
     'Training Coordinator', '2024-01-08', 62000.00),

    (1009, 3, NULL, 'Rohan', 'Gupta', 'rohan.gupta@example.com',
     'Finance Manager', '2018-11-19', 130000.00),
    (1010, 3, 1009, 'Tara', 'Menon', 'tara.menon@example.com',
     'Financial Analyst', '2020-07-20', 85000.00),
    (1011, 3, 1009, 'Arjun', 'Singh', 'arjun.singh@example.com',
     'Senior Accountant', '2021-10-11', 82000.00),
    (1012, 3, 1009, 'Nisha', 'Reddy', 'nisha.reddy@example.com',
     'Accounts Executive', '2023-02-06', 64000.00),

    (1013, 4, NULL, 'Kavya', 'Joshi', 'kavya.joshi@example.com',
     'Sales Manager', '2019-05-13', 118000.00),
    (1014, 4, 1013, 'Aditya', 'Verma', 'aditya.verma@example.com',
     'Account Executive', '2021-03-22', 76000.00),
    (1015, 4, 1013, 'Pooja', 'Kulkarni', 'pooja.kulkarni@example.com',
     'Sales Representative', '2022-08-01', 70000.00),
    (1016, 4, 1013, 'Rahul', 'Bose', 'rahul.bose@example.com',
     'Business Development Executive', '2024-02-12', 66000.00),

    (1017, 5, NULL, 'Neha', 'Kapoor', 'neha.kapoor@example.com',
     'Operations Manager', '2018-06-18', 120000.00),
    (1018, 5, 1017, 'Dev', 'Malhotra', 'dev.malhotra@example.com',
     'Operations Analyst', '2020-12-07', 79000.00),
    (1019, 5, 1017, 'Mira', 'Chowdhury', 'mira.chowdhury@example.com',
     'Logistics Coordinator', '2022-05-16', 67000.00),
    (1020, 5, 1017, 'Karan', 'Pillai', 'karan.pillai@example.com',
     'Facilities Coordinator', '2023-09-25', 61000.00);

INSERT INTO projects (
    project_id, project_name, start_date, end_date, status, budget
) VALUES
    (2001, 'Employee Self-Service Portal', '2025-01-15', NULL, 'active', 250000.00),
    (2002, 'Cloud Infrastructure Upgrade', '2025-02-01', NULL, 'active', 400000.00),
    (2003, 'Quality Automation Initiative', '2025-03-10', '2025-12-15', 'active', 150000.00),
    (2004, 'Recruitment Process Improvement', '2025-01-20', '2025-08-30', 'completed', 90000.00),
    (2005, 'Learning Management Rollout', '2025-04-01', NULL, 'active', 120000.00),
    (2006, 'Financial Reporting Modernization', '2025-02-10', NULL, 'active', 210000.00),
    (2007, 'Annual Budget Planning', '2025-05-01', '2025-11-30', 'active', 80000.00),
    (2008, 'Customer Relationship Platform', '2025-03-01', NULL, 'active', 320000.00),
    (2009, 'Sales Analytics Dashboard', '2025-06-15', NULL, 'planned', 175000.00),
    (2010, 'Regional Operations Expansion', '2025-01-05', NULL, 'active', 500000.00);

INSERT INTO employee_projects (
    employee_id, project_id, assigned_on, project_role, allocation_pct
) VALUES
    (1001, 2001, '2025-01-15', 'Technical Lead', 40.00),
    (1001, 2002, '2025-02-01', 'Architecture Lead', 30.00),
    (1002, 2001, '2025-01-20', 'Backend Engineer', 60.00),
    (1002, 2003, '2025-03-10', 'Automation Engineer', 30.00),
    (1003, 2002, '2025-02-05', 'Cloud Engineer', 50.00),
    (1004, 2003, '2025-03-12', 'QA Analyst', 60.00),

    (1005, 2004, '2025-01-20', 'Project Sponsor', 20.00),
    (1005, 2005, '2025-04-01', 'HR Workstream Lead', 30.00),
    (1006, 2004, '2025-01-22', 'Recruitment Lead', 50.00),
    (1007, 2005, '2025-04-03', 'Change Manager', 40.00),
    (1007, 2006, '2025-02-12', 'HR Liaison', 20.00),
    (1008, 2006, '2025-02-15', 'Training Coordinator', 35.00),

    (1009, 2007, '2025-05-01', 'Finance Lead', 40.00),
    (1009, 2008, '2025-03-01', 'Budget Advisor', 20.00),
    (1010, 2007, '2025-05-05', 'Budget Analyst', 50.00),
    (1011, 2008, '2025-03-05', 'Reporting Analyst', 40.00),
    (1011, 2009, '2025-06-15', 'Data Analyst', 25.00),
    (1012, 2009, '2025-06-20', 'Accounts Analyst', 35.00),

    (1013, 2010, '2025-01-05', 'Sales Sponsor', 20.00),
    (1013, 2001, '2025-01-15', 'Customer Requirements Lead', 15.00),
    (1014, 2010, '2025-01-10', 'Regional Account Lead', 50.00),
    (1015, 2002, '2025-02-10', 'Customer Liaison', 20.00),
    (1015, 2010, '2025-01-12', 'Regional Sales Representative', 40.00),
    (1016, 2003, '2025-03-15', 'Process Reviewer', 25.00),

    (1017, 2004, '2025-01-20', 'Operations Sponsor', 15.00),
    (1017, 2005, '2025-04-01', 'Operations Lead', 25.00),
    (1018, 2005, '2025-04-05', 'Process Analyst', 40.00),
    (1019, 2006, '2025-02-20', 'Logistics Analyst', 30.00),
    (1019, 2007, '2025-05-10', 'Operations Analyst', 25.00),
    (1020, 2008, '2025-03-10', 'Facilities Coordinator', 20.00);

-- Expected counts: departments=5, employees=20, projects=10,
-- employee_projects=30.
SELECT 'departments' AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'employee_projects', COUNT(*) FROM employee_projects;

COMMIT;
