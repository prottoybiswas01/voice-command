"""
System Actions Module for X Assistant (Phase 6 Upgraded & Debugged).
Handles Windows OS application launches, system time/date queries, power management, and exit routines.
Locates absolute executable paths for Chrome, Edge, VS Code, Notepad, Calculator, Explorer, etc.
"""

import os
import sys
import subprocess
import webbrowser
from datetime import datetime
from typing import Dict, Any, Tuple
from core.logger import logger
from core.database import db


class SystemActionsHandler:
    """Executes Windows system commands and controls with Phase-6 robust path resolution."""

    def __init__(self) -> None:
        pass

    def execute_app_launch(self, app_name: str) -> str:
        """Open specified local Windows application."""
        clean_app = app_name.lower().strip()

        # Common Windows Installation Directories
        program_files = os.environ.get("ProgramFiles", r"C:\Program Files")
        program_files_x86 = os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")
        local_app_data = os.environ.get("LOCALAPPDATA", r"C:\Users\USER\AppData\Local")

        app_launchers = {
            "chrome": [
                rf"{program_files}\Google\Chrome\Application\chrome.exe",
                rf"{program_files_x86}\Google\Chrome\Application\chrome.exe",
                rf"{local_app_data}\Google\Chrome\Application\chrome.exe",
                "start chrome",
                "chrome"
            ],
            "edge": [
                rf"{program_files_x86}\Microsoft\Edge\Application\msedge.exe",
                rf"{program_files}\Microsoft\Edge\Application\msedge.exe",
                "start msedge",
                "msedge"
            ],
            "vscode": [
                rf"{local_app_data}\Programs\Microsoft VS Code\Code.exe",
                rf"{program_files}\Microsoft VS Code\Code.exe",
                "code",
                "start code"
            ],
            "notepad": ["notepad.exe", "start notepad"],
            "calculator": ["calc.exe", "start calc"],
            "explorer": ["explorer.exe"],
            "task_manager": ["taskmgr.exe"]
        }

        if clean_app not in app_launchers:
            try:
                subprocess.Popen(f'start "" "{clean_app}"', shell=True)
                msg = f"Opening {clean_app.capitalize()}."
                logger.info(msg)
                db.log_command(f"open_app:{clean_app}", "SUCCESS", msg)
                return msg
            except Exception as err:
                msg = f"Application '{clean_app}' not recognized."
                logger.warning(msg)
                return msg

        candidates = app_launchers[clean_app]
        launched = False

        for item in candidates:
            if os.path.exists(item):
                try:
                    subprocess.Popen([item])
                    launched = True
                    break
                except Exception as err:
                    logger.debug(f"Failed to launch path {item}: {err}")
            else:
                try:
                    if item.startswith("start "):
                        subprocess.Popen(item, shell=True)
                    else:
                        subprocess.Popen(f'start "" "{item}"', shell=True)
                    launched = True
                    break
                except Exception as err:
                    logger.debug(f"Failed to launch command {item}: {err}")

        # Browser fallback using webbrowser module
        if not launched and clean_app in ["chrome", "edge"]:
            try:
                webbrowser.open("https://www.google.com")
                launched = True
            except Exception:
                pass

        if launched:
            msg = f"Opening {clean_app.replace('_', ' ').capitalize()}."
            logger.info(msg)
            db.log_command(f"open_app:{clean_app}", "SUCCESS", msg)
            return msg
        else:
            msg = f"Failed to open {clean_app}. Please check path installation."
            logger.error(msg)
            db.log_command(f"open_app:{clean_app}", "FAILED", msg)
            return msg

    def get_current_time(self) -> str:
        """Return formatted current system time."""
        now = datetime.now()
        time_str = now.strftime("%I:%M %p")
        msg = f"The current time is {time_str}."
        logger.info(msg)
        return msg

    def get_current_date(self) -> str:
        """Return formatted current date."""
        now = datetime.now()
        date_str = now.strftime("%A, %B %d, %Y")
        msg = f"Today's date is {date_str}."
        logger.info(msg)
        return msg

    def handle_greeting(self) -> str:
        """Return warm welcome greeting."""
        now_hour = datetime.now().hour
        if now_hour < 12:
            time_greeting = "Good morning"
        elif now_hour < 18:
            time_greeting = "Good afternoon"
        else:
            time_greeting = "Good evening"
            
        return f"{time_greeting}! I am X Assistant Phase 6. How can I help you today?"

    def confirm_power_action(self, action: str) -> str:
        """Request user confirmation for critical power commands."""
        if action == "shutdown":
            return "Are you sure you want to shutdown the computer? Say confirm to proceed."
        elif action == "restart":
            return "Are you sure you want to restart the computer? Say confirm to proceed."
        elif action == "sleep":
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Putting computer to sleep. Goodnight."
        return "Unknown power action."

    def execute_confirmed_power_action(self, action: str) -> str:
        """Execute shutdown or restart after confirmation."""
        try:
            if action == "shutdown":
                os.system("shutdown /s /t 5")
                return "Shutting down the computer in 5 seconds."
            elif action == "restart":
                os.system("shutdown /r /t 5")
                return "Restarting the computer in 5 seconds."
        except Exception as err:
            logger.error(f"Power command error: {err}")
            return f"Failed to execute {action}: {err}"
        return "Invalid power action."


# Global SystemActionsHandler instance
system_actions = SystemActionsHandler()
