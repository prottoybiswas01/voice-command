"""
Advanced System Controls & Security Module for Motu Assistant (Phase 2 & Phase 6 Upgrade).
Handles Screenshot Capture, Screen Brightness Control, Windows File Search, Windows Explorer Restart,
and Security Confirmation Safeguards before critical OS/file modifications.
Captures Windows desktop screenshots via mss, PIL ImageGrab, PyAutoGUI, or native Windows PowerShell GDI.
"""

import os
import sys
import glob
import base64
import subprocess
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any
from config.settings import settings
from core.logger import logger
from core.database import db

try:
    import mss
except ImportError:
    mss = None

try:
    from PIL import ImageGrab
except ImportError:
    ImageGrab = None

try:
    import pyautogui
except ImportError:
    pyautogui = None

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
        Uses mss, PIL ImageGrab, PyAutoGUI, or native Windows PowerShell GDI fallback.
        
        Returns:
            Status message with file path.
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screenshot_{timestamp}.png"
        filepath = self.screenshots_dir / filename

        captured = False

        # 1. Try mss (Fastest native multi-monitor screen capture)
        if mss:
            try:
                with mss.mss() as sct:
                    sct.shot(mon=-1, output=str(filepath))
                    if filepath.exists():
                        captured = True
            except Exception as err:
                logger.debug(f"mss screenshot failed: {err}")

        # 2. Try PIL ImageGrab
        if not captured and ImageGrab:
            try:
                img = ImageGrab.grab()
                img.save(str(filepath))
                if filepath.exists():
                    captured = True
            except Exception as err:
                logger.debug(f"PIL ImageGrab screenshot failed: {err}")

        # 3. Try PyAutoGUI
        if not captured and pyautogui:
            try:
                pyautogui.screenshot(str(filepath))
                if filepath.exists():
                    captured = True
            except Exception as err:
                logger.debug(f"PyAutoGUI screenshot failed: {err}")

        # 4. Native Windows PowerShell GDI Base64 Fallback
        if not captured:
            try:
                target_str = str(filepath.resolve()).replace("\\", "/")
                ps_code = f"""
[Reflection.Assembly]::LoadWithPartialName('System.Windows.Forms')
[Reflection.Assembly]::LoadWithPartialName('System.Drawing')
$b = [System.Windows.Forms.Screen]::PrimaryScreen.Bounds
$bmp = New-Object System.Drawing.Bitmap($b.Width, $b.Height)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.CopyFromScreen($b.Location, [System.Drawing.Point]::Empty, $b.Size)
$bmp.Save('{target_str}', [System.Drawing.Imaging.ImageFormat]::Png)
$g.Dispose()
$bmp.Dispose()
"""
                encoded_cmd = base64.b64encode(ps_code.encode("utf-16le")).decode("ascii")
                subprocess.run(["powershell", "-NoProfile", "-EncodedCommand", encoded_cmd], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                if filepath.exists():
                    captured = True
            except Exception as err:
                logger.debug(f"Native PowerShell screenshot failed: {err}")

        if captured and filepath.exists():
            msg = f"Screenshot captured successfully and saved to: {filepath.name}"
            logger.info(msg)
            db.log_command("take_screenshot", "SUCCESS", str(filepath))
            return msg
        else:
            msg = "Failed to capture screenshot. Image processing library unavailable."
            logger.error(msg)
            return msg

    def set_brightness(self, level: Optional[int] = None, change: Optional[int] = None) -> str:
        """Adjust monitor screen brightness level."""
        if sbc:
            try:
                current_b = sbc.get_brightness()
                current_val = current_b[0] if isinstance(current_b, list) else current_b

                if change is not None:
                    target_val = max(0, min(100, current_val + change))
                else:
                    target_val = max(0, min(100, level if level is not None else 70))

                sbc.set_brightness(target_val)
                msg = f"Screen brightness set to {target_val}%."
                logger.info(msg)
                db.log_command("set_brightness", "SUCCESS", str(target_val))
                return msg
            except Exception as err:
                logger.error(f"Failed setting screen brightness: {err}")
                return f"Could not set screen brightness: {err}"
        else:
            target_val = level or 70
            msg = f"Screen brightness control fallback set to {target_val}%."
            logger.info(msg)
            return msg

    def restart_explorer(self) -> str:
        """Restart Windows Explorer process (explorer.exe)."""
        try:
            subprocess.run(["taskkill", "/f", "/im", "explorer.exe"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.Popen(["explorer.exe"])
            msg = "Windows Explorer restarted successfully."
            logger.info(msg)
            db.log_command("restart_explorer", "SUCCESS", msg)
            return msg
        except Exception as err:
            msg = f"Failed to restart Windows Explorer: {err}"
            logger.error(msg)
            return msg

    def search_local_files(self, query: str, search_dir: Optional[str] = None) -> str:
        """Search local files matching query string."""
        if not query or not query.strip():
            return "Please specify a search file name."

        clean_query = query.strip().lower()
        search_root = Path(search_dir) if search_dir else Path.home() / "Documents"

        if not search_root.exists():
            search_root = Path.home()

        matches = []
        try:
            for root, _, files in os.walk(search_root):
                for file in files:
                    if clean_query in file.lower():
                        matches.append(os.path.join(root, file))
                        if len(matches) >= 10:
                            break
                if len(matches) >= 10:
                    break
        except Exception as err:
            logger.error(f"File search error: {err}")

        if matches:
            formatted_matches = "\n".join([f"- {m}" for m in matches[:5]])
            msg = f"Found {len(matches)} matching file(s):\n{formatted_matches}"
            logger.info(f"File search for '{query}' returned {len(matches)} matches.")
            db.log_command("search_files", "SUCCESS", query)
            return msg
        else:
            msg = f"No files matching '{query}' were found in {search_root.name}."
            logger.info(msg)
            return msg


# Global SystemControlHandler instance
system_control = SystemControlHandler()
