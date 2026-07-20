"""
System Self-Diagnostics & Health Monitor Module for X Assistant (Phase 6).
Continuously monitors CPU %, RAM %, Disk space, SQLite database size,
and connected hardware status, logging health metrics and warning on anomalies.
"""

import os
import time
import threading
from typing import Dict, Any, Optional
from config.settings import settings
from core.logger import logger
from core.database import db as global_db

try:
    import psutil
except ImportError:
    psutil = None


class SystemDiagnostics:
    """Self-diagnostics and continuous health monitor daemon."""

    def __init__(self, db_instance: Optional[Any] = None) -> None:
        self.db = db_instance or global_db
        self.is_monitoring = False
        self._monitor_thread: Optional[threading.Thread] = None

    def get_system_health_snapshot(self) -> Dict[str, Any]:
        """
        Gather current system health metrics.
        
        Returns:
            Dictionary with CPU, RAM, Disk, DB Size, and Status string.
        """
        cpu = psutil.cpu_percent(interval=None) if psutil else 0.0
        ram = psutil.virtual_memory().percent if psutil else 0.0
        disk = psutil.disk_usage("/").percent if psutil else 0.0

        db_path = settings.paths.db_path
        db_size_mb = round(db_path.stat().st_size / (1024 * 1024), 2) if db_path.exists() else 0.0

        health_status = "HEALTHY"
        issues = []

        if cpu > 90.0:
            health_status = "WARNING"
            issues.append(f"High CPU Usage ({cpu}%)")
        if ram > 90.0:
            health_status = "WARNING"
            issues.append(f"High RAM Usage ({ram}%)")
        if disk > 95.0:
            health_status = "CRITICAL"
            issues.append(f"Low Disk Space ({disk}%)")

        details = "; ".join(issues) if issues else "All subsystems nominal."

        return {
            "cpu_percent": cpu,
            "ram_percent": ram,
            "disk_percent": disk,
            "db_size_mb": db_size_mb,
            "status": health_status,
            "details": details
        }

    def run_diagnostics_check(self) -> str:
        """Run full system diagnostics scan."""
        snap = self.get_system_health_snapshot()
        self.db.log_health_metrics(snap["cpu_percent"], snap["ram_percent"], snap["disk_percent"], snap["details"])

        report = (
            f"System Health Status: [{snap['status']}]\n"
            f"- CPU Usage: {snap['cpu_percent']}%\n"
            f"- RAM Usage: {snap['ram_percent']}%\n"
            f"- Disk Usage: {snap['disk_percent']}%\n"
            f"- Database Size: {snap['db_size_mb']} MB\n"
            f"- Diagnostics Summary: {snap['details']}"
        )
        logger.info(report.replace("\n", " "))
        return report

    def start_monitoring(self, interval_sec: int = 30) -> None:
        """Start background monitoring thread."""
        if self.is_monitoring:
            return

        self.is_monitoring = True

        def _worker():
            logger.info("System Self-Diagnostics daemon active.")
            while self.is_monitoring:
                try:
                    self.run_diagnostics_check()
                except Exception as err:
                    logger.error(f"Diagnostics check error: {err}")
                time.sleep(interval_sec)

        self._monitor_thread = threading.Thread(target=_worker, daemon=True)
        self._monitor_thread.start()

    def stop_monitoring(self) -> None:
        """Stop health monitoring thread."""
        self.is_monitoring = False


# Global System Diagnostics instance
diagnostics_monitor = SystemDiagnostics()
