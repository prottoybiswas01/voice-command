"""
Speech-To-Text (STT) Engine for X Assistant (Phase 6 Final Upgrade).
Handles Audio Input Capture from Microphone via PyAudio / sounddevice with Voice Activity Detection (VAD),
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
    """Speech-To-Text engine supporting PyAudio & sounddevice microphone audio capture with VAD."""

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

    def _record_audio_sounddevice(self, timeout: int = 4, phrase_time_limit: int = 8) -> Optional[sr.AudioData]:
        """
        Record audio from default microphone using sounddevice with RMS Energy Voice Activity Detection (VAD).
        Automatically detects speech start and stops recording when speech ends.
        """
        sample_rate = 16000
        chunk_duration = 0.1  # 100ms chunks
        chunk_samples = int(sample_rate * chunk_duration)
        silence_threshold = 250  # RMS energy threshold for speech
        max_silence_duration = 1.0  # Stop 1.0s after speech ends

        audio_frames = []
        speech_started = False
        silence_start_time = None
        start_time = time.time()

        try:
            with sd.InputStream(samplerate=sample_rate, channels=1, dtype='int16') as stream:
                while True:
                    elapsed = time.time() - start_time
                    if not speech_started and elapsed > timeout:
                        return None
                    if speech_started and (time.time() - start_time) > phrase_time_limit:
                        break

                    data, _ = stream.read(chunk_samples)
                    samples = np.frombuffer(data, dtype=np.int16)
                    if len(samples) == 0:
                        continue

                    # RMS energy calculation
                    rms = np.sqrt(np.mean(samples.astype(np.float32)**2))

                    if rms > silence_threshold:
                        if not speech_started:
                            speech_started = True
                            start_time = time.time()
                        audio_frames.append(data.tobytes())
                        silence_start_time = None
                    else:
                        if speech_started:
                            audio_frames.append(data.tobytes())
                            if silence_start_time is None:
                                silence_start_time = time.time()
                            elif time.time() - silence_start_time >= max_silence_duration:
                                break

            if speech_started and audio_frames:
                raw_bytes = b"".join(audio_frames)
                return sr.AudioData(raw_bytes, sample_rate, 2)
        except Exception as err:
            logger.error(f"sounddevice VAD capture error: {err}")

        return None

    def listen_and_recognize(self, timeout: int = 4, phrase_time_limit: int = 8, language: Optional[str] = None) -> Optional[str]:
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

        # B. Capture via sounddevice Microphone Stream with VAD
        elif self.backend == "sounddevice" and sd and np:
            audio_data = self._record_audio_sounddevice(timeout=timeout, phrase_time_limit=phrase_time_limit)

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
        return self.listen_and_recognize(timeout=4, phrase_time_limit=8)


# Global STT Engine instance
stt_engine = STTEngine()
