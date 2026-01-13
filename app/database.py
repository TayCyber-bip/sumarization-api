"""Database utilities for chat history management"""

import sqlite3
from contextlib import contextmanager
from typing import List, Dict

DB_PATH = "chat_history.db"


@contextmanager
def get_db_connection():
    """Context manager for database connections"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_database():
    """Initialize the database with chat history table"""
    with get_db_connection() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS chat_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT NOT NULL,
                user_message TEXT NOT NULL,
                assistant_message TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """
        )
        # Create indexes for better performance
        try:
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_session_id ON chat_history(session_id)"
            )
            conn.execute(
                "CREATE INDEX IF NOT EXISTS idx_created_at ON chat_history(created_at)"
            )
        except:
            pass  # Indexes might already exist


def get_chat_history(session_id: str, limit: int = 10) -> List[Dict[str, str]]:
    """Get chat history from database for a session"""
    with get_db_connection() as conn:
        cursor = conn.execute(
            "SELECT user_message, assistant_message FROM chat_history WHERE session_id = ? ORDER BY created_at DESC LIMIT ?",
            (session_id, limit),
        )
        rows = cursor.fetchall()
        # Reverse to get chronological order
        history = []
        for row in reversed(rows):
            history.append(
                {"user": row["user_message"], "assistant": row["assistant_message"]}
            )
        return history


def save_chat_message(session_id: str, user_message: str, assistant_message: str):
    """Save chat message to database"""
    with get_db_connection() as conn:
        conn.execute(
            "INSERT INTO chat_history (session_id, user_message, assistant_message) VALUES (?, ?, ?)",
            (session_id, user_message, assistant_message),
        )
