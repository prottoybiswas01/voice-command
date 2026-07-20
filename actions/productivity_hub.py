"""
Productivity Hub Module for X Assistant (Phase 3).
Integrates Pomodoro Focus Timer, Windows Clipboard History tracking, Calendar events, and Voice Notes.
"""

import time
import threading
from typing import List, Dict, Any, Optional
from core.logger import logger
from core.database import db
from brain.pomodoro import pomodoro_timer
from actions.recorder import recorder

try:
    import pyperclip
except ImportError:
    pyperclip = None
    logger.warning("pyperclip library not installed. Clipboard history tracking disabled.")


class ProductivityHub:
    """Manages Pomodoro, Clipboard, Calendar, and Voice Notes."""

    def __init__(self) -> None:
        self.is_clipboard_daemon_active = False
        self._start_clipboard_daemon()

    # Pomodoro Focus Timer
    def control_pomodoro(self, action: str = "start", focus_min: int = 25, break_min: int = 5) -> str:
        """Control Pomodoro Focus session."""
        if action == "start":
            return pomodoro_timer.start_session(focus_min, break_min)
        elif action == "stop":
            return pomodoro_timer.stop_session()
        else:
            return pomodoro_timer.get_status()

    # Clipboard History Tracking
    def get_clipboard_history(self, limit: int = 5) -> str:
        """Retrieve recent Windows clipboard history snippets."""
        history = db.get_clipboard_history(limit=limit)
        if not history:
            return "Clipboard history is empty."

        snippets = [f"{i+1}. '{item['content'][:60]}...'" for i, item in enumerate(history)]
        msg = f"Recent Clipboard History ({len(history)} items):\n" + "\n".join(snippets)
        return msg

    def _start_clipboard_daemon(self) -> None:
        """Background thread tracking text copied to Windows clipboard."""
        if not pyperclip:
            return

        def _clipboard_worker():
            self.is_clipboard_daemon_active = True
            last_text = ""
            while self.is_clipboard_daemon_active:
                try:
                    current_text = pyperclip.paste()
                    if current_text and current_text != last_text and len(current_text.strip()) > 3:
                        last_text = current_text
                        db.save_clipboard_text(current_text)
                except Exception:
                    pass
                time.sleep(2)

        thread = threading.Thread(target=_clipboard_worker, daemon=True)
        thread.start()

    # Calendar Events
    def add_calendar_event(self, title: str, event_date: str, event_time: str = "09:00 AM", description: str = "") -> str:
        """Add new calendar event."""
        if not title:
            return "Please specify a title for the calendar event."

        event_id = db.add_calendar_event(title, event_date, event_time, description)
        msg = f"Calendar event added: '{title}' on {event_date} at {event_time}."
        logger.info(msg)
        return msg

    def list_calendar_events(self) -> str:
        """List upcoming calendar events."""
        events = db.get_upcoming_calendar_events()
        if not events:
            return "No upcoming calendar events found."

        items = [f"{i+1}. {e['title']} ({e['event_date']} {e['event_time']})" for i, e in enumerate(events)]
        msg = "Upcoming Calendar Events: " + "; ".join(items)
        return msg

    # Voice Note Recording Shortcut
    def record_voice_note(self, duration_sec: int = 10) -> str:
        """Record microphone audio note."""
        return recorder.record_audio_note(duration_sec)


# Global Productivity Hub instance
productivity_hub = ProductivityHub()
