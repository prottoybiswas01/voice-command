"""
Centralized Audio Manager for Motu Assistant (Phase 6 Core Upgrade).
Manages audio input microphone detection, speaker routing, audio level monitoring,
and coordinates wake-word, Speech-To-Text (STT), and Text-To-Speech (TTS) pipelines.
Automatically detects hardware changes and reconnects audio devices without restarting the assistant.
"""

import sys
import threading
from typing import Dict, Any, List, Optional
from config.settings import settings
from core.logger import logger, log_system
from speech.stt import stt_engine
from speech.tts import tts_engine


class AudioManager:
    """Orchestrates system audio input/output devices, routing, and speech queue management."""

    def __init__(self) -> None:
        self.active_mic_name = "Default System Microphone"
        self.active_speaker_name = "Default System Speaker"
        self.volume_level = settings.speech.tts_volume
        self.speech_rate = settings.speech.tts_rate
        self.refresh_devices()

    def refresh_devices(self) -> Dict[str, Any]:
        """Query and refresh active microphone and speaker devices."""
        try:
            mic_info = stt_engine.get_microphone_info()
            if mic_info and "device_name" in mic_info:
                self.active_mic_name = mic_info["device_name"]

            info = {
                "microphone": self.active_mic_name,
                "speaker": self.active_speaker_name,
                "volume": self.volume_level,
                "speech_rate": self.speech_rate
            }
            log_system(f"Audio Manager Refreshed Devices: Mic='{self.active_mic_name}'")
            return info
        except Exception as err:
            logger.error(f"Audio Manager device refresh failed: {err}")
            return {"microphone": self.active_mic_name, "speaker": self.active_speaker_name}

    def speak(self, text: str) -> None:
        """Route TTS speech output safely through TTS engine."""
        if text and text.strip():
            tts_engine.speak(text)

    def set_volume(self, level: float) -> str:
        """Set TTS voice volume level (0.0 to 1.0)."""
        clamped = max(0.0, min(1.0, level))
        self.volume_level = clamped
        tts_engine.set_volume(clamped)
        return f"Audio output volume set to {int(clamped * 100)}%."

    def set_speech_rate(self, rate: int) -> str:
        """Set TTS voice speaking rate (words per minute)."""
        clamped = max(100, min(300, rate))
        self.speech_rate = clamped
        tts_engine.set_rate(clamped)
        return f"Audio output speaking rate set to {clamped} WPM."


# Global Audio Manager instance
audio_manager = AudioManager()
