import sqlite3
from contextlib import contextmanager
from pathlib import Path

from config import DATA_DIR, DB_PATH

SCHEMA = """
CREATE TABLE IF NOT EXISTS employees (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT UNIQUE NOT NULL, department TEXT NOT NULL, role TEXT NOT NULL, salary REAL NOT NULL, status TEXT NOT NULL DEFAULT 'active');
CREATE TABLE IF NOT EXISTS candidates (id INTEGER PRIMARY KEY, name TEXT NOT NULL, email TEXT NOT NULL, job_title TEXT NOT NULL, stage TEXT NOT NULL DEFAULT 'applied', score REAL DEFAULT 0);
CREATE TABLE IF NOT EXISTS time_entries (id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL, event TEXT NOT NULL, occurred_at TEXT NOT NULL, note TEXT DEFAULT '', FOREIGN KEY(employee_id) REFERENCES employees(id));
CREATE TABLE IF NOT EXISTS payroll_runs (id INTEGER PRIMARY KEY, period TEXT NOT NULL, gross REAL NOT NULL, deductions REAL NOT NULL, net REAL NOT NULL, status TEXT NOT NULL, created_at TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS benefits (id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL, name TEXT NOT NULL, value REAL NOT NULL, active INTEGER NOT NULL DEFAULT 1, FOREIGN KEY(employee_id) REFERENCES employees(id));
CREATE TABLE IF NOT EXISTS courses (id INTEGER PRIMARY KEY, title TEXT NOT NULL, duration_hours REAL NOT NULL, completion_rate REAL NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS performance_reviews (id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL, cycle TEXT NOT NULL, score REAL NOT NULL, status TEXT NOT NULL, FOREIGN KEY(employee_id) REFERENCES employees(id));
CREATE TABLE IF NOT EXISTS shifts (id INTEGER PRIMARY KEY, employee_id INTEGER NOT NULL, starts_at TEXT NOT NULL, ends_at TEXT NOT NULL, status TEXT NOT NULL DEFAULT 'planned', FOREIGN KEY(employee_id) REFERENCES employees(id));
CREATE TABLE IF NOT EXISTS feedback (id INTEGER PRIMARY KEY, employee_id INTEGER, category TEXT NOT NULL, message TEXT NOT NULL, sentiment TEXT NOT NULL, created_at TEXT NOT NULL, FOREIGN KEY(employee_id) REFERENCES employees(id));
"""


@contextmanager
def connection():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def initialize() -> None:
    with connection() as conn:
        conn.executescript(SCHEMA)


def rows(query: str, params: tuple = ()) -> list[dict]:
    with connection() as conn:
        return [dict(row) for row in conn.execute(query, params).fetchall()]


def insert(table: str, values: dict) -> dict:
    columns = ", ".join(values)
    marks = ", ".join("?" for _ in values)
    with connection() as conn:
        cursor = conn.execute(f"INSERT INTO {table} ({columns}) VALUES ({marks})", tuple(values.values()))
        return {"id": cursor.lastrowid, **values}
