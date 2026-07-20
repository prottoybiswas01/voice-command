"""
Speech-To-Text (STT) Engine for X Assistant.
Handles audio input capture from Microphone and converts speech to text using SpeechRecognition / Vosk.
"""

import sys
from typing import Optional
from config.settings import settings
from core.logger import logger

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logger.warning("speech_recognition module is not installed. STT fallback to text prompt mode.")


class STTEngine:
    """Speech-To-Text engine supporting PyAudio / SpeechRecognition with language selection."""

    def __init__(self) -> None:
        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = None
        self.is_available = False

        if sr:
            try:
                self.microphone = sr.Microphone()
                with self.microphone as source:
                    self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
                self.is_available = True
                logger.info("Microphone and Speech Recognition initialized successfully.")
            except Exception as err:
                logger.warning(f"Microphone initialization failed: {err}. Speech input disabled.")

    def listen_and_recognize(self, timeout: int = 5, phrase_time_limit: int = 8, language: Optional[str] = None) -> Optional[str]:
        """
        Listen to microphone input and convert to text.
        
        Args:
            timeout: Max seconds to wait for speech to start.
            phrase_time_limit: Max duration of recognized phrase.
            language: Speech language code ('bn-BD', 'en-US', or settings default).
            
        Returns:
            Recognized string prompt, or None if unrecognized/failed.
        """
        if not self.is_available or not self.recognizer or not self.microphone:
            return None

        lang = language or settings.speech.stt_language_primary

        try:
            with self.microphone as source:
                logger.debug("Listening for voice input...")
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)

            logger.debug("Processing speech recognition...")
            
            # First attempt recognition with primary language (e.g. Bangla bn-BD)
            try:
                text = self.recognizer.recognize_google(audio, language=lang)
                if text:
                    logger.info(f"STT Recognized ({lang}): {text}")
                    return text
            except sr.UnknownValueError:
                # If primary language fails, fallback to secondary language (e.g. English en-US)
                secondary_lang = settings.speech.stt_language_secondary
                if lang != secondary_lang:
                    try:
                        text = self.recognizer.recognize_google(audio, language=secondary_lang)
                        if text:
                            logger.info(f"STT Recognized Fallback ({secondary_lang}): {text}")
                            return text
                    except Exception:
                        pass
                return None
            except sr.RequestError as req_err:
                logger.error(f"Speech recognition service error: {req_err}")
                return None

        except sr.WaitTimeoutError:
            logger.debug("Listening timed out waiting for speech.")
            return None
        except Exception as err:
            logger.error(f"Unexpected error in STT engine: {err}")
            return None

    def listen_once(self) -> Optional[str]:
        """Convenience method for a single listening cycle."""
        return self.listen_and_recognize(timeout=5, phrase_time_limit=10)


# Global STT engine instance
stt_engine = STTEngine()
