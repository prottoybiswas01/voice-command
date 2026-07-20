"""
Text-To-Speech (TTS) Engine for X Assistant (Phase 6 Debugged & Upgraded).
Provides spoken audio synthesis via pyttsx3 with console output fallback.
"""

import sys
import threading
from typing import Optional
from config.settings import settings
from core.logger import logger

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    logger.warning("pyttsx3 module not installed. TTS will default to console output.")


class TTSEngine:
    """Text-To-Speech engine supporting PyTTSx3 voice synthesis."""

    def __init__(self) -> None:
        self.engine = None
        self.is_available = False

        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", settings.speech.tts_rate)
                self.engine.setProperty("volume", settings.speech.tts_volume)
                self.is_available = True
                logger.info("Text-To-Speech engine initialized successfully.")
            except Exception as err:
                logger.warning(f"PyTTSx3 TTS initialization failed: {err}. Defaulting to console speech output.")

    def speak(self, text: str, sync: bool = False) -> None:
        """
        Synthesize speech from input text and output to speaker / console.
        
        Args:
            text: Text to speak.
            sync: If True, blocks thread until speech completes.
        """
        if not text or not text.strip():
            return

        clean_text = text.strip()
        print(f"\n🤖 [Assistant Speech]: {clean_text}\n")
        logger.info(f"Assistant Speech: {clean_text}")

        if not self.is_available or not self.engine:
            return

        def _speak_worker():
            try:
                self.engine.say(clean_text)
                self.engine.runAndWait()
            except Exception as err:
                logger.error(f"TTS Speech error: {err}")

        if sync:
            _speak_worker()
        else:
            threading.Thread(target=_speak_worker, daemon=True).start()

    def stop(self) -> None:
        """Stop TTS playback."""
        if self.is_available and self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass


# Global TTS Engine instance
tts_engine = TTSEngine()
