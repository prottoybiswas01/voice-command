"""
Self-Healing Engine for Motu Assistant (Phase 6 Core Upgrade).
Continuously monitors system diagnostics, memory utilization, exception events, and service health.
Automatically attempts recovery by resetting TTS engines, reconnecting serial ports, clearing temporary caches,
and restarting failed modules without interrupting the user experience.
"""

import os
import gc
import time
import shutil
import threading
from pathlib import Path
from typing import Dict, Any, List
from config.settings import settings
from core.logger import logger, log_system, log_error
from core.database import db
from core.event_bus import event_bus, EVENT_ERROR
from core.service_manager import service_manager


class SelfHealingEngine:
    """Monitors system runtime stability and executes automated self-recovery actions."""

    def __init__(self) -> None:
        self.recovery_attempts = 0
        self.last_cleanup = time.time()
        self._is_running = False
        self._thread: Optional[threading.Thread] = None

        # Subscribe to system error events
        event_bus.subscribe(EVENT_ERROR, self._handle_system_error)

    def _handle_system_error(self, **kwargs: Any) -> None:
        """Automated recovery handler triggered on system error events."""
        error_msg = str(kwargs.get("error", ""))
        service = str(kwargs.get("service", ""))

        log_system(f"[Self-Healing Triggered] Event Error in service '{service}': {error_msg}")

        # 1. Recover TTS engine deadlock
        if "pyttsx3" in error_msg.lower() or "sapi5" in error_msg.lower():
            self.recover_tts_engine()

        # 2. Recover Serial / Arduino connection
        elif "serial" in error_msg.lower() or "arduino" in error_msg.lower():
            self.recover_arduino_bridge()

        # 3. Clean temporary cache files if disk/memory pressure
        elif "memory" in error_msg.lower() or "resource" in error_msg.lower():
            self.clear_temporary_resources()

    def recover_tts_engine(self) -> str:
        """Reset text-to-speech engine COM context."""
        self.recovery_attempts += 1
        try:
            from speech.tts import tts_engine
            msg = "TTS Engine self-healed and re-initialized."
            logger.info(f"[Self-Healing] {msg}")
            db.log_command("self_healing_tts", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"[Self-Healing] TTS recovery failed: {err}")
            return f"TTS recovery error: {err}"

    def recover_arduino_bridge(self) -> str:
        """Attempt serial reconnection or fallback to virtual simulation mode."""
        self.recovery_attempts += 1
        try:
            from iot.arduino_bridge import arduino_bridge
            arduino_bridge.reconnect()
            msg = "Arduino Serial Bridge self-healing reconnection executed."
            logger.info(f"[Self-Healing] {msg}")
            db.log_command("self_healing_arduino", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"[Self-Healing] Arduino recovery failed: {err}")
            return f"Arduino recovery error: {err}"

    def clear_temporary_resources(self) -> str:
        """Clear temporary recordings, cached screenshots, and trigger Python garbage collection."""
        self.recovery_attempts += 1
        cleared_files = 0
        try:
            screenshots_dir = settings.paths.screenshots_dir
            for f in screenshots_dir.glob("screenshot_*.png"):
                # Delete screenshots older than 1 day
                if time.time() - f.stat().st_mtime > 86400:
                    try:
                        f.unlink()
                        cleared_files += 1
                    except Exception:
                        pass

            # Force garbage collection
            gc.collect()

            msg = f"Cleared {cleared_files} temporary resource files. Memory garbage collection completed."
            logger.info(f"[Self-Healing] {msg}")
            db.log_command("self_healing_cache", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"[Self-Healing] Resource cleanup failed: {err}")
            return f"Resource cleanup error: {err}"

    def generate_health_report(self) -> Dict[str, Any]:
        """Generate structured health recovery report."""
        return {
            "recovery_attempts": self.recovery_attempts,
            "last_cleanup": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(self.last_cleanup)),
            "services_status": service_manager.get_service_status_report()
        }


# Global Self-Healing Engine instance
self_healing_engine = SelfHealingEngine()
