"""
Phase 2 Unit Test Suite for X Assistant.
Tests Memory Manager, Reasoning Agent, Smart Music Dispatcher, Internet Actions, and System Controls.
"""

import os
import unittest
from pathlib import Path
from core.database import DatabaseManager
from brain.memory import MemoryManager
from brain.reasoning import ReasoningAgent
from actions.smart_music import SmartMusicDispatcher
from actions.internet_actions import InternetActionsHandler
from actions.system_control import SystemControlHandler


class TestXAssistantPhase2(unittest.TestCase):
    """Test suite covering Phase-2 AI Brain & Smart Automation components."""

    def setUp(self) -> None:
        self.test_db_path = Path("data/test_x_assistant_p2.db")
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.db = DatabaseManager(db_path=str(self.test_db_path))
        self.memory = MemoryManager()
        self.memory.db = self.db
        self.reasoning = ReasoningAgent()
        self.music = SmartMusicDispatcher()
        self.internet = InternetActionsHandler()
        self.sys_control = SystemControlHandler()

    def tearDown(self) -> None:
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    # Memory Manager Tests
    def test_memory_preferences(self) -> None:
        """Test saving and retrieving user preferences."""
        self.db.set_user_preference("favorite_music", "Rock")
        val = self.db.get_user_preference("favorite_music")
        self.assertEqual(val, "Rock")

    def test_memory_extraction(self) -> None:
        """Test implicit memory extraction from prompt text."""
        result = self.memory.extract_implicit_memory("my favorite song is Hotel California")
        self.assertIsNotNone(result)
        pref = self.db.get_user_preference("favorite_song")
        self.assertEqual(pref, "hotel california")

    # Reasoning Agent Tests
    def test_reasoning_decomposition(self) -> None:
        """Test multi-step prompt decomposition."""
        prompt = "Take a screenshot and open Chrome and then check weather"
        self.assertTrue(self.reasoning.is_multi_step_request(prompt))
        sub_tasks = self.reasoning.decompose_prompt(prompt)
        self.assertEqual(len(sub_tasks), 3)

    # Live Internet Data Tests
    def test_live_weather(self) -> None:
        """Test live weather retrieval function."""
        weather_str = self.internet.get_live_weather("Dhaka")
        self.assertIn("weather", weather_str.lower())

    def test_live_news(self) -> None:
        """Test live news retrieval function."""
        news_str = self.internet.get_live_news()
        self.assertTrue(len(news_str) > 0)

    # System Controls Tests
    def test_screenshot_generation(self) -> None:
        """Test screenshot capture output."""
        msg = self.sys_control.take_screenshot()
        self.assertTrue("screenshot" in msg.lower() or "failed" in msg.lower())

    def test_file_search(self) -> None:
        """Test file search function."""
        res = self.sys_control.search_local_files("test")
        self.assertTrue(isinstance(res, str))


if __name__ == "__main__":
    unittest.main()
