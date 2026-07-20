"""
Unit tests for SystemChecker startup diagnostics module.
"""

import unittest
from core.system_checker import system_checker


class TestSystemChecker(unittest.TestCase):
    """Test suite covering SystemChecker diagnostics."""

    def test_run_all_checks(self) -> None:
        results = system_checker.run_all_checks()
        self.assertIn("1. Python Version", results)
        self.assertIn("2. Dependencies", results)
        self.assertIn("3. Microphone", results)
        self.assertIn("4. Speaker / TTS", results)
        self.assertIn("5. Internet Status", results)
        self.assertIn("6. Ollama Server", results)
        self.assertIn("7. AI Model", results)
        self.assertIn("8. Configuration", results)
        self.assertIn("9. Directories", results)
        self.assertIn("10. Database Schema", results)
        self.assertIn("11. Debug Logs", results)


if __name__ == "__main__":
    unittest.main()
