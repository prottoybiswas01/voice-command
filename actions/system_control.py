"""
Advanced System Controls & Security Module for X Assistant (Phase 2).
Handles Screenshot Capture, Screen Brightness Control, Windows File Search, Windows Explorer Restart,
and Security Confirmation Safeguards before critical OS/file modifications.
"""

import os
import sys
import glob
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from config.settings import settings
from core.logger import logger
from core.database import db

try:
    import pyautogui
except ImportError:
    pyautogui = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    import screen_brightness_control as sbc
except ImportError:
    sbc = None
    logger.warning("screen_brightness_control module not installed. Brightness control fallback active.")


class SystemControlHandler:
    """Manages Windows OS hardware actions, screen capture, file indexing, and security checks."""

    def __init__(self) -> None:
        self.screenshots_dir = settings.paths.screenshots_dir
        self.screenshots_dir.mkdir(parents=True, exist_ok=True)

    def take_screenshot(self) -> str:
        """
        Capture desktop screen and save to data/screenshots/ folder.
        
        Returns:
            Status message with file path.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        captured = False

        if pyautogui:
            try:
                pyautogui.screenshot(str(filepath))
                captured = True
            except Exception as err:
                logger.debug(f"PyAutoGUI screenshot failed: {err}")

        if not captured and ImageGrab:
            try:
                img = ImageGrab.grab()
                img.save(str(filepath))
                captured = True
            except Exception as err:
                logger.debug(f"PIL ImageGrab screenshot failed: {err}")

        if captured and filepath.exists():
            msg = f"Screenshot captured and saved to: {filepath.name}"
            logger.info(msg)
            db.log_command("take_screenshot", "SUCCESS", str(filepath))
            return msg
        else:
            msg = "Failed to capture screenshot. Image processing library unavailable."
            logger.error(msg)
            return msg

    def set_brightness(self, level: Optional[int] = None, change: Optional[int] = None) -> str:
        """
        Adjust monitor screen brightness level.
        
        Args:
            level: Target percentage (0 - 100).
            change: Relative change (+20 or -20).
            
        Returns:
            Status message string.
        """
        if sbc:
            try:
                current_b = sbc.get_brightness()
                current_val = current_b[0] if isinstance(current_b, list) else current_b

                if change is not None:
                    target_val = max(0, min(100, current_val + change))
                else:
                    target_val = max(0, min(100, level if level is not None else 70))

                sbc.set_brightness(target_val)
                msg = f"Screen brightness adjusted to {target_val}%."
                logger.info(msg)
                db.log_command("set_brightness", "SUCCESS", msg)
                return msg
            except Exception as err:
                logger.error(f"Failed to adjust screen brightness via sbc: {err}")

        # PowerShell fallback for brightness
        try:
            target_val = max(0, min(100, level if level is not None else 70))
            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {target_val})"
            subprocess.run(["powershell", "-Command", ps_cmd], capture_output=True)
            msg = f"Set screen brightness to {target_val}%."
            logger.info(msg)
            return msg
        except Exception as err:
            logger.error(f"PowerShell brightness fallback error: {err}")

        return "Screen brightness adjustment failed."

    def restart_explorer(self) -> str:
        """Restart Windows File Explorer process (explorer.exe)."""
        try:
            subprocess.run("taskkill /f /im explorer.exe", shell=True, capture_output=True)
            subprocess.Popen("explorer.exe", shell=True)
            msg = "Windows File Explorer restarted successfully."
            logger.info(msg)
            db.log_command("restart_explorer", "SUCCESS", msg)
            return msg
        except Exception as err:
            logger.error(f"Failed to restart Windows Explorer: {err}")
            return f"Failed to restart Windows Explorer: {err}"

    def search_local_files(self, query: str, search_dir: Optional[str] = None) -> str:
        """
        Search user documents, downloads, and desktop for files matching query.
        
        Args:
            query: File substring query string.
            search_dir: Optional root directory to search.
            
        Returns:
            Found file list string summary.
        """
        if not query or not query.strip():
            return "Please specify a file name or keyword to search."

        clean_query = query.strip().lower()
        search_roots = [
            Path.home() / "Documents",
            Path.home() / "Downloads",
            Path.home() / "Desktop"
        ]

        found_files: List[Path] = []

        for root in search_roots:
            if not root.exists():
                continue
            try:
                for path in root.rglob(f"*{clean_query}*"):
                    if path.is_file():
                        found_files.append(path)
                        if len(found_files) >= 5:
                            break
            except Exception:
                continue

        if not found_files:
            return f"No files matching '{clean_query}' were found in Documents, Downloads, or Desktop."

        file_names = [f"{i+1}. {f.name} ({f.parent.name})" for i, f in enumerate(found_files)]
        msg = f"Found {len(found_files)} matching files: " + ", ".join(file_names)
        logger.info(msg)
        return msg

    def check_security_confirmation(self, action_type: str, item_name: str) -> Tuple[bool, str]:
        """
        Evaluate if an action requires explicit user confirmation.
        
        Args:
            action_type: 'shutdown', 'restart', 'delete', 'close_app'.
            item_name: Target item name.
            
        Returns:
            Tuple of (requires_confirm: bool, prompt_message: str).
        """
        critical_actions = ["shutdown", "restart", "delete", "close_app"]

        if action_type in critical_actions:
            prompt = f"SECURITY ALERT: Are you sure you want to proceed with '{action_type}' on '{item_name}'? Say confirm to proceed."
            logger.warning(f"Security gate triggered for {action_type} - {item_name}")
            return True, prompt

        return False, ""


# Global SystemControlHandler instance
system_control = SystemControlHandler()
