"""
Logging framework for X Assistant (Unicode Safe Upgrade).
Handles daily execution logging, error logging, debug logging, and Unicode-safe console output.
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
    """Manages custom daily, debug, and error log file handlers with Unicode safety."""

    _logger_instance: Optional[logging.Logger] = None

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

        daily_log_file = logs_dir / f"daily_{today_str}.log"
        error_log_file = logs_dir / f"error_{today_str}.log"
        debug_log_file = logs_dir / "debug.log"

        formatter = logging.Formatter(
            fmt="[%(asctime)s] [%(levelname)s] [%(name)s]: %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )

        # File handler for all daily logs
        daily_handler = logging.FileHandler(daily_log_file, encoding="utf-8")
        daily_handler.setLevel(logging.INFO)
        daily_handler.setFormatter(formatter)
        logger.addHandler(daily_handler)

        # File handler for error logs
        error_handler = logging.FileHandler(error_log_file, encoding="utf-8")
        error_handler.setLevel(logging.ERROR)
        error_handler.setFormatter(formatter)
        logger.addHandler(error_handler)

        # File handler for debug logs
        debug_handler = logging.FileHandler(debug_log_file, encoding="utf-8")
        debug_handler.setLevel(logging.DEBUG)
        debug_handler.setFormatter(formatter)
        logger.addHandler(debug_handler)

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

        console_handler = UnicodeSafeStreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

        cls._logger_instance = logger
        return logger


def get_logger(name: str = "XAssistant") -> logging.Logger:
    """Get initialized logger instance."""
    return DualLogger.get_logger(name)


logger = get_logger("XAssistant")
