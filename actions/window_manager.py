"""
Native Win32 Application Window Manager Module for X Assistant (Phase 3).
Controls active Windows application windows: Minimize, Maximize, Restore, Close, and Bring to Foreground.
"""

import sys
import ctypes
from typing import List, Dict, Any, Optional
from core.logger import logger
from core.database import db

try:
    import win32gui
    import win32con
    import win32process
except ImportError:
    win32gui = None
    win32con = None
    win32process = None
    logger.warning("pywin32 library unavailable. Window Manager controls will operate in fallback mode.")


class WindowManager:
    """Manages application windows using native Windows API."""

    def __init__(self) -> None:
        self.user32 = ctypes.windll.user32 if hasattr(ctypes, "windll") else None

    def list_open_windows(self) -> List[Dict[str, Any]]:
        """
        Enumerate all visible desktop top-level windows.
        
        Returns:
            List of dict items containing hwnd and window title string.
        """
        windows: List[Dict[str, Any]] = []

        if win32gui:
            def enum_windows_callback(hwnd, extra):
                if win32gui.IsWindowVisible(hwnd):
                    title = win32gui.GetWindowText(hwnd).strip()
                    if title and title not in ["Program Manager", "Settings"]:
                        windows.append({"hwnd": hwnd, "title": title})
                return True

            try:
                win32gui.EnumWindows(enum_windows_callback, None)
            except Exception as err:
                logger.error(f"Error enumerating windows: {err}")

        return windows

    def find_window_by_keyword(self, keyword: str) -> Optional[int]:
        """Find window HWND matching keyword string."""
        if not keyword:
            return None

        clean_k = keyword.lower().strip()
        open_wins = self.list_open_windows()

        for win in open_wins:
            if clean_k in win["title"].lower():
                return win["hwnd"]

        return None

    def minimize_window(self, app_keyword: Optional[str] = None) -> str:
        """Minimize active window or specified app window."""
        if not win32gui or not win32con:
            return "PyWin32 is required for window minimization."

        hwnd = self.find_window_by_keyword(app_keyword) if app_keyword else win32gui.GetForegroundWindow()
        if not hwnd:
            return f"Window for '{app_keyword}' not found."

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            title = win32gui.GetWindowText(hwnd)
            msg = f"Minimized window: '{title}'."
            logger.info(msg)
            db.log_command("minimize_window", "SUCCESS", title)
            return msg
        except Exception as err:
            logger.error(f"Failed to minimize window: {err}")
            return f"Failed to minimize window: {err}"

    def maximize_window(self, app_keyword: Optional[str] = None) -> str:
        """Maximize target window."""
        if not win32gui or not win32con:
            return "PyWin32 is required for window maximization."

        hwnd = self.find_window_by_keyword(app_keyword) if app_keyword else win32gui.GetForegroundWindow()
        if not hwnd:
            return f"Window for '{app_keyword}' not found."

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            title = win32gui.GetWindowText(hwnd)
            msg = f"Maximized window: '{title}'."
            logger.info(msg)
            db.log_command("maximize_window", "SUCCESS", title)
            return msg
        except Exception as err:
            logger.error(f"Failed to maximize window: {err}")
            return f"Failed to maximize window: {err}"

    def bring_to_front(self, app_keyword: str) -> str:
        """Switch focus to application window."""
        if not win32gui or not win32con:
            return "PyWin32 is required for window switching."

        hwnd = self.find_window_by_keyword(app_keyword)
        if not hwnd:
            return f"Could not find open window matching '{app_keyword}'."

        try:
            win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            title = win32gui.GetWindowText(hwnd)
            msg = f"Switched focus to window: '{title}'."
            logger.info(msg)
            db.log_command("switch_window", "SUCCESS", title)
            return msg
        except Exception as err:
            logger.error(f"Failed to switch to window: {err}")
            return f"Failed to switch window focus: {err}"

    def close_window(self, app_keyword: Optional[str] = None) -> str:
        """Close target application window."""
        if not win32gui or not win32con:
            return "PyWin32 is required for window closing."

        hwnd = self.find_window_by_keyword(app_keyword) if app_keyword else win32gui.GetForegroundWindow()
        if not hwnd:
            return f"Window for '{app_keyword}' not found."

        try:
            title = win32gui.GetWindowText(hwnd)
            win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)
            msg = f"Closed application window: '{title}'."
            logger.info(msg)
            db.log_command("close_window", "SUCCESS", title)
            return msg
        except Exception as err:
            logger.error(f"Failed to close window: {err}")
            return f"Failed to close window: {err}"


# Global Window Manager instance
window_manager = WindowManager()
