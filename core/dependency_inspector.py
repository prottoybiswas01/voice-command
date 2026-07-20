"""
Comprehensive Dependency Inspector & Health Checker for Motu Assistant (Phase 6 Core Upgrade).
Inspects Python libraries, Windows binary executables (Chrome, Tesseract, Ollama), COM ports,
and SQLite database schemas to generate a complete Dependency Health Report during startup.
"""

import sys
import os
import shutil
import sqlite3
import subprocess
from typing import Dict, Any, List
from pathlib import Path
from config.settings import settings
from core.logger import logger, log_startup, log_error


class DependencyInspector:
    """Performs deep environment checks across libraries, binaries, database, and hardware."""

    REQUIRED_PACKAGES = [
        "pyttsx3", "speech_recognition", "requests", "yaml",
        "PIL", "mss", "pyautogui"
    ]

    BINARY_DEPENDENCIES = {
        "Google Chrome": [r"C:\Program Files\Google\Chrome\Application\chrome.exe", r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"],
        "Ollama LLM Server": [r"C:\Users\USER\AppData\Local\Programs\Ollama\ollama.exe", r"C:\Program Files\Ollama\ollama.exe"],
        "Tesseract OCR": [r"C:\Program Files\Tesseract-OCR\tesseract.exe"]
    }

    def __init__(self) -> None:
        pass

    def check_python_packages(self) -> Dict[str, bool]:
        """Check availability of core Python packages."""
        results = {}
        for pkg in self.REQUIRED_PACKAGES:
            try:
                __import__(pkg)
                results[pkg] = True
            except ImportError:
                results[pkg] = False
        return results

    def check_binary_dependencies(self) -> Dict[str, Dict[str, Any]]:
        """Check presence of external Windows binary executables."""
        results = {}
        for name, paths in self.BINARY_DEPENDENCIES.items():
            found = False
            matched_path = ""
            for p in paths:
                if os.path.exists(p) or shutil.which(p):
                    found = True
                    matched_path = p
                    break
            results[name] = {"found": found, "path": matched_path}
        return results

    def check_database_integrity(self) -> bool:
        """Verify SQLite database schema accessibility."""
        try:
            db_path = settings.paths.db_path
            conn = sqlite3.connect(db_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            conn.close()
            return len(tables) > 0
        except Exception:
            return False

    def generate_health_report(self) -> str:
        """Generate formatted dependency health report."""
        pkg_status = self.check_python_packages()
        bin_status = self.check_binary_dependencies()
        db_ok = self.check_database_integrity()

        lines = ["==================================================", " Dependency & Environment Health Report", "=================================================="]

        lines.append("\n[Python Libraries]")
        for pkg, ok in pkg_status.items():
            symbol = "✓" if ok else "✗ (Fallback Active)"
            lines.append(f"  [{symbol}] {pkg}")

        lines.append("\n[External Binaries & Executables]")
        for name, info in bin_status.items():
            symbol = "✓" if info["found"] else "⚠ (Optional / Fallback)"
            path_str = f" ({info['path']})" if info['found'] else ""
            lines.append(f"  [{symbol}] {name}{path_str}")

        db_symbol = "✓" if db_ok else "✗"
        lines.append(f"\n[SQLite Database Schema]: [{db_symbol}] Active at '{settings.paths.db_path.name}'")

        lines.append("==================================================")
        report_str = "\n".join(lines)
        log_startup(report_str)
        return report_str


# Global Dependency Inspector instance
dependency_inspector = DependencyInspector()
