"""
Web Server & REST API Module for X Assistant (Phase 6 Ecosystem Upgrade).
Provides a lightweight, multi-threaded HTTP Web Server exposing REST APIs and serving
a modern Cyberpunk Glassmorphism Web UI Dashboard.
"""

import sys
import os
import json
import threading
import socketserver
from http.server import HTTPServer, BaseHTTPRequestHandler
from pathlib import Path
from typing import Optional, Dict, Any

from config.settings import settings
from core.logger import logger
from core.database import db
from core.event_bus import event_bus
from actions.productivity_actions import productivity_actions
from brain.pomodoro import pomodoro_timer
from brain.rag_knowledge import rag_knowledge_base
from brain.personalities import personality_manager
from plugins.plugin_manager import plugin_manager
from actions.security_auditor import security_auditor
from actions.workflow_engine import workflow_engine
from iot.arduino_bridge import arduino_bridge
from iot.device_manager import device_manager
from iot.smart_home import smart_home_controller
from vision.camera_engine import camera_engine
from vision.detector import vision_detector
from vision.ocr_engine import ocr_engine
from vision.vision_actions import vision_actions_handler

# Reference to central XAssistantController instance
_assistant_controller = None


def set_assistant_controller(controller: Any) -> None:
    global _assistant_controller
    _assistant_controller = controller


_fallback_controller = None

def _get_controller() -> Any:
    global _assistant_controller, _fallback_controller
    if _assistant_controller:
        return _assistant_controller
    if _fallback_controller is None:
        from main import XAssistantController
        _fallback_controller = XAssistantController()
    return _fallback_controller


class ThreadedHTTPServer(socketserver.ThreadingMixIn, HTTPServer):
    """Multi-threaded HTTP Server handling parallel web clients."""
    daemon_threads = True


class WebDashboardHandler(BaseHTTPRequestHandler):
    """HTTP Request Handler delivering REST APIs and static Web UI assets."""

    def log_message(self, format: str, *args: Any) -> None:
        """Suppress standard HTTP server request logs to keep terminal clean."""
        pass

    def _send_json(self, data: Dict[str, Any], status_code: int = 200) -> None:
        try:
            body = json.dumps(data, indent=2, default=str).encode("utf-8")
            self.send_response(status_code)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
            self.send_header("Access-Control-Allow-Headers", "Content-Type")
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        except Exception as err:
            logger.error(f"Failed to send JSON response: {err}")

    def _send_file(self, file_path: Path, content_type: str) -> None:
        if not file_path.exists():
            self.send_error(404, "File Not Found")
            return
        try:
            with open(file_path, "rb") as f:
                content = f.read()
            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(len(content)))
            self.end_headers()
            self.wfile.write(content)
        except Exception as err:
            logger.error(f"Failed to serve static file '{file_path}': {err}")
            self.send_error(500, "Internal Server Error")

    def do_OPTIONS(self) -> None:
        """Handle CORS pre-flight requests."""
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self) -> None:
        try:
            path = self.path.split("?")[0]
            web_dir = settings.web.web_dir

            if path in ("/", "/index.html"):
                self._send_file(web_dir / "index.html", "text/html; charset=utf-8")
                return
            elif path == "/style.css":
                self._send_file(web_dir / "style.css", "text/css; charset=utf-8")
                return
            elif path == "/app.js":
                self._send_file(web_dir / "app.js", "application/javascript; charset=utf-8")
                return
            elif path == "/favicon.ico":
                self.send_response(204)
                self.end_headers()
                return

            # REST API Routes
            if path == "/api/status":
                self._handle_get_status()
            elif path == "/api/iot":
                self._handle_get_iot()
            elif path == "/api/rag/docs":
                self._handle_get_rag_docs()
            elif path == "/api/vision":
                self._handle_get_vision()
            elif path == "/api/workflows":
                self._handle_get_workflows()
            elif path == "/api/plugins":
                self._handle_get_plugins()
            elif path == "/api/audit":
                self._handle_get_audit()
            else:
                self.send_error(404, "API Endpoint Not Found")
        except Exception as err:
            import traceback
            traceback.print_exc()
            self._send_json({"error": str(err)}, 500)

    def do_POST(self) -> None:
        try:
            path = self.path.split("?")[0]

            if path == "/api/command":
                self._handle_post_command()
            elif path == "/api/iot/control":
                self._handle_post_iot_control()
            elif path == "/api/workflows/run":
                self._handle_post_workflow_run()
            elif path == "/api/rag/upload":
                self._handle_post_rag_upload()
            else:
                self.send_error(404, "API Endpoint Not Found")
        except Exception as err:
            import traceback
            traceback.print_exc()
            self._send_json({"error": str(err)}, 500)

    # --- API GET HANDLERS ---
    def _handle_get_status(self) -> None:
        sys_info = productivity_actions.get_system_info("all")
        pomo_status = pomodoro_timer.get_status()
        camera_active = camera_engine.is_camera_active
        p_key = personality_manager.active_personality
        personality = personality_manager.PERSONALITIES.get(p_key, personality_manager.PERSONALITIES["standard"])

        data = {
            "name": settings.assistant.name,
            "version": settings.assistant.version,
            "system_info": sys_info,
            "pomodoro": pomo_status,
            "camera_active": camera_active,
            "active_personality": personality["name"],
            "personality_desc": personality["prompt"],
            "backend_mode": "Virtual Simulation" if arduino_bridge.simulation_mode else "Hardware Serial"
        }
        self._send_json(data)

    def _handle_get_iot(self) -> None:
        telemetry = arduino_bridge.get_latest_telemetry()
        states = device_manager.get_all_device_states() if hasattr(device_manager, "get_all_device_states") else {}
        data = {
            "arduino_connected": arduino_bridge.is_connected,
            "is_simulated": arduino_bridge.simulation_mode,
            "temperature": telemetry.get("temp", 28.5),
            "humidity": telemetry.get("humidity", 65.0),
            "motion": bool(telemetry.get("motion", False)),
            "gas": bool(telemetry.get("gas", 0) > 300),
            "relay_light": states.get("relay_light", "OFF") == "ON",
            "relay_fan": states.get("relay_fan", "OFF") == "ON",
            "servo_lock_angle": states.get("servo_lock", 0)
        }
        self._send_json(data)

    def _handle_get_rag_docs(self) -> None:
        docs = db.get_all_knowledge_documents()
        self._send_json({"documents": docs})

    def _handle_get_vision(self) -> None:
        last_desc = vision_actions_handler.handle_vision_command("describe_scene", {})
        count_desc = vision_actions_handler.handle_vision_command("count_people", {})
        data = {
            "scene_description": last_desc,
            "people_count": count_desc,
            "camera_active": camera_engine.is_camera_active
        }
        self._send_json(data)

    def _handle_get_workflows(self) -> None:
        workflows = [
            {"id": "work_mode", "title": "⚡ Start Work Mode", "command": "start work mode", "description": "Launches VS Code, Chrome, GitHub, and Pomodoro Focus Mode"},
            {"id": "good_night", "title": "🌙 Good Night Scene", "command": "good night", "description": "Turns off all relays, locks door servo, and arms security sensors"}
        ]
        self._send_json({"workflows": workflows})

    def _handle_get_plugins(self) -> None:
        plugins = plugin_manager.list_plugins()
        self._send_json({"plugins": plugins})

    def _handle_get_audit(self) -> None:
        summary = security_auditor.get_audit_trail_summary(limit=15)
        logs = db.get_recent_audit_logs(limit=15) if hasattr(db, "get_recent_audit_logs") else []
        self._send_json({"summary": summary, "logs": logs})

    # --- API POST HANDLERS ---
    def _read_json_body(self) -> Dict[str, Any]:
        content_length = int(self.headers.get("Content-Length", 0))
        if content_length == 0:
            return {}
        raw_body = self.rfile.read(content_length).decode("utf-8")
        return json.loads(raw_body) if raw_body else {}

    def _handle_post_command(self) -> None:
        try:
            body = self._read_json_body()
            cmd = body.get("command", "").strip()
            if not cmd:
                self._send_json({"success": False, "error": "Empty command prompt"}, 400)
                return

            ctrl = _get_controller()
            response = ctrl.process_command(cmd)

            self._send_json({"success": True, "command": cmd, "response": response})
        except Exception as err:
            logger.error(f"Error processing web command: {err}")
            self._send_json({"success": False, "error": str(err)}, 500)

    def _handle_post_iot_control(self) -> None:
        try:
            body = self._read_json_body()
            cmd = body.get("command", "").strip()
            action = body.get("action", "").strip()
            params = body.get("params", {})

            if cmd:
                ctrl = _get_controller()
                result = ctrl.process_command(cmd)
                self._send_json({"success": True, "result": result})
            elif action:
                result = smart_home_controller.handle_voice_command(action, params)
                self._send_json({"success": True, "result": result})
            else:
                self._send_json({"success": False, "error": "Missing action or command"}, 400)
        except Exception as err:
            logger.error(f"Error executing IoT control: {err}")
            self._send_json({"success": False, "error": str(err)}, 500)

    def _handle_post_workflow_run(self) -> None:
        try:
            body = self._read_json_body()
            cmd = body.get("command", "start work mode")
            res = workflow_engine.execute_voice_workflow(cmd)
            self._send_json({"success": True, "result": res})
        except Exception as err:
            logger.error(f"Error executing workflow: {err}")
            self._send_json({"success": False, "error": str(err)}, 500)

    def _handle_post_rag_upload(self) -> None:
        try:
            content_type = self.headers.get("Content-Type", "")
            content_length = int(self.headers.get("Content-Length", 0))
            raw_bytes = self.rfile.read(content_length) if content_length > 0 else b""

            if "multipart/form-data" in content_type and b"filename=" in raw_bytes:
                headers_part, body_part = raw_bytes.split(b"\r\n\r\n", 1)
                filename = "uploaded_doc.txt"
                for line in headers_part.decode("utf-8", errors="ignore").split("\r\n"):
                    if "filename=" in line:
                        filename = line.split("filename=")[1].strip('"').strip("'").split(";")[0]
                        break
                filename = os.path.basename(filename)
                if b"\r\n--" in body_part:
                    body_part = body_part.rsplit(b"\r\n--", 1)[0]
                save_path = settings.paths.knowledge_dir / filename
                with open(save_path, "wb") as f:
                    f.write(body_part)
                res = rag_knowledge_base.import_document(save_path)
                self._send_json({"success": True, "message": res, "filename": filename})
                return

            # Fallback JSON upload
            body = json.loads(raw_bytes.decode("utf-8")) if raw_bytes else {}
            filename = body.get("filename", "document.txt")
            content = body.get("content", "")
            if content:
                save_path = settings.paths.knowledge_dir / filename
                with open(save_path, "w", encoding="utf-8") as f:
                    f.write(content)
                res = rag_knowledge_base.import_document(save_path)
                self._send_json({"success": True, "message": res, "filename": filename})
                return

            self._send_json({"success": False, "error": "No file uploaded"}, 400)
        except Exception as err:
            logger.error(f"Error uploading RAG document: {err}")
            self._send_json({"success": False, "error": str(err)}, 500)


class WebDashboardServer:
    """Manager for Web Dashboard HTTP Server background thread."""

    def __init__(self, host: Optional[str] = None, port: Optional[int] = None) -> None:
        self.host = host or settings.web.host
        self.port = port or settings.web.port
        self.server: Optional[ThreadedHTTPServer] = None
        self.thread: Optional[threading.Thread] = None
        self.is_running = False

    def start(self, controller: Optional[Any] = None) -> None:
        if self.is_running:
            return

        if controller:
            set_assistant_controller(controller)

        # Ensure web asset directory exists
        settings.web.web_dir.mkdir(parents=True, exist_ok=True)

        try:
            self.server = ThreadedHTTPServer((self.host, self.port), WebDashboardHandler)
            self.is_running = True
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            url = f"http://localhost:{self.port}"
            logger.info(f"⚡ X Assistant Web Dashboard Server listening at {url}")
            print(f"\n🌐 [Web Server] Dashboard UI active & ready at: {url}\n")
        except Exception as err:
            logger.error(f"Failed to start Web Dashboard Server on port {self.port}: {err}")
            self.is_running = False

    def stop(self) -> None:
        if self.server and self.is_running:
            self.server.shutdown()
            self.server.server_close()
            self.is_running = False
            logger.info("Web Dashboard Server stopped.")


# Global Web Server Manager instance
web_server_manager = WebDashboardServer()
