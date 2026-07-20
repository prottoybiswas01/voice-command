"""
Production-Ready 4-File Logging Framework for Motu Assistant (Phase 6 Core Upgrade).
Automatically generates and manages:
1. startup.log: Diagnostic check, configuration validation, and module loading events.
2. system.log: General operational execution logs, commands, and hardware events.
3. error.log: Warnings, exception stack traces, and system failures.
4. debug.log: Detailed low-level execution trace logs.

Guarantees logging operations never crash the application using Unicode-safe stream handlers
and exception-isolated file writers.
"""

import sys
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional
from config.settings import settings

# Ensure Windows stdout/stderr handles UTF-8 Unicode characters without charmap errors
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

if hasattr(sys.stderr, "reconfigure"):
    try:
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


class DualLogger:
    """Manages custom startup, system, debug, and error log file handlers with Unicode safety."""

    _logger_instance: Optional[logging.Logger] = None
    _startup_logger: Optional[logging.Logger] = None

    @classmethod
    def get_logger(cls, name: str = "XAssistant") -> logging.Logger:
        if cls._logger_instance is not None:
            return cls._logger_instance

        logger = logging.getLogger(name)
        logger.setLevel(logging.DEBUG)
        logger.propagate = False

        if logger.handlers:
            return logger

        today_str = datetime.now().strftime("%Y-%m-%d")
        logs_dir = settings.paths.logs_dir
        logs_dir.mkdir(parents=True, exist_ok=True)

        startup_log_file = logs_dir / "startup.log"
        system_log_file = logs_dir / "system.log"
        error_log_file = logs_dir / "error.log"
        debug_log_file = logs_dir / "debug.log"

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        try:
            # 1. Startup Log Handler
            startup_handler = logging.FileHandler(startup_log_file, encoding="utf-8")
            startup_handler.setLevel(logging.INFO)
            startup_handler.setFormatter(formatter)
            logger.addHandler(startup_handler)

            # 2. System Log Handler
            system_handler = logging.FileHandler(system_log_file, encoding="utf-8")
            system_handler.setLevel(logging.INFO)
            system_handler.setFormatter(formatter)
            logger.addHandler(system_handler)

            # 3. Error Log Handler
            error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
            error_handler.setLevel(logging.WARNING)
            error_handler.setFormatter(formatter)
            logger.addHandler(error_handler)

            # 4. Debug Log Handler
            debug_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
            debug_handler.setLevel(logging.DEBUG)
            debug_handler.setFormatter(formatter)
            logger.addHandler(debug_handler)

        except Exception as file_err:
            print(f"[Warning] Safe Logger FileHandler initialization exception: {file_err}")

        # Console handler with Unicode fallback error handling
        class UnicodeSafeStreamHandler(logging.StreamHandler):
            def emit(self, record):
                try:
                    msg = self.format(record)
                    stream = self.stream
                    stream.write(msg + self.terminator)
                    self.flush()
                except UnicodeEncodeError:
                    safe_msg = str(record.getMessage()).encode("ascii", "replace").decode("ascii")
                    stream.write(f"[{self.formatter.formatTime(record)}] [{record.levelname}] [{record.name}]: {safe_msg}" + self.terminator)
                    self.flush()
                except Exception:
                    self.handleError(record)

        try:
            console_handler = UnicodeSafeStreamHandler(sys.stdout)
            console_handler.setLevel(logging.INFO)
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)
        except Exception as console_err:
            print(f"[Warning] Safe Logger StreamHandler exception: {console_err}")

        cls._logger_instance = logger
        return logger


def get_logger(name: str = "XAssistant") -> logging.Logger:
    """Get initialized logger instance."""
    return DualLogger.get_logger(name)


logger = get_logger("XAssistant")


def log_startup(message: str) -> None:
    """Log startup sequence event safely."""
    try:
        logger.info(f"[STARTUP] {message}")
    except Exception:
        pass


def log_system(message: str) -> None:
    """Log general system operational event safely."""
    try:
        logger.info(f"[SYSTEM] {message}")
    except Exception:
        pass


def log_error(message: str) -> None:
    """Log exception or error safely."""
    try:
        logger.error(f"[ERROR] {message}")
    except Exception:
        pass


def log_debug(message: str) -> None:
    """Log low-level debug trace safely."""
    try:
        logger.debug(f"[DEBUG] {message}")
    except Exception:
        pass
