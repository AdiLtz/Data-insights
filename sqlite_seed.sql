-- SQLite sample data.
-- Requires sqlite_schema.sql to have been applied first.
-- Inserts 5 departments, 20 employees, 10 projects, and 30 assignments.
-- Keep this pragma enabled on each SQLite connection for FK enforcement.

PRAGMA foreign_keys = ON;
BEGIN TRANSACTION;

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

COMMIT;

SELECT 'departments' AS table_name, COUNT(*) AS row_count FROM departments
UNION ALL
SELECT 'employees', COUNT(*) FROM employees
UNION ALL
SELECT 'projects', COUNT(*) FROM projects
UNION ALL
SELECT 'employee_projects', COUNT(*) FROM employee_projects;
