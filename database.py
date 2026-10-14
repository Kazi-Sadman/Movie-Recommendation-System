"""
Simple SQLite database for watchlist and favorites.
Beginner-friendly: just a few functions, no ORM, no complex code.
"""

import os
import sqlite3
from pathlib import Path
from typing import List, Optional

# On Render, set DB_PATH to a file inside a mounted Persistent Disk
# (e.g. /var/data/movies.db). Locally it defaults to ./movies.db
DB_PATH = os.getenv("DB_PATH", str(Path(__file__).resolve().parent / "movies.db"))


def get_connection() -> sqlite3.Connection:
    """Open a connection and make rows behave like dictionaries."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create the tables if they don't exist yet. Safe to call every startup."""
    conn = get_connection()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS collection (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                tmdb_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                poster_url TEXT,
                release_date TEXT,
                vote_average REAL,
                kind TEXT NOT NULL,          -- 'watchlist' or 'favorite'
                watched INTEGER NOT NULL DEFAULT 0,
                added_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(tmdb_id, kind)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_item(tmdb_id: int, title: str, poster_url: Optional[str],
             release_date: Optional[str], vote_average: Optional[float],
             kind: str) -> bool:
    """Add a movie. Returns False if it was already there (duplicate)."""
    conn = get_connection()
    try:
        conn.execute(
            """
            INSERT OR IGNORE INTO collection
                (tmdb_id, title, poster_url, release_date, vote_average, kind)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (tmdb_id, title, poster_url, release_date, vote_average, kind),
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()


def remove_item(tmdb_id: int, kind: str) -> bool:
    conn = get_connection()
    try:
        cur = conn.execute(
            "DELETE FROM collection WHERE tmdb_id = ? AND kind = ?",
            (tmdb_id, kind),
        )
        conn.commit()
        return cur.rowcount > 0
    finally:
        conn.close()


def list_items(kind: str) -> List[dict]:
    conn = get_connection()
    try:
        rows = conn.execute(
            "SELECT * FROM collection WHERE kind = ? ORDER BY added_at DESC",
            (kind,),
        ).fetchall()
        return [dict(r) for r in rows]
    finally:
        conn.close()


def toggle_watched(tmdb_id: int) -> Optional[dict]:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT watched FROM collection WHERE tmdb_id = ? AND kind = 'watchlist'",
            (tmdb_id,),
        ).fetchone()
        if row is None:
            return None
        new_value = 0 if row["watched"] else 1
        conn.execute(
            "UPDATE collection SET watched = ? WHERE tmdb_id = ? AND kind = 'watchlist'",
            (new_value, tmdb_id),
        )
        conn.commit()
        return {"tmdb_id": tmdb_id, "watched": bool(new_value)}
    finally:
        conn.close()


def is_in_collection(tmdb_id: int, kind: str) -> bool:
    conn = get_connection()
    try:
        row = conn.execute(
            "SELECT 1 FROM collection WHERE tmdb_id = ? AND kind = ?",
            (tmdb_id, kind),
        ).fetchone()
        return row is not None
    finally:
        conn.close()