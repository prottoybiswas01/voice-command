"""
Phase 6 Unit Test Suite for X Assistant.
Tests Local RAG Knowledge Base, Plugin Framework, Macro Workflows, AI Personalities, and Self-Diagnostics.
"""

import os
import unittest
from pathlib import Path
from core.database import DatabaseManager
from core.diagnostics import SystemDiagnostics
from brain.rag_knowledge import LocalRAGKnowledgeBase
from brain.personalities import AIPersonalityManager
from plugins.plugin_manager import PluginManager
from actions.workflow_engine import WorkflowEngine


class TestXAssistantPhase6(unittest.TestCase):
    """Test suite covering Phase-6 Ultimate Personal AI Ecosystem."""

    def setUp(self) -> None:
        self.test_db_path = Path("data/test_x_assistant_p6.db")
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.db = DatabaseManager(db_path=str(self.test_db_path))
        self.diagnostics = SystemDiagnostics(db_instance=self.db)
        self.rag = LocalRAGKnowledgeBase(db_instance=self.db)
        self.personality = AIPersonalityManager()
        self.plugin_mgr = PluginManager()
        self.workflow_mgr = WorkflowEngine()

        self.sample_txt = Path("data/test_doc.txt")
        self.sample_txt.write_text("X Assistant Phase 6 RAG test content block.", encoding="utf-8")

    def tearDown(self) -> None:
        if self.sample_txt.exists():
            try:
                self.sample_txt.unlink()
            except Exception:
                pass

        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    # Self-Diagnostics Tests
    def test_diagnostics_snapshot(self) -> None:
        """Test health snapshot and diagnostics report."""
        snap = self.diagnostics.get_system_health_snapshot()
        self.assertIn("status", snap)

        report = self.diagnostics.run_diagnostics_check()
        self.assertIn("System Health Status", report)

    # RAG Knowledge Base Tests
    def test_rag_document_import_and_query(self) -> None:
        """Test document import and RAG chunk query."""
        import_msg = self.rag.import_document(self.sample_txt)
        self.assertIn("Successfully imported", import_msg)

        res = self.rag.query_knowledge_base("Phase 6 RAG")
        self.assertIsNotNone(res)
        self.assertIn("Source", res)

    # AI Personalities Tests
    def test_personality_switching(self) -> None:
        """Test switching AI personalities."""
        msg = self.personality.set_personality("professional")
        self.assertIn("Professional", msg)

    # Plugin Manager Tests
    def test_plugin_execution(self) -> None:
        """Test dynamic plugin command execution."""
        res = self.plugin_mgr.execute_plugin_command("test plugin")
        self.assertIsNotNone(res)

    # Workflow Engine Tests
    def test_workflow_execution(self) -> None:
        """Test macro workflow execution."""
        executed_commands = []
        def dummy_executor(cmd: str) -> str:
            executed_commands.append(cmd)
            return "OK"

        res = self.workflow_mgr.execute_workflow("start work mode", dummy_executor)
        self.assertIsNotNone(res)
        self.assertGreater(len(executed_commands), 0)


if __name__ == "__main__":
    unittest.main()
