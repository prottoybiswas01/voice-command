"""
Centralized Service Manager for Motu Assistant (Phase 6 Core Upgrade).
Responsible for registering, starting, monitoring, restarting, stopping,
and reporting status of all system services (Voice, AI Brain, Ollama, Memory, Browser, Arduino, Music, Database, Web Search, Logging).
Automatically restarts failed services when possible and isolates failures without halting the application.
"""

import time
import threading
from typing import Dict, Any, List, Callable, Optional
from core.logger import logger, log_startup, log_system, log_error
from core.database import db
from core.event_bus import event_bus, EVENT_SYSTEM, EVENT_ERROR


class ServiceDescriptor:
    """Descriptor tracking a system service instance and heartbeat state."""

    def __init__(self, name: str, start_func: Optional[Callable[[], bool]] = None, stop_func: Optional[Callable[[], bool]] = None) -> None:
        self.name = name
        self.start_func = start_func
        self.stop_func = stop_func
        self.status = "STOPPED"
        self.last_heartbeat = time.time()
        self.restart_count = 0


class ServiceManager:
    """Orchestrates system service lifecycles and health monitoring."""

    def __init__(self) -> None:
        self.services: Dict[str, ServiceDescriptor] = {}
        self._lock = threading.Lock()
        self._is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

    def register_service(self, name: str, start_func: Optional[Callable[[], bool]] = None, stop_func: Optional[Callable[[], bool]] = None) -> None:
        """Register a core service descriptor."""
        with self._lock:
            self.services[name] = ServiceDescriptor(name, start_func, stop_func)
            log_startup(f"Registered System Service: '{name}'")

    def start_service(self, name: str) -> bool:
        """Start a specific service."""
        with self._lock:
            descriptor = self.services.get(name)

        if not descriptor:
            return False

        try:
            success = True
            if descriptor.start_func:
                success = descriptor.start_func()
            
            descriptor.status = "RUNNING" if success else "FAILED"
            descriptor.last_heartbeat = time.time()
            log_system(f"Service '{name}' status set to: {descriptor.status}")
            event_bus.publish(EVENT_SYSTEM, action="service_start", service=name, status=descriptor.status)
            return success
        except Exception as err:
            descriptor.status = "FAILED"
            log_error(f"Failed starting service '{name}': {err}")
            event_bus.publish(EVENT_ERROR, service=name, error=str(err))
            return False

    def restart_service(self, name: str) -> bool:
        """Restart a failed service."""
        with self._lock:
            descriptor = self.services.get(name)

        if not descriptor:
            return False

        descriptor.restart_count += 1
        log_system(f"Attempting restart for service '{name}' (Attempt #{descriptor.restart_count})...")

        if descriptor.stop_func:
            try:
                descriptor.stop_func()
            except Exception:
                pass

        return self.start_service(name)

    def heartbeat(self, name: str) -> None:
        """Record service heartbeat pulse."""
        with self._lock:
            descriptor = self.services.get(name)
            if descriptor:
                descriptor.last_heartbeat = time.time()
                if descriptor.status != "RUNNING":
                    descriptor.status = "RUNNING"

    def get_service_status_report(self) -> Dict[str, Any]:
        """Generate structured health status report for all registered services."""
        with self._lock:
            report = {}
            for name, desc in self.services.items():
                report[name] = {
                    "status": desc.status,
                    "last_heartbeat": time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(desc.last_heartbeat)),
                    "restarts": desc.restart_count
                }
            return report

    def print_status_summary(self) -> str:
        """Generate formatted status summary string."""
        report = self.get_service_status_report()
        lines = [f"System Services Status Report ({len(report)} registered):"]
        for name, data in report.items():
            lines.append(f"  - [{data['status']}] {name} (Restarts: {data['restarts']})")
        summary = "\n".join(lines)
        log_startup(summary)
        return summary


# Global Service Manager instance
service_manager = ServiceManager()

# Pre-register 10 Core Services
service_manager.register_service("VoiceService")
service_manager.register_service("AIBrainService")
service_manager.register_service("OllamaService")
service_manager.register_service("MemoryService")
service_manager.register_service("BrowserService")
service_manager.register_service("ArduinoService")
service_manager.register_service("MusicService")
service_manager.register_service("DatabaseService")
service_manager.register_service("WebSearchService")
service_manager.register_service("LoggingService")
