"""
Text-To-Speech (TTS) Engine for X Assistant.
Converts text responses to natural sounding spoken audio using pyttsx3 (SAPI5 offline engine).
"""

import threading
import queue
from typing import Optional
from config.settings import settings
from core.logger import logger

try:
    import pyttsx3
except ImportError:
    pyttsx3 = None
    logger.warning("pyttsx3 module not installed. TTS will default to console output.")


class TTSEngine:
    """Offline Text-To-Speech engine using SAPI5 with async queue playback."""

    def __init__(self) -> None:
        self.engine = None
        self.speech_queue: queue.Queue = queue.Queue()
        self.is_running = False
        self._worker_thread: Optional[threading.Thread] = None

        if pyttsx3:
            try:
                self.engine = pyttsx3.init()
                self.engine.setProperty("rate", settings.speech.tts_rate)
                self.engine.setProperty("volume", settings.speech.tts_volume)
                
                # Attempt to select best voice (prefer standard natural voice if available)
                voices = self.engine.getProperty("voices")
                if voices:
                    # Select first default female or male voice
                    self.engine.setProperty("voice", voices[0].id)

                logger.info("Text-To-Speech engine initialized successfully.")
            except Exception as err:
                logger.error(f"Failed to initialize pyttsx3 engine: {err}")
                self.engine = None

        self.start_worker()

    def start_worker(self) -> None:
        """Start background worker thread for non-blocking speech execution."""
        self.is_running = True
        self._worker_thread = threading.Thread(target=self._process_queue, daemon=True)
        self._worker_thread.start()

    def _process_queue(self) -> None:
        """Process queued text items and speak them sequentially."""
        while self.is_running:
            try:
                text = self.speech_queue.get(timeout=1.0)
                if not text:
                    continue

                logger.info(f"Speaking: {text}")
                print(f"\n🤖 X Assistant: {text}\n")

                if self.engine:
                    try:
                        self.engine.say(text)
                        self.engine.runAndWait()
                    except Exception as speech_err:
                        logger.error(f"Error speaking text with pyttsx3: {speech_err}")

                self.speech_queue.task_done()
            except queue.Empty:
                continue
            except Exception as err:
                logger.error(f"TTS Worker exception: {err}")

    def speak(self, text: str, sync: bool = False) -> None:
        """
        Speak specified text prompt.
        
        Args:
            text: Text to speak out loud.
            sync: If True, blocks until speech is finished.
        """
        if not text or not text.strip():
            return

        self.speech_queue.put(text.strip())

        if sync:
            self.speech_queue.join()

    def stop(self) -> None:
        """Stop current speech and clear queue."""
        with self.speech_queue.mutex:
            self.speech_queue.queue.clear()
        if self.engine:
            try:
                self.engine.stop()
            except Exception:
                pass


# Global TTS Engine instance
tts_engine = TTSEngine()
