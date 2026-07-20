"""
Unit Test Suite for X Assistant.
Tests Database CRUD operations, Intent Classification, and Utility modules.
"""

import os
import unittest
from pathlib import Path
from config.settings import Settings
from core.database import DatabaseManager
from brain.intent_parser import IntentParser
from utils.helpers import clean_text, is_bangla_text, format_timestamp


class TestXAssistant(unittest.TestCase):
    """Test suite covering core business logic of X Assistant."""

    def setUp(self) -> None:
        """Set up temporary testing database."""
        self.test_db_path = Path("data/test_x_assistant.db")
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.db = DatabaseManager(db_path=str(self.test_db_path))
        self.parser = IntentParser()

    def tearDown(self) -> None:
        """Clean up test database."""
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    # Database Tests
    def test_database_todos(self) -> None:
        """Test Todo creation, fetching, and completion."""
        todo_id = self.db.add_todo("Buy groceries")
        self.assertGreater(todo_id, 0)

        pending = self.db.get_pending_todos()
        self.assertEqual(len(pending), 1)
        self.assertEqual(pending[0]["task"], "Buy groceries")

        completed = self.db.complete_todo(todo_id)
        self.assertTrue(completed)
        self.assertEqual(len(self.db.get_pending_todos()), 0)

    def test_database_notes(self) -> None:
        """Test Note saving and reading."""
        note_id = self.db.add_note("Meeting", "Project discussion at 3 PM")
        self.assertGreater(note_id, 0)

        notes = self.db.get_notes()
        self.assertEqual(len(notes), 1)
        self.assertEqual(notes[0]["content"], "Project discussion at 3 PM")

    def test_database_conversations(self) -> None:
        """Test conversation logging."""
        self.db.log_conversation("Hello", "Hi there!", "en")
        history = self.db.get_recent_conversations()
        self.assertEqual(len(history), 1)
        self.assertEqual(history[0]["user_input"], "Hello")

    # Intent Parser Tests
    def test_intent_app_launch(self) -> None:
        """Test app launch intent recognition."""
        intent = self.parser.parse("open chrome")
        self.assertEqual(intent.name, "open_app")
        self.assertEqual(intent.params.get("app"), "chrome")

    def test_intent_time_and_date(self) -> None:
        """Test time and date query classification."""
        intent_time = self.parser.parse("what time is it")
        self.assertEqual(intent_time.name, "get_time")

        intent_date = self.parser.parse("what is today's date")
        self.assertEqual(intent_date.name, "get_date")

    def test_intent_volume_control(self) -> None:
        """Test volume adjustment intent classification."""
        intent = self.parser.parse("volume up")
        self.assertEqual(intent.name, "volume_control")
        self.assertEqual(intent.params.get("command"), "up")

    # Utility Function Tests
    def test_bangla_text_detection(self) -> None:
        """Test detection of Bangla characters."""
        self.assertTrue(is_bangla_text("হ্যালো কেমন আছেন"))
        self.assertFalse(is_bangla_text("Hello how are you"))

    def test_clean_text(self) -> None:
        """Test text normalization."""
        self.assertEqual(clean_text("  hello   world  "), "hello world")


if __name__ == "__main__":
    unittest.main()
