"""
SQLite Database Layer for X Assistant (Phase 3 Upgrade).
Provides persistent storage for conversations, commands, todos, notes, reminders, user preferences,
memory buffer, command stats, audit logs, clipboard history, calendar events, and pomodoro sessions.
"""

import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from config.settings import settings
from core.logger import logger


class DatabaseManager:
    """Manages SQLite connections and Phase-3 CRUD operations."""

    def __init__(self, db_path: Optional[str] = None) -> None:
        self.db_path = str(db_path or settings.paths.db_path)
        self.init_db()

    def get_connection(self) -> sqlite3.Connection:
        """Get database connection with dict row factory."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_db(self) -> None:
        """Initialize database schema tables for Phase-1, Phase-2 & Phase-3."""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()

                # Phase-1 & 2 Tables
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS conversation_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_input TEXT NOT NULL,
                        assistant_response TEXT NOT NULL,
                        language TEXT DEFAULT 'en',
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        command TEXT NOT NULL,
                        status TEXT NOT NULL,
                        details TEXT,
                        executed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS todos (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        task TEXT NOT NULL,
                        is_completed BOOLEAN DEFAULT 0,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS notes (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        content TEXT NOT NULL,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS reminders (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        message TEXT NOT NULL,
                        remind_at DATETIME NOT NULL,
                        status TEXT DEFAULT 'pending',
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS user_preferences (
                        pref_key TEXT PRIMARY KEY,
                        pref_value TEXT NOT NULL,
                        updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS memory_buffer (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        memory_key TEXT NOT NULL,
                        memory_value TEXT NOT NULL,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS command_stats (
                        command TEXT PRIMARY KEY,
                        usage_count INTEGER DEFAULT 1,
                        last_used_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Phase-3: Audit Logs table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS audit_logs (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        action_type TEXT NOT NULL,
                        target_item TEXT NOT NULL,
                        user_confirmed BOOLEAN DEFAULT 1,
                        status TEXT DEFAULT 'SUCCESS',
                        details TEXT,
                        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Phase-3: Clipboard History table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS clipboard_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        content TEXT NOT NULL,
                        copied_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Phase-3: Calendar Events table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS calendar_events (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        title TEXT NOT NULL,
                        event_date TEXT NOT NULL,
                        event_time TEXT DEFAULT '09:00 AM',
                        description TEXT,
                        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                # Phase-3: Pomodoro Sessions table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS pomodoro_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        focus_minutes INTEGER DEFAULT 25,
                        break_minutes INTEGER DEFAULT 5,
                        completed_at DATETIME DEFAULT CURRENT_TIMESTAMP
                    )
                """)

                conn.commit()
                logger.info("Phase-3 Database schema initialized successfully.")

        except Exception as err:
            logger.error(f"Database initialization error: {err}")

    # Phase-3: Audit Logs CRUD
    def log_audit_event(self, action_type: str, target_item: str, user_confirmed: bool = True, status: str = "SUCCESS", details: str = "") -> None:
        """Record critical action to security audit logs."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO audit_logs (action_type, target_item, user_confirmed, status, details) VALUES (?, ?, ?, ?, ?)",
                    (action_type, target_item, 1 if user_confirmed else 0, status, details)
                )
                conn.commit()
                logger.info(f"Audit Logged: {action_type} -> {target_item} [{status}]")
        except Exception as err:
            logger.error(f"Failed to record audit event: {err}")

    def get_recent_audit_logs(self, limit: int = 15) -> List[Dict[str, Any]]:
        """Retrieve recent security audit logs."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT action_type, target_item, user_confirmed, status, details, timestamp FROM audit_logs ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch audit logs: {err}")
            return []

    # Phase-3: Clipboard History CRUD
    def save_clipboard_text(self, content: str) -> None:
        """Save text snippet to clipboard history."""
        if not content or not content.strip():
            return
        try:
            with self.get_connection() as conn:
                # Avoid inserting duplicate consecutive text
                cursor = conn.execute("SELECT content FROM clipboard_history ORDER BY id DESC LIMIT 1")
                row = cursor.fetchone()
                if row and row["content"] == content:
                    return

                conn.execute("INSERT INTO clipboard_history (content) VALUES (?)", (content,))
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to save clipboard content: {err}")

    def get_clipboard_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent clipboard history snippets."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT id, content, copied_at FROM clipboard_history ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch clipboard history: {err}")
            return []

    # Phase-3: Calendar Events CRUD
    def add_calendar_event(self, title: str, event_date: str, event_time: str = "09:00 AM", description: str = "") -> int:
        """Add calendar event."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "INSERT INTO calendar_events (title, event_date, event_time, description) VALUES (?, ?, ?, ?)",
                    (title, event_date, event_time, description)
                )
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to add calendar event: {err}")
            return 0

    def get_upcoming_calendar_events(self, limit: int = 5) -> List[Dict[str, Any]]:
        """Get upcoming calendar events."""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT id, title, event_date, event_time, description FROM calendar_events ORDER BY id DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch calendar events: {err}")
            return []

    # Phase-3: Pomodoro Sessions CRUD
    def log_pomodoro_session(self, focus_minutes: int = 25, break_minutes: int = 5) -> None:
        """Record completed Pomodoro focus session."""
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO pomodoro_sessions (focus_minutes, break_minutes) VALUES (?, ?)",
                    (focus_minutes, break_minutes)
                )
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to log pomodoro session: {err}")

    # Conversation & Command History
    def log_conversation(self, user_input: str, response: str, language: str = "en") -> None:
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

    def log_command(self, command: str, status: str, details: str = "") -> None:
        try:
            with self.get_connection() as conn:
                conn.execute(
                    "INSERT INTO command_history (command, status, details) VALUES (?, ?, ?)",
                    (command, status, details)
                )
                conn.execute("""
                    INSERT INTO command_stats (command, usage_count, last_used_at)
                    VALUES (?, 1, CURRENT_TIMESTAMP)
                    ON CONFLICT(command) DO UPDATE SET
                    usage_count = usage_count + 1,
                    last_used_at = CURRENT_TIMESTAMP
                """, (command,))
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to log command: {err}")

    def get_frequent_commands(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(
                    "SELECT command, usage_count, last_used_at FROM command_stats ORDER BY usage_count DESC LIMIT ?",
                    (limit,)
                )
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to get frequent commands: {err}")
            return []

    # Preferences, Memories, Todos, Notes, Reminders
    def set_user_preference(self, key: str, value: str) -> None:
        try:
            with self.get_connection() as conn:
                conn.execute("""
                    INSERT INTO user_preferences (pref_key, pref_value, updated_at)
                    VALUES (?, ?, CURRENT_TIMESTAMP)
                    ON CONFLICT(pref_key) DO UPDATE SET
                    pref_value = excluded.pref_value,
                    updated_at = CURRENT_TIMESTAMP
                """, (key.lower().strip(), value.strip()))
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to set preference {key}: {err}")

    def get_user_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT pref_value FROM user_preferences WHERE pref_key = ?", (key.lower().strip(),))
                row = cursor.fetchone()
                return row["pref_value"] if row else default
        except Exception as err:
            logger.error(f"Failed to fetch preference {key}: {err}")
            return default

    def get_all_preferences(self) -> Dict[str, str]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT pref_key, pref_value FROM user_preferences")
                return {row["pref_key"]: row["pref_value"] for row in cursor.fetchall()}
        except Exception as err:
            logger.error(f"Failed to fetch preferences: {err}")
            return {}

    def add_memory(self, key: str, value: str) -> None:
        try:
            with self.get_connection() as conn:
                conn.execute("INSERT INTO memory_buffer (memory_key, memory_value) VALUES (?, ?)", (key.lower().strip(), value.strip()))
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to store memory: {err}")

    def get_all_memories(self, limit: int = 20) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT memory_key, memory_value, timestamp FROM memory_buffer ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch memories: {err}")
            return []

    def add_todo(self, task: str) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("INSERT INTO todos (task) VALUES (?)", (task,))
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to add todo: {err}")
            return 0

    def get_pending_todos(self) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT id, task, created_at FROM todos WHERE is_completed = 0 ORDER BY id ASC")
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to get pending todos: {err}")
            return []

    def complete_todo(self, todo_id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("UPDATE todos SET is_completed = 1 WHERE id = ?", (todo_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as err:
            logger.error(f"Failed to complete todo: {err}")
            return False

    def add_note(self, title: str, content: str) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("INSERT INTO notes (title, content) VALUES (?, ?)", (title, content))
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to add note: {err}")
            return 0

    def delete_note(self, note_id: int) -> bool:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("DELETE FROM notes WHERE id = ?", (note_id,))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as err:
            logger.error(f"Failed to delete note {note_id}: {err}")
            return False

    def get_notes(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT id, title, content, created_at FROM notes ORDER BY id DESC LIMIT ?", (limit,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch notes: {err}")
            return []

    def add_reminder(self, message: str, remind_at: str) -> int:
        try:
            with self.get_connection() as conn:
                cursor = conn.execute("INSERT INTO reminders (message, remind_at) VALUES (?, ?)", (message, remind_at))
                conn.commit()
                return cursor.lastrowid or 0
        except Exception as err:
            logger.error(f"Failed to add reminder: {err}")
            return 0

    def get_due_reminders(self) -> List[Dict[str, Any]]:
        try:
            now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with self.get_connection() as conn:
                cursor = conn.execute("SELECT id, message, remind_at FROM reminders WHERE status = 'pending' AND remind_at <= ?", (now_str,))
                return [dict(row) for row in cursor.fetchall()]
        except Exception as err:
            logger.error(f"Failed to fetch due reminders: {err}")
            return []

    def mark_reminder_triggered(self, reminder_id: int) -> None:
        try:
            with self.get_connection() as conn:
                conn.execute("UPDATE reminders SET status = 'triggered' WHERE id = ?", (reminder_id,))
                conn.commit()
        except Exception as err:
            logger.error(f"Failed to update reminder status: {err}")


# Global Phase-3 database instance
db = DatabaseManager()
