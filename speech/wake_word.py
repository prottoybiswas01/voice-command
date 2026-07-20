"""
Wake Word Listener for X Assistant.
Continuously listens for wake words ("X", "Hey X", "X Listen") to trigger assistant activation.
"""

import time
from typing import Callable, Optional, List
from config.settings import settings
from speech.stt import stt_engine
from core.logger import logger
from core.event_bus import event_bus


class WakeWordDetector:
    """Wake Word Detector monitoring microphone for activation trigger words."""

    def __init__(self, wake_words: Optional[List[str]] = None) -> None:
        self.wake_words = [w.lower() for w in (wake_words or settings.assistant.wake_words)]
        # Add phonetic/transliterated variants for Bangla speech matching
        self.wake_words.extend(["এক্স", "হে এক্স", "এক্স শোনো", "এক্স শোন", "hey x", "x listen"])
        self.is_listening = False

    def is_wake_word_present(self, text: str) -> bool:
        """
        Check if input text contains any configured wake word.
        
        Args:
            text: Input phrase recognized by STT engine.
            
        Returns:
            True if wake word matches, False otherwise.
        """
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
            on_detected_callback: Optional function executed when wake word is detected.
            
        Returns:
            True if wake word heard, False otherwise.
        """
        recognized_text = stt_engine.listen_and_recognize(timeout=3, phrase_time_limit=4)
        if recognized_text and self.is_wake_word_present(recognized_text):
            logger.info(f"Wake word detected from voice input: '{recognized_text}'")
            event_bus.publish("wake_word_detected", text=recognized_text)
            if on_detected_callback:
                on_detected_callback()
            return True

        return False

    def start_loop(self, on_detected_callback: Callable[[], None]) -> None:
        """Run continuous wake word listening loop in background."""
        self.is_listening = True
        logger.info("Wake word detector active. Listening for 'X', 'Hey X', 'X Listen'...")
        
        while self.is_listening:
            try:
                self.listen_for_wake_word(on_detected_callback)
                time.sleep(0.1)
            except Exception as err:
                logger.error(f"Error in wake word loop: {err}")
                time.sleep(1.0)

    def stop(self) -> None:
        """Stop wake word detection loop."""
        self.is_listening = False


# Global Wake Word instance
wake_word_detector = WakeWordDetector()
