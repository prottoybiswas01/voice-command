"""
System Actions Module for X Assistant.
Handles Windows OS application launches, system time/date queries, power management, and exit routines.
"""

import os
import sys
import subprocess
from datetime import datetime
from typing import Dict, Any, Tuple
from core.logger import logger
from core.database import db


class SystemActionsHandler:
    """Executes Windows system commands and controls."""

    def __init__(self) -> None:
        self.app_paths = {
            "chrome": ["chrome.exe", "start chrome"],
            "edge": ["msedge.exe", "start msedge"],
            "vscode": ["code", "code.cmd"],
            "notepad": ["notepad.exe"],
            "calculator": ["calc.exe"],
            "explorer": ["explorer.exe"],
            "task_manager": ["taskmgr.exe"]
        }

    def execute_app_launch(self, app_name: str) -> str:
        """
        Open specified local Windows application.
        
        Args:
            app_name: Name of application key.
            
        Returns:
            Status response message.
        """
        if app_name not in self.app_paths:
            msg = f"Application '{app_name}' is not recognized."
            logger.warning(msg)
            return msg

        commands = self.app_paths[app_name]
        launched = False

        for cmd in commands:
            try:
                if cmd.startswith("start "):
                    subprocess.Popen(cmd, shell=True)
                else:
                    subprocess.Popen([cmd], shell=True)
                launched = True
                break
            except Exception as err:
                logger.debug(f"Failed to launch via {cmd}: {err}")

        if launched:
            msg = f"Opening {app_name.replace('_', ' ').capitalize()}."
            logger.info(msg)
            db.log_command(f"open_app:{app_name}", "SUCCESS", msg)
            return msg
        else:
            msg = f"Failed to open {app_name}. Please verify path installation."
            logger.error(msg)
            db.log_command(f"open_app:{app_name}", "FAILED", msg)
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
            
        return f"{time_greeting}! I am X Assistant. How can I assist you today?"

    def confirm_power_action(self, action: str) -> str:
        """
        Request user confirmation for critical power commands.
        
        Args:
            action: 'shutdown', 'restart', or 'sleep'.
            
        Returns:
            Confirmation prompt message.
        """
        if action == "shutdown":
            return "Are you sure you want to shutdown the computer? Say confirm to proceed."
        elif action == "restart":
            return "Are you sure you want to restart the computer? Say confirm to proceed."
        elif action == "sleep":
            return "Putting computer to sleep."
            # Native Windows sleep command
            os.system("rundll32.exe powrprof.dll,SetSuspendState 0,1,0")
            return "Goodnight. Computer is going to sleep."
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
