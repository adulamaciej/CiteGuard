import os
import sqlite3
from datetime import datetime

from config import BASE_DIR

DB_PATH = os.path.join(BASE_DIR, "data", "results_log.db")


def get_connection():
    """Opens a connection to the SQLite database, creating the table if needed."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.execute("""
        CREATE TABLE IF NOT EXISTS results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            question TEXT NOT NULL,
            answer TEXT NOT NULL,
            verified INTEGER NOT NULL,
            reasoning TEXT NOT NULL
        )
    """)
    return conn


def log_result(question: str, answer: str, verified: bool, reasoning: str):
    """Inserts one row into the results table after each /ask call."""
    conn = get_connection()
    conn.execute(
        "INSERT INTO results (timestamp, question, answer, verified, reasoning) VALUES (?, ?, ?, ?, ?)",
        (datetime.utcnow().isoformat(), question, answer, int(verified), reasoning),
    )
    conn.commit()
    conn.close()


def fetch_all_results():
    """Returns all logged results as a list of dicts."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute(
        "SELECT timestamp, question, answer, verified, reasoning FROM results ORDER BY id"
    ).fetchall()
    conn.close()
    return [dict(row) for row in rows]


def fetch_stats():
    """Returns aggregate stats: count and average answer length, grouped by verified status."""
    conn = get_connection()
    conn.row_factory = sqlite3.Row
    rows = conn.execute("""
        SELECT verified, COUNT(*) as count, AVG(LENGTH(answer)) as avg_answer_length
        FROM results
        GROUP BY verified
    """).fetchall()
    conn.close()
    return [dict(row) for row in rows]