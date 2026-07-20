"""
Wake Word Listener for X Assistant (Phase 6 Final Upgrade & Bangla Fix).
Continuously monitors microphone for wake words ("X", "Hey X", "X Listen", "হে এক্স", "এক্স")
using boundary regex matching to prevent false substring matches,
and extracts any command payload spoken after the wake word in a single utterance.
"""

import re
import time
from typing import Callable, Optional, List, Tuple
from config.settings import settings
from speech.stt import stt_engine
from core.logger import logger
from core.event_bus import event_bus


class WakeWordDetector:
    """Wake Word Detector monitoring microphone for activation trigger words with regex boundary matching."""

    def __init__(self, wake_words: Optional[List[str]] = None) -> None:
        self.wake_words = [w.lower() for w in (wake_words or settings.assistant.wake_words)]
        self.wake_words.extend([
            "হে মটু", "হেই মটু", "মটু শোনো", "মটু শোন", "মটু",
            "hey motu", "motu listen", "motu",
            "হে এক্স", "হেই এক্স", "এক্স শোনো", "এক্স শোন", "এক্সে", "এক্স",
            "hey x", "x listen", "x"
        ])
        self.is_listening = False
        self._waiting_logged = False

    def is_wake_word_present(self, text: str) -> Tuple[bool, str]:
        """
        Check if input text contains any configured wake word using boundary matching.
        
        Args:
            text: Input phrase recognized by STT engine.
            
        Returns:
            Tuple of (wake_word_found_bool, remaining_command_text).
        """
        if not text:
            return False, ""

        clean_text = text.lower().strip()
        # Sort wake words by length descending so multi-word wake phrases ("hey x", "x listen") match before single "x"
        sorted_words = sorted(self.wake_words, key=len, reverse=True)

        for word in sorted_words:
            # Use boundary matching suitable for ASCII and Unicode Bangla scripts
            pattern = r'(?:^|\s|\b)' + re.escape(word) + r'(?:$|\s|\b)'
            match = re.search(pattern, clean_text)
            if match:
                # Extract command text remaining after removing the wake word
                command_remainder = re.sub(pattern, " ", clean_text, count=1).strip()
                return True, command_remainder

        return False, ""

    def listen_for_wake_word(self, on_detected_callback: Optional[Callable[[str], None]] = None) -> Tuple[bool, str]:
        """
        Perform a single listening iteration for wake word.
        
        Args:
            on_detected_callback: Function executed when wake word is detected, passing command payload.
            
        Returns:
            Tuple of (wake_word_detected_bool, command_payload).
        """
        if not self._waiting_logged:
            print("Waiting for wake word...")
            logger.debug("Waiting for wake word...")
            self._waiting_logged = True

        recognized_text = stt_engine.listen_and_recognize(timeout=3, phrase_time_limit=8)
        if recognized_text:
            print(f"[Voice System] Recognized speech: \"{recognized_text}\"")
            is_present, command_payload = self.is_wake_word_present(recognized_text)
            if is_present:
                print(f"[Voice System] Wake word detected in phrase: \"{recognized_text}\" (Command payload: '{command_payload}')")
                logger.info(f"[Voice System] Wake word detected: '{recognized_text}' -> payload: '{command_payload}'")
                event_bus.publish("wake_word_detected", text=recognized_text)
                self._waiting_logged = False
                if on_detected_callback:
                    on_detected_callback(command_payload)
                return True, command_payload

        return False, ""

    def start_loop(self, on_detected_callback: Callable[[str], None]) -> None:
        """Run continuous wake word listening loop in background thread."""
        self.is_listening = True
        self._waiting_logged = False
        print("\n[Voice System] Wake word detector active.")
        print("[Voice System] Listening for 'X', 'Hey X', 'X Listen', 'এক্স'...")
        logger.info("[Voice System] Wake word detector active.")

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
