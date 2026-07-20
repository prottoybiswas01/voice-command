"""
Media & Volume Actions Module for X Assistant.
Manages system audio volume (up, down, mute) and media playback keys (play, pause, stop).
"""

from core.logger import logger
from core.database import db

try:
    import pyautogui
except ImportError:
    pyautogui = None
    logger.warning("pyautogui module not installed. Keyboard media keys simulation limited.")


class MediaActionsHandler:
    """Controls volume and media playback using Windows keyboard shortcuts."""

    def control_volume(self, command: str) -> str:
        """
        Adjust system audio volume or mute state.
        
        Args:
            command: 'up', 'down', or 'mute'.
            
        Returns:
            Status message string.
        """
        if not pyautogui:
            return "PyAutoGUI is required for hardware volume control."

        try:
            if command == "up":
                for _ in range(5):
                    pyautogui.press("volumeup")
                msg = "Volume increased."
            elif command == "down":
                for _ in range(5):
                    pyautogui.press("volumedown")
                msg = "Volume decreased."
            elif command == "mute":
                pyautogui.press("volumemute")
                msg = "Volume muted or unmuted."
            else:
                msg = f"Unknown volume command: {command}"

            logger.info(f"Media action: {msg}")
            db.log_command(f"volume:{command}", "SUCCESS", msg)
            return msg

        except Exception as err:
            logger.error(f"Error controlling volume: {err}")
            return f"Failed to adjust volume: {err}"

    def control_media(self, command: str) -> str:
        """
        Control media playback (Play/Pause/Stop).
        
        Args:
            command: 'play', 'pause', or 'stop'.
            
        Returns:
            Status message string.
        """
        if not pyautogui:
            return "PyAutoGUI is required for media key simulation."

        try:
            if command in ["play", "pause"]:
                pyautogui.press("playpause")
                msg = "Media playback toggled (Play/Pause)."
            elif command == "stop":
                pyautogui.press("stop")
                msg = "Media playback stopped."
            else:
                msg = f"Unknown media command: {command}"

            logger.info(f"Media control action: {msg}")
            db.log_command(f"media:{command}", "SUCCESS", msg)
            return msg

        except Exception as err:
            logger.error(f"Error controlling media playback: {err}")
            return f"Failed to control media: {err}"


# Global MediaActionsHandler instance
media_actions = MediaActionsHandler()
