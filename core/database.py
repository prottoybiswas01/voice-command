"""
SQLite Database Layer for X Assistant.
Provides persistent storage for conversation history, command history, todos, notes, and reminders.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import settings
from core.logger import logger


class DatabaseManager:
    """Manages SQLite connections and CRUD operations for X Assistant."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = str(db_path or settings.paths.db_path)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with dict row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initialize database schema tables."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Conversation history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_input TEXT NOT NULL,
                        assistant_response TEXT NOT NULL,
                        language TEXT DEFAULT 'en',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Command history table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command TEXT NOT NULL,
                        status TEXT NOT NULL,
                        details TEXT,
                        executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Todo list table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS todos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT NOT NULL,
                        is_completed BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Simple Notes table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Reminders table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL,
                        remind_at DATETIME NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                logger.info("Database schema initialized successfully.")

        except Exception as err:
            logger.error(f"Database initialization error: {err}")

    # Conversation History
    def log_conversation(self, user_input: str, response: str, language: str = "en") -> None:
        """Record a conversation exchange."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO conversation_history (user_input, assistant_response, language) VALUES (?, ?, ?)",
                    (user_input, response, language)
                )
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to log conversation: {err}")

    def get_recent_conversations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent conversation history."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT user_input, assistant_response, language, timestamp FROM conversation_history ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to retrieve conversation history: {err}")
            return []

    # Command History
    def log_command(self, command: str, status: str, details: str = "") -> None:
        """Record an executed command."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO command_history (command, status, details) VALUES (?, ?, ?)",
                    (command, status, details)
                )
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to log command: {err}")

    def get_recent_commands(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Retrieve recent command logs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT command, status, details, executed_at FROM command_history ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to retrieve command history: {err}")
            return []

    # Todos
    def add_todo(self, task: str) -> int:
        """Add a new todo task."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("INSERT INTO todos (task) VALUES (?)", (task,))
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to add todo: {err}")
            return 0

    def get_pending_todos(self) -> List[Dict[str, Any]]:
        """Retrieve all active todos."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT id, task, created_at FROM todos WHERE is_completed = 0 ORDER BY id ASC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to get pending todos: {err}")
            return []

    def complete_todo(self, todo_id: int) -> bool:
        """Mark a todo task as completed."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("UPDATE todos SET is_completed = 1 WHERE id = ?", (todo_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as err:
            logger.error(f"Failed to complete todo {todo_id}: {err}")
            return False

    # Notes
    def add_note(self, title: str, content: str) -> int:
        """Add a new note."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to save note: {err}")
            return 0

    def get_notes(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get list of notes."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch notes: {err}")
            return []

    # Reminders
    def add_reminder(self, message: str, remind_at: str) -> int:
        """Schedule a reminder (remind_at in 'YYYY-MM-DD HH:MM:SS' format)."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO reminders (message, remind_at) VALUES (?, ?)",
                    (message, remind_at)
                )
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to add reminder: {err}")
            return 0

    def get_due_reminders(self) -> List[Dict[str, Any]]:
        """Retrieve due reminders that are pending."""
        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, message, remind_at FROM reminders WHERE status = 'pending' AND remind_at <= ?",
                    (now_str,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch due reminders: {err}")
            return []

    def mark_reminder_triggered(self, reminder_id: int) -> None:
        """Mark reminder as completed/triggered."""
        try:
            with self.get_connection() as conn:
                conn.execute("UPDATE reminders SET status = 'triggered' WHERE id = ?", (reminder_id,))
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to update reminder status: {err}")


# Global database instance
db = DatabaseManager()
