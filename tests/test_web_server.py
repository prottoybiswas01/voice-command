"""
Unit Tests for Web Server REST API Endpoints & Dashboard Interface.
"""

import sys
import os
import unittest
import urllib.request
import json
import time
from pathlib import Path

# Add workspace root to sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from config.settings import settings
from ui.web_server import web_server_manager
from main import XAssistantController


class TestWebServerAPI(unittest.TestCase):
    """Test suite for X Assistant Web Dashboard HTTP REST APIs."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.port = 8090
        settings.web.port = cls.port
        web_server_manager.port = cls.port
        cls.controller = XAssistantController()
        time.sleep(0.5)

    @classmethod
    def tearDownClass(cls) -> None:
        web_server_manager.stop()

    def _get_json(self, endpoint: str) -> dict:
        url = f"http://127.0.0.1:{self.port}{endpoint}"
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            return data

    def _post_json(self, endpoint: str, payload: dict) -> dict:
        url = f"http://127.0.0.1:{self.port}{endpoint}"
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(url, data=body, headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as resp:
            self.assertEqual(resp.status, 200)
            data = json.loads(resp.read().decode("utf-8"))
            return data

    def test_01_index_html_serving(self) -> None:
        url = f"http://127.0.0.1:{self.port}/"
        with urllib.request.urlopen(url) as resp:
            self.assertEqual(resp.status, 200)
            html = resp.read().decode("utf-8")
            self.assertIn("<title>X Assistant Phase 6", html)

    def test_02_status_endpoint(self) -> None:
        data = self._get_json("/api/status")
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("active_personality", data)

    def test_03_iot_endpoint(self) -> None:
        data = self._get_json("/api/iot")
        self.assertIn("temperature", data)
        self.assertIn("humidity", data)
        self.assertIn("relay_light", data)

    def test_04_iot_control_endpoint(self) -> None:
        res = self._post_json("/api/iot/control", {"command": "turn on room light"})
        self.assertTrue(res.get("success"))

    def test_05_rag_docs_endpoint(self) -> None:
        data = self._get_json("/api/rag/docs")
        self.assertIn("documents", data)

    def test_06_vision_endpoint(self) -> None:
        data = self._get_json("/api/vision")
        self.assertIn("scene_description", data)

    def test_07_workflows_endpoint(self) -> None:
        data = self._get_json("/api/workflows")
        self.assertIn("workflows", data)

    def test_08_plugins_endpoint(self) -> None:
        data = self._get_json("/api/plugins")
        self.assertIn("plugins", data)

    def test_09_audit_endpoint(self) -> None:
        data = self._get_json("/api/audit")
        self.assertIn("summary", data)

    def test_10_post_command_endpoint(self) -> None:
        res = self._post_json("/api/command", {"command": "what is the room temperature"})
        self.assertTrue(res.get("success"))
        self.assertIn("°C", res.get("response", ""))


if __name__ == "__main__":
    unittest.main()
