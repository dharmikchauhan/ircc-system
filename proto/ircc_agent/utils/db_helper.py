import os
import sqlite3
from pathlib import Path

# Resolve paths relative to this file so they work regardless of CWD
_HERE = Path(__file__).resolve().parent          # ircc_agent/utils/
_AGENT_ROOT = _HERE.parent                  # proto/
DB_PATH = str(_AGENT_ROOT / "mock-data" / "xyzmart-erp.db")
_SQL_INIT = str(_AGENT_ROOT / "mock-data" / "db-setup.sql")

def _init_database():
    # Check if the database file already exists
    if os.path.exists(DB_PATH):
        print(f"Mock database '{DB_PATH}' already exists. Skipping initialization.")
        return

    print(f"Mock database '{DB_PATH}' not found. Initializing with data...")

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.executescript(open(_SQL_INIT).read())
        conn.commit()
        print("Database initialized and mock data inserted successfully.")


def _execute_read_query(query: str, params: tuple) -> dict:
    """Internal helper to extract data from mock SQLite database."""
    _init_database()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            row = cursor.fetchone()
            if row:
                return dict(row)
            return {"error": "No data found in local mock database."}
    except sqlite3.Error as e:
        return {"error": f"Local database failure: {str(e)}"}


def _execute_fetchall_query(query: str, params: tuple) -> list[dict]:
    """Internal helper to extract all matched data from mock SQLite database."""
    _init_database()
    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()
            cursor.execute(query, params)
            rows = cursor.fetchall()
            if rows:
                return [dict(row) for row in rows]
            return {"error": "No data found in local mock database."}
    except sqlite3.Error as e:
        return {"error": f"Local database failure: {str(e)}"}