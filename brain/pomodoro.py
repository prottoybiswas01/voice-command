"""
Pomodoro Focus Timer & Work Habits Module for X Assistant (Phase 3).
Provides focus timers (25m work / 5m break) with sound notifications and focus session tracking.
"""

import time
import threading
from typing import Optional, Callable
from config.settings import settings
from core.logger import logger
from core.database import db
from speech.tts import tts_engine


class PomodoroTimer:
    """Pomodoro Focus Timer daemon."""

    def __init__(self) -> None:
        self.focus_minutes = settings.agent.pomodoro_focus_minutes
        self.break_minutes = settings.agent.pomodoro_break_minutes
        self.is_active = False
        self.mode = "IDLE"  # IDLE, FOCUS, BREAK
        self.time_remaining_seconds = 0
        self._timer_thread: Optional[threading.Thread] = None

    def start_session(self, focus_min: Optional[int] = None, break_min: Optional[int] = None) -> str:
        """
        Start a new Pomodoro Focus session.
        
        Args:
            focus_min: Custom focus duration minutes.
            break_min: Custom break duration minutes.
        """
        if self.is_active:
            return f"Pomodoro session already running ({self.time_remaining_seconds // 60} minutes remaining)."

        self.focus_minutes = focus_min or settings.agent.pomodoro_focus_minutes
        self.break_minutes = break_min or settings.agent.pomodoro_break_minutes
        self.is_active = True
        self.mode = "FOCUS"
        self.time_remaining_seconds = self.focus_minutes * 60

        self._timer_thread = threading.Thread(target=self._run_timer, daemon=True)
        self._timer_thread.start()

        msg = f"Pomodoro Focus session started! Work focused for {self.focus_minutes} minutes."
        logger.info(msg)
        return msg

    def stop_session(self) -> str:
        """Stop active Pomodoro timer."""
        if not self.is_active:
            return "No active Pomodoro session to stop."

        self.is_active = False
        self.mode = "IDLE"
        msg = "Pomodoro Focus session stopped."
        logger.info(msg)
        return msg

    def get_status(self) -> str:
        """Return human-readable countdown status string."""
        if not self.is_active:
            return "Pomodoro Timer is IDLE."

        mins = self.time_remaining_seconds // 60
        secs = self.time_remaining_seconds % 60
        return f"Pomodoro [{self.mode}]: {mins:02d}:{secs:02d} remaining."

    def _run_timer(self) -> None:
        """Background countdown worker loop."""
        while self.is_active and self.time_remaining_seconds > 0:
            time.sleep(1)
            self.time_remaining_seconds -= 1

        if not self.is_active:
            return

        if self.mode == "FOCUS":
            # Focus period completed
            db.log_pomodoro_session(self.focus_minutes, self.break_minutes)
            msg = f"Great job! Focus session completed. Take a {self.break_minutes} minute break."
            logger.info(msg)
            tts_engine.speak(msg)
            
            # Switch to Break mode
            self.mode = "BREAK"
            self.time_remaining_seconds = self.break_minutes * 60
            while self.is_active and self.time_remaining_seconds > 0:
                time.sleep(1)
                self.time_remaining_seconds -= 1

            if self.is_active:
                break_msg = "Break time is over! Ready for the next focus session."
                logger.info(break_msg)
                tts_engine.speak(break_msg)

        self.is_active = False
        self.mode = "IDLE"


# Global Pomodoro Timer instance
pomodoro_timer = PomodoroTimer()
