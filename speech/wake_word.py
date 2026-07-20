"""
Wake Word Listener for X Assistant (Phase 6 Cleaned & Fixed).
Continuously monitors microphone for wake words ("X", "Hey X", "X Listen", "হে এক্স")
and notifies orchestrator when activation triggers are spoken.
"""

import time
from typing import Callable, Optional, List
from config.settings import settings
from speech.stt import stt_engine
from core.logger import logger
from core.event_bus import event_bus


class WakeWordDetector:
    """Wake Word Detector monitoring microphone for activation trigger words without console spam."""

    def __init__(self, wake_words: Optional[List[str]] = None) -> None:
        self.wake_words = [w.lower() for w in (wake_words or settings.assistant.wake_words)]
        self.wake_words.extend(["엑스", "হে এক্স", "এক্স শোনো", "এক্স শোন", "hey x", "x listen", "x"])
        self.is_listening = False
        self._waiting_logged = False

    def is_wake_word_present(self, text: str) -> bool:
        """Check if input text contains any configured wake word."""
        if not text:
            return False

        clean_text = text.lower().strip()
        for word in self.wake_words:
            if word in clean_text:
                return True
        return False

    def listen_for_wake_word(self, on_detected_callback: Optional[Callable[[], None]] = None) -> bool:
        """
        Perform a single listening iteration for wake word.
        
        Args:
            on_detected_callback: Function executed when wake word is detected.
            
        Returns:
            True if wake word heard, False otherwise.
        """
        if not self._waiting_logged:
            print("Waiting for wake word...")
            logger.debug("Waiting for wake word...")
            self._waiting_logged = True

        recognized_text = stt_engine.listen_and_recognize(timeout=3, phrase_time_limit=4)
        if recognized_text:
            print(f"[Voice System] Recognized speech: \"{recognized_text}\"")
            if self.is_wake_word_present(recognized_text):
                print(f"[Voice System] Wake word detected: \"{recognized_text}\"")
                logger.info(f"[Voice System] Wake word detected: '{recognized_text}'")
                event_bus.publish("wake_word_detected", text=recognized_text)
                self._waiting_logged = False  # Reset for next prompt
                if on_detected_callback:
                    on_detected_callback()
                return True

        return False

    def start_loop(self, on_detected_callback: Callable[[], None]) -> None:
        """Run continuous wake word listening loop in background thread."""
        self.is_listening = True
        self._waiting_logged = False
        print("\n[Voice System] Wake word detector active.")
        print("[Voice System] Listening for 'X', 'Hey X', 'X Listen'...")
        logger.info("[Voice System] Wake word detector active.")

        while self.is_listening:
            try:
                self.listen_for_wake_word(on_detected_callback)
                time.sleep(0.2)
            except Exception as err:
                logger.error(f"Error in wake word loop: {err}")
                time.sleep(1.0)

    def stop(self) -> None:
        """Stop wake word detection loop."""
        self.is_listening = False


# Global Wake Word instance
wake_word_detector = WakeWordDetector()
