"""
Screen and Audio Microphone Recorder Module for X Assistant (Phase 3).
Handles desktop video screen recording and microphone voice audio recording.
"""

import time
import wave
import threading
from datetime import datetime
from pathlib import Path
from typing import Optional
from config.settings import settings
from core.logger import logger
from core.database import db

try:
    import pyaudio
except ImportError:
    pyaudio = None

try:
    import pyautogui
except ImportError:
    pyautogui = None


class ScreenAndAudioRecorder:
    """Manages background screen video capture and microphone audio recording."""

    def __init__(self) -> None:
        self.recordings_dir = settings.paths.recordings_dir
        self.audio_dir = settings.paths.audio_dir
        self.recordings_dir.mkdir(parents=True, exist_ok=True)
        self.audio_dir.mkdir(parents=True, exist_ok=True)

        self.is_recording_audio = False
        self.is_recording_screen = False
        self._audio_thread: Optional[threading.Thread] = None

    def record_audio_note(self, duration_seconds: int = 10) -> str:
        """
        Record microphone audio for specified duration seconds.
        
        Args:
            duration_seconds: Recording duration in seconds.
            
        Returns:
            Status message with saved .wav file path.
        """
        if not pyaudio:
            return "PyAudio module is required for microphone recording."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"voice_note_{timestamp}.wav"
        filepath = self.audio_dir / filename

        def _record_worker():
            try:
                p = pyaudio.PyAudio()
                stream = p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=44100,
                    input=True,
                    frames_per_buffer=1024
                )

                logger.info(f"Recording audio for {duration_seconds} seconds...")
                frames = []

                for _ in range(0, int(44100 / 1024 * duration_seconds)):
                    data = stream.read(1024)
                    frames.append(data)

                stream.stop_stream()
                stream.close()
                p.terminate()

                with wave.open(str(filepath), "wb") as wf:
                    wf.setnchannels(1)
                    wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
                    wf.setframerate(44100)
                    wf.writeframes(b"".join(frames))

                logger.info(f"Audio recording saved: {filepath.name}")
                db.log_command("record_audio", "SUCCESS", str(filepath))
            except Exception as err:
                logger.error(f"Error recording audio: {err}")

        self._audio_thread = threading.Thread(target=_record_worker, daemon=True)
        self._audio_thread.start()

        msg = f"Started audio recording for {duration_seconds} seconds. Saving to: '{filename}'."
        return msg

    def record_screen_snapshot_series(self, duration_seconds: int = 5) -> str:
        """
        Capture sequence of desktop screen snapshots.
        
        Args:
            duration_seconds: Duration of snapshot sequence.
        """
        if not pyautogui:
            return "PyAutoGUI is required for screen recording."

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        session_dir = self.recordings_dir / f"screen_rec_{timestamp}"
        session_dir.mkdir(parents=True, exist_ok=True)

        def _screen_worker():
            try:
                end_time = time.time() + duration_seconds
                idx = 1
                while time.time() < end_time:
                    filepath = session_dir / f"frame_{idx:04d}.png"
                    pyautogui.screenshot(str(filepath))
                    idx += 1
                    time.sleep(0.5)

                logger.info(f"Captured {idx-1} screen frames to: {session_dir.name}")
                db.log_command("record_screen", "SUCCESS", str(session_dir))
            except Exception as err:
                logger.error(f"Error recording screen: {err}")

        thread = threading.Thread(target=_screen_worker, daemon=True)
        thread.start()

        msg = f"Started screen recording for {duration_seconds} seconds. Frames saving to: '{session_dir.name}'."
        return msg


# Global Recorder instance
recorder = ScreenAndAudioRecorder()
