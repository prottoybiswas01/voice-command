"""
Speech-To-Text (STT) Engine for X Assistant (Phase 6 Debugged & Upgraded).
Handles Audio Input Capture from Microphone via PyAudio / sounddevice,
initializes ambient noise thresholds, and converts speech to text using SpeechRecognition.
"""

import sys
import time
from typing import Optional
from config.settings import settings
from core.logger import logger

try:
    import speech_recognition as sr
except ImportError:
    sr = None
    logger.warning("speech_recognition module is not installed. STT fallback mode active.")

try:
    import sounddevice as sd
    import numpy as np
except ImportError:
    sd = None
    np = None


class STTEngine:
    """Speech-To-Text engine supporting PyAudio & sounddevice microphone audio capture."""

    def __init__(self) -> None:
        self.recognizer = sr.Recognizer() if sr else None
        self.microphone = None
        self.is_available = False
        self.backend = "none"

        print("\n[Voice System] Initializing Microphone...")
        logger.info("[Voice System] Initializing Microphone...")

        if not sr:
            print("[Voice System] WARNING: speech_recognition library missing. Run setup.bat / install.bat.")
            logger.warning("speech_recognition library missing.")
            return

        # Attempt 1: PyAudio / SpeechRecognition native Microphone
        try:
            self.microphone = sr.Microphone()
            with self.microphone as source:
                self.recognizer.adjust_for_ambient_noise(source, duration=0.5)
            self.is_available = True
            self.backend = "pyaudio"
            print("[Voice System] Microphone initialized successfully. (Backend: PyAudio)")
            logger.info("Microphone initialized successfully via PyAudio.")
            return
        except Exception as err:
            logger.debug(f"PyAudio microphone init failed: {err}. Attempting sounddevice backend...")

        # Attempt 2: sounddevice + numpy microphone audio capture
        if sd and np:
            try:
                # Query default input audio device
                dev_info = sd.query_devices(kind='input')
                dev_name = dev_info.get('name', 'Default Microphone')
                self.is_available = True
                self.backend = "sounddevice"
                print(f"[Voice System] Microphone initialized successfully. (Backend: sounddevice - {dev_name})")
                logger.info(f"Microphone initialized successfully via sounddevice ({dev_name}).")
                return
            except Exception as err:
                logger.warning(f"sounddevice microphone check failed: {err}")

        print("[Voice System] WARNING: Microphone hardware not available. Voice STT operating in fallback prompt mode.")
        logger.warning("Microphone hardware not available.")

    def listen_and_recognize(self, timeout: int = 5, phrase_time_limit: int = 8, language: Optional[str] = None) -> Optional[str]:
        """
        Listen to microphone input and convert to text.
        
        Args:
            timeout: Max seconds to wait for speech start.
            phrase_time_limit: Max duration of recorded phrase.
            language: Speech language code ('bn-BD', 'en-US').
            
        Returns:
            Recognized speech string or None.
        """
        if not self.is_available or not self.recognizer:
            return None

        lang = language or settings.speech.stt_language_primary
        audio_data = None

        print("Listening...")
        logger.info("Listening...")

        # A. Capture via PyAudio Native Microphone
        if self.backend == "pyaudio" and self.microphone:
            try:
                with self.microphone as source:
                    audio_data = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            except sr.WaitTimeoutError:
                return None
            except Exception as err:
                logger.error(f"PyAudio capture error: {err}")
                return None

        # B. Capture via sounddevice Microphone Buffer
        elif self.backend == "sounddevice" and sd and np:
            try:
                sample_rate = 16000
                channels = 1
                recording = sd.rec(int(phrase_time_limit * sample_rate), samplerate=sample_rate, channels=channels, dtype='int16')
                sd.wait()
                raw_bytes = recording.tobytes()
                audio_data = sr.AudioData(raw_bytes, sample_rate, 2)
            except Exception as err:
                logger.error(f"sounddevice capture error: {err}")
                return None

        if not audio_data:
            return None

        print("[Voice System] Processing speech recognition...")
        logger.info("[Voice System] Processing speech recognition...")

        # Primary Language Recognition (bn-BD / Bangla)
        try:
            text = self.recognizer.recognize_google(audio_data, language=lang)
            if text and text.strip():
                print(f"[Voice System] Recognized speech ({lang}): \"{text}\"")
                logger.info(f"Recognized speech ({lang}): \"{text}\"")
                return text.strip()
        except sr.UnknownValueError:
            pass
        except sr.RequestError as req_err:
            logger.error(f"Speech recognition API error: {req_err}")
            return None
        except Exception:
            pass

        # Secondary Language Fallback Recognition (en-US / English)
        secondary_lang = settings.speech.stt_language_secondary
        if lang != secondary_lang:
            try:
                text = self.recognizer.recognize_google(audio_data, language=secondary_lang)
                if text and text.strip():
                    print(f"[Voice System] Recognized speech ({secondary_lang}): \"{text}\"")
                    logger.info(f"Recognized speech ({secondary_lang}): \"{text}\"")
                    return text.strip()
            except Exception:
                pass

        return None

    def listen_once(self) -> Optional[str]:
        """Convenience single listening cycle."""
        return self.listen_and_recognize(timeout=5, phrase_time_limit=10)


# Global STT Engine instance
stt_engine = STTEngine()
