"""
Productivity and System Metrics Actions Module for X Assistant.
Handles Todo tasks, Notes, Reminders, and OS hardware health stats (CPU, RAM, Battery, Network).
"""

import time
import socket
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List
from core.logger import logger
from core.database import db
from speech.tts import tts_engine

try:
    import psutil
except ImportError:
    psutil = None
    logger.warning("psutil module not installed. Hardware system diagnostics limited.")


class ProductivityActionsHandler:
    """Manages system diagnostics and productivity items (Todos, Notes, Reminders)."""

    def __init__(self) -> None:
        self._start_reminder_daemon()

    # System Metrics (CPU, RAM, Battery, Internet)
    def get_system_info(self, metric: str = "all") -> str:
        """
        Gather CPU, RAM, Battery, and Internet connectivity metrics.
        
        Args:
            metric: 'battery', 'cpu', 'ram', 'internet', or 'all'.
            
        Returns:
            Human readable metrics summary string.
        """
        results: List[str] = []

        if metric in ["cpu", "all"]:
            cpu_percent = psutil.cpu_percent(interval=0.5) if psutil else "N/A"
            results.append(f"CPU usage is at {cpu_percent}%.")

        if metric in ["ram", "all"]:
            if psutil:
                ram = psutil.virtual_memory()
                ram_percent = ram.percent
                results.append(f"RAM usage is at {ram_percent}% ({round(ram.used / (1024**3), 1)}GB used).")
            else:
                results.append("RAM info N/A.")

        if metric in ["battery", "all"]:
            if psutil and hasattr(psutil, "sensors_battery"):
                battery = psutil.sensors_battery()
                if battery:
                    plugged = "plugged in" if battery.power_plugged else "on battery"
                    results.append(f"Battery is at {battery.percent}% ({plugged}).")
                else:
                    results.append("No battery detected.")
            else:
                results.append("Battery info N/A.")

        if metric in ["internet", "all"]:
            is_connected = self.check_internet_connection()
            status = "Online and connected" if is_connected else "Offline"
            results.append(f"Internet status: {status}.")

        response = " ".join(results)
        logger.info(f"System Info ({metric}): {response}")
        return response

    def check_internet_connection(self, host: str = "8.8.8.8", port: int = 53, timeout: int = 3) -> bool:
        """Ping external DNS to check internet status."""
        try:
            socket.setdefaulttimeout(timeout)
            socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
            return True
        except Exception:
            return False

    # Todos Management
    def add_todo_task(self, task: str) -> str:
        """Add a new task to todo list."""
        if not task:
            return "Please specify a task to add to your todo list."

        row_id = db.add_todo(task)
        msg = f"Task added to todo list: '{task}'."
        logger.info(msg)
        return msg

    def list_todo_tasks(self) -> str:
        """Read pending todo tasks."""
        todos = db.get_pending_todos()
        if not todos:
            return "Your todo list is empty! Great job."

        taskList = [f"{i+1}. {item['task']}" for i, item in enumerate(todos)]
        msg = f"You have {len(todos)} pending tasks: " + ", ".join(taskList)
        return msg

    # Notes Management
    def save_simple_note(self, content: str, title: str = "Voice Note") -> str:
        """Save a new note to database."""
        if not content:
            return "What would you like me to note down?"

        db.add_note(title=title, content=content)
        msg = f"Note saved: '{content}'."
        logger.info(msg)
        return msg

    def read_notes(self) -> str:
        """Retrieve latest notes."""
        notes = db.get_notes(limit=3)
        if not notes:
            return "You have no saved notes."

        summary = [f"Note {i+1}: {n['content']}" for i, n in enumerate(notes)]
        return "Here are your recent notes: " + "; ".join(summary)

    # Reminders Management
    def set_reminder(self, message: str, delay_minutes: int = 10) -> str:
        """
        Schedule a reminder message.
        
        Args:
            message: Message to remind user.
            delay_minutes: Minutes from now to fire reminder.
        """
        if not message:
            return "What should I remind you about?"

        remind_time = (datetime.now() + timedelta(minutes=delay_minutes)).strftime("%Y-%m-%d %H:%M:%S")
        db.add_reminder(message, remind_time)

        msg = f"Reminder set for '{message}' in {delay_minutes} minutes."
        logger.info(msg)
        return msg

    def _start_reminder_daemon(self) -> None:
        """Start background daemon checking for due reminders every 10 seconds."""
        def check_reminders():
            while True:
                try:
                    due_list = db.get_due_reminders()
                    for item in due_list:
                        reminder_msg = f"REMINDER ALERT: {item['message']}"
                        logger.info(reminder_msg)
                        tts_engine.speak(reminder_msg)
                        db.mark_reminder_triggered(item['id'])
                except Exception as err:
                    logger.error(f"Error checking reminders: {err}")
                time.sleep(10)

        thread = threading.Thread(target=check_reminders, daemon=True)
        thread.start()


# Global ProductivityActionsHandler instance
productivity_actions = ProductivityActionsHandler()
