
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS incidents;

CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    role TEXT NOT NULL
);

CREATE TABLE incidents (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    category TEXT NOT NULL,
    location TEXT NOT NULL,
    person_involved TEXT NOT NULL,
    status TEXT DEFAULT 'Pending',
    assigned_dept TEXT,
    resolution_photo TEXT
);

INSERT INTO users (username, role) VALUES ('admin_user', 'admin'), ('student_user', 'student'), ('facilities_dept', 'department');
