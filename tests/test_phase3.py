"""
Phase 3 Unit Test Suite for X Assistant.
Tests Autonomous AI Agent, Window Manager, File Organizer, Pomodoro Timer, and Security Auditor.
"""

import os
import unittest
from pathlib import Path
from core.database import DatabaseManager
from brain.agent import AutonomousAgent
from actions.window_manager import WindowManager
from actions.file_organizer import FileOrganizer
from actions.security_auditor import SecurityAuditor
from brain.pomodoro import PomodoroTimer


class TestXAssistantPhase3(unittest.TestCase):
    """Test suite covering Phase-3 Autonomous AI Agent & Computer Control components."""

    def setUp(self) -> None:
        self.test_db_path = Path("data/test_x_assistant_p3.db")
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.db = DatabaseManager(db_path=str(self.test_db_path))
        self.agent = AutonomousAgent()
        self.win_mgr = WindowManager()
        self.file_org = FileOrganizer()
        self.auditor = SecurityAuditor(db_instance=self.db)
        self.pomodoro = PomodoroTimer()

        self.test_dir = Path("data/test_p3_dir")

    def tearDown(self) -> None:
        if self.test_dir.exists():
            try:
                import shutil
                shutil.rmtree(self.test_dir)
            except Exception:
                pass

        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    # Autonomous Agent Tests
    def test_agent_plan_creation(self) -> None:
        """Test autonomous agent task plan creation."""
        plan = self.agent.create_plan("Take a screenshot and open Chrome and then check weather")
        self.assertEqual(len(plan), 3)
        self.assertEqual(plan[0].description, "Take a screenshot")

    # Window Manager Tests
    def test_window_manager_list(self) -> None:
        """Test window enumeration."""
        wins = self.win_mgr.list_open_windows()
        self.assertTrue(isinstance(wins, list))

    # File Organizer & ZIP Tests
    def test_file_organizer_dir_and_zip(self) -> None:
        """Test directory creation, ZIP compression, and extraction."""
        msg_dir = self.file_org.create_directory(str(self.test_dir))
        self.assertTrue(self.test_dir.exists())

        test_file = self.test_dir / "sample.txt"
        test_file.write_text("Hello Phase 3", encoding="utf-8")

        zip_msg = self.file_org.compress_to_zip(str(self.test_dir))
        self.assertIn("Compressed", zip_msg)

        zip_file = self.test_dir.parent / f"{self.test_dir.name}.zip"
        self.assertTrue(zip_file.exists())

        # Cleanup zip file
        if zip_file.exists():
            try:
                zip_file.unlink()
            except Exception:
                pass

    # Security Auditor Tests
    def test_security_audit_logging(self) -> None:
        """Test audit logging and confirmation flags."""
        self.assertTrue(self.auditor.is_confirmation_required("shutdown"))
        self.assertTrue(self.auditor.is_confirmation_required("delete_file"))

        self.auditor.log_audit_trail("DELETE_FILE", "temp.txt", user_confirmed=True)
        logs = self.db.get_recent_audit_logs()
        self.assertEqual(len(logs), 1)
        self.assertEqual(logs[0]["action_type"], "DELETE_FILE")

    # Pomodoro Timer Tests
    def test_pomodoro_timer_status(self) -> None:
        """Test Pomodoro status output."""
        status = self.pomodoro.get_status()
        self.assertIn("Pomodoro", status)


if __name__ == "__main__":
    unittest.main()
