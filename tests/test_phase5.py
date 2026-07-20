"""
Phase 5 Unit Test Suite for X Assistant.
Tests Camera Engine, Vision Detector, OCR Engine, Multimodal Synthesizer, and Vision Actions Handler.
"""

import os
import unittest
from pathlib import Path
from core.database import DatabaseManager
from vision.camera_engine import CameraEngine
from vision.detector import VisionDetector
from vision.ocr_engine import OCREngine
from vision.vision_actions import VisionActionsHandler
from brain.multimodal import MultimodalSynthesizer


class TestXAssistantPhase5(unittest.TestCase):
    """Test suite covering Phase-5 Vision AI, Multimodal Intelligence & Smart Recognition."""

    def setUp(self) -> None:
        self.test_db_path = Path("data/test_x_assistant_p5.db")
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

        self.db = DatabaseManager(db_path=str(self.test_db_path))
        self.camera = CameraEngine()
        self.detector = VisionDetector()
        self.ocr = OCREngine()
        self.vision_actions = VisionActionsHandler()
        self.multimodal = MultimodalSynthesizer()

    def tearDown(self) -> None:
        if self.test_db_path.exists():
            try:
                os.remove(self.test_db_path)
            except Exception:
                pass

    # Camera Engine Tests
    def test_camera_engine_privacy_defaults(self) -> None:
        """Test camera privacy defaults and photo capture."""
        success, msg = self.camera.capture_photo()
        self.assertTrue(success)

    # Vision Detector Tests
    def test_vision_detector_scene_summary(self) -> None:
        """Test scene summary and person counting."""
        summary = self.detector.describe_current_scene()
        self.assertIn("see", summary)

        count = self.detector.count_people()
        self.assertGreaterEqual(count, 1)

    # OCR Engine Tests
    def test_ocr_engine_fallback(self) -> None:
        """Test OCR extraction fallback."""
        text = self.ocr.extract_text_from_screen()
        self.assertIn("screen", text.lower())

    # Smart Vision Actions Tests
    def test_vision_actions_describe_scene(self) -> None:
        """Test vision action handlers."""
        res = self.vision_actions.handle_vision_command("describe_scene", {})
        self.assertTrue(isinstance(res, str))

        people_msg = self.vision_actions.handle_vision_command("count_people", {})
        self.assertIn("person", people_msg)

    # Multimodal Synthesizer Tests
    def test_multimodal_context_building(self) -> None:
        """Test multimodal context synthesis."""
        context = self.multimodal.build_multimodal_context("What is the room temperature and what do you see?")
        self.assertIn("SYSTEM MULTIMODAL CONTEXT", context)
        self.assertIn("Vision Scene", context)


if __name__ == "__main__":
    unittest.main()
