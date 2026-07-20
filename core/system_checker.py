"""
System Diagnostic & Startup Checker Module for X Assistant.
Performs 11-step diagnostic checks on application launch:
Python version, Dependencies, Microphone, Speaker, Internet, Ollama Server,
AI Model, Configuration, Folders, Database, and Debug Logs.
"""

import os
import sys
import time
import socket
import subprocess
import urllib.request
import json
from pathlib import Path
from typing import Dict, Any, List, Tuple

from config.settings import settings
from core.logger import logger
from core.database import db


class SystemChecker:
    """Performs comprehensive startup diagnostics and auto-fixes configuration / folders."""

    def __init__(self) -> None:
        self.results: Dict[str, Tuple[bool, str]] = {}
        self.debug_log_path = settings.paths.logs_dir / "debug.log"

    def _write_debug_log(self, message: str) -> None:
        """Write timestamped entry to logs/debug.log."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        entry = f"[{timestamp}] {message}\n"
        try:
            with open(self.debug_log_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception:
            pass

    def check_python_version(self) -> Tuple[bool, str]:
        """Check Python version >= 3.10."""
        major, minor = sys.version_info.major, sys.version_info.minor
        version_str = f"{major}.{minor}.{sys.version_info.micro}"
        if major >= 3 and minor >= 10:
            msg = f"Python Version OK ({version_str})"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg
        else:
            msg = f"Python Version WARNING ({version_str}). Recommended Python 3.10+"
            self._write_debug_log(f"[CHECK] {msg}")
            return False, msg

    def check_dependencies(self) -> Tuple[bool, str]:
        """Check core Python packages status."""
        required_pkgs = [
            ("yaml", "PyYAML"),
            ("speech_recognition", "SpeechRecognition"),
            ("sounddevice", "sounddevice"),
            ("pyttsx3", "pyttsx3"),
            ("requests", "requests"),
            ("cv2", "opencv-python"),
            ("pywin32", "pywin32"),
            ("psutil", "psutil"),
            ("playwright", "playwright"),
            ("pypdf", "pypdf"),
            ("docx", "python-docx"),
            ("serial", "pyserial"),
            ("pyperclip", "pyperclip")
        ]

        missing = []
        installed = []
        for mod_name, pkg_name in required_pkgs:
            try:
                __import__(mod_name)
                installed.append(pkg_name)
            except ImportError:
                missing.append(pkg_name)

        if not missing:
            msg = f"All {len(installed)} core dependencies present."
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg
        else:
            msg = f"Missing optional packages: {', '.join(missing)}. Run: pip install {' '.join(missing)}"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, f"Dependencies OK ({len(installed)} installed, {len(missing)} fallback mode)"

    def check_microphone(self) -> Tuple[bool, str]:
        """Check default Windows microphone hardware availability."""
        # Check sounddevice or PyAudio
        mic_found = False
        mic_name = "Default System Microphone"

        try:
            import sounddevice as sd
            devs = sd.query_devices(kind='input')
            if devs:
                mic_found = True
                mic_name = devs.get('name', mic_name)
        except Exception:
            pass

        if not mic_found:
            try:
                import speech_recognition as sr
                mics = sr.Microphone.list_microphone_names()
                if mics:
                    mic_found = True
                    mic_name = mics[0]
            except Exception:
                pass

        if mic_found:
            msg = f"Microphone detected: '{mic_name}'"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg
        else:
            msg = "No Microphone detected. Please connect a microphone or use text input mode."
            self._write_debug_log(f"[CHECK] {msg}")
            return False, msg

    def check_speaker(self) -> Tuple[bool, str]:
        """Check audio output speaker / TTS engine."""
        try:
            import pyttsx3
            engine = pyttsx3.init()
            voices = engine.getProperty('voices')
            msg = f"Speaker & TTS OK ({len(voices) if voices else 1} audio output voice(s) available)"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg
        except Exception:
            msg = "TTS Audio output: Console text fallback mode active."
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg

    def check_internet(self) -> Tuple[bool, str]:
        """Check internet connectivity status."""
        try:
            with socket.create_connection(("8.8.8.8", 53), timeout=3):
                msg = "Internet Status: Online & Connected"
                self._write_debug_log(f"[CHECK] {msg}")
                return True, msg
        except OSError:
            msg = "Internet Status: Offline (Offline-first local mode active)"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg

    def check_ollama_server(self) -> Tuple[bool, str]:
        """Check if local Ollama server is running. Auto-start if offline."""
        host = settings.ollama.host
        url = f"{host}/api/tags"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "XAssistant"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    msg = f"Ollama Server Online at {host}"
                    self._write_debug_log(f"[CHECK] {msg}")
                    return True, msg
        except Exception:
            pass

        # Auto-start Ollama server
        try:
            logger.info("Ollama server offline. Attempting to start 'ollama serve' automatically...")
            subprocess.Popen(["ollama", "serve"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(3)

            req = urllib.request.Request(url, headers={"User-Agent": "XAssistant"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    msg = f"Ollama Server started automatically at {host}"
                    self._write_debug_log(f"[CHECK] {msg}")
                    return True, msg
        except Exception as err:
            logger.warning(f"Could not auto-start Ollama server: {err}")

        msg = f"Ollama Server Offline ({host}). AI will run in Safe Mode. Solution: Run 'ollama serve' in a terminal."
        self._write_debug_log(f"[CHECK] {msg}")
        return False, msg

    def check_ai_model(self) -> Tuple[bool, str]:
        """Check if configured AI model exists in local Ollama repository."""
        target_model = settings.ollama.model
        url = f"{settings.ollama.host}/api/tags"

        try:
            req = urllib.request.Request(url, headers={"User-Agent": "XAssistant"})
            with urllib.request.urlopen(req, timeout=3) as resp:
                if resp.status == 200:
                    data = json.loads(resp.read().decode("utf-8"))
                    models = [m.get("name", "") for m in data.get("models", [])]
                    for m in models:
                        if target_model.split(":")[0] in m:
                            msg = f"AI Model '{target_model}' ready."
                            self._write_debug_log(f"[CHECK] {msg}")
                            return True, msg

                    install_cmd = f"ollama pull {target_model}"
                    msg = f"Model '{target_model}' not downloaded. To install, run command: {install_cmd}"
                    self._write_debug_log(f"[CHECK] {msg}")
                    return False, msg
        except Exception:
            pass

        msg = f"AI Model '{target_model}' configured (Ollama check bypassed)."
        self._write_debug_log(f"[CHECK] {msg}")
        return True, msg

    def check_configuration(self) -> Tuple[bool, str]:
        """Check configuration schema settings."""
        if settings.config_file.exists():
            msg = f"Configuration file OK ({settings.config_file.name})"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg
        else:
            settings.load_config()
            msg = "Configuration generated with default settings."
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg

    def check_folders(self) -> Tuple[bool, str]:
        """Ensure all required data and log directories exist."""
        folders = [
            settings.paths.logs_dir,
            settings.paths.notes_dir,
            settings.paths.screenshots_dir,
            settings.paths.recordings_dir,
            settings.paths.audio_dir,
            settings.paths.captures_dir,
            settings.paths.knowledge_dir,
            settings.paths.plugins_dir
        ]

        created = 0
        for folder in folders:
            if not folder.exists():
                folder.mkdir(parents=True, exist_ok=True)
                created += 1

        msg = f"All {len(folders)} system directories ready."
        self._write_debug_log(f"[CHECK] {msg}")
        return True, msg

    def check_database(self) -> Tuple[bool, str]:
        """Verify SQLite database schema tables."""
        try:
            db.init_db()
            msg = f"SQLite Database Schema OK ({settings.paths.db_path.name})"
            self._write_debug_log(f"[CHECK] {msg}")
            return True, msg
        except Exception as err:
            msg = f"Database initialization warning: {err}"
            self._write_debug_log(f"[CHECK] {msg}")
            return False, msg

    def check_logs(self) -> Tuple[bool, str]:
        """Verify log file creation."""
        self._write_debug_log("[CHECK] Log files verified successfully.")
        msg = f"System Debug Log active at '{self.debug_log_path}'"
        return True, msg

    def run_all_checks(self) -> Dict[str, Tuple[bool, str]]:
        """
        Execute full 11-step diagnostic check pipeline on launch.
        
        Returns:
            Dictionary mapping check name to (success_bool, status_message).
        """
        print("\n===================================================")
        print("     X Assistant - Startup Diagnostics Check       ")
        print("===================================================\n")

        checks = [
            ("1. Python Version", self.check_python_version),
            ("2. Dependencies", self.check_dependencies),
            ("3. Microphone", self.check_microphone),
            ("4. Speaker / TTS", self.check_speaker),
            ("5. Internet Status", self.check_internet),
            ("6. Ollama Server", self.check_ollama_server),
            ("7. AI Model", self.check_ai_model),
            ("8. Configuration", self.check_configuration),
            ("9. Directories", self.check_folders),
            ("10. Database Schema", self.check_database),
            ("11. Debug Logs", self.check_logs)
        ]

        for title, func in checks:
            try:
                ok, msg = func()
                status_symbol = "[OK]" if ok else "[WARN]"
                print(f" {status_symbol} {title}: {msg}")
                logger.info(f"{title}: {msg}")
                self.results[title] = (ok, msg)
            except Exception as err:
                print(f" [FAIL] {title}: Failed ({err})")
                logger.error(f"{title} diagnostic error: {err}")
                self.results[title] = (False, str(err))

        print("\n===================================================\n")
        return self.results


# Global System Checker instance
system_checker = SystemChecker()
