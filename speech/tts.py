"""
Text-To-Speech (TTS) Engine for Motu Assistant (Phase 6 Core Upgrade).
Provides thread-safe spoken audio synthesis via PyTTSx3 with COM context isolation
and console output fallback.
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
    """Thread-safe Text-To-Speech engine supporting PyTTSx3 voice synthesis."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self.is_available = pyttsx3 is not None
        if self.is_available:
            logger.info("Text-To-Speech engine initialized successfully.")
        else:
            logger.warning("PyTTSx3 unavailable. Defaulting to console speech output.")

    def speak(self, text: str, sync: bool = False) -> None:
        """
        Synthesize speech from input text and output to speaker / console.
        Thread-safe wrapper isolating SAPI5 COM engine per call.
        """
        if not text or not text.strip():
            return

        clean_text = text.strip()
        print(f"\n🤖 [Assistant Speech]: {clean_text}\n")
        logger.info(f"Assistant Speech: {clean_text}")

        if not self.is_available:
            return

        def _speak_worker():
            with self._lock:
                try:
                    engine = pyttsx3.init()
                    engine.setProperty("rate", settings.speech.tts_rate)
                    engine.setProperty("volume", settings.speech.tts_volume)
                    engine.say(clean_text)
                    engine.runAndWait()
                    engine.stop()
                except Exception as err:
                    logger.error(f"TTS Speech error: {err}")

        if sync:
            _speak_worker()
        else:
            threading.Thread(target=_speak_worker, daemon=True).start()

    def set_volume(self, volume: float) -> None:
        """Update TTS volume setting."""
        settings.speech.tts_volume = max(0.0, min(1.0, volume))

    def set_rate(self, rate: int) -> None:
        """Update TTS speech rate setting."""
        settings.speech.tts_rate = max(100, min(300, rate))

    def stop(self) -> None:
        """Stop active speech."""
        pass


# Global TTS Engine instance
tts_engine = TTSEngine()
