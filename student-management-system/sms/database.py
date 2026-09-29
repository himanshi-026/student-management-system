"""SQLite connection and schema."""
import sqlite3

SCHEMA = """
CREATE TABLE IF NOT EXISTS students (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    reg_no      TEXT NOT NULL UNIQUE,
    name        TEXT NOT NULL,
    email       TEXT NOT NULL UNIQUE,
    phone       TEXT NOT NULL,
    department  TEXT NOT NULL,
    year        INTEGER NOT NULL CHECK (year BETWEEN 1 AND 4),
    created_at  TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS courses (
    code     TEXT PRIMARY KEY,
    title    TEXT NOT NULL,
    credits  INTEGER NOT NULL CHECK (credits BETWEEN 1 AND 10)
);
CREATE TABLE IF NOT EXISTS enrollments (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_code  TEXT    NOT NULL REFERENCES courses(code) ON DELETE CASCADE,
    marks        REAL CHECK (marks IS NULL OR (marks >= 0 AND marks <= 100)),
    UNIQUE (student_id, course_code)
);
CREATE TABLE IF NOT EXISTS attendance (
    id           INTEGER PRIMARY KEY AUTOINCREMENT,
    student_id   INTEGER NOT NULL REFERENCES students(id) ON DELETE CASCADE,
    course_code  TEXT    NOT NULL REFERENCES courses(code) ON DELETE CASCADE,
    day          TEXT    NOT NULL,
    present      INTEGER NOT NULL CHECK (present IN (0, 1)),
    UNIQUE (student_id, course_code, day)
);
"""


def connect(path: str = "sms.db") -> sqlite3.Connection:
    conn = sqlite3.connect(path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
    conn.executescript(SCHEMA)
    return conn
